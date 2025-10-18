import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Loan Data Dashboard", layout="wide")


@st.cache_data
def load_data(path):
    df = pd.read_parquet(path, columns=[
        'issue_date',
        'purpose_description',
        'grade',
        'address_state',
        'loan_amount',
        'interest_rate',
        'annual_income',
        'loan_status',
        'term'
        ]
    )
    df['grade'] = df['grade'].astype('category') 
    df['purpose_description'] = df['purpose_description'].astype('category')
    df['address_state'] = df['address_state'].astype('category')
    df['loan_status'] = df['loan_status'].astype('category')
    df['term'] = df['term'].astype('category')
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
    options=sorted(df['purpose_description'].unique()),
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
    (df['purpose_description'].isin(purpose_filter)) &
    (df['grade'].isin(grade_filter)) &
    (df['address_state'].isin(state_filter))
]

loan_text = f"**Loans Shown:** {len(filtered):,}    |   \n"

# --- Main Dashboard ---
st.title("Loan Data Dashboard")

total_loans = filtered['loan_amount'].sum()
avg_int_rate = filtered['interest_rate'].mean() * 100
avg_income = filtered['annual_income'].mean()

col1, col2, col3 = st.columns(3)

st.divider()

# --- Charts ---
with col1:
    st.metric("Filtered Date Range", f"{year_range[0]} – {year_range[1]}")
    st.metric("Total Loan Amount", f"${total_loans:,.0f}")

    # st.subheader("Loan Trends Over Time")
    loans_per_month = filtered.groupby(filtered['issue_date'].dt.to_period("M"))['loan_amount'].sum().reset_index()
    loans_per_month['issue_date'] = loans_per_month['issue_date'].astype(str)
    fig1 = px.line(
        loans_per_month,
        x='issue_date',
        y='loan_amount',
        labels={
            "issue_date": "Issue Date",
            "loan_amount": "Loan Amount",
        },
        title="Total Loan Volume Over Time"
    )
    st.plotly_chart(fig1, use_container_width=True)

    plot_term_data = filtered.groupby('term')['loan_amount'].sum().reset_index()


    fig2 = px.bar(
        plot_term_data,
        x='loan_amount',
        y='term',
        color='term',
        title="Loan Amount by Term",
        orientation="h",
        labels={
            "loan_amount": "Loan Amount",
            "term": "Term",
            }
    )
    st.plotly_chart(fig2, use_container_width=True)



with col2:
    with st.container(height=75, border=False):
        st.markdown('<p style="font-size: 14px;">Filtered Loan Purposes:<br></p>' + ', '.join(purpose_filter), unsafe_allow_html=True)

    col2.metric("Average Interest Rate", f"{avg_int_rate:.2f}%")

    plot_grade_data = filtered.groupby('grade')['loan_amount'].sum().reset_index()
    plot_grade_data = plot_grade_data[plot_grade_data['grade'].isin(grade_filter)]

    fig3 = px.bar(
        plot_grade_data,
        x='grade',
        y='loan_amount',
        color='grade',
        title="Loan Amount by Credit Grade",
        labels={
            "grade": "Grade",
            "loan_amount": "Loan Amount",
            },
        category_orders={'grade': ['A', 'B', 'C', 'D', 'E', 'F', 'G']},
    )
    st.plotly_chart(fig3, use_container_width=True)

    status_counts = filtered['loan_status'].value_counts().reset_index()
    status_counts.columns = ['loan_status', 'count']
    fig4 = px.pie(
        status_counts,
        values='count',
        names='loan_status',
        title='Loan Status Distribution')
    st.plotly_chart(fig4)


with col3: 

    col3.metric("Loans Shown", f"{len(filtered)}")
    col3.metric("Average Borrower Annual Income", f"${avg_income:,.0f}")

    state_summary = (
        filtered.groupby('address_state')
        .agg(total_amount=('loan_amount', 'sum'), count=('loan_amount', 'count'))
        .reset_index()
    )
    fig5 = px.choropleth(
        state_summary,
        locations='address_state',
        locationmode="USA-states",
        color='total_amount',
        color_continuous_scale="Blues",
        scope="usa",
        title="Total Loan Amount by State"
    )
    st.plotly_chart(fig5, use_container_width=True)


    # pie_fig4 = px.pie(
    #     status_counts,
    #     values='count',
    #     names='loan_status',
    #     title='Loan Status Distributiontest')
    # st.plotly_chart(pie_fig4)


    # # Interest Rate Distribution:
    # fig = px.histogram(
    #     filtered,
    #     x='interest_rate',
    #     nbins=40,
    #     color='grade',
    #     title="Interest Rate Distribution"
    # )
    # st.plotly_chart(fig, use_container_width=True)


    # # Income Distribution by Purpose
    plot_purpose_data = filtered.groupby('purpose_description')['loan_amount'].sum().reset_index()
    plot_purpose_data = plot_purpose_data[plot_purpose_data['purpose_description'].isin(purpose_filter)]

    fig6 = px.bar(
        plot_purpose_data,
        x='purpose_description',
        y='loan_amount',
        color='purpose_description',
        title="Income Distribution by Purpose",
    )
    st.plotly_chart(fig6, use_container_width=True)


# st.divider()
