import streamlit as st
import pandas as pd
import plotly.express as px

# ---- Load Data ----
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/94d364e98061cd58f8b52224f33037aa7ca3ed5f/DV2.csv"
    df = pd.read_csv(url, encoding='latin1')
    df.columns = [col.strip().replace("ï»¿", "") for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    return df

df = load_data()

# ---- Page Config ----
st.set_page_config(page_title="Car Retailer Dashboard", layout="wide")
st.title("🚗 Car Retailer Sales Dashboard")

# ---- Sidebar Filters ----
with st.sidebar:
    st.header("🔍 Filters")
    salespeople = st.multiselect("Salesperson", sorted(df['Salesperson'].dropna().unique()))
    car_makes = st.multiselect("Car Make", sorted(df['Car Make'].dropna().unique()))
    car_years = st.multiselect("Car Year", sorted(df['Car Year'].dropna().unique()))
    selected_metric = st.radio("Metric", ["Sale Price", "Commission Earned"], index=0)

# ---- Filter Data ----
filtered_df = df.copy()
if salespeople:
    filtered_df = filtered_df[filtered_df['Salesperson'].isin(salespeople)]
if car_makes:
    filtered_df = filtered_df[filtered_df['Car Make'].isin(car_makes)]
if car_years:
    filtered_df = filtered_df[filtered_df['Car Year'].astype(str).isin(car_years)]

# ---- Bar Chart ----
st.subheader(f"📊 Top 10 Salespeople by {selected_metric}")
top_salespeople = filtered_df.groupby('Salesperson')[selected_metric].sum().nlargest(10).reset_index()
bar_fig = px.bar(
    top_salespeople, y='Salesperson', x=selected_metric, orientation='h',
    template='plotly_dark', color_discrete_sequence=['#1f77b4']
)
st.plotly_chart(bar_fig, use_container_width=True)

# ---- Pie Chart ----
st.subheader(f"🧩 Top 10 Car Makes by {selected_metric}")
car_make_metric = filtered_df.groupby('Car Make')[selected_metric].sum().nlargest(10).reset_index()
pie_fig = px.pie(
    car_make_metric, names='Car Make', values=selected_metric, hole=0.3,
    template='plotly_dark', color_discrete_sequence=px.colors.sequential.Plasma_r
)
st.plotly_chart(pie_fig, use_container_width=True)

# ---- Trend Line Chart ----
st.subheader("📈 Sales and Commission Trend by Quarter")
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_fig = px.line(
    trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'],
    markers=True, template='plotly_dark', labels={'value': 'Amount', 'Quarter': 'Quarter'}
)
st.plotly_chart(trend_fig, use_container_width=True)
