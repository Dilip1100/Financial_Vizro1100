import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="DBT Dashboard", layout="wide")

# Title and description
st.title("📊 DBT Data Dashboard")
st.markdown("Visualize revenue, loss, and customer insights from the DBT dataset.")

# Load CSV with caching
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/main/DBT.csv"
    return pd.read_csv(url, encoding="latin1")

df = load_data()

# Rename columns just in case
df.columns = ["CUSTOMERNAME", "COUNTRY", "YEAR_ID", "QTR_ID", "TOTALLOSS", "TOTALREVENUE", "PROFIT"]

# Sidebar filters
with st.sidebar:
    st.header("🔧 Filters")
    selected_years = st.multiselect(
        "Select Year(s):", options=sorted(df["YEAR_ID"].unique()), default=[df["YEAR_ID"].max()]
    )
    selected_metric = st.radio("Metric to Display:", options=["TOTALREVENUE", "TOTALLOSS"])

# Filtered data
filtered_df = df[df["YEAR_ID"].isin(selected_years)]

# Top 10 customers bar chart
top_customers = (
    filtered_df.groupby("CUSTOMERNAME")[selected_metric].sum().nlargest(10).reset_index()
)
fig_bar = px.bar(
    top_customers,
    x=selected_metric,
    y="CUSTOMERNAME",
    orientation="h",
    title=f"Top 10 Customers by {selected_metric}",
    template="plotly_dark",
    color_discrete_sequence=["#1f77b4"]
)

# Top 10 countries pie chart
top_countries = (
    filtered_df.groupby("COUNTRY")[selected_metric].sum().nlargest(10).reset_index()
)
fig_pie = px.pie(
    top_countries,
    names="COUNTRY",
    values=selected_metric,
    title=f"Top 10 Countries by {selected_metric}",
    color_discrete_sequence=px.colors.qualitative.Set3
)

# Revenue & Loss trend line chart
trend_df = (
    filtered_df.groupby("QTR_ID")[["TOTALREVENUE", "TOTALLOSS"]].sum().reset_index()
)
fig_trend = px.line(
    trend_df,
    x="QTR_ID",
    y=["TOTALREVENUE", "TOTALLOSS"],
    title="Quarterly Revenue and Loss Trend",
    markers=True,
    template="plotly_dark"
)

# Layout
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_bar, use_container_width=True)
with col2:
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.plotly_chart(fig_trend, use_container_width=True)
