{{ config(materialized='table') }}

SELECT
    member_id as borrower_id,
    annual_inc,
    emp_length
    emp_title,
    emp_length,
    home_ownership, 
    annual_inc, 
    addr_state,
    fico_range_low,
    fico_range_high  

FROM {{ ref('stg_loan_data_selected_cols') }}
