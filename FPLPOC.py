import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------- Page Setup -----------------
st.set_page_config(page_title="📊 FPL One Trust - Unified Dashboard", layout="wide")
st.title("📊 FPL One Trust - Investment & Automobile Dashboard")

# ----------------- Dark Theme -----------------
st.markdown("""
    <style>
        body, .stApp {
            background-color: #121212;
            color: #E0E0E0;
            font-family: 'Segoe UI', sans-serif;
        }
        .stSelectbox, .stMultiselect, .stRadio, .stMetric, .stDownloadButton {
            background-color: #1E1E1E;
            color: #E0E0E0;
        }
        .stMetricLabel {
            color: #AAAAAA !important;
        }
        .stButton>button {
            background-color: #333333;
            color: #FAFAFA;
        }
        .css-1d391kg {
            background-color: #1E1E1E;
            border-radius: 0.5rem;
        }
        .stDataFrame, .element-container {
            color: #FAFAFA;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------- Load Data (CSV + Mock) -----------------
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

def load_mock_investment_data():
    np.random.seed(42)
    dates = pd.date_range(start="2023-01-01", periods=18, freq="M")
    funds = ['Balanced Fund', 'Equity Fund', 'Debt Fund', 'Tax Saver Fund', 'Retirement Fund']
    advisors = ["Advisor A", "Advisor B", "Advisor C", "Advisor D"]
    clients = [f"Client {i}" for i in range(1, 51)]
    car_makes = ["Toyota", "Ford", "Honda", "Hyundai", "Tata"]
    car_models = ["Model A", "Model B", "Model C", "Model D", "Model E"]

    df = pd.DataFrame({
        "Date": np.random.choice(dates, 500),
        "Fund": np.random.choice(funds, 500),
        "Advisor": np.random.choice(advisors, 500),
        "Client": np.random.choice(clients, 500),
        "Investment Amount": np.random.randint(10000, 500000, 500),
        "Car Make": np.random.choice(car_makes, 500),
        "Car Model": np.random.choice(car_models, 500),
        "Car Year": np.random.choice(range(2015, 2024), 500),
        "Sale Price": np.random.randint(200000, 2000000, 500)
    })
    df['Returns'] = df['Investment Amount'] * np.random.uniform(0.02, 0.12, size=len(df))
    df['Date'] = pd.to_datetime(df['Date'])
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df

retail_df = load_retail_csv()
invest_df = load_mock_investment_data()

# Combine data sources on common columns (mock join)
retail_df['Source'] = 'Retail CSV'
invest_df['Source'] = 'Mock Investment'

# Merge for visualization
common_cols = list(set(retail_df.columns) & set(invest_df.columns))
full_df = pd.concat([retail_df[common_cols], invest_df[common_cols]], ignore_index=True)

# ----------------- Filters -----------------
st.sidebar.header("🔍 Filters")

salespeople = st.sidebar.multiselect("Salesperson", sorted(retail_df['Salesperson'].dropna().unique()))
car_makes = st.sidebar.multiselect("Car Make", sorted(full_df['Car Make'].dropna().unique()))
car_years = st.sidebar.multiselect("Car Year", sorted(full_df['Car Year'].dropna().unique()))
advisors = st.sidebar.multiselect("Advisor", sorted(invest_df['Advisor'].unique()))
funds = st.sidebar.multiselect("Fund", sorted(invest_df['Fund'].unique()))
metric = st.sidebar.radio("Metric", ["Sale Price", "Commission Earned", "Investment Amount", "Returns"], horizontal=True)

# Apply filters
filtered_df = full_df.copy()
if salespeople:
    filtered_df = filtered_df[filtered_df['Salesperson'].isin(salespeople)]
if car_makes:
    filtered_df = filtered_df[filtered_df['Car Make'].isin(car_makes)]
if car_years:
    filtered_df = filtered_df[filtered_df['Car Year'].astype(str).isin(car_years)]
if advisors:
    filtered_df = filtered_df[filtered_df['Advisor'].isin(advisors)]
if funds:
    filtered_df = filtered_df[filtered_df['Fund'].isin(funds)]

# ----------------- Metrics -----------------
st.markdown("### 📌 Summary Metrics")
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("💰 Total Sales", f"${filtered_df['Sale Price'].sum():,.0f}")
with k2:
    st.metric("💹 Total Returns", f"${filtered_df['Returns'].sum():,.0f}")
with k3:
    st.metric("💼 Total AUM", f"${filtered_df['Investment Amount'].sum():,.0f}")
with k4:
    st.metric("🧾 Transactions", f"{filtered_df.shape[0]:,}")

# ----------------- Charts -----------------
st.subheader(f"📊 Top 10 by {metric}")
top_group = 'Salesperson' if metric in ["Sale Price", "Commission Earned"] else 'Advisor'
top_data = filtered_df.groupby(top_group)[metric].sum().nlargest(10).reset_index()
st.plotly_chart(px.bar(top_data, x=top_group, y=metric, template='plotly_dark'), use_container_width=True)

st.subheader("🚘 Top Car Makes and Models by Sale Price")
col1, col2 = st.columns(2)
with col1:
    cmake = filtered_df.groupby('Car Make')['Sale Price'].sum().nlargest(10).reset_index()
    st.plotly_chart(px.pie(cmake, names='Car Make', values='Sale Price', hole=0.3, template='plotly_dark'))
with col2:
    cmodel = filtered_df.groupby('Car Model')['Sale Price'].sum().nlargest(10).reset_index()
    st.plotly_chart(px.bar(cmodel, x='Car Model', y='Sale Price', template='plotly_dark'))

st.subheader("📈 Quarterly Trends")
trend_df = filtered_df.groupby('Quarter')[["Sale Price", "Commission Earned", "Investment Amount", "Returns"]].sum().reset_index()
st.plotly_chart(px.line(trend_df, x='Quarter', y=trend_df.columns[1:], markers=True, template='plotly_dark'), use_container_width=True)

# ----------------- Tabs -----------------
st.markdown("---")
st.header("🧪 Business Operations")
tab1, tab2, tab3 = st.tabs(["👥 HR Overview", "📦 Inventory Status", "📞 CRM Interactions"])

with tab1:
    st.subheader("👥 HR Overview")
    hr_data = pd.DataFrame({
        "Employee ID": [f"E{1000+i}" for i in range(10)],
        "Name": [f"Employee {i}" for i in range(1, 11)],
        "Role": ["Advisor", "Manager", "Tech", "Clerk", "Advisor", "Tech", "HR", "Manager", "Clerk", "Advisor"],
        "Join Date": pd.date_range(start="2019-01-01", periods=10, freq="180D"),
        "Salary": [60000 + i*2000 for i in range(10)],
        "Performance Score": [round(x, 1) for x in np.random.uniform(2.5, 5.0, 10)]
    })
    st.dataframe(hr_data, use_container_width=True)
    st.plotly_chart(px.histogram(hr_data, x="Performance Score", nbins=5, template="plotly_dark"), use_container_width=True)

with tab2:
    st.subheader("📦 Inventory Status")
    inventory_data = pd.DataFrame({
        "Part ID": [f"P{i:03d}" for i in range(1, 11)],
        "Part Name": [f"Part {i}" for i in range(1, 11)],
        "Car Make": np.random.choice(filtered_df['Car Make'].dropna().unique(), size=10),
        "Stock Level": np.random.randint(0, 100, size=10),
        "Reorder Level": np.random.randint(10, 50, size=10),
        "Unit Cost": [round(x, 2) for x in np.random.uniform(50, 500, 10)]
    })
    st.dataframe(inventory_data, use_container_width=True)
    low_stock = inventory_data[inventory_data['Stock Level'] < inventory_data['Reorder Level']]
    st.bar_chart(low_stock.set_index("Part Name")["Stock Level"])

with tab3:
    st.subheader("📞 CRM Interactions")
    crm_data = pd.DataFrame({
        "Customer ID": [f"C{100+i}" for i in range(10)],
        "Customer Name": [f"Customer {chr(65+i)}" for i in range(10)],
        "Contact Date": pd.date_range(end=pd.to_datetime("today"), periods=10),
        "Interaction Type": np.random.choice(["Inquiry", "Complaint", "Follow-up", "Feedback"], size=10),
        "Salesperson": np.random.choice(retail_df['Salesperson'].dropna().unique(), size=10),
        "Satisfaction Score": [round(x, 1) for x in np.random.uniform(1.0, 5.0, 10)]
    })
    st.dataframe(crm_data, use_container_width=True)
    st.plotly_chart(px.box(crm_data, x="Interaction Type", y="Satisfaction Score", template="plotly_dark"), use_container_width=True)

# ----------------- Download -----------------
st.markdown("### 📥 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "merged_dashboard_data.csv", "text/csv")
