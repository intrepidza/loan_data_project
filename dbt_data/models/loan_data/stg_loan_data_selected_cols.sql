{{ config(materialized='table') }}

SELECT
    CAST(id AS INT) AS loan_id,
    CAST(id AS INT) AS borrower_id,
    CAST(loan_amnt AS DECIMAL) AS loan_amount,
    term,
     CAST(REPLACE(int_rate, '%', '') AS DOUBLE) / 100 AS interest_rate,
    installment,
    grade,
    sub_grade,
    emp_title AS employment_title,
    emp_length AS employment_length,
    home_ownership, 
    annual_inc AS annual_income, 
    LAST_DAY(CAST(strptime(issue_d, '%b-%Y') AS DATE)) AS issue_date,
    loan_status,
    title,
    addr_state AS address_state,
    fico_range_low,
    fico_range_high
FROM {{ source('duckdb', 'raw_loan_data') }}
WHERE SUBSTRING(issue_d, 5, 8) >= '2018'