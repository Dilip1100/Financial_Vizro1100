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
st.set_page_config(page_title="🏥 Medical College & Hospital Dashboard", layout="wide")
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

# ----------------- Data Generation -----------------
def generate_doctor_data(n=100):
    return pd.DataFrame([{
        "Doctor ID": fake.unique.uuid4()[:6],
        "Doctor Name": fake.name(),
        "Department": random.choice(all_medical_departments)
    } for _ in range(n)])

def generate_patient_data(n=500, doctor_df=None):
    patients = []
    for _ in range(n):
        dept = random.choice(all_medical_departments)
        assigned_doctors = doctor_df[doctor_df['Department'] == dept]
        doctor_name = assigned_doctors['Doctor Name'].sample(1).values[0] if not assigned_doctors.empty else "Unknown"
        admission_date = datetime.date(2025, random.randint(1, 12), random.randint(1, 28))
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

def generate_admin_data():
    return pd.DataFrame([{
        "Department": dept,
        "Month": f"2025-{month:02d}",
        "HR Count": random.randint(5, 25),
        "Finance Expense (in Lakh ₹)": round(random.uniform(5.0, 20.0), 2),
        "Insurance Claims Processed": random.randint(10, 100)
    } for dept in admin_departments for month in range(1, 13)])

# ----------------- Load Data -----------------
doctor_df = generate_doctor_data()
patient_df = generate_patient_data(doctor_df=doctor_df)
admin_df = generate_admin_data()

# ----------------- Filters -----------------
st.markdown("### 🔍 Filters")
f1, f2, f3, f4, f5 = st.columns([2, 2, 2, 3, 3])
with f1:
    department_filter = st.multiselect("Department", all_medical_departments)
with f2:
    sex_filter = st.multiselect("Gender", ["Male", "Female"])
with f3:
    blood_filter = st.multiselect("Blood Group", patient_df["Blood Group"].unique())
with f4:
    doctor_filter = st.multiselect("Doctor", doctor_df["Doctor Name"].unique())
with f5:
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
k2.metric("Clinical Patients", (filtered['Type'] == 'Clinical').sum())
k3.metric("Non-Clinical Patients", (filtered['Type'] == 'Non-Clinical').sum())
k4.metric("Total Doctors", len(doctor_df))

# ----------------- Patient & Doctor Tables -----------------
st.markdown("### 📋 Patient Information")
st.dataframe(filtered, use_container_width=True)

st.markdown("### 👨‍⚕️ Doctor Assignments")
st.dataframe(doctor_df, use_container_width=True)

# ----------------- Patient Distribution -----------------
st.markdown("### 📈 Patient Distribution")
d1, d2 = st.columns(2)
with d1:
    pie = px.pie(filtered, names="Sex", title="Gender Distribution")
    pie.update_layout(template="plotly_dark")
    st.plotly_chart(pie, use_container_width=True)

with d2:
    dept_counts = filtered["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Patient Count"]
    bar = px.bar(dept_counts, x="Department", y="Patient Count", color="Department", title="Patients by Department")
    bar.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(bar, use_container_width=True)

# ----------------- Admin Department Overview -----------------
st.markdown("### 🗂️ Admin Department Overview")
tabs = st.tabs(["Finance", "HR", "Insurance"])

with tabs[0]:
    st.subheader("💰 Finance Overview")
    st.dataframe(admin_df, use_container_width=True)
    fig = px.line(admin_df, x="Month", y="Finance Expense (in Lakh ₹)", color="Department", title="Monthly Finance Expenses")
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("👥 HR Overview")
    fig = px.line(admin_df, x="Month", y="HR Count", color="Department", title="Monthly HR Count")
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("🛡️ Insurance Overview")
    fig = px.line(admin_df, x="Month", y="Insurance Claims Processed", color="Department", title="Monthly Insurance Claims Processed")
    fig.update_layout(template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

# ----------------- End -----------------
