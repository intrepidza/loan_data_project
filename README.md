Description:

Loan origination ETL and Dashboard mini-project
It uses the Kaggle python package to download a Kaggle dataset relating to Lending Club loan data between the years 2007 to 2020...
DBT SQL models are used to derive the dimension and fact tables in a DuckDB database.
A Parquet file is generated from the resulting tables, to be used by Streamlit.
Dagster is used to orchestrate the process.

-----------

Dataset details:
URL: https://www.kaggle.com/datasets/ethon0426/lending-club-20072020q1

To note: 
- According to the dictionary, the dataset once container a 'member_id' column representing a borrower. This no longer exists. For the sake of simplification, it will be assumed that every loan entry is associated with a unique borrower. (using same 'id')


-----------

Dashboard is viewable at:
- https://loandatadashboard.streamlit.app

loan_data.parquet - Showing only data from 2016 onwards.
( out of 2.9+ million rows)
(This is owing to Github and Streamlit file-size limitations for free usage.)



-----------

Requirements:
- Python 3.12
- Own Kaggle account

-----------

N.B. Folders:

loan_origination_project/

├─ dagster/

│  ├─ dagster_code/     <--- Contains definitions for Dagster Assets/Resources/Jobs

│  │  ├─ assets.py      <--- Dagster Assets...

├─ dbt_data/

│  ├─ models/           <--- Contains DBT SQL models

-----------

Steps:

-----------

1) Copy branch to local compute path.

2) Create .env file in project root folder with variables:
    KAGGLE_USERNAME="[ENTER_YOUR_USERNAME_HERE]"
    KAGGLE_KEY="[ENTER_YOUR_API_KEY_HERE]"

2) Using PowerShell, navigate to root of project and create python virtual environment with command: python -m venv .venv

3) Activate virtual environment with command: .venv/scripts/activate

4) Install Python dependencies with command: pip install -r requirements_local.txt

5) Navigate to 'dagster' folder and run command: $env:DAGSTER_HOME = Get-Location

6) Run command: dagster dev

7) In web-browser:
    - navigate to: http://127.0.0.1:3000
    - Jobs > click ellipsis '...' next to '01_file_load_job' > Launch new run
    - Jobs > click ellipsis '...' next to '02_dbt_assets_job' > Launch new run
    - Jobs > click ellipsis '...' next to '03_file_extracts_job' > Launch new run

-----------

Dagster will materialize the below assets in order:

    '01_file_load_job':
    - kaggle_loan_data_csv = Uses 'kaggle' Python module to download the dataset from Kaggle website in CSV format
    - raw_loan_data =  Imports the resulting CSV file into a table in a newly created DuckDB database 'loan_data.duckdb' in Project root directory
    
    '02_dbt_assets_job':
    - stg_loan_data_selected_cols = uses DBT model to populate table with subset of columns from the 'raw_loan_data' table
    - dim_borrowers = uses DBT model to populate dimension table with borrower specific attributes
    - dim_loans = uses DBT model to populate dimension table with loan specific attributes
    - fct_loan_data = uses DBT model to populate fact table with loan specific measures

    '03_file_extracts_job':
    - loan_data_parquet = Generates a Parquet file from dimension tables and fact table. (Currently limited to 1.5 million rows owing to Github/Streamlit free usage limits.)


-----------


Dagster Lineage:

![alt text](https://github.com/intrepidza/loan_data_dashboard/blob/main/assets/dagster_lineage.jpg?raw=true)


-----------


- Pip installs:
Minimum (for Streamlit):
= streamlit
= duckdb
= plotly

Additional:
= dagster
= dagster-webserver
= dagster-dbt
= kaggle
= dbt-duckdb