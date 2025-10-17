# loan_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px
import duckdb

st.set_page_config(page_title="Loan Data Dashboard", layout="wide")

@st.cache_data
def load_data(path):
    df = pd.read_parquet(path)
    print("Data loaded from Parquet file.")
    return df

# @st.cache_data
# def load_data(path):
#     with duckdb.connect("loan_data.duckdb") as conn:
#         df_loans = conn.execute("""
#                         SELECT *
#                         FROM fct_loan_data fct
#                         INNER JOIN dim_borrowers b on b.borrower_id = fct.borrower_id
#                         INNER JOIN dim_loans l on l.loan_id = fct.loan_id
#                         INNER JOIN dim_calendar c on c.calendar_id = fct.calendar_id 
#         """).fetchdf()
#         return df_loans

df = load_data('loan_data.parquet')

year_range = st.sidebar.slider(
    "Issue Year Range",
    int(df['issue_date'].dt.year.min()),
    int(df['issue_date'].dt.year.max()),
    (2018, 2020)
)

purpose_labels = {
    "debt_consolidation": "Debt Consolidation",
    "credit_card": "Credit Card",
    "home_improvement": "Home Improvement",
    "major_purchase": "Major Purchase",
    "car": "Car",
    "small_business": "Small Business",
    "wedding": "Wedding",
    "medical": "Medical",
    "moving": "Moving",
    "house": "House",
    "renewable_energy": "Renewable Energy",
    "vacation": "Vacation",
    "educational": "Educational",
    "other": "Other"
}

available_purposes = sorted(df['purpose'].dropna().unique())
friendly_options = [
    purpose_labels.get(p, p.replace("_", " ").title()) for p in available_purposes
]
friendly_default = [
    purpose_labels.get(p, p.replace("_", " ").title()) for p in [
        "debt_consolidation",
        "credit_card"
    ]
]

purpose_filter_friendly = st.sidebar.multiselect(
    "Loan Purpose",
    options=friendly_options,
    default=friendly_default
)

reverse_map = {v: k for k, v in purpose_labels.items()}
purpose_filter = [
    reverse_map.get(p, p.lower().replace(" ", "_")) for p in purpose_filter_friendly
]

grade_filter = st.sidebar.multiselect(
    "Credit Grade",
    options=sorted(df['grade'].unique()),
    default=["A", "B", "C"]
)

state_filter = st.sidebar.multiselect(
    "State",
    options=sorted(df['address_state'].dropna().unique()),
    default=df['address_state'].dropna().unique()
)

filtered = df[
    (df['issue_date'].dt.year.between(year_range[0], year_range[1])) &
    (df['purpose'].isin(purpose_filter)) &
    (df['grade'].isin(grade_filter)) &
    (df['address_state'].isin(state_filter))
]

loan_text = f"**Loans Shown:** {len(filtered):,}    |   \n"

# --- Main Dashboard ---
st.title("Loan Data Dashboard")
# st.markdown(
st.text(f"Loans Shown:".ljust(25) + f"{len(filtered):,}")
st.text(f"Date Range:".ljust(25) + f"{year_range[0]} – {year_range[1]}")
st.text(f"Filtered Purposes:".ljust(25) + f"{', '.join(purpose_filter_friendly)}")


# KPIs
total_loans = filtered['loan_amount'].sum()
avg_int_rate = filtered['interest_rate'].astype(str).str.replace('%','').astype(float).mean()
avg_income = filtered['annual_income'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Loan Amount", f"${total_loans:,.0f}")
col2.metric("Average Interest Rate", f"{avg_int_rate:.2f}%")
col3.metric("Average Annual Income", f"${avg_income:,.0f}")

st.divider()

# --- Charts ---
# tab1, tab2, tab3 = st.tabs(["Trends", "Distribution", "Geography"])

with col1:
    st.subheader("Loan Origination Trends Over Time")
    loans_per_month = filtered.groupby(filtered['issue_date'].dt.to_period("M"))['loan_amount'].sum().reset_index()
    loans_per_month['issue_date'] = loans_per_month['issue_date'].astype(str)
    fig = px.line(
        loans_per_month, x='issue_date', y='loan_amount',
        title="Total Loan Volume Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

    # st.subheader("Loan Status Distribution")
    # status_counts = filtered['loan_status'].value_counts().reset_index()
    # status_counts.columns = ['loan_status', 'count']
    # pie_fig = px.pie(
    #     status_counts,
    #     values='count',
    #     names='loan_status',
    #     title='Loan Status Distribution')
    # st.plotly_chart(pie_fig)

with col2:
    st.subheader("Loan Distributions")
    # c1, c2 = st.columns(2)
    c1 = st.columns(1)

    with c1:
        fig = px.box(
            filtered,
            x='grade',
            y='loan_amount',
            color='grade',
            title="Loan Amount by Credit Grade"
        )
        st.plotly_chart(fig, use_container_width=True)

    # with c2:
    #     fig = px.histogram(
    #         filtered,
    #         x='interest_rate',
    #         nbins=40,
    #         color='grade',
    #         title="Interest Rate Distribution"
    #     )
    #     st.plotly_chart(fig, use_container_width=True)

    # fig2 = px.bar(
    #     filtered,
    #     y='annual_income',
    #     x='purpose',
    #     color='grade',
    #     title="Income Distribution by Purpose",
    #     nbins=10,
    #     # box=True
    # )
    # st.plotly_chart(fig2, use_container_width=True)

# with col3:
#     st.subheader("Loans by State")
#     state_summary = (
#         filtered.groupby('address_state')
#         .agg(total_amount=('loan_amount', 'sum'), count=('loan_amount', 'count'))
#         .reset_index()
#     )
#     fig = px.choropleth(
#         state_summary,
#         locations='address_state',
#         locationmode="USA-states",
#         color='total_amount',
#         color_continuous_scale="Blues",
#         scope="usa",
#         title="Total Loan Amount by State"
#     )
#     st.plotly_chart(fig, use_container_width=True)

st.divider()
# st.caption("Data: Lending Club Public Dataset (2007–2020 Q1) — Dashboard by Streamlit + Plotly")
