import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random

try:
    from faker import Faker
except ImportError:
    st.error("Missing required library 'Faker'. Please install it by running 'pip install faker' in your terminal.")
    st.stop()

# ----------------- Setup -----------------
st.set_page_config(page_title="🏥 Medical College & Hospital Dashboard", layout="wide")
st.title("🏥 Medical College & Hospital Dashboard")

# ----------------- Initialize Faker -----------------
fake = Faker()

# ----------------- Configuration -----------------
admin_departments = ['Hospital Admin - Finance', 'Hospital Admin - HR', 'Hospital Admin - Insurance',
                     'College Admin - Finance', 'College Admin - HR']

non_clinical_departments = [
    "Pharmacology", "Lab Tests", "Biopsy", "Pathology", "Microbiology",
    "Forensic", "Anatomy", "Physiology", "Biochemistry"
]

clinical_departments = [
    "General Medicals", "General Surgery", "Orthopedics", "Dermatology",
    "ENT", "Ophthalmology", "Psychiatrics", "Nephrology", "Cardiology",
    "Neuro Surgery", "Plastic Surgery", "Medical Oncology",
    "Surgical Oncology", "Gastroenterology Medical", "Gastroenterology Surgical"
]

all_medical_departments = clinical_departments + non_clinical_departments

# ----------------- Generate Dummy Patient Data -----------------
def generate_patient_data(n=500):
    patients = []
    for _ in range(n):
        dept = random.choice(all_medical_departments)
        patients.append({
            "Patient ID": fake.unique.uuid4()[:8],
            "Name": fake.name(),
            "Sex": random.choice(["Male", "Female", "Other"]),
            "Contact": fake.phone_number(),
            "Marital Status": random.choice(["Married", "Single", "Divorced"]),
            "Blood Group": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
            "Religion": random.choice(["Hindu", "Muslim", "Christian", "Other"]),
            "Symptoms": fake.sentence(nb_words=6),
            "Department": dept,
            "Type": "Clinical" if dept in clinical_departments else "Non-Clinical"
        })
    return pd.DataFrame(patients)

# ----------------- Generate Dummy Admin Data -----------------
def generate_admin_data():
    records = []
    for dept in admin_departments:
        for month in range(1, 13):
            records.append({
                "Department": dept,
                "Month": f"2025-{month:02d}",
                "HR Count": random.randint(5, 25) if 'HR' in dept else None,
                "Finance Expense (in Lakh ₹)": random.uniform(5.0, 20.0) if 'Finance' in dept else None,
                "Insurance Claims Processed": random.randint(10, 100) if 'Insurance' in dept else None
            })
    return pd.DataFrame(records)

# ----------------- Load Dummy Data -----------------
patient_df = generate_patient_data()
admin_df = generate_admin_data()

# ----------------- Filters -----------------
st.sidebar.header("🔍 Filters")
department_filter = st.sidebar.multiselect("Select Department", all_medical_departments)
sex_filter = st.sidebar.multiselect("Select Gender", patient_df["Sex"].unique())
blood_filter = st.sidebar.multiselect("Select Blood Group", patient_df["Blood Group"].unique())

filtered_patients = patient_df.copy()
if department_filter:
    filtered_patients = filtered_patients[filtered_patients["Department"].isin(department_filter)]
if sex_filter:
    filtered_patients = filtered_patients[filtered_patients["Sex"].isin(sex_filter)]
if blood_filter:
    filtered_patients = filtered_patients[filtered_patients["Blood Group"].isin(blood_filter)]

# ----------------- KPIs -----------------
st.markdown("### 📊 Key Metrics")
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("🧑‍🤝‍🧑 Total Patients", len(filtered_patients))
with k2:
    st.metric("🧬 Clinical Patients", (filtered_patients['Type'] == 'Clinical').sum())
with k3:
    st.metric("🔬 Non-Clinical Patients", (filtered_patients['Type'] == 'Non-Clinical').sum())
with k4:
    st.metric("🧾 Admin Departments", len(admin_departments))

# ----------------- Patient Table -----------------
st.markdown("### 📋 Patient Information")
st.dataframe(filtered_patients, use_container_width=True)

# ----------------- Patient Distribution -----------------
st.markdown("### 📈 Patient Distribution")
c1, c2 = st.columns(2)

with c1:
    sex_chart = px.pie(filtered_patients, names='Sex', title='Gender Distribution')
    sex_chart.update_layout(template='plotly_dark')
    st.plotly_chart(sex_chart, use_container_width=True)

with c2:
    dept_chart = px.bar(
        filtered_patients["Department"].value_counts().reset_index(),
        x='index', y='Department',
        labels={'index': 'Department', 'Department': 'Patient Count'},
        title="Patients by Department",
        color='Department'
    )
    dept_chart.update_layout(template='plotly_dark', xaxis_tickangle=-45)
    st.plotly_chart(dept_chart, use_container_width=True)

# ----------------- Admin Department Overview -----------------
st.markdown("### 🗂️ Admin Department Overview")
st.dataframe(admin_df, use_container_width=True)

# Metrics by type
admin_metrics = st.selectbox("Select Admin Metric", ["HR Count", "Finance Expense (in Lakh ₹)", "Insurance Claims Processed"])
metric_df = admin_df.dropna(subset=[admin_metrics])

admin_metric_chart = px.line(
    metric_df,
    x="Month",
    y=admin_metrics,
    color="Department",
    title=f"Monthly {admin_metrics}"
)
admin_metric_chart.update_layout(template='plotly_dark')
st.plotly_chart(admin_metric_chart, use_container_width=True)

# ----------------- End -----------------
