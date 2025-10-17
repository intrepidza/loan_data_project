{{ config(
    materialized='table',
    unique_key='calendar_id'
) }}

WITH stg_data AS (
    SELECT DISTINCT
        issue_date,
        DATE_PART('year', issue_date) AS issue_year,
    FROM {{ ref('stg_loan_data_selected_cols') }}
    ORDER BY issue_date
)

SELECT
    {{ dbt_utils.generate_surrogate_key(['issue_date']) }} AS calendar_id,
    issue_date,
    issue_year

FROM stg_data
ORDER BY issue_date