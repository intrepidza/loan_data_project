from dagster import asset, AssetExecutionContext, AssetKey, SourceAsset, RetryPolicy
from dotenv import load_dotenv
from dagster_dbt import DbtCliResource, dbt_assets, DagsterDbtTranslator
import os
from pathlib import Path
from typing import Any, Mapping, Optional

# Load .env file variables
load_dotenv()

os.environ['KAGGLE_USERNAME'] = os.getenv('KAGGLE_USERNAME')
os.environ['KAGGLE_KEY'] = os.getenv('KAGGLE_KEY')

# import kaggle after variable specification
import kaggle

# Kaggle dataset download and DuckDB creation/insert Assets
# @asset(
#     name="kaggle_loan_data_csv",
#     group_name="01_file_loading",
#     description="Downloads Loan Dataset from Kaggle"
# )
# def kaggle_loan_data_csv(context: AssetExecutionContext) -> str:
#     dataset = "ethon0426/lending-club-20072020q1"
#     destination_dir = Path.cwd().parent
#     output_dir = destination_dir.joinpath('_processing')

#     context.log.info(f"Downloading {dataset} to {output_dir}")
#     kaggle.api.dataset_download_files(dataset, path=output_dir, unzip=True)

#     os.rename('../_processing/Loan_status_2007-2020Q3.gzip', '../_processing/Loan_status_2007-2020Q3.csv')

#     context.log.info("Download complete.")

#     return os.path.abspath(output_dir)


@asset(
        # deps=["kaggle_loan_data_csv"],
        required_resource_keys={"duckdb"},
        group_name="01_file_loading",
)
def raw_loan_data(context):
    """Load raw CSV data into DuckDB staging table."""
    csv_path = "../_processing/Loan_status_2007-2020Q3.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    db = context.resources.duckdb
    with db.connect() as conn:
        context.log.info(f"Loading {csv_path} into DuckDB...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE raw_loan_data AS
            SELECT *
            FROM read_csv('{csv_path}',
                header=true,
                delim=',',
                auto_detect=true,
                types={{'id': 'VARCHAR', 'initial_list_status': 'VARCHAR'}}
            )
        """)
        context.log.info("staging_loan_data created successfully.")

# ----------------------------------------------------------------------------------------------
# Initially attempted 'multi-asset' method for DBT assets but this does not reference dependencies correctly...

# class CustomDagsterDbtTranslator(DagsterDbtTranslator):
#     def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> Optional[str]:
#         return "02_dbt_assets"


# @dbt_assets(
#         manifest=Path("../dbt_data/target/manifest.json"),
#         dagster_dbt_translator=CustomDagsterDbtTranslator(),
#     )
# def dbt_project_assets(context: AssetExecutionContext, dbt: DbtCliResource):
#     yield from dbt.cli(["build"], context=context).stream()
# ----------------------------------------------------------------------------------------------

# DBT Assets
dbt_group_name = "02_dbt_model_transformation"


@asset(
        deps=["raw_loan_data"],
        group_name=dbt_group_name,
        pool="db",
)
def stg_loan_data_selected_cols(dbt: DbtCliResource):
    dbt.cli(["run", "--select", "stg_loan_data_selected_cols"]).wait()


@asset(
        deps=["stg_loan_data_selected_cols"],
        group_name=dbt_group_name,
        pool="db",
        retry_policy=RetryPolicy(
            max_retries=3,
            delay=5.0,  # 1 second initial delay
        )
)
def dim_calendar(dbt: DbtCliResource):
    dbt.cli(["run", "--select", "dim_calendar"]).wait()


@asset(
        deps=["stg_loan_data_selected_cols"],
        group_name=dbt_group_name,
        pool="db",
        retry_policy=RetryPolicy(
            max_retries=3,
            delay=5.0,  # 1 second initial delay
        )
)
def dim_borrowers(dbt: DbtCliResource):
    dbt.cli(["run", "--select", "dim_borrowers"]).wait()


@asset(
        deps=["stg_loan_data_selected_cols"],  #, "dim_calendar"],
        group_name=dbt_group_name,
        pool="db",
        retry_policy=RetryPolicy(
            max_retries=3,
            delay=5.0,  # 1 second initial delay
        )
)
def dim_loans(dbt: DbtCliResource):
    dbt.cli(["run", "--select", "dim_loans"]).wait()


@asset(
        deps=["stg_loan_data_selected_cols", "dim_calendar"],
        group_name=dbt_group_name,
        pool="db",
)
def fct_loan_data(dbt: DbtCliResource):
    dbt.cli(["run", "--select", "fct_loan_data"]).wait()


# Parquet file Asset for Streamlit
@asset(
        deps=["fct_loan_data", "dim_borrowers", "dim_loans"],
        required_resource_keys={"duckdb"},
        group_name="03_file_extracts",
)
def loan_data_parquet(context):
    """Generate Parquet file to be used by Streamlit."""

    db = context.resources.duckdb
    with db.connect() as conn:
        context.log.info(f"Loading dataset from DuckDB...")
        result = conn.execute(f"""
            SELECT *
            FROM fct_loan_data fct
            INNER JOIN dim_borrowers b on b.borrower_id = fct.borrower_id
            INNER JOIN dim_loans l on l.loan_id = fct.loan_id
            INNER JOIN dim_calendar c on c.calendar_id = fct.calendar_id
        """).fetchdf()

        result.to_parquet('../loan_data.parquet')

        context.log.info("Parquet file created successfully.")
