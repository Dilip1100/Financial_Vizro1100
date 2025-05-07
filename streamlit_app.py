import streamlit as st
import pandas as pd
import plotly.express as px


df = pd.read_csv("https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/main/DBT.csv", encoding="latin1")

", encoding="latin1")
df.columns = ["CUSTOMERNAME", "COUNTRY", "YEAR_ID", "QTR_ID", "TOTALLOSS", "TOTALREVENUE", "PROFIT"]

st.set_page_config(page_title="DBT Dashboard", layout="wide")

# Sidebar filters
st.sidebar.header("Filter")
years = df["YEAR_ID"].unique()
selected_years = st.sidebar.multiselect("Select Years", sorted(years), default=years.max())
metric = st.sidebar.radio("Metric", ["TOTALREVENUE", "TOTALLOSS"])

# Filtered data
filtered_df = df[df["YEAR_ID"].isin(selected_years)]

# Bar Chart: Top Customers
top_customers = filtered_df.groupby("CUSTOMERNAME")[metric].sum().nlargest(10).reset_index()
fig_bar = px.bar(top_customers, x=metric, y="CUSTOMERNAME", orientation="h", title=f"Top 10 Customers by {metric}", template="plotly_dark")
st.plotly_chart(fig_bar, use_container_width=True)

# Pie Chart: Top Countries
top_countries = filtered_df.groupby("COUNTRY")[metric].sum().nlargest(10).reset_index()
fig_pie = px.pie(top_countries, names="COUNTRY", values=metric, title=f"Top 10 Countries by {metric}")
st.plotly_chart(fig_pie, use_container_width=True)

# Line Chart: Quarterly Trends
trend_df = filtered_df.groupby("QTR_ID")[["TOTALREVENUE", "TOTALLOSS"]].sum().reset_index()
fig_line = px.line(trend_df, x="QTR_ID", y=["TOTALREVENUE", "TOTALLOSS"], title="Revenue & Loss Trend Over Quarters", markers=True)
st.plotly_chart(fig_line, use_container_width=True)
