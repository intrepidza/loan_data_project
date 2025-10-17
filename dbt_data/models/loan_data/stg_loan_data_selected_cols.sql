{{ config(materialized='table') }}

SELECT
    id AS loan_id,
    id AS member_id,
    loan_amnt,
    funded_amnt,
    term,
    int_rate,
    installment,
    grade,
    sub_grade,
    emp_title,
    emp_length,
    home_ownership, 
    annual_inc, 
    LAST_DAY(CAST(strptime(issue_d, '%b-%Y') AS DATE)) AS issue_date,
    loan_status,
    purpose,
    title,
    addr_state,
    fico_range_low,
    fico_range_high
FROM {{ source('duckdb', 'raw_loan_data') }}