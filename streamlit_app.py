import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Loan Data Dashboard", layout="wide")


@st.cache_data
def load_data(path):
    df = pd.read_parquet(path, columns=[
        'issue_date',
        'title',
        'grade',
        'address_state',
        'loan_amount',
        'interest_rate',
        'annual_income',
        'loan_status'
        ]
    )
    df['grade'] = df['grade'].astype('category') 
    df['title'] = df['title'].astype('category')
    df['address_state'] = df['address_state'].astype('category')
    df['loan_status'] = df['loan_status'].astype('category')
    print("Data loaded from Parquet file.")
    return df


df = load_data('loan_data.parquet')

year_range = st.sidebar.slider(
    "Issue Year Range",
    int(df['issue_date'].dt.year.min()),
    int(df['issue_date'].dt.year.max()),
    (2018, 2020)
)

purpose_filter = st.sidebar.multiselect(
    "Loan Purpose",
    options=sorted(df['title'].unique()),
    default=["Debt consolidation", "Credit card refinancing"]
)

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
    (df['title'].isin(purpose_filter)) &
    (df['grade'].isin(grade_filter)) &
    (df['address_state'].isin(state_filter))
]

loan_text = f"**Loans Shown:** {len(filtered):,}    |   \n"

# --- Main Dashboard ---
st.title("Loan Data Dashboard")


total_loans = filtered['loan_amount'].sum()
# avg_int_rate = filtered['interest_rate'].astype(str).str.replace('%','').astype(float).mean()
avg_int_rate = filtered['interest_rate'].mean()
avg_income = filtered['annual_income'].mean()

col1, col2, col3 = st.columns(3)


# col3.metric("Filtered Purposes", ", ".join(purpose_filter))


st.divider()


# --- Charts ---

with col1:
    st.metric("Date Range", f"{year_range[0]} – {year_range[1]}")
    st.metric("Total Loan Amount", f"${total_loans:,.0f}")

    # st.subheader("Loan Trends Over Time")
    loans_per_month = filtered.groupby(filtered['issue_date'].dt.to_period("M"))['loan_amount'].sum().reset_index()
    loans_per_month['issue_date'] = loans_per_month['issue_date'].astype(str)
    fig = px.line(
        loans_per_month, x='issue_date', y='loan_amount',
        title="Total Loan Volume Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)



with col2:
    with st.container(height=75, border=False):
        st.markdown('<p style="font-size: 14px;">Filtered Purposes:<br></p>' + ', '.join(purpose_filter), unsafe_allow_html=True)

    col2.metric("Average Interest Rate", f"{avg_int_rate:.2f}%")

    # st.subheader("Loan Distributions")

    plot_data = filtered.groupby('grade')['loan_amount'].sum().reset_index()
    plot_data = plot_data[plot_data['grade'].isin(grade_filter)]

    fig = px.bar(
        plot_data,
        x='grade',
        y='loan_amount',
        color='grade',
        title="Loan Amount by Credit Grade",
        category_orders={'grade': ['A', 'B', 'C']},
    )
    st.plotly_chart(fig, use_container_width=True)

    # st.subheader("Loan Status Distribution")
    status_counts = filtered['loan_status'].value_counts().reset_index()
    status_counts.columns = ['loan_status', 'count']
    pie_fig = px.pie(
        status_counts,
        values='count',
        names='loan_status',
        title='Loan Status Distribution')
    st.plotly_chart(pie_fig)

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
    #     x='purpose',
    #     y='annual_income',
    #     color='grade',
    #     title="Income Distribution by Purpose",
    # )
    # st.plotly_chart(fig2, use_container_width=True)

with col3: 

    col3.metric("Loans Shown", f"{len(filtered)}")
    col3.metric("Average Borrower Annual Income", f"${avg_income:,.0f}")

    # st.subheader("Loans by State")
    state_summary = (
        filtered.groupby('address_state')
        .agg(total_amount=('loan_amount', 'sum'), count=('loan_amount', 'count'))
        .reset_index()
    )
    fig = px.choropleth(
        state_summary,
        locations='address_state',
        locationmode="USA-states",
        color='total_amount',
        color_continuous_scale="Blues",
        scope="usa",
        title="Total Loan Amount by State"
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()
# st.caption("Data: Lending Club Public Dataset (2007–2020 Q1) — Dashboard by Streamlit + Plotly")
