# Enhanced Medical College & Hospital Dashboard with Monochrome Theme and Faker Data

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from faker import Faker
import random
from datetime import datetime, timedelta
import os
import sys

# ----------------- Try Importing Faker -----------------
try:
    from faker import Faker
except ImportError:
    os.system(f"{sys.executable} -m pip install faker")
    from faker import Faker

# Initialize Faker
fake = Faker()

# ----------------- Page Setup -----------------
st.set_page_config(page_title="Medical College & Hospital Dashboard", layout="wide")
st.markdown("""
    <style>
        body, .stApp {
            background-color: #1C1C1C;
            color: #D3D3D3;
            font-family: 'Segoe UI', sans-serif;
        }
        .stSelectbox, .stMultiselect, .stRadio, .stMetric, .stDownloadButton, .stTextInput {
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
st.title("🏥 Medical College & Hospital Dashboard")
st.markdown("Advanced insights for healthcare operations and patient management", unsafe_allow_html=True)

# ----------------- Configuration -----------------
admin_departments = ['Hospital Admin - Finance', 'Hospital Admin - HR', 'Hospital Admin - Insurance',
                     'College Admin - Finance', 'College Admin - HR']

non_clinical_departments = [
    "Pharmacology", "Lab Tests", "Biopsy", "Pathology", "Microbiology",
    "Forensic", "Anatomy", "Physiology", "Biochemistry"
]

clinical_departments = [
    "General Medicine", "General Surgery", "Orthopedics", "Dermatology",
    "ENT", "Ophthalmology", "Psychiatry", "Nephrology", "Cardiology",
    "Neurosurgery", "Plastic Surgery", "Medical Oncology",
    "Surgical Oncology", "Gastroenterology Medical", "Gastroenterology Surgical"
]

all_medical_departments = clinical_departments + non_clinical_departments

# ----------------- Data Generation -----------------
def generate_doctor_data(n=200):
    specialties = ["MD", "MS", "DM", "MCh", "PhD", "MBBS"]
    return pd.DataFrame([{
        "Doctor ID": f"D{1000+i}",
        "Doctor Name": fake.name(),
        "Department": random.choice(all_medical_departments),
        "Specialty": random.choice(specialties),
        "Years of Experience": random.randint(2, 30),
        "Email": fake.email()
    } for i in range(n)])

def generate_patient_data(n=1000, doctor_df=None):
    patients = []
    for _ in range(n):
        dept = random.choice(all_medical_departments)
        assigned_doctors = doctor_df[doctor_df['Department'] == dept]
        doctor_name = assigned_doctors['Doctor Name'].sample(1).values[0] if not assigned_doctors.empty else "Unknown"
        admission_date = fake.date_between(start_date="-2y", end_date="today")
        age = random.randint(18, 90)
        patients.append({
            "Patient ID": f"P{1000+i}",
            "Name": fake.name(),
            "Age": age,
            "Sex": random.choice(["Male", "Female", "Other"]),
            "Contact": fake.phone_number(),
            "Marital Status": random.choice(["Married", "Single", "Divorced", "Widowed"]),
            "Blood Group": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
            "Religion": random.choice(["Hindu", "Muslim", "Christian", "Sikh", "Other"]),
            "Symptoms": fake.sentence(nb_words=6),
            "Department": dept,
            "Doctor": doctor_name,
            "Type": "Clinical" if dept in clinical_departments else "Non-Clinical",
            "Admission Date": admission_date,
            "Treatment Cost (₹)": round(random.uniform(5000, 500000), 2)
        })
    return pd.DataFrame(patients)

def generate_admin_data():
    return pd.DataFrame([{
        "Department": dept,
        "Month": f"2025-{month:02d}",
        "HR Count": random.randint(10, 50),
        "Finance Expense (in Lakh ₹)": round(random.uniform(10.0, 50.0), 2),
        "Insurance Claims Processed": random.randint(20, 200),
        "Patient Satisfaction Score": round(random.uniform(3.0, 5.0), 1)
    } for dept in admin_departments for month in range(1, 13)])

# ----------------- Load Data -----------------
doctor_df = generate_doctor_data()
patient_df = generate_patient_data(doctor_df=doctor_df)
admin_df = generate_admin_data()

# ----------------- Filters -----------------
st.markdown('<div class="section-header">🔍 Filter Options</div>', unsafe_allow_html=True)
f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 3, 3])
with f1:
    department_filter = st.multiselect("Department", sorted(all_medical_departments), key="department")
with f2:
    sex_filter = st.multiselect("Gender", ["Male", "Female", "Other"], key="sex")
with f3:
    blood_filter = st.multiselect("Blood Group", sorted(patient_df["Blood Group"].unique()), key="blood")
with f4:
    doctor_filter = st.multiselect("Doctor", sorted(doctor_df["Doctor Name"].unique()), key="doctor")
with f5:
    search_term = st.text_input("Search (Name, Symptoms, Contact, etc.)", key="search")

filtered = patient_df.copy()
if department_filter:
    filtered = filtered[filtered["Department"].isin(department_filter)]
if sex_filter:
    filtered = filtered[filtered["Sex"].isin(sex_filter)]
if blood_filter:
    filtered = filtered[filtered["Blood Group"].isin(blood_filter)]
if doctor_filter:
    filtered = filtered[filtered["Doctor"].isin(doctor_filter)]
if search_term:
    term = search_term.lower()
    filtered = filtered[filtered.apply(lambda r: term in str(r.values).lower(), axis=1)]

# ----------------- KPIs -----------------
st.markdown('<div class="section-header">📊 Key Metrics</div>', unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Patients", len(filtered))
k2.metric("Clinical Patients", (filtered['Type'] == 'Clinical').sum())
k3.metric("Non-Clinical Patients", (filtered['Type'] == 'Non-Clinical').sum())
k4.metric("Total Doctors", len(doctor_df))
k5.metric("Avg Treatment Cost (₹)", f"{filtered['Treatment Cost (₹)'].mean():,.0f}" if not filtered.empty else 0)

# ----------------- Download Button -----------------
st.markdown('<div class="section-header">📅 Download Filtered Data</div>', unsafe_allow_html=True)
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download Patient Data", csv, "filtered_patients.csv", "text/csv")

# ----------------- Patient Heatmap -----------------
st.markdown('<div class="section-header">🌡️ Patient Distribution Heatmap</div>', unsafe_allow_html=True)
filtered['Month'] = pd.to_datetime(filtered['Admission Date']).dt.strftime("%Y-%m")
heatmap_data = filtered.pivot_table(
    values='Patient ID',
    index='Department',
    columns='Month',
    aggfunc='count',
    fill_value=0
)
heatmap_fig = px.imshow(
    heatmap_data,
    color_continuous_scale='Greys',
    template='plotly_dark',
    text_auto=True,
    aspect='auto'
)
heatmap_fig.update_layout(
    height=600,
    plot_bgcolor='#2A2A2A',
    paper_bgcolor='#2A2A2A',
    font=dict(color='#D3D3D3')
)
st.plotly_chart(heatmap_fig, use_container_width=True)

# ----------------- Patient & Doctor Tables -----------------
st.markdown('<div class="section-header">📋 Patient Information</div>', unsafe_allow_html=True)
st.dataframe(filtered, use_container_width=True)

st.markdown('<div class="section-header">👨‍⚕️ Doctor Assignments</div>', unsafe_allow_html=True)
st.dataframe(doctor_df, use_container_width=True)

# ----------------- Patient Distribution -----------------
st.markdown('<div class="section-header">📈 Patient Distribution</div>', unsafe_allow_html=True)
d1, d2 = st.columns(2)
with d1:
    pie = px.pie(filtered, names="Sex", title="Gender Distribution", color_discrete_sequence=px.colors.sequential.Greys)
    pie.update_layout(
        template="plotly_dark",
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(pie, use_container_width=True)

with d2:
    dept_counts = filtered["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Patient Count"]
    bar = px.bar(
        dept_counts,
        x="Department",
        y="Patient Count",
        color="Department",
        title="Patients by Department",
        color_discrete_sequence=px.colors.sequential.Greys
    )
    bar.update_layout(
        template="plotly_dark",
        xaxis_tickangle=-45,
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(bar, use_container_width=True)

# ----------------- Admission Trends -----------------
st.markdown('<div class="section-header">📊 Admission Trends</div>', unsafe_allow_html=True)
admission_trend = filtered.groupby('Month')[['Patient ID']].count().reset_index()
admission_trend.columns = ['Month', 'Patient Count']
trend_fig = px.line(
    admission_trend,
    x='Month',
    y='Patient Count',
    markers=True,
    template='plotly_dark',
    color_discrete_sequence=['#A9A9A9']
)
trend_fig.update_layout(
    plot_bgcolor='#2A2A2A',
    paper_bgcolor='#2A2A2A',
    font=dict(color='#D3D3D3')
)
st.plotly_chart(trend_fig, use_container_width=True)

# ----------------- Department Performance Table -----------------
st.markdown('<div class="section-header">🏥 Department Performance</div>', unsafe_allow_html=True)
dept_performance = filtered.groupby('Department').agg({
    'Patient ID': 'count',
    'Treatment Cost (₹)': ['mean', 'sum']
}).round(2)
dept_performance.columns = ['Patient Count', 'Avg Treatment Cost (₹)', 'Total Treatment Cost (₹)']
dept_performance = dept_performance.reset_index()
st.dataframe(
    dept_performance.style.format({
        'Avg Treatment Cost (₹)': '₹{:,.2f}',
        'Total Treatment Cost (₹)': '₹{:,.2f}'
    }),
    use_container_width=True
)

# ----------------- Admin Department Overview -----------------
st.markdown('<div class="section-header">🗂️ Admin Department Insights</div>', unsafe_allow_html=True)
tabs = st.tabs(["💰 Finance", "👥 HR", "🛡️ Insurance", "😊 Satisfaction"])

with tabs[0]:
    st.subheader("💰 Finance Overview")
    st.dataframe(admin_df[admin_df["Department"].str.contains("Finance")], use_container_width=True)
    fig = px.line(
        admin_df[admin_df["Department"].str.contains("Finance")],
        x="Month",
        y="Finance Expense (in Lakh ₹)",
        color="Department",
        title="Monthly Finance Expenses",
        color_discrete_sequence=['#A9A9A9', '#808080']
    )
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("👥 HR Overview")
    st.dataframe(admin_df[admin_df["Department"].str.contains("HR")], use_container_width=True)
    fig = px.line(
        admin_df[admin_df["Department"].str.contains("HR")],
        x="Month",
        y="HR Count",
        color="Department",
        title="Monthly HR Count",
        color_discrete_sequence=['#A9A9A9', '#808080']
    )
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("🛡️ Insurance Overview")
    st.dataframe(admin_df[admin_df["Department"].str.contains("Insurance")], use_container_width=True)
    fig = px.line(
        admin_df[admin_df["Department"].str.contains("Insurance")],
        x="Month",
        y="Insurance Claims Processed",
        color="Department",
        title="Monthly Insurance Claims Processed",
        color_discrete_sequence=['#A9A9A9']
    )
    fig.update_layout(
        template='plotly_dark',
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(fig, use_container_width=True)

with tabs[3]:
    st.subheader("😊 Patient Satisfaction")
    st.dataframe(admin_df[['Department', 'Month', 'Patient Satisfaction Score']], use_container_width=True)
    fig = px.box(
        admin_df,
        x="Department",
        y="Patient Satisfaction Score",
        title="Satisfaction Score by Department",
        template="plotly_dark",
        color_discrete_sequence=['#A9A9A9']
    )
    fig.update_layout(
        plot_bgcolor='#2A2A2A',
        paper_bgcolor='#2A2A2A',
        font=dict(color='#D3D3D3')
    )
    st.plotly_chart(fig, use_container_width=True)

# ----------------- Patient Demographics -----------------
st.markdown('<div class="section-header">👤 Patient Demographics Analysis</div>', unsafe_allow_html=True)
demo_data = filtered.copy()
demo_data['Age Group'] = pd.cut(
    demo_data['Age'],
    bins=[0, 18, 35, 50, 65, 100],
    labels=['0-18', '19-35', '36-50', '51-65', '65+']
)
st.dataframe(demo_data[['Patient ID', 'Age Group', 'Sex', 'Blood Group', 'Religion', 'Treatment Cost (₹)']], use_container_width=True)

st.markdown("#### 🎂 Age Group Distribution")
age_dist = px.histogram(
    demo_data,
    x="Age Group",
    color="Sex",
    template="plotly_dark",
    color_discrete_sequence=px.colors.sequential.Greys
)
age_dist.update_layout(
    plot_bgcolor='#2A2A2A',
    paper_bgcolor='#2A2A2A',
    font=dict(color='#D3D3D3')
)
st.plotly_chart(age_dist, use_container_width=True)

st.markdown("#### 💰 Treatment Cost by Age Group")
cost_by_age = px.box(
    demo_data,
    x="Age Group",
    y="Treatment Cost (₹)",
    template="plotly_dark",
    color_discrete_sequence=['#A9A9A9']
)
cost_by_age.update_layout(
    plot_bgcolor='#2A2A2A',
    paper_bgcolor='#2A2A2A',
    font=dict(color='#D3D3D3')
)
st.plotly_chart(cost_by_age, use_container_width=True)

# ----------------- Footer -----------------
st.markdown("""
    <hr style='border: 1px solid #4A4A4A;'>
    <center>
        <small style='color: #A9A9A9;'>© 2025 One Trust | Empowering healthcare decisions</small>
    </center>
""", unsafe_allow_html=True)
