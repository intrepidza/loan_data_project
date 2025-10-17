{{ config(materialized='table') }}

SELECT
    borrower_id,
    annual_income,
    employment_title,
    employment_length
    home_ownership, 
    annual_income, 
    address_state,
    fico_range_low,
    fico_range_high  

FROM {{ ref('stg_loan_data_selected_cols') }}
