import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import datetime
import os
import sys

# ----------------- Try Importing Faker -----------------
try:
    from faker import Faker
except ImportError:
    os.system(f"{sys.executable} -m pip install faker")
    from faker import Faker

# ----------------- Setup -----------------
st.set_page_config(page_title="🏥 Medical Dashboard", layout="wide")
st.markdown("""
    <style>
    body {background-color: #111111; color: #f1f1f1;}
    .stApp {background-color: #111111;}
    </style>
""", unsafe_allow_html=True)

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

# ----------------- Generate Doctor Data -----------------
def generate_doctor_data(n=100):
    doctors = []
    for _ in range(n):
        dept = random.choice(all_medical_departments)
        doctors.append({
            "Doctor ID": fake.unique.uuid4()[:6],
            "Doctor Name": fake.name(),
            "Department": dept
        })
    return pd.DataFrame(doctors)

# ----------------- Generate Patient Data -----------------
def generate_patient_data(n=500, doctor_df=None):
    patients = []
    for _ in range(n):
        dept = random.choice(all_medical_departments)
        admission_date = datetime.date(2025, random.randint(1, 12), random.randint(1, 28))
        assigned_doctors = doctor_df[doctor_df['Department'] == dept]
        doctor_name = assigned_doctors['Doctor Name'].sample(1).values[0] if not assigned_doctors.empty else "Unknown"
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
            "Doctor": doctor_name,
            "Type": "Clinical" if dept in clinical_departments else "Non-Clinical",
            "Admission Date": admission_date
        })
    return pd.DataFrame(patients)

# ----------------- Generate Admin Data -----------------
def generate_admin_data():
    records = []
    for dept in admin_departments:
        for month in range(1, 13):
            records.append({
                "Department": dept,
                "Month": f"2025-{month:02d}",
                "HR Count": random.randint(5, 25),
                "Finance Expense (in Lakh ₹)": round(random.uniform(5.0, 20.0), 2),
                "Insurance Claims Processed": random.randint(10, 100)
            })
    return pd.DataFrame(records)

# ----------------- Load Data -----------------
doctor_df = generate_doctor_data()
patient_df = generate_patient_data(doctor_df=doctor_df)
admin_df = generate_admin_data()

# ----------------- Filters -----------------
st.markdown("### 🔍 Filters")
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 3])
with col1:
    department_filter = st.multiselect("Department", all_medical_departments)
with col2:
    sex_filter = st.multiselect("Gender", ["Male", "Female"])
with col3:
    blood_filter = st.multiselect("Blood Group", patient_df["Blood Group"].unique())
with col4:
    doctor_filter = st.multiselect("Doctor", doctor_df["Doctor Name"].unique())
with col5:
    search_term = st.text_input("Search (Name, Symptoms, Contact, etc.)")

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
st.markdown("### 📊 Key Metrics")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Patients", len(filtered))
k2.metric("Clinical", (filtered['Type'] == 'Clinical').sum())
k3.metric("Non-Clinical", (filtered['Type'] == 'Non-Clinical').sum())
k4.metric("Total Doctors", len(doctor_df))

# ----------------- Tables -----------------
st.markdown("### 📋 Patient Info")
st.dataframe(filtered, use_container_width=True)

st.markdown("### 👨‍⚕️ Doctor Assignments")
st.dataframe(doctor_df, use_container_width=True)

# ----------------- END -----------------
