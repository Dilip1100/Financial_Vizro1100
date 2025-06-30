# Final Merged Script: Enhanced Automotive Dashboard with Faker Data and Monochrome Theme

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# ----------------- Page Setup -----------------
st.set_page_config(page_title="Automotive Dashboard", layout="wide")
st.markdown("""
    <style>
        body, .stApp {
            background-color: #1C1C1C;
            color: #D3D3D3;
            font-family: 'Segoe UI', sans-serif;
        }
        .stSelectbox, .stMultiselect, .stRadio, .stMetric, .stDownloadButton {
            background-color: #2A2A2A;
            color: #D3D3D3;
            border: 1px solid #4A4A4A;
            border-radius: 0.3rem;
            padding: 0.5rem;
        }
        .stMetricLabel {
            color: #A9A9A9 !important;
            font-size: 0.9rem;
        }
        .stMetricValue {
            font-size: 1.5rem;
            font-weight: bold;
            color: #FFFFFF;
        }
        .stButton>button {
            background-color: #4A4A4A;
            color: #D3D3D3;
            border: 1px solid #606060;
            border-radius: 0.3rem;
            padding: 0.5rem 1rem;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #606060;
            color: #FFFFFF;
        }
        .css-1d391kg {
            background-color: #2A2A2A;
            border: 1px solid #4A4A4A;
            border-radius: 0.5rem;
            padding: 1rem;
        }
        .stDataFrame, .element-container {
            color: #D3D3D3;
            background-color: #2A2A2A;
            border: 1px solid #4A4A4A;
            border-radius: 0.5rem;
            padding: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #2A2A2A;
            color: #D3D3D3;
            border: 1px solid #4A4A4A;
            border-radius: 0.3rem;
            margin: 0.2rem;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #3A3A3A;
            color: #FFFFFF;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            background-color: #4A4A4A;
            color: #FFFFFF;
        }
        footer {visibility: hidden;}
        .section-header {
            color: #D3D3D3;
            border-bottom: 2px solid #606060;
            padding-bottom: 0.5rem;
            margin-bottom: 1rem;
        }
        hr {
            border-color: #4A4A4A;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Header -----------------
st.image("https://github.com/Dilip1100/Financial_Vizro1100/blob/18a12404b6962363258f0078ae6f0d2a025c88bb/LOGO.jpg", width=180)
st.title(" Automotive Analytics Dashboard")
st.markdown("Advanced insights for automotive sales and operations", unsafe_allow_html=True)

# ----------------- Load Retail CSV Data -----------------
@st.cache_data
def load_retail_csv():
    url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/94d364e98061cd58f8b52224f33037aa7ca3ed5f/DV2.csv"
    df = pd.read_csv(url, encoding='latin1')
    df.columns = df.columns.str.strip().str.replace("ï»¿", "", regex=False).str.replace("﻿", "", regex=False)
    if 'Date' not in df.columns:
        st.error(f"Expected 'Date' column not found. Columns present: {df.columns.tolist()}")
        return pd.DataFrame()
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df

df = load_retail_csv()

if df.empty:
    st.stop()

# ----------------- Filters -----------------
st.markdown('<div class="section-header">🔍 Filter Options</div>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
with col1:
    salespeople = st.multiselect("Salesperson", sorted(df['Salesperson'].dropna().unique()), key="salespeople")
with col2:
    car_makes = st.multiselect("Car Make", sorted(df['Car Make'].dropna().unique()), key="car_makes")
with col3:
    car_years = st.multiselect("Car Year", sorted(df['Car Year'].dropna().unique()), key="car_years")
with col4:
    selected_metric = st.radio("Metric", ["Sale Price", "Commission Earned"], index=0, horizontal=True)

# Optional Car Model Slicer
selected_model = None
if car_makes and len(car_makes) == 1:
    model_options = df[df['Car Make'] == car_makes[0]]['Car Model'].dropna().unique()
    selected_model = st.selectbox(f"Model for {car_makes[0]}", sorted(model_options))

# Apply Filters
filtered_df = df.copy()
if salespeople:
    filtered_df = filtered_df[filtered_df['Salesperson'].isin(salespeople)]
if car_makes:
    filtered_df = filtered_df[filtered_df['Car Make'].isin(car_makes)]
if selected_model:
    filtered_df = filtered_df[filtered_df['Car Model'] == selected_model]
if car_years:
    filtered_df = filtered_df[filtered_df['Car Year'].astype(str).isin(car_years)]

# ----------------- Summary Metrics -----------------
st.markdown('<div class="section-header">📌 Key Performance Indicators</div>', unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("💰 Total Sales", f"${filtered_df['Sale Price'].sum():,.0f}")
with k2:
    st.metric("🏆 Total Commission", f"${filtered_df['Commission Earned'].sum():,.0f}")
with k3:
    avg_price = filtered_df['Sale Price'].mean() if not filtered_df.empty else 0
    st.metric("📊 Avg Sale Price", f"${avg_price:,.0f}")
with k4:
    st.metric("📦 Transactions", f"{filtered_df.shape[0]:,}")

# ----------------- KPI Trend Line -----------------
st.markdown('<div class="section-header">📈 KPI Trend Analysis</div>', unsafe_allow_html=True)
kpi_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
kpi_fig = go.Figure()
kpi_fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Sale Price'], name='Sale Price', line=dict(color='#A9A9A9')))
kpi_fig.add_trace(go.Scatter(x=kpi_trend['Month'], y=kpi_trend['Commission Earned'], name='Commission', line=dict(color='#808080')))
kpi_fig.update_layout(
    template='plotly_dark',
    height=400,
    xaxis_title="Month",
    yaxis_title="Amount ($)",
    hovermode="x unified",
    plot_bgcolor='#2A2A2A',
    paper_bgcolor='#2A2A2A',
    font=dict(color='#D3D3D3')
)
st.plotly_chart(kpi_fig, use_container_width=True)

# ----------------- Download Button -----------------
st.markdown('<div class="section-header">📅 Download Filtered Data</div>', unsafe_allow_html=True)
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_car_sales.csv", "text/csv")

# ----------------- Animated 3D Investment vs Sales -----------------
st.markdown('<div class="section-header">🎥 3D Sales Visualization</div>', unsafe_allow_html=True)
filtered_df['MonthStr'] = pd.to_datetime(filtered_df['Date']).dt.strftime("%Y-%m")
animated_fig = px.scatter_3d(
    filtered_df,
    x="Commission Earned",
    y="Sale Price",
    z="Car Year",
    animation_frame="MonthStr",
    color="Salesperson",
    size="Sale Price",
    template="plotly_dark",
    opacity=0.7,
    color_continuous_scale='Greys'
)
animated_fig.update_layout(height=650, plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'))
st.plotly_chart(animated_fig, use_container_width=True)

# ----------------- Sales Heatmap -----------------
st.markdown('<div class="section-header">🌡️ Sales Performance Heatmap</div>', unsafe_allow_html=True)
heatmap_data = filtered_df.pivot_table(
    values=selected_metric,
    index='Salesperson',
    columns='Car Make',
    aggfunc='sum',
    fill_value=0
)
heatmap_fig = px.imshow(
    heatmap_data,
    color_continuous_scale='Greys',
    template='plotly_dark',
    text_auto='.2s',
    aspect='auto'
)
heatmap_fig.update_layout(height=500, plot_bgcolor='#2A2A2A', paper_bgcolor='#2A2A2A', font=dict(color='#D3D3D3'))
st.plotly_chart(heatmap_fig, use_container_width=True)

# ----------------- Existing Charts -----------------
st.markdown('<div class="section-header">📊 Top Performers</div>', unsafe_allow_html=True)
top_salespeople = (
    filtered_df.groupby('Salesperson')[selected_metric]
    .sum().nlargest(10).reset_index().sort_values(by=selected_metric)
)
bar_fig = go.Figure(data=[
    go.Bar(
        x=top_salespeople['Salesperson'],
        y=top_salespeople[selected_metric],
        marker=dict(color=top_salespeople[selected_metric], colorscale='Greys', showscale=True, line=dict(color='#D3D3D3', width=1.2)),
        hovertemplate='<b>%{x}</b><br>' + selected_metric + ': %{y:$,.0f}<extra></extra>',
    )
])
bar_fig.update_layout(
    template='plotly_dark',
    xaxis_title="Salesperson",
    yaxis_title=selected_metric,
    height=500,
    plot_bgcolor='#2A2A2A',
    paper_bgcolor='#2A2A2A',
    font=dict(color='#D3D3D3')
)
st.plotly_chart(bar_fig, use_container_width=True)

# ----------------- Car Make/Model Analysis -----------------
st.markdown('<div class="section-header">🧹 Vehicle Sales Analysis</div>', unsafe_allow_html=True)
col_left, col_right = st.columns(2)
with col_left:
    car_make_metric = filtered_df.groupby('Car Make')['Sale Price'].sum().nlargest(10).reset_index()
    pie_fig_make = px.pie(car_make_metric, names='Car Make', values='Sale Price', hole=0.2, color_discrete_sequence=px.colors.sequential.Greys)
    pie_fig_make.update_layout(
        template='plotly_dark',
        height=700,
        title="Top Car Makes by Sale Price",
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(pie_fig_make, use_container_width=True)

with col_right:
    car_model_metric = filtered_df.groupby('Car Model')['Sale Price'].sum().nlargest(10).reset_index()
    pie_fig_model = px.pie(car_model_metric, names='Car Model', values='Sale Price', hole=0.2, color_discrete_sequence=px.colors.sequential.Greys[::-1])
    pie_fig_model.update_layout(
        template='plotly_dark',
        height=700,
        title="Top Car Models by Sale Price",
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(pie_fig_model, use_container_width=True)

# ----------------- Car Model Comparison Table -----------------
st.markdown('<div class="section-header">🚘 Car Model Comparison</div>', unsafe_allow_html=True)
model_comparison = filtered_df.groupby(['Car Make', 'Car Model']).agg({
    'Sale Price': ['mean', 'sum', 'count'],
    'Commission Earned': 'mean'
}).round(2)
model_comparison.columns = ['Avg Sale Price', 'Total Sales', 'Transaction Count', 'Avg Commission']
model_comparison = model_comparison.reset_index()
st.dataframe(
    model_comparison.style.format({
        'Avg Sale Price': '${:,.2f}',
        'Total Sales': '${:,.2f}',
        'Avg Commission': '${:,.2f}'
    }),
    use_container_width=True
)

# ----------------- Trends -----------------
st.markdown('<div class="section-header">📈 Sales and Commission Trend</div>', unsafe_allow_html=True)
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change().fillna(0) * 100
trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change().fillna(0) * 100
trend_fig = px.line(
    trend_df,
    x='Quarter',
    y=['Sale Price', 'Commission Earned'],
    markers=True,
    template='plotly_dark',
    color_discrete_sequence=['#A9A9A9', '#808080']
)
trend_fig.update_layout(
    plot_bgcolor='#2A2A2A',
    paper_bgcolor='#2A2A2A',
    font=dict(color='#D3D3D3')
)
st.plotly_chart(trend_fig, use_container_width=True)

with st.expander("🔍 View Quarter-over-Quarter % Change Table", expanded=True):
    st.dataframe(trend_df[['Quarter', 'Sale Price QoQ %', 'Commission QoQ %']].style.format({'Sale Price QoQ %': '{:.2f}%', 'Commission QoQ %': '{:.2f}%'}), use_container_width=True)

with st.expander("🎞️ View Monthly Animated Trend", expanded=True):
    monthly_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
    melted = monthly_trend.melt(id_vars='Month', var_name='Metric', value_name='Amount')
    animated_fig = px.bar(
        melted,
        x='Metric',
        y='Amount',
        animation_frame='Month',
        template='plotly_dark',
        color='Metric',
        color_discrete_sequence=['#A9A9A9', '#808080']
    )
    animated_fig.update_layout(
        yaxis_tickprefix="$",
        height=500,
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(animated_fig, use_container_width=True)

# ----------------- Business Operations Tabs -----------------
st.markdown('<div class="section-header">🧪 Business Operations Insights</div>', unsafe_allow_html=True)
tab1, tab2, tab3, tab4 = st.tabs(["👥 HR Overview", "📦 Inventory Status", "📞 CRM Interactions", "👤 Customer Demographics"])

with tab1:
    st.subheader("👥 HR Overview")
    hr_data = pd.DataFrame({
        "Employee ID": [f"E{1000+i}" for i in range(20)],
        "Name": [fake.name() for _ in range(20)],
        "Role": [random.choice(["Sales Executive", "Sales Manager", "Service Technician", "Admin Clerk", "HR Specialist", "Finance Analyst"]) for _ in range(20)],
        "Department": [random.choice(["Sales", "Service", "Admin", "HR", "Finance"]) for _ in range(20)],
        "Join Date": [fake.date_between(start_date="-5y", end_date="today") for _ in range(20)],
        "Salary": [random.randint(45000, 120000) for _ in range(20)],
        "Performance Score": [round(random.uniform(2.5, 5.0), 1) for _ in range(20)]
    })
    st.dataframe(hr_data, use_container_width=True)
    st.markdown("#### 📈 Performance Distribution")
    st.plotly_chart(
        px.histogram(
            hr_data,
            x="Performance Score",
            nbins=10,
            template="plotly_dark",
            color_discrete_sequence=['#A9A9A9']
        ).update_layout(
            plot_bgcolor='#2A2A2A',
            paper_bgcolor='#2A2A2A',
            font=dict(color='#D3D3D3')
        ),
        use_container_width=True
    )

with tab2:
    st.subheader("📦 Inventory Status")
    inventory_data = pd.DataFrame({
        "Part ID": [f"P{i:04d}" for i in range(1, 21)],
        "Part Name": [fake.word().capitalize() + " " + random.choice(["Filter", "Brake", "Tire", "Battery", "Sensor", "Pump"]) for _ in range(20)],
        "Car Make": [random.choice(df['Car Make'].dropna().unique()) for _ in range(20)],
        "Stock Level": [random.randint(0, 150) for _ in range(20)],
        "Reorder Level": [random.randint(10, 60) for _ in range(20)],
        "Unit Cost": [round(random.uniform(20, 600), 2) for _ in range(20)]
    })
    st.dataframe(inventory_data, use_container_width=True)
    st.markdown("#### 🔻 Low Stock Alert")
    low_stock = inventory_data[inventory_data['Stock Level'] < inventory_data['Reorder Level']]
    st.bar_chart(low_stock.set_index("Part Name")["Stock Level"], color="#A9A9A9")

with tab3:
    st.subheader("📞 CRM Interactions")
    crm_data = pd.DataFrame({
        "Customer ID": [f"C{100+i}" for i in range(20)],
        "Customer Name": [fake.name() for _ in range(20)],
        "Contact Date": [fake.date_between(start_date="-1y", end_date="today") for _ in range(20)],
        "Interaction Type": [random.choice(["Inquiry", "Complaint", "Follow-up", "Feedback", "Service Request"]) for _ in range(20)],
        "Salesperson": [random.choice(df['Salesperson'].dropna().unique()) for _ in range(20)],
        "Satisfaction Score": [round(random.uniform(1.0, 5.0), 1) for _ in range(20)]
    })
    st.dataframe(crm_data, use_container_width=True)
    st.markdown("#### 📊 Satisfaction Over Time")
    line_chart_data = crm_data.copy()
    line_chart_data["Contact Date"] = pd.to_datetime(line_chart_data["Contact Date"])
    line_chart_data = line_chart_data.groupby("Contact Date")["Satisfaction Score"].mean().reset_index()
    line_fig = px.line(
        line_chart_data,
        x="Contact Date",
        y="Satisfaction Score",
        markers=True,
        template="plotly_dark",
        color_discrete_sequence=['#A9A9A9']
    )
    line_fig.update_layout(
        plot_bgcolor='#2A2A2A',
        paper_bgвигcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(line_fig, use_container_width=True)
    st.markdown("####  Satisfaction Score by Interaction Type")
    st.plotly_chart(
        px.box(
            crm_data,
            x="Interaction Type",
            y="Satisfaction Score",
            template="plotly_dark",
            color_discrete_sequence=['#A9A9A9']
        ).update_layout(
            plot_bgcolor='#2A2A2A',
            paper_bgcolor='#2A2A2A',
            font=dict(color='#D3D3D3')
        ),
        use_container_width=True
    )

with tab4:
    st.subheader("👤 Customer Demographics Analysis")
    demo_data = pd.DataFrame({
        "Customer ID": [f"C{100+i}" for i in range(20)],
        "Age Group": [random.choice(["18-25", "26-35", "36-45", "46-55", "55+"]) for _ in range(20)],
        "Region": [fake.state() for _ in range(20)],
        "Purchase Amount": [round(random.uniform(15000, 100000), 2) for _ in range(20)],
        "Preferred Make": [random.choice(df['Car Make'].dropna().unique()) for _ in range(20)]
    })
    st.dataframe(demo_data, use_container_width=True)
    st.markdown("####  Age Group Distribution")
    age_dist = px.histogram(
        demo_data,
        x="Age Group",
        color="Region",
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Greys
    )
    age_dist.update_layout(
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(age_dist, use_container_width=True)
    st.markdown("####  Purchase Amount by Region")
    region_purchase = px.box(
        demo_data,
        x="Region",
        y="Purchase Amount",
        template="plotly_dark",
        color_discrete_sequence=['#A9A9A9']
    )
    region_purchase.update_layout(
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(region_purchase, use_container_width=True)

# ----------------- Footer -----------------
st.markdown("""
    <hr style='border: 1px solid #4A4A4A;'>
    <center>
        <small style='color: #A9A9A9;'>© 2025 One Trust | Crafted for smarter auto-financial decisions</small>
    </center>
""", unsafe_allow_html=True)
