import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ----------------- Page Setup -----------------
st.set_page_config(page_title="🚗 Car Retailer Dashboard", layout="wide")
st.title("🚗 Car Retailer Sales Dashboard")

# ----------------- Dark Monochrome Theme -----------------
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

# ----------------- Filters -----------------
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

# ----------------- Optional Car Model Slicer -----------------
selected_model = None
if car_makes and len(car_makes) == 1:
    model_options = df[df['Car Make'] == car_makes[0]]['Car Model'].dropna().unique()
    selected_model = st.selectbox(f"Model for {car_makes[0]}", sorted(model_options))

# ----------------- Filtered Data -----------------
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
st.markdown("### 📥 Download Filtered Data")
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_car_sales.csv", "text/csv")

# ----------------- Bar Chart: Top Salespeople -----------------
st.subheader(f"📊 Top 10 Salespeople by {selected_metric}")
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
            colorscale='Greys',
            showscale=True,
            line=dict(color='white', width=1.2)
        ),
        hovertemplate='<b>%{x}</b><br>' + selected_metric + ': %{y:$,.0f}<extra></extra>',
    )
])
bar_fig.update_layout(
    template='plotly_dark',
    xaxis_title="Salesperson",
    yaxis_title=selected_metric,
    height=500
)
st.plotly_chart(bar_fig, use_container_width=True)

# ----------------- Pie Charts: Top Car Makes & Models -----------------
st.subheader("🧩 Top 10 Car Makes and Models by Sale Price")
col_left, col_right = st.columns(2)

with col_left:
    car_make_metric = (
        filtered_df.groupby('Car Make')['Sale Price']
        .sum().nlargest(10).reset_index()
    )
    pulls_make = [0.1 if i == 0 else 0.05 for i in range(len(car_make_metric))]

    pie_fig_make = go.Figure(data=[
        go.Pie(
            labels=car_make_metric['Car Make'],
            values=car_make_metric['Sale Price'],
            pull=pulls_make,
            hole=0.2,
            marker=dict(
                colors=px.colors.sequential.Greys,
                line=dict(color='white', width=1)
            ),
            textinfo='label+percent',
            hoverinfo='label+percent+value'
        )
    ])
    pie_fig_make.update_layout(template='plotly_dark', height=700, title="Top Car Makes by Sale Price")
    st.plotly_chart(pie_fig_make, use_container_width=True)

with col_right:
    car_model_metric = (
        filtered_df.groupby('Car Model')['Sale Price']
        .sum().nlargest(10).reset_index()
    )
    pulls_model = [0.1 if i == 0 else 0.05 for i in range(len(car_model_metric))]

    pie_fig_model = go.Figure(data=[
        go.Pie(
            labels=car_model_metric['Car Model'],
            values=car_model_metric['Sale Price'],
            pull=pulls_model,
            hole=0.2,
            marker=dict(
                colors=px.colors.sequential.Greys[::-1],
                line=dict(color='white', width=1)
            ),
            textinfo='label+percent',
            hoverinfo='label+percent+value'
        )
    ])
    pie_fig_model.update_layout(template='plotly_dark', height=700, title="Top Car Models by Sale Price")
    st.plotly_chart(pie_fig_model, use_container_width=True)

# ----------------- Trend Line -----------------
st.subheader("📈 Sales and Commission Trend by Quarter")
trend_df = filtered_df.groupby('Quarter')[['Sale Price', 'Commission Earned']].sum().reset_index()
trend_df['Sale Price QoQ %'] = trend_df['Sale Price'].pct_change().fillna(0) * 100
trend_df['Commission QoQ %'] = trend_df['Commission Earned'].pct_change().fillna(0) * 100

trend_fig = px.line(
    trend_df, x='Quarter', y=['Sale Price', 'Commission Earned'],
    markers=True, template='plotly_dark',
    color_discrete_sequence=['#AAAAAA', '#555555'],
    labels={'value': 'Amount', 'Quarter': 'Quarter'}
)
st.plotly_chart(trend_fig, use_container_width=True)

# ----------------- QoQ % Change Table -----------------
with st.expander("🔍 View Quarter-over-Quarter % Change Table", expanded=True):
    st.dataframe(
        trend_df[['Quarter', 'Sale Price QoQ %', 'Commission QoQ %']].style.format({
            'Sale Price QoQ %': '{:.2f}%',
            'Commission QoQ %': '{:.2f}%'
        }),
        use_container_width=True
    )

# ----------------- Monthly Animated Trend -----------------
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
        color_discrete_sequence=['#AAAAAA', '#555555'],
        labels={'Amount': 'Amount ($)', 'Metric': 'Metric'},
        title="📽️ Monthly Trend Animation"
    )
    animated_fig.update_layout(yaxis_tickprefix="$", height=500)
    st.plotly_chart(animated_fig, use_container_width=True)
