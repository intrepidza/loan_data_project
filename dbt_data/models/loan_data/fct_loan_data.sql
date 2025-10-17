{{ config(
  materialized='table'
) }}

SELECT
  loan_id,
  borrower_id,
  c.calendar_id,
  loan_amount,
  funded_amount,
  CAST(REPLACE(interest_rate, '%', '') AS DOUBLE) / 100 AS interest_rate,
  installment

FROM {{ ref('stg_loan_data_selected_cols') }} f
INNER JOIN {{ ref('dim_calendar') }} c ON c.issue_date = f.issue_date
WHERE loan_status IS NOT NULL
