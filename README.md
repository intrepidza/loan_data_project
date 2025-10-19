
# Loan data ETL and Dashboard mini-project

## Description:

Small end to end data project that uses the Kaggle python package to download a dataset relating to Lending Club loan data between the years 2007 to 2020, loads the raw data into a DuckDB database after which DBT SQL models are used to transform the data and create dimension and fact tables from which a final dataset is derived and extracted in a Parquet file to be referenced in a Streamlit dashboard. 

The entire process is orchestrated with Dagster.

## Dataset details:
Dataset URL: https://www.kaggle.com/datasets/ethon0426/lending-club-20072020q1

To note:
- File has over 2.9 million records and 142 columns.
- It includes accepted loans issued by Lending Club over between the years 2007 through 2020, including details on borrower characteristics, credit and account history, loan terms, loan status (current, paid, default, etc.).
- I'm using this dataset even though it's US related, since there does not appear to be a readily available SA dataset.
- According to the dictionary, the dataset once container a 'member_id' column representing a borrower. This no longer exists. For the sake of simplification, it will be assumed that every loan entry is associated with a unique borrower. (using same 'id')
- Limitations of the dataset are that it mostly reflects approved loans. No view of the methodology used to approve the loans.
- Data is more useful as a post-issuance risk check to assess how much money is allocated to which types of loans, and the associated credit grades.

## Dashboard is viewable at:
- https://loandatadashboard.streamlit.app

The resulting Dashboard represents data between 2018 and 2020. This is read from the parquet file 'loan_data.parquet' residing in the current source Github repository. (Only a subset of years were extracted owing to Github and Streamlit file-size limitations for free usage.)

The Dashboard allows one to filter on the Loan Purpose, Credit Rating and State. It provides an overview of the amount loaned, what purpose it was loaned for, the States of borrowers to which money was loaned, the term, and relating Credit Grades.

![alt text](https://github.com/intrepidza/loan_data_project/blob/main/assets/loan_data_dashboard.png?raw=true)


## Important files/folders:

```
├── dagster
│   ├── dagster_code                    <-- Contains Dagster Resource + Assets 
│   │   ├── assets.py
│   │   ├── definitions.py
│   │   ├── jobs.py
│   │   └── resources.py
├── dbt_data
│   ├── models
│   │   ├── loan_data                   <-- Contains DBT Model SQL
│   │   │   ├── dim_borrowers.sql
│   │   │   ├── dim_calendar.sql
│   │   │   ├── dim_loans.sql
│   │   │   ├── fct_loan_data.sql
│   │   │   └── stg_loan_data_selected_cols.sql
│   │   └── sources.yml
├── ddb_queries.ipynb                   <-- Jupyter Notebook DuckDB adhoc queries
├── loan_data.parquet
├── requirements.txt                    <-- Requirements for Streamlit
├── requirements_local.txt              <-- Requirements for local install
└── streamlit_app.py                    <-- Script used by Streamlit
```


# In order to run locally:

## Requirements:
- Python 3.12
- Own Kaggle account and generation of API Token. 

## Steps:

1) Copy Github branch to local computer path:

    git clone https://github.com/intrepidza/loan_data_project.git

2) Create .env file in project root folder with variables:

    KAGGLE_USERNAME="[ENTER_YOUR_USERNAME_HERE]"

    KAGGLE_KEY="[ENTER_YOUR_API_KEY_HERE]"

3) Using PowerShell, navigate to root of project and create python virtual environment with command: 

    python -m venv .venv

4) Activate virtual environment with command: 

    .venv/scripts/activate

5) Install Python dependencies with command: 

    pip install -r requirements_local.txt

6) Navigate to 'dagster' folder and run command: 

    $env:DAGSTER_HOME = Get-Location

7) Run command: 

    dagster dev

8) In web-browser:
- Navigate to: http://127.0.0.1:3000
- Jobs > click ellipsis '...' next to '01_file_load_job' > Launch new run
- Jobs > click ellipsis '...' next to '02_dbt_model_transformation_job' > Launch new run (confirm if prompted)
- Jobs > click ellipsis '...' next to '03_file_extracts_job' > Launch new run (confirm if prompted)

![alt text](https://github.com/intrepidza/loan_data_project/blob/main/assets/job_run.png?raw=true)

- Assets > View Lineage > Click gear icon on bottom right > Change graph to horizontal orientation (to view Assets as they materialize)

![alt text](https://github.com/intrepidza/loan_data_project/blob/main/assets/dagster_asset_materialization.png?raw=true)


(Job method of materialization necessary since DuckDB is a single-user database. Alternative would be to change dependencies.)

9) To run Streamlit locally:
- Navigate back to project root path and run command: streamlit run streamlit_app.py 


## Result:

Dagster will materialize the below assets in order:

### 01_file_load_job:
- kaggle_loan_data_csv = Uses 'kaggle' Python module to download the dataset from Kaggle website in CSV format
- raw_loan_data =  Imports the resulting CSV file into a table in a newly created DuckDB database 'loan_data.duckdb' in Project root directory

### 02_dbt_assets_job:
- stg_loan_data_selected_cols = uses DBT model to populate table with subset of columns from the 'raw_loan_data' table
- dim_borrowers = uses DBT model to populate dimension table with borrower specific attributes
- dim_loans = uses DBT model to populate dimension table with loan specific attributes
- fct_loan_data = uses DBT model to populate fact table with loan specific measures

![alt text](https://github.com/intrepidza/loan_data_project/blob/main/assets/dbt_lineage.png?raw=true)

### 03_file_extracts_job:
- loan_data_parquet = Generates a Parquet file from dimension tables and fact table. (Currently limited to 1.5 million rows owing to Github/Streamlit free usage limits.)


