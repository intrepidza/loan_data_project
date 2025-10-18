import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="Loan Data Dashboard", layout="wide")

@st.cache_data
def load_data(path):
    df = pd.read_parquet(path, columns=['issue_date', 'title', 'grade', 'address_state', 'loan_amount'])
    df['grade'] = df['grade'].astype('category')
    df['title'] = df['title'].astype('category')
    df['address_state'] = df['address_state'].astype('category')
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

st.title("Loan Data Dashboard")

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

st.divider()
