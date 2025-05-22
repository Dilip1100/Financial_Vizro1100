import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="DBT Dashboard", layout="wide")

# Title and description
st.title("📊 DBT Data Dashboard")
st.markdown("Visualize revenue, loss, and customer insights from the DBT dataset.")

# Theme toggle
theme = st.sidebar.radio("Select Theme:", ["Dark", "Light"], index=0)
plotly_template = "plotly_dark" if theme == "Dark" else "plotly_white"

# Load CSV with caching
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/main/DBT.csv"
    return pd.read_csv(url, encoding="latin1")

df = load_data()

# Rename columns
df.columns = ["CUSTOMERNAME", "COUNTRY", "YEAR_ID", "QTR_ID", "TOTALLOSS", "TOTALREVENUE", "PROFIT"]

# Sidebar filters
with st.sidebar:
    st.header("🔧 Filters")
    selected_years = st.multiselect(
        "Select Year(s):", options=sorted(df["YEAR_ID"].unique()), default=[df["YEAR_ID"].max()]
    )
    selected_metric = st.radio("Metric to Display:", options=["TOTALREVENUE", "TOTALLOSS"])
    
    st.markdown("### Quarter-over-Quarter Comparison")
    selected_q_year = st.selectbox("Select Year:", sorted(df["YEAR_ID"].unique(), reverse=True))
    selected_q_qtr = st.selectbox("Select Quarter:", [1, 2, 3, 4])

# Filtered data for main dashboard
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
    template=plotly_template,
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
    color_discrete_sequence=px.colors.qualitative.Set3,
    template=plotly_template
)

# Revenue, Loss, and Profit trend line chart
trend_df = (
    filtered_df.groupby("QTR_ID")[["TOTALREVENUE", "TOTALLOSS", "PROFIT"]].sum().reset_index()
)
fig_trend = px.line(
    trend_df,
    x="QTR_ID",
    y=["TOTALREVENUE", "TOTALLOSS", "PROFIT"],
    title="Quarterly Revenue, Loss, and Profit Trend",
    markers=True,
    template=plotly_template
)

# Quarter-over-Quarter logic
current_df = df[(df["YEAR_ID"] == selected_q_year) & (df["QTR_ID"] == selected_q_qtr)]

if selected_q_qtr == 1:
    prev_year = selected_q_year - 1
    prev_qtr = 4
else:
    prev_year = selected_q_year
    prev_qtr = selected_q_qtr - 1

prev_df = df[(df["YEAR_ID"] == prev_year) & (df["QTR_ID"] == prev_qtr)]

# Aggregated totals
curr_revenue = current_df["TOTALREVENUE"].sum()
curr_loss = current_df["TOTALLOSS"].sum()
curr_profit = current_df["PROFIT"].sum()

prev_revenue = prev_df["TOTALREVENUE"].sum()
prev_loss = prev_df["TOTALLOSS"].sum()
prev_profit = prev_df["PROFIT"].sum()

# Differences and percentages
def calc_change(curr, prev):
    diff = curr - prev
    pct = (diff / prev * 100) if prev else 0
    return diff, pct

rev_diff, rev_pct = calc_change(curr_revenue, prev_revenue)
loss_diff, loss_pct = calc_change(curr_loss, prev_loss)
profit_diff, profit_pct = calc_change(curr_profit, prev_profit)

# Layout: Charts
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_bar, use_container_width=True)
with col2:
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.plotly_chart(fig_trend, use_container_width=True)

# Layout: Quarter-over-Quarter comparison
st.markdown("## 📈 Quarter-over-Quarter Comparison")
st.markdown(f"**Current Period:** Year {selected_q_year}, Q{selected_q_qtr}")
st.markdown(f"**Previous Period:** Year {prev_year}, Q{prev_qtr}")

col3, col4, col5 = st.columns(3)
with col3:
    st.metric("Total Revenue", f"${curr_revenue:,.0f}", f"${rev_diff:,.0f} ({rev_pct:.1f}%)")
with col4:
    st.metric("Total Loss", f"${curr_loss:,.0f}", f"${loss_diff:,.0f} ({loss_pct:.1f}%)")
with col5:
    st.metric("Total Profit", f"${curr_profit:,.0f}", f"${profit_diff:,.0f} ({profit_pct:.1f}%)")

# Export option
st.markdown("### 📥 Export Filtered Data")
st.download_button(
    label="Download CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_dbt_data.csv",
    mime="text/csv"
)
