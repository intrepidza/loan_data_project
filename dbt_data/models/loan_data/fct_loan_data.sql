{{ config(
  materialized='table'
) }}

SELECT
  loan_id,
  member_id AS borrower_id,
  loan_amnt AS loan_amount,
  funded_amnt AS funded_amount,
  CAST(REPLACE(int_rate, '%', '') AS DOUBLE) / 100 AS interest_rate,
  installment

FROM {{ ref('stg_loan_data_selected_cols') }}
WHERE loan_status IS NOT NULL
