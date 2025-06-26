import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import datetime

# ----------------- Page Setup -----------------
st.set_page_config(page_title="🚗 Car Retailer Dashboard", layout="wide")

# ----------------- Theme Toggle -----------------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

with st.sidebar:
    theme_choice = st.radio("🎨 Theme", ["Dark", "Light"], index=0 if st.session_state.theme == "Dark" else 1)
    st.session_state.theme = theme_choice
    refresh = st.button("🔄 Refresh Data")

if refresh:
    st.experimental_rerun()

# ----------------- Apply Theme -----------------
if st.session_state.theme == "Dark":
    st.markdown("""
        <style>
            body, .stApp { background-color: #121212; color: #E0E0E0; }
            .stSelectbox, .stMultiselect, .stRadio, .stMetric, .stDownloadButton {
                background-color: #1E1E1E; color: #E0E0E0;
            }
            .stMetricLabel { color: #AAAAAA !important; }
            .stButton>button { background-color: #333333; color: #FAFAFA; }
            .css-1d391kg { background-color: #1E1E1E; border-radius: 0.5rem; }
            .metric-card { background-color: #1E1E1E; padding: 1rem; border-radius: 12px; transition: 0.3s; }
            .metric-card:hover { background-color: #2A2A2A; transform: scale(1.02); }
        </style>
    """, unsafe_allow_html=True)
    plotly_template = "plotly_dark"
    color_sequence = px.colors.sequential.Greys
else:
    st.markdown("""
        <style>
            body, .stApp { background-color: #FFFFFF; color: #000000; }
            .stSelectbox, .stMultiselect, .stRadio, .stMetric, .stDownloadButton {
                background-color: #F5F5F5; color: #000000;
            }
            .stMetricLabel { color: #555555 !important; }
            .stButton>button { background-color: #DDDDDD; color: #000000; }
            .css-1d391kg { background-color: #F0F0F0; border-radius: 0.5rem; }
            .metric-card { background-color: #F5F5F5; padding: 1rem; border-radius: 12px; transition: 0.3s; }
            .metric-card:hover { background-color: #E5E5E5; transform: scale(1.02); }
        </style>
    """, unsafe_allow_html=True)
    plotly_template = "plotly_white"
    color_sequence = px.colors.sequential.Greys

# ----------------- Load Data -----------------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/94d364e98061cd58f8b52224f33037aa7ca3ed5f/DV2.csv"
    df = pd.read_csv(url, encoding='latin1')
    df.columns = [col.strip().replace("ï»¿", "") for col in df.columns]
    df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# ----------------- Sidebar Filters -----------------
with st.sidebar:
    st.title("🔧 Filters")
    salespeople = st.multiselect("Salesperson", sorted(df['Salesperson'].dropna().unique()))
    car_makes = st.multiselect("Car Make", sorted(df['Car Make'].dropna().unique()))
    car_years = st.multiselect("Car Year", sorted(df['Car Year'].dropna().unique()))

    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.date_input("Date Range", [min_date, max_date])

    selected_metric = st.radio("Metric", ["Sale Price", "Commission Earned"], index=0)

# ----------------- Filter Data -----------------
filtered_df = df.copy()
if salespeople:
    filtered_df = filtered_df[filtered_df['Salesperson'].isin(salespeople)]
if car_makes:
    filtered_df = filtered_df[filtered_df['Car Make'].isin(car_makes)]
if car_years:
    filtered_df = filtered_df[filtered_df['Car Year'].astype(str).isin(car_years)]
if len(date_range) == 2:
    filtered_df = filtered_df[
        (filtered_df['Date'] >= pd.to_datetime(date_range[0])) &
        (filtered_df['Date'] <= pd.to_datetime(date_range[1]))
    ]

# ----------------- Title -----------------
st.title("🚗 Car Retailer Sales Dashboard")

# ----------------- Summary Metrics -----------------
st.markdown("### 📌 Summary Metrics")
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="metric-card">💰 **Total Sales**<br>${filtered_df["Sale Price"].sum():,.0f}</div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="metric-card">🏆 **Total Commission**<br>${filtered_df["Commission Earned"].sum():,.0f}</div>', unsafe_allow_html=True)
with k3:
    avg_price = filtered_df['Sale Price'].mean() if not filtered_df.empty else 0
    st.markdown(f'<div class="metric-card">📊 **Avg Sale Price**<br>${avg_price:,.0f}</div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="metric-card">📦 **Transactions**<br>{filtered_df.shape[0]:,}</div>', unsafe_allow_html=True)

# ----------------- Download Buttons -----------------
st.markdown("### 📁 Export Data")
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    filtered_df.to_excel(writer, index=False, sheet_name='FilteredData')
st.download_button("Download CSV", filtered_df.to_csv(index=False).encode(), "filtered_data.csv", "text/csv")
st.download_button("Download Excel", excel_buffer.getvalue(), "filtered_data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
st.download_button("Download JSON", filtered_df.to_json(orient="records").encode(), "filtered_data.json", "application/json")

# ----------------- Bar Chart -----------------
st.subheader(f"📊 Top 10 Salespeople by {selected_metric}")
top_salespeople = (
    filtered_df.groupby('Salesperson')[selected_metric]
    .sum().nlargest(10).reset_index().sort_values(by=selected_metric)
)
bar_fig = go.Figure(data=[
    go.Bar(
        x=top_salespeople['Salesperson'],
        y=top_salespeople[selected_metric],
        marker=dict(color=top_salespeople[selected_metric], colorscale='Greys', line=dict(color='white', width=1)),
        hovertemplate='<b>%{x}</b><br>' + selected_metric + ': %{y:$,.0f}<extra></extra>',
    )
])
bar_fig.update_layout(template=plotly_template, xaxis_title="Salesperson", yaxis_title=selected_metric, height=500)
st.plotly_chart(bar_fig, use_container_width=True)

# ----------------- Pie Chart -----------------
st.subheader(f"🧩 Top 10 Car Makes by {selected_metric}")
car_make_metric = (
    filtered_df.groupby('Car Make')[selected_metric]
    .sum().nlargest(10).reset_index()
)
pulls = [0.1 if i == 0 else 0.05 for i in range(len(car_make_metric))]
pie_fig = go.Figure(data=[
    go.Pie(
        labels=car_make_metric['Car Make'],
        values=car_make_metric[selected_metric],
        pull=pulls,
        hole=0.2,
        marker=dict(colors=color_sequence, line=dict(color='white', width=1)),
        textinfo='label+percent',
        hoverinfo='label+percent+value'
    )
])
pie_fig.update_layout(template=plotly_template, height=500)
st.plotly_chart(pie_fig, use_container_width=False)

# ----------------- Trend Line -----------------
st.subheader("📈 Sales and Commission Trend by Quarter")
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change().fillna(0) * 100
trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change().fillna(0) * 100
trend_fig = px.line(
    trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'],
    markers=True, template=plotly_template,
    color_discrete_sequence=['#AAAAAA', '#555555'],
    labels={'value': 'Amount', 'Quarter': 'Quarter'}
)
st.plotly_chart(trend_fig, use_container_width=True)

# ----------------- QoQ Table -----------------
with st.expander("🔍 View Quarter-over-Quarter % Change Table", expanded=True):
    st.dataframe(
        trend_df[['Quarter', 'Sale Price QoQ %', 'Commission QoQ %']].style.format({
            'Sale Price QoQ %': '{:.2f}%',
            'Commission QoQ %': '{:.2f}%'
        }),
        use_container_width=True
    )

# ----------------- Monthly Animation -----------------
with st.expander("🎞️ View Monthly Animated Trend", expanded=True):
    monthly_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
    melted = monthly_trend.melt(id_vars='Month', var_name='Metric', value_name='Amount')
    animated_fig = px.bar(
        melted,
        x='Metric',
        y='Amount',
        animation_frame='Month',
        template=plotly_template,
        color='Metric',
        color_discrete_sequence=['#AAAAAA', '#555555'],
        labels={'Amount': 'Amount ($)', 'Metric': 'Metric'},
        title="📽️ Monthly Trend Animation"
    )
    animated_fig.update_layout(yaxis_tickprefix="$", height=500)
    st.plotly_chart(animated_fig, use_container_width=True)
