{{ config(materialized='table') }}

SELECT
  loan_id,
  term,
  grade AS risk_grade,
  sub_grade AS risk_sub_grade,
  issue_date,
  DATE_PART('year', issue_date) AS issue_year,
  loan_status,
  purpose,
  title,
  CASE
    WHEN grade IN ('A', 'B') THEN 'Low Risk'
    WHEN grade IN ('C', 'D') THEN 'Medium Risk'
    ELSE 'High Risk'
  END AS risk_category

FROM {{ ref('stg_loan_data_selected_cols') }}
WHERE loan_status IS NOT NULL
