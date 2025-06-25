# Enhanced Streamlit Car Retailer Dashboard with Advanced Analytics
import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
import plotly.graph_objects as go

# ---- Load Data ----
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/94d364e98061cd58f8b52224f33037aa7ca3ed5f/DV2.csv"
    df = pd.read_csv(url, encoding='latin1')
    df.columns = [col.strip().replace("ï»¿", "") for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    # Assume cost price is 85% of sale price for profit calculation
    df['Cost Price'] = df['Sale Price'] * 0.85
    df['Profit'] = df['Sale Price'] - df['Cost Price']
    return df

df = load_data()

# ---- Page Setup ----
st.set_page_config(page_title="Car Retailer Dashboard", layout="wide")
st.title("🚗 Car Retailer Sales Dashboard")

# ---- Filters ----
with st.container():
    col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
    with col1:
        salespeople = st.multiselect("Salesperson", sorted(df['Salesperson'].dropna().unique()))
    with col2:
        car_makes = st.multiselect("Car Make", sorted(df['Car Make'].dropna().unique()))
    with col3:
        car_years = st.multiselect("Car Year", sorted(df['Car Year'].dropna().unique()))
    with col4:
        selected_metric = st.radio("Metric", ["Sale Price", "Commission Earned"], index=0, horizontal=True)

# ---- Filter Data ----
filtered_df = df.copy()
if salespeople:
    filtered_df = filtered_df[filtered_df['Salesperson'].isin(salespeople)]
if car_makes:
    filtered_df = filtered_df[filtered_df['Car Make'].isin(car_makes)]
if car_years:
    filtered_df = filtered_df[filtered_df['Car Year'].astype(str).isin(car_years)]

# ---- KPI Cards ----
st.markdown("### 📌 Summary Metrics")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("💰 Total Sales", f"${filtered_df['Sale Price'].sum():,.0f}")
with kpi2:
    st.metric("🏆 Total Commission", f"${filtered_df['Commission Earned'].sum():,.0f}")
with kpi3:
    avg_price = filtered_df['Sale Price'].mean() if not filtered_df.empty else 0
    st.metric("📊 Avg Sale Price", f"${avg_price:,.0f}")
with kpi4:
    st.metric("📦 Transactions", f"{filtered_df.shape[0]:,}")

# ---- Download Data ----
st.download_button("⬇️ Download Filtered Data", filtered_df.to_csv(index=False), "filtered_data.csv")

# ---- Bar Chart: Salespeople ----
st.subheader(f"📊 Top 10 Salespeople by {selected_metric}")
top_salespeople = filtered_df.groupby('Salesperson')[selected_metric].sum().nlargest(10).reset_index()
bar_fig = px.bar(
    top_salespeople, y='Salesperson', x=selected_metric, orientation='h',
    template='plotly_dark', color_discrete_sequence=['#1f77b4']
)
st.plotly_chart(bar_fig, use_container_width=True)

# ---- 3D-style Pie Chart ----
st.subheader(f"🧩 Top 10 Car Makes by {selected_metric}")
car_make_metric = filtered_df.groupby('Car Make')[selected_metric].sum().nlargest(10).reset_index()
pull_values = [0.1 if i == 0 else 0.05 for i in range(len(car_make_metric))]
pie_fig = px.pie(
    car_make_metric, names='Car Make', values=selected_metric, hole=0.3,
    template='plotly_dark', color_discrete_sequence=px.colors.sequential.Plasma_r
)
pie_fig.update_traces(pull=pull_values, rotation=45, textinfo='label+percent', textposition='outside')
pie_fig.update_layout(height=600, width=900)
st.plotly_chart(pie_fig, use_container_width=False)

# ---- Trend Line ----
st.subheader("📈 Sales and Commission Trend by Quarter")
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change().fillna(0) * 100
trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change().fillna(0) * 100
trend_fig = px.line(
    trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'],
    markers=True, template='plotly_dark', labels={'value': 'Amount', 'Quarter': 'Quarter'}
)
st.plotly_chart(trend_fig, use_container_width=True)

# ---- QoQ Table ----
with st.expander("📊 View QoQ % Change Table"):
    st.dataframe(trend_df[['Quarter', 'Sale Price QoQ %', 'Commission QoQ %']].style.format("{:.2f}%"))

# ---- Sunburst Chart (Make > Model) ----
st.subheader("🌿 Contribution by Make and Model")
if 'Car Model' in df.columns:
    sunburst_fig = px.sunburst(
        filtered_df, path=['Car Make', 'Car Model'], values='Sale Price',
        template='plotly_dark', color_continuous_scale='Blues'
    )
    st.plotly_chart(sunburst_fig, use_container_width=True)

# ---- Scatter Matrix ----
st.subheader("🔬 Feature Correlation")
scatter_fig = px.scatter_matrix(
    filtered_df,
    dimensions=['Sale Price', 'Commission Earned', 'Profit'],
    template='plotly_dark'
)
st.plotly_chart(scatter_fig, use_container_width=True)

# ---- Forecasting (Prophet) ----
st.subheader("📅 Sales Forecasting (90 Days)")
if not filtered_df.empty:
    forecast_df = filtered_df[['Date', 'Sale Price']].rename(columns={'Date': 'ds', 'Sale Price': 'y'})
    model = Prophet()
    model.fit(forecast_df)
    future = model.make_future_dataframe(periods=90)
    forecast = model.predict(future)
    forecast_fig = px.line(forecast, x='ds', y='yhat', template='plotly_dark', title='Projected Sales')
    st.plotly_chart(forecast_fig, use_container_width=True)

# ---- Animated Monthly Trend ----
with st.expander("🎞️ View Monthly Animated Trend"):
    monthly_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
    melted = monthly_trend.melt(id_vars='Month', var_name='Metric', value_name='Amount')
    animated_fig = px.bar(
        melted, x='Metric', y='Amount', animation_frame='Month',
        template='plotly_dark', color='Metric'
    )
    animated_fig.update_layout(yaxis_tickprefix="$", height=500)
    st.plotly_chart(animated_fig, use_container_width=True)
