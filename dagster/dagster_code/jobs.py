import dagster as dg


# Job for Kaggle file download and DuckDB creation/inserts
file_load_job = dg.define_asset_job(
    name="01_file_load_job",
    selection=[
        # kaggle_loan_data_csv,
        "raw_loan_data",
    ]
)

# Job for generating tables from DBT models
dbt_assets_job = dg.define_asset_job(
    name="02_dbt_assets_job",
    selection=[
        "stg_loan_data_selected_cols",
        "dim_borrowers",
        "dim_loans",
        "fct_loan_data"
    ]
)

# Job for generating Parquet file from final dataset
file_extracts_job = dg.define_asset_job(
    name="03_file_extracts_job",
    selection=[
        "loan_data_parquet"
    ]
)
