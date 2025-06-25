import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet

# ---- Load Data ----
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/94d364e98061cd58f8b52224f33037aa7ca3ed5f/DV2.csv"
    df = pd.read_csv(url, encoding='latin1')
    df.columns = [col.strip().replace("\ufeff", "") for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    return df

df = load_data()

# ---- Page Config ----
st.set_page_config(page_title="Car Retailer Dashboard", layout="wide")
st.title("\U0001F697 Car Retailer Sales Dashboard")

# ---- Top Filters ----
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

# ---- Bar Chart ----
st.subheader(f"\U0001F4CA Top 10 Salespeople by {selected_metric}")
top_salespeople = filtered_df.groupby('Salesperson')[selected_metric].sum().nlargest(10).reset_index()
bar_fig = px.bar(
    top_salespeople, y='Salesperson', x=selected_metric, orientation='h',
    template='plotly_dark', color_discrete_sequence=['#1f77b4']
)
st.plotly_chart(bar_fig, use_container_width=True)

# ---- Pie Chart ----
st.subheader(f"\U0001F9E9 Top 10 Car Makes by {selected_metric}")
car_make_metric = filtered_df.groupby('Car Make')[selected_metric].sum().nlargest(10).reset_index()
pie_fig = px.pie(
    car_make_metric, names='Car Make', values=selected_metric, hole=0.3,
    template='plotly_dark', color_discrete_sequence=px.colors.sequential.Plasma_r
)
pie_fig.update_traces(pull=[0.05]*10, textposition='inside', textinfo='percent+label')
pie_fig.update_layout(width=800, height=600)
st.plotly_chart(pie_fig, use_container_width=False)

# ---- Trend Line Chart ----
st.subheader("\U0001F4C8 Sales and Commission Trend by Quarter")
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_fig = px.line(
    trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'],
    markers=True, template='plotly_dark', labels={'value': 'Amount', 'Quarter': 'Quarter'}
)
st.plotly_chart(trend_fig, use_container_width=True)

# ---- QoQ Change Table ----
st.subheader("\U0001F4CA Quarter-over-Quarter % Change")
trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change() * 100
trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change() * 100
styled_df = trend_df[['Quarter', 'Sale Price QoQ %', 'Commission QoQ %']].copy()
styled_df[['Sale Price QoQ %', 'Commission QoQ %']] = styled_df[['Sale Price QoQ %', 'Commission QoQ %']].fillna(0)
st.dataframe(
    styled_df.style.format({
        'Sale Price QoQ %': "{:.2f}%",
        'Commission QoQ %': "{:.2f}%"
    })
)

# ---- Forecasting ----
st.subheader("\U0001F4C5 Sales Forecasting (90 Days)")
if not filtered_df.empty:
    forecast_df = filtered_df[['Date', 'Sale Price']].rename(columns={'Date': 'ds', 'Sale Price': 'y'})
    forecast_df = forecast_df.dropna()
    if not forecast_df.empty:
        model = Prophet()
        model.fit(forecast_df)
        future = model.make_future_dataframe(periods=90)
        forecast = model.predict(future)
        forecast_fig = px.line(forecast, x='ds', y='yhat', template='plotly_dark', title='Projected Sales')
        st.plotly_chart(forecast_fig, use_container_width=True)
    else:
        st.info("Not enough data for forecasting.")
else:
    st.info("No data available for forecasting.")
