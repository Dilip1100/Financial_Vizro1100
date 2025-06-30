# Final Merged Script:  + CarDemo + Animated 3D View + All Components

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------- Page Setup -----------------
st.set_page_config(page_title="Automotive Dashboard", layout="wide")
st.markdown("""
    <style>
        body, .stApp {
            background-color: #1a1a1a;
            color: #f1f1f1;
            font-family: 'Segoe UI', sans-serif;
        }
        .stSelectbox, .stMultiselect, .stRadio, .stMetric, .stDownloadButton {
            background-color: #262626;
            color: #f1f1f1;
        }
        .stMetricLabel {
            color: #bbbbbb !important;
        }
        .stButton>button {
            background-color: #404040;
            color: #f1f1f1;
        }
        .css-1d391kg {
            background-color: #262626;
            border-radius: 0.5rem;
        }
        .stDataFrame, .element-container {
            color: #f1f1f1;
        }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ----------------- Header -----------------
st.image("https://fplonetrust.com/img/logo.webp", width=180)
st.title("🚘  One Trust - Unified Automotive Dashboard")

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
st.markdown("### 🔍 Filter Options")
col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
with col1:
    salespeople = st.multiselect("Salesperson", sorted(df['Salesperson'].dropna().unique()))
with col2:
    car_makes = st.multiselect("Car Make", sorted(df['Car Make'].dropna().unique()))
with col3:
    car_years = st.multiselect("Car Year", sorted(df['Car Year'].dropna().unique()))
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
st.markdown("### 📌 Summary Metrics")
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

# ----------------- Download Button -----------------
st.markdown("### 📅 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_car_sales.csv", "text/csv")

# ----------------- Animated 3D Investment vs Sales -----------------
st.markdown("### 🎥 Animated 3D Investment vs Sales")
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
    opacity=0.7
)
animated_fig.update_layout(height=650)
st.plotly_chart(animated_fig, use_container_width=True)

# ----------------- Existing Charts -----------------
st.subheader(f"📊 Top 10 Salespeople by {selected_metric}")
top_salespeople = (
    filtered_df.groupby('Salesperson')[selected_metric]
    .sum().nlargest(10).reset_index().sort_values(by=selected_metric)
)
bar_fig = go.Figure(data=[
    go.Bar(
        x=top_salespeople['Salesperson'],
        y=top_salespeople[selected_metric],
        marker=dict(color=top_salespeople[selected_metric], colorscale='Greys', showscale=True, line=dict(color='white', width=1.2)),
        hovertemplate='<b>%{x}</b><br>' + selected_metric + ': %{y:$,.0f}<extra></extra>',
    )
])
bar_fig.update_layout(template='plotly_dark', xaxis_title="Salesperson", yaxis_title=selected_metric, height=500)
st.plotly_chart(bar_fig, use_container_width=True)

st.subheader("🧹 Top 10 Car Makes and Models by Sale Price")
col_left, col_right = st.columns(2)

with col_left:
    car_make_metric = filtered_df.groupby('Car Make')['Sale Price'].sum().nlargest(10).reset_index()
    pie_fig_make = px.pie(car_make_metric, names='Car Make', values='Sale Price', hole=0.2, color_discrete_sequence=px.colors.sequential.Greys)
    pie_fig_make.update_layout(template='plotly_dark', height=700, title="Top Car Makes by Sale Price")
    st.plotly_chart(pie_fig_make, use_container_width=True)

with col_right:
    car_model_metric = filtered_df.groupby('Car Model')['Sale Price'].sum().nlargest(10).reset_index()
    pie_fig_model = px.pie(car_model_metric, names='Car Model', values='Sale Price', hole=0.2, color_discrete_sequence=px.colors.sequential.Greys[::-1])
    pie_fig_model.update_layout(template='plotly_dark', height=700, title="Top Car Models by Sale Price")
    st.plotly_chart(pie_fig_model, use_container_width=True)

# ----------------- Trends -----------------
st.subheader("📈 Sales and Commission Trend by Quarter")
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change().fillna(0) * 100
trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change().fillna(0) * 100
trend_fig = px.line(trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'], markers=True, template='plotly_dark', color_discrete_sequence=['#AAAAAA', '#555555'])
st.plotly_chart(trend_fig, use_container_width=True)

with st.expander("🔍 View Quarter-over-Quarter % Change Table", expanded=True):
    st.dataframe(trend_df[['Quarter', 'Sale Price QoQ %', 'Commission QoQ %']].style.format({'Sale Price QoQ %': '{:.2f}%', 'Commission QoQ %': '{:.2f}%'}), use_container_width=True)

with st.expander("🎞️ View Monthly Animated Trend", expanded=True):
    monthly_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
    melted = monthly_trend.melt(id_vars='Month', var_name='Metric', value_name='Amount')
    animated_fig = px.bar(melted, x='Metric', y='Amount', animation_frame='Month', template='plotly_dark', color='Metric', color_discrete_sequence=['#AAAAAA', '#555555'])
    animated_fig.update_layout(yaxis_tickprefix="$", height=500)
    st.plotly_chart(animated_fig, use_container_width=True)

# ----------------- Business Operations Tabs -----------------
st.markdown("---")
st.header("🧪 Business Operations Insights")
tab1, tab2, tab3 = st.tabs(["👥 HR Overview", "📦 Inventory Status", "📞 CRM Interactions"])

with tab1:
    st.subheader("👥 HR Overview")
    hr_data = pd.DataFrame({
        "Employee ID": [f"E{1000+i}" for i in range(10)],
        "Name": [f"Employee {i}" for i in range(1, 11)],
        "Role": ["Sales Exec", "Manager", "Technician", "Clerk", "Sales Exec", "Technician", "HR", "Manager", "Clerk", "Sales Exec"],
        "Department": ["Sales", "Sales", "Service", "Admin", "Sales", "Service", "HR", "Sales", "Admin", "Sales"],
        "Join Date": pd.date_range(start="2018-01-01", periods=10, freq="180D"),
        "Salary": [50000 + i*1500 for i in range(10)],
        "Performance Score": [round(x, 1) for x in np.random.uniform(2.5, 5.0, 10)]
    })
    st.dataframe(hr_data, use_container_width=True)
    st.markdown("#### 📈 Performance Distribution")
    st.plotly_chart(px.histogram(hr_data, x="Performance Score", nbins=5, template="plotly_dark"), use_container_width=True)

with tab2:
    st.subheader("📦 Inventory Status")
    inventory_data = pd.DataFrame({
        "Part ID": [f"P{i:03d}" for i in range(1, 11)],
        "Part Name": [f"Part {i}" for i in range(1, 11)],
        "Car Make": np.random.choice(df['Car Make'].dropna().unique(), size=10),
        "Stock Level": np.random.randint(0, 100, size=10),
        "Reorder Level": np.random.randint(10, 50, size=10),
        "Unit Cost": [round(x, 2) for x in np.random.uniform(50, 500, 10)]
    })
    st.dataframe(inventory_data, use_container_width=True)
    st.markdown("#### 🔻 Low Stock Alert")
    low_stock = inventory_data[inventory_data['Stock Level'] < inventory_data['Reorder Level']]
    st.bar_chart(low_stock.set_index("Part Name")["Stock Level"])

with tab3:
    st.subheader("📞 CRM Interactions")
    crm_data = pd.DataFrame({
        "Customer ID": [f"C{100+i}" for i in range(10)],
        "Customer Name": [f"Customer {chr(65+i)}" for i in range(10)],
        "Contact Date": pd.date_range(end=pd.to_datetime("today"), periods=10),
        "Interaction Type": np.random.choice(["Inquiry", "Complaint", "Follow-up", "Feedback"], size=10),
        "Salesperson": np.random.choice(df['Salesperson'].dropna().unique(), size=10),
        "Satisfaction Score": [round(x, 1) for x in np.random.uniform(1.0, 5.0, 10)]
    })
    st.dataframe(crm_data, use_container_width=True)

    # Add line chart before box plot
    st.markdown("#### 📊 Satisfaction Over Time")
    line_chart_data = crm_data.copy()
    line_chart_data["Contact Date"] = pd.to_datetime(line_chart_data["Contact Date"])
    line_chart_data = line_chart_data.groupby("Contact Date")["Satisfaction Score"].mean().reset_index()
    line_fig = px.line(line_chart_data, x="Contact Date", y="Satisfaction Score", markers=True, template="plotly_dark")
    st.plotly_chart(line_fig, use_container_width=True)

    st.markdown("#### 😊 Satisfaction Score by Interaction Type")
    st.plotly_chart(px.box(crm_data, x="Interaction Type", y="Satisfaction Score", template="plotly_dark"), use_container_width=True)

# ----------------- Footer -----------------
st.markdown("""
    <hr style='border: 1px solid #333;'>
    <center>
        <small>© 2025  One Trust | Crafted for smarter auto-financial decisions</small>
    </center>
""", unsafe_allow_html=True)
