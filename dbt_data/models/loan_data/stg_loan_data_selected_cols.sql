{{ config(materialized='table') }}

SELECT
    CAST(id AS INT) AS loan_id,
    CAST(id AS INT) AS borrower_id,
    loan_amnt AS loan_amount,
    funded_amnt AS funded_amount,
    term,
    int_rate AS interest_rate,
    installment,
    grade,
    sub_grade,
    emp_title AS employment_title,
    emp_length AS employment_length,
    home_ownership, 
    annual_inc AS annual_income, 
    LAST_DAY(CAST(strptime(issue_d, '%b-%Y') AS DATE)) AS issue_date,
    loan_status,
    purpose,
    title,
    addr_state AS address_state,
    fico_range_low,
    fico_range_high
FROM {{ source('duckdb', 'raw_loan_data') }}
WHERE SUBSTRING(issue_d, 5, 8) >= '2018'