import streamlit as st
import plotly.express as px
import duckdb
import pandas as pd


# # Connect to DuckDB database and retrieve data:
# with duckdb.connect("loan_data.duckdb") as conn:
#     df_loans = conn.execute("""
#                     SELECT *
#                     FROM fct_loan_data fct
#                     INNER JOIN dim_borrowers b on b.borrower_id = fct.borrower_id
#                     INNER JOIN dim_loans l on l.loan_id = fct.loan_id
#                     INNER JOIN dim_calendar c on c.calendar_id = fct.calendar_id 
#     """).fetchdf()

@st.cache_data
def load_data(path):
    with duckdb.connect("loan_data.duckdb") as conn:
        df_loans = conn.execute("""
               SELECT *
               FROM fct_loan_data fct
               INNER JOIN dim_borrowers b on b.borrower_id = fct.borrower_id
               INNER JOIN dim_loans l on l.loan_id = fct.loan_id
               INNER JOIN dim_calendar c on c.calendar_id = fct.calendar_id
               WHERE issue_date >= '2020-01-01'         
        """).fetchdf()
        print('data loaded')
        return df_loans

# df_loans = pd.read_csv('test.csv')
# df_loans = pd.read_parquet('loan_data.parquet')

# Streamlit app
st.title("Loan Origination Dashboard")

# Filter for home ownership
st.subheader("Filter by Home Ownership")
home_ownership_options = df_loans['home_ownership'].unique().tolist()
selected_home_ownership = st.multiselect(
    "Select Home Ownership:", home_ownership_options, default=None
)

# Filter data
if selected_home_ownership:
    filtered_df = df_loans[df_loans['home_ownership'].isin(selected_home_ownership)]
else:
    filtered_df = df_loans

# Visualization 1: Loan Status Pie Chart
st.subheader("Loan Status Distribution")
status_counts = filtered_df['loan_status'].value_counts().reset_index()
status_counts.columns = ['loan_status', 'count']
pie_fig = px.pie(status_counts, values='count', names='loan_status', title='Loan Status Distribution')
st.plotly_chart(pie_fig)

# Visualization 2: Average Loan Amount by Risk Category
st.subheader("Average Loan Amount by Risk Category")
amount_by_risk = filtered_df.groupby('risk_category')['loan_amount'].mean().reset_index()
bar_fig = px.bar(amount_by_risk, x='risk_category', y='loan_amount', title='Average Loan Amount by Risk Category')
st.plotly_chart(bar_fig)

# Visualization 3: Loan Originations by Year
st.subheader("Loan Originations by Year")
year_counts = filtered_df.groupby('issue_year').size().reset_index(name='count')
line_fig = px.line(year_counts, x='issue_year', y='count', title='Loan Originations by Year')
st.plotly_chart(line_fig)
