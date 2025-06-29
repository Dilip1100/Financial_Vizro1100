import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import random
import os
import sys

# ----------------- Try Importing Faker -----------------
try:
    from faker import Faker
except ImportError:
    os.system(f"{sys.executable} -m pip install faker")
    from faker import Faker

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
            "Sex": random.choice(["Male", "Female"]),
            "Contact": fake.phone_number(),
            "Marital Status": random.choice(["Married", "Single", "Divorced"]),
            "Blood Group": random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]),
            "Religion": random.choice(["Hindu", "Muslim", "Christian", "Other"]),
            "Symptoms": fake.sentence(nb_words=6),
            "Department": dept,
            "Type": "Clinical" if dept in clinical_departments else "Non-Clinical"
        })
    df = pd.DataFrame(patients)
    return df.dropna()

# ----------------- Generate Dummy Admin Data -----------------
def generate_admin_data():
    records = []
    for dept in admin_departments:
        for month in range(1, 13):
            records.append({
                "Department": dept,
                "Month": f"2025-{month:02d}",
                "HR Count": random.randint(5, 25) if 'HR' in dept else 0,
                "Finance Expense (in Lakh ₹)": random.uniform(5.0, 20.0) if 'Finance' in dept else 0,
                "Insurance Claims Processed": random.randint(10, 100) if 'Insurance' in dept else 0
            })
    df = pd.DataFrame(records)
    return df.dropna()

# ----------------- Load Dummy Data -----------------
patient_df = generate_patient_data()
admin_df = generate_admin_data()

# ----------------- Top Filters -----------------
st.markdown("### 🔍 Filters")
colf1, colf2, colf3, colf4 = st.columns([3, 2, 2, 3])
with colf1:
    department_filter = st.multiselect("Select Department", all_medical_departments)
with colf2:
    sex_filter = st.multiselect("Select Gender", ["Male", "Female"])
with colf3:
    blood_filter = st.multiselect("Select Blood Group", patient_df["Blood Group"].unique())
with colf4:
    search_term = st.text_input("Search Patients (Name, Symptoms, Contact, etc.)")

filtered_patients = patient_df.copy()
if department_filter:
    filtered_patients = filtered_patients[filtered_patients["Department"].isin(department_filter)]
if sex_filter:
    filtered_patients = filtered_patients[filtered_patients["Sex"].isin(sex_filter)]
if blood_filter:
    filtered_patients = filtered_patients[filtered_patients["Blood Group"].isin(blood_filter)]
if search_term:
    search_term_lower = search_term.lower()
    filtered_patients = filtered_patients[
        filtered_patients.apply(lambda row: search_term_lower in str(row.values).lower(), axis=1)
    ]

# ----------------- KPIs -----------------
st.markdown("### 📊 Key Metrics")
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric("🢑 Total Patients", len(filtered_patients))
with k2:
    st.metric("🧬 Clinical Patients", (filtered_patients['Type'] == 'Clinical').sum())
with k3:
    st.metric("🔬 Non-Clinical Patients", (filtered_patients['Type'] == 'Non-Clinical').sum())
with k4:
    st.metric("📟 Admin Departments", len(admin_departments))

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
    dept_counts = filtered_patients["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Patient Count"]
    dept_chart = px.bar(
        dept_counts,
        x='Department', y='Patient Count',
        title="Patients by Department",
        color='Department'
    )
    dept_chart.update_layout(template='plotly_dark', xaxis_tickangle=-45)
    st.plotly_chart(dept_chart, use_container_width=True)

# ----------------- Admin Department Overview -----------------
st.markdown("### 🗂️ Admin Department Overview")

admin_tabs = st.tabs(["Finance", "HR", "Insurance"])

with admin_tabs[0]:
    st.subheader("💰 Finance Overview")
    finance_df = admin_df[admin_df["Finance Expense (in Lakh ₹)"] > 0]
    st.dataframe(finance_df, use_container_width=True)
    fig = px.line(finance_df, x="Month", y="Finance Expense (in Lakh ₹)", color="Department", title="Monthly Finance Expenses")
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with admin_tabs[1]:
    st.subheader("👥 HR Overview")
    hr_df = admin_df[admin_df["HR Count"] > 0]
    st.dataframe(hr_df, use_container_width=True)
    fig = px.line(hr_df, x="Month", y="HR Count", color="Department", title="Monthly HR Count")
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with admin_tabs[2]:
    st.subheader("🛡️ Insurance Overview")
    ins_df = admin_df[admin_df["Insurance Claims Processed"] > 0]
    st.dataframe(ins_df, use_container_width=True)
    fig = px.line(ins_df, x="Month", y="Insurance Claims Processed", color="Department", title="Monthly Insurance Claims Processed")
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# ----------------- End -----------------
