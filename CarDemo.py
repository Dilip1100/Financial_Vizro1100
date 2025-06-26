import streamlit as st
import pandas as pd
import plotly.express as px
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
    return df

df = load_data()

# ---- Page Config ----
st.set_page_config(page_title="🚗 Car Retailer Dashboard", layout="wide")
st.title("🚗 Car Retailer Sales Dashboard")

# ---- Apply Custom Theme ----
st.markdown("""
    <style>
        body, .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stSelectbox, .stMultiselect, .stRadio, .stMetric, .stDownloadButton {
            background-color: #1C1F26;
            color: #FAFAFA;
        }
        .stMetricLabel {
            color: #BBBBBB !important;
        }
        .stButton>button {
            background-color: #3A3F4B;
            color: white;
        }
        .css-1d391kg {
            background-color: #1C1F26;
            border-radius: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---- Top Filters (Slicers) ----
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

# ---- KPI Summary Cards ----
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

# ---- Download Filtered Data ----
st.markdown("### 📥 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_car_sales.csv", "text/csv")

# ---- 3D-Style Bar Chart: Top Salespeople ----
st.subheader(f"📊 Top 10 Salespeople by {selected_metric} (3D Style)")
top_salespeople = (
    filtered_df.groupby('Salesperson')[selected_metric]
    .sum().nlargest(10).reset_index().sort_values(by=selected_metric)
)

bar_fig = go.Figure(data=[
    go.Bar(
        x=top_salespeople['Salesperson'],
        y=top_salespeople[selected_metric],
        marker=dict(
            color=top_salespeople[selected_metric],
            colorscale='Inferno',
            showscale=True,
            line=dict(color='gray', width=1.5)
        ),
        hovertemplate='<b>%{x}</b><br>' + selected_metric + ': %{y:$,.0f}<extra></extra>',
    )
])

bar_fig.update_layout(
    template="plotly_dark",
    title=f"Top 10 Salespeople by {selected_metric}",
    xaxis_title="Salesperson",
    yaxis_title=selected_metric,
    margin=dict(l=40, r=20, t=60, b=80),
    height=600,
    scene_camera_eye=dict(x=1.5, y=1.5, z=0.8),
)
st.plotly_chart(bar_fig, use_container_width=True)

# ---- 3D-Style Pie Chart: Top Car Makes ----
st.subheader(f"🧩 Top 10 Car Makes by {selected_metric} (3D Style)")

car_make_metric = (
    filtered_df.groupby('Car Make')[selected_metric]
    .sum().nlargest(10).reset_index()
)
pull_values = [0.1 if i == 0 else 0.05 for i in range(len(car_make_metric))]

pie_fig = go.Figure(data=[
    go.Pie(
        labels=car_make_metric['Car Make'],
        values=car_make_metric[selected_metric],
        hole=0.2,
        pull=pull_values,
        marker=dict(
            colors=px.colors.sequential.Inferno,
            line=dict(color='white', width=1.5)
        ),
        hoverinfo='label+percent+value',
        textinfo='label+percent',
    )
])

pie_fig.update_layout(
    template="plotly_dark",
    title=f"Top 10 Car Makes by {selected_metric}",
    height=600,
    showlegend=True
)
st.plotly_chart(pie_fig, use_container_width=False)

# ---- Trend Line with QoQ % Change ----
st.subheader("📈 Sales and Commission Trend by Quarter")
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change().fillna(0) * 100
trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change().fillna(0) * 100

trend_fig = px.line(
    trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'],
    markers=True, template='plotly_dark',
    labels={'value': 'Amount', 'Quarter': 'Quarter'}
)
st.plotly_chart(trend_fig, use_container_width=True)

with st.expander("🔍 View Quarter-over-Quarter % Change Table"):
    st.dataframe(
        trend_df[['Quarter', 'Sale Price QoQ %', 'Commission QoQ %']].style.format({
            'Sale Price QoQ %': '{:.2f}%',
            'Commission QoQ %': '{:.2f}%'
        }),
        use_container_width=True
    )

# ---- Animated Monthly Trend ----
with st.expander("🎞️ View Monthly Animated Trend"):
    monthly_trend = filtered_df.groupby('Month')[['Sale Price', 'Commission Earned']].sum().reset_index()
    melted = monthly_trend.melt(id_vars='Month', var_name='Metric', value_name='Amount')

    animated_fig = px.bar(
        melted,
        x='Metric',
        y='Amount',
        animation_frame='Month',
        template='plotly_dark',
        color='Metric',
        color_discrete_sequence=px.colors.sequential.Inferno,
        labels={'Amount': 'Amount ($)', 'Metric': 'Metric'},
        title="📽️ Monthly Trend Animation"
    )
    animated_fig.update_layout(yaxis_tickprefix="$", height=500)
    st.plotly_chart(animated_fig, use_container_width=True)
