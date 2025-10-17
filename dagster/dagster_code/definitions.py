import dagster as dg
from dagster_code.assets import (
    # kaggle_loan_data_csv,
    raw_loan_data,
    # dbt_project_assets,
    stg_loan_data_selected_cols,
    dim_calendar,
    dim_borrowers,
    dim_loans,
    loan_data_parquet,
    fct_loan_data,
)
from dagster_code.resources import (
    duckdb_resource,
    dbt_resource,
)
from dagster_code.jobs import (
    file_load_job,
    dbt_assets_job,
    file_extracts_job,
)


@dg.definitions
def resources():
    return dg.Definitions(
        assets=[
            # kaggle_loan_data_csv,
            raw_loan_data,
            # dbt_project_assets,
            stg_loan_data_selected_cols,
            dim_calendar,
            dim_borrowers,
            dim_loans,
            loan_data_parquet,
            fct_loan_data,
            loan_data_parquet,
        ],
        resources={
            "duckdb": duckdb_resource,
            "dbt": dbt_resource,
        },
        jobs=[
            file_load_job,
            dbt_assets_job,
            file_extracts_job,
        ]
    )
