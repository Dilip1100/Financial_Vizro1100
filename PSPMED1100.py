import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np # Import numpy to handle NA values

# ----------------- Page Setup -----------------
st.set_page_config(page_title="🏥 Hospital Infrastructure Dashboard", layout="wide")
st.title("🏥 Hospital Infrastructure Dashboard")

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
    # Use the raw GitHub URL for the CSV file to ensure correct parsing
    csv_url = "https://raw.githubusercontent.com/Dilip1100/Financial_Vizro1100/469f2e286cfd500538a995721489daad0503dd1d/PMC%20Hospital%20Infrastructure.csv"
    
    # Load data from the attached CSV file, skipping bad lines
    df = pd.read_csv(csv_url, encoding='latin1', on_bad_lines='skip')

    # Step 1: Strip leading/trailing whitespace from all column names
    df.columns = df.columns.str.strip()

    # Step 2: Define a dictionary for renaming columns
    # Keys are the exact column names after stripping, values are the desired new names
    rename_mapping = {
        'Type  (Hospital / Nursing Home / Lab)': 'Facility Type', 
        'Class : (Public / Private)': 'Class (Public/Private)',
        'Pharmacy Available : Yes/No': 'Pharmacy Available',
        'Number of Beds in facility type': 'Number of Beds',
        'Number of Doctors / Physicians': 'Number of Doctors',
        'Number of Nurses': 'Number of Nurses',
        'Number of Midwives Professional': 'Number of Midwives',
        'Ambulance Service Available': 'Ambulance Service',
        'Count of Ambulance': 'Ambulance Count',
    }

    # Apply renaming to the DataFrame columns
    df = df.rename(columns=rename_mapping)

    # Convert numerical columns, handling 'N.A.' and other non-numeric values
    numerical_cols = [
        'Number of Beds in Emergency Wards',
        'Number of Beds',
        'Number of Doctors',
        'Number of Nurses',
        'Number of Midwives',
        'Average Monthly Patient Footfall',
        'Ambulance Count'
    ]
    for col in numerical_cols:
        # Ensure the column exists before attempting to convert it
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace('N.A.', str(np.nan), regex=False),
                errors='coerce'
            ).fillna(0).astype(int)
        else:
            # This warning should ideally not be triggered with correct renaming
            print(f"Warning: Column '{col}' not found in DataFrame for numerical conversion.")

    return df

df = load_data()

# ----------------- Filters -----------------
with st.container():
    col1, col2, col3, col4 = st.columns([3, 3, 2, 2])
    with col1:
        # Multiselect filter for Zone Name
        zones = st.multiselect("Zone Name", sorted(df['Zone Name'].dropna().unique()))
    with col2:
        # Multiselect filter for Facility Type
        facility_types = st.multiselect("Facility Type", sorted(df['Facility Type'].dropna().unique()))
    with col3:
        # Multiselect filter for Class (Public/Private)
        classes = st.multiselect("Class", sorted(df['Class (Public/Private)'].dropna().unique()))
    with col4:
        # Radio button to select the metric for analysis in summary and bar charts
        selected_metric = st.radio("Metric", [
            "Number of Beds",
            "Number of Doctors",
            "Number of Nurses",
            "Average Monthly Patient Footfall",
            "Ambulance Count"
        ], index=0, horizontal=True)

# ----------------- Optional Ward Name Slicer (if only one zone is selected) -----------------
selected_ward = None
if zones and len(zones) == 1:
    # Get unique ward names for the selected zone
    ward_options = df[df['Zone Name'] == zones[0]]['Ward Name'].dropna().unique()
    # Provide a selectbox for Ward Name to narrow down facilities within a zone
    selected_ward = st.selectbox(f"Ward Name for {zones[0]}", sorted(ward_options))

# ----------------- Filtered Data -----------------
# Create a copy of the DataFrame to apply filters
filtered_df = df.copy()
if zones:
    filtered_df = filtered_df[filtered_df['Zone Name'].isin(zones)]
if facility_types:
    filtered_df = filtered_df[filtered_df['Facility Type'].isin(facility_types)]
if classes:
    filtered_df = filtered_df[filtered_df['Class (Public/Private)'].isin(classes)]
if selected_ward:
    filtered_df = filtered_df[filtered_df['Ward Name'] == selected_ward]

# ----------------- Summary Metrics -----------------
st.markdown("### 📌 Summary Metrics")
# Display key performance indicators using Streamlit's metric function
k1, k2, k3, k4 = st.columns(4)

with k1:
    # Total Number of Facilities after filtering
    st.metric("🏥 Total Facilities", f"{filtered_df.shape[0]:,}")
with k2:
    # Sum of 'Number of Beds' for filtered facilities
    total_beds = filtered_df['Number of Beds'].sum()
    st.metric("🛏️ Total Beds", f"{total_beds:,}")
with k3:
    # Sum of 'Number of Doctors' for filtered facilities
    total_doctors = filtered_df['Number of Doctors'].sum()
    st.metric("👨‍⚕️ Total Doctors", f"{total_doctors:,}")
with k4:
    # Sum of 'Average Monthly Patient Footfall' for filtered facilities
    total_footfall = filtered_df['Average Monthly Patient Footfall'].sum()
    st.metric("🚶‍♂️ Total Patient Footfall (Monthly)", f"{total_footfall:,}")

# ----------------- Download Button -----------------
st.markdown("### 📥 Download Filtered Data")
# Allow users to download the currently filtered dataset as a CSV
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_hospital_data.csv", "text/csv")

# ----------------- Bar Chart: Top Facilities by Selected Metric -----------------
st.subheader(f"📊 Top 10 Facilities by {selected_metric}")
# Group by 'Facility Name' and sum the selected metric, then get the top 10
top_facilities = (
    filtered_df.groupby('Facility Name')[selected_metric]
    .sum().nlargest(10).reset_index().sort_values(by=selected_metric)
)

bar_fig = go.Figure(data=[
    go.Bar(
        x=top_facilities['Facility Name'],
        y=top_facilities[selected_metric],
        marker=dict(
            color=top_facilities[selected_metric],
            colorscale='Greys', # Use a monochrome color scale for consistent theme
            showscale=True,
            line=dict(color='white', width=1.2)
        ),
        hovertemplate='<b>%{x}</b><br>' + selected_metric + ': %{y:,f}<extra></extra>',
    )
])
bar_fig.update_layout(
    template='plotly_dark', # Use dark theme for the plot
    xaxis_title="Facility Name",
    yaxis_title=selected_metric,
    height=500,
    xaxis_tickangle=-45 # Angle x-axis labels for better readability on many labels
)
st.plotly_chart(bar_fig, use_container_width=True) # Display the bar chart

# ----------------- Pie Charts: Distribution by Facility Type & Class -----------------
st.subheader("🧩 Distribution of Facilities by Type and Class")
col_left, col_right = st.columns(2)

with col_left:
    # Distribution of facilities by type (e.g., Hospital, Dispensary, Lab)
    facility_type_counts = filtered_df['Facility Type'].value_counts()
    
    # Calculate percentages for grouping
    total_facilities = facility_type_counts.sum()
    threshold = 0.02 * total_facilities # 2% threshold for 'Other' category

    # Group small categories into 'Other'
    main_types = facility_type_counts[facility_type_counts >= threshold]
    other_count = facility_type_counts[facility_type_counts < threshold].sum()

    if other_count > 0:
        facility_type_distribution = pd.concat([main_types, pd.Series({'Other': other_count})]).reset_index()
    else:
        facility_type_distribution = main_types.reset_index()
        
    facility_type_distribution.columns = ['Facility Type', 'Count'] # Rename columns

    # Determine pull for explosion effect on pie chart, emphasizing the largest slice
    pulls_type = [0.1 if i == 0 else 0.05 for i in range(len(facility_type_distribution))]

    pie_fig_type = go.Figure(data=[
        go.Pie(
            labels=facility_type_distribution['Facility Type'],
            values=facility_type_distribution['Count'],
            pull=pulls_type,
            hole=0.2, # Creates a donut chart
            marker=dict(
                colors=px.colors.sequential.Greys, # Use a sequential monochrome palette for consistency
                line=dict(color='white', width=1) # White border for slices
            ),
            textinfo='label+percent', # Display label and percentage on slices
            hoverinfo='label+percent+value' # Display label, percentage, and value on hover
        )
    ])
    pie_fig_type.update_layout(template='plotly_dark', height=700, title="Distribution by Facility Type")
    st.plotly_chart(pie_fig_type, use_container_width=True) # Display the pie chart

with col_right:
    # Distribution of facilities by class (Public/Private)
    class_distribution = (
        filtered_df['Class (Public/Private)'].value_counts().reset_index()
    )
    class_distribution.columns = ['Class (Public/Private)', 'Count'] # Rename columns

    # Determine pull for explosion effect on pie chart, emphasizing the largest slice
    pulls_class = [0.1 if i == 0 else 0.05 for i in range(len(class_distribution))]

    pie_fig_class = go.Figure(data=[
        go.Pie(
            labels=class_distribution['Class (Public/Private)'],
            values=class_distribution['Count'],
            pull=pulls_class,
            hole=0.2, # Creates a donut chart
            marker=dict(
                colors=px.colors.sequential.Greys[::-1], # Reversed sequential monochrome palette
                line=dict(color='white', width=1) # White border for slices
            ),
            textinfo='label+percent', # Display label and percentage on slices
            hoverinfo='label+percent+value' # Display label, percentage, and value on hover
        )
    ])
    pie_fig_class.update_layout(template='plotly_dark', height=700, title="Distribution by Class (Public/Private)")
    st.plotly_chart(pie_fig_class, use_container_width=True) # Display the pie chart

# No time-series charts as the dataset does not contain date/time information.
