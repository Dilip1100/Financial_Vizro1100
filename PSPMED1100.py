import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import os
import sys
import datetime

# ----------------- Try Importing Faker -----------------
try:
    from faker import Faker
except ImportError:
    os.system(f"{sys.executable} -m pip install faker")
    from faker import Faker

# ----------------- Setup -----------------
st.set_page_config(page_title="🏥 Medical Dashboard", layout="wide")
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

# ----------------- Generate Patient Data -----------------
def generate_patient_data(n=500):
    patients = []
    for _ in range(n):
        dept = random.choice(all_medical_departments)
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
patient_df = generate_patient_data()
admin_df = generate_admin_data()

# ----------------- Filters -----------------
st.sidebar.header("🔍 Filters")
department_filter = st.sidebar.multiselect("Department", all_medical_departments)
sex_filter = st.sidebar.multiselect("Gender", ["Male", "Female"])
blood_filter = st.sidebar.multiselect("Blood Group", patient_df["Blood Group"].unique())
search_term = st.sidebar.text_input("Search (Name, Symptoms, Contact, etc.)")

filtered = patient_df.copy()
if department_filter:
    filtered = filtered[filtered["Department"].isin(department_filter)]
if sex_filter:
    filtered = filtered[filtered["Sex"].isin(sex_filter)]
if blood_filter:
    filtered = filtered[filtered["Blood Group"].isin(blood_filter)]
if search_term:
    term = search_term.lower()
    filtered = filtered[filtered.apply(lambda r: term in str(r.values).lower(), axis=1)]

# ----------------- KPIs -----------------
st.markdown("### 📊 Key Metrics")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Patients", len(filtered))
k2.metric("Clinical", (filtered['Type'] == 'Clinical').sum())
k3.metric("Non-Clinical", (filtered['Type'] == 'Non-Clinical').sum())
k4.metric("Admin Departments", len(admin_departments))

# ----------------- Patient Table -----------------
st.markdown("### 📋 Patient Info")
st.dataframe(filtered, use_container_width=True)

# ----------------- Visualizations -----------------
st.markdown("### 📈 Distributions")
c1, c2 = st.columns(2)

# 1. Gender Distribution (Pie 3D style)
with c1:
    gender_data = filtered['Sex'].value_counts()
    fig = go.Figure(data=[go.Pie(labels=gender_data.index, values=gender_data.values,
                                 hole=0.3, pull=[0.05]*len(gender_data),
                                 textinfo='label+percent')])
    fig.update_layout(title="Gender Distribution", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# 2. Department-wise Patients (Bar)
with c2:
    dept_counts = filtered["Department"].value_counts().reset_index()
    dept_counts.columns = ["Department", "Count"]
    fig = px.bar(dept_counts, x="Department", y="Count", color="Department",
                 title="Patients by Department")
    fig.update_layout(template="plotly_dark", xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

# 3. Blood Group Pie
st.markdown("### 🩸 Blood Group Distribution")
blood_counts = filtered["Blood Group"].value_counts().reset_index()
blood_counts.columns = ["Blood Group", "Count"]
fig = px.pie(blood_counts, names="Blood Group", values="Count", title="Blood Group Share")
fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# 4. Monthly Admissions Line
st.markdown("### 📅 Monthly Admissions")
monthly = pd.to_datetime(filtered["Admission Date"]).dt.to_period("M").value_counts().sort_index()
fig = px.line(x=monthly.index.astype(str), y=monthly.values, labels={"x": "Month", "y": "Admissions"})
fig.update_layout(title="Monthly Patient Admissions", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# 5. Religion Donut
st.markdown("### 🛐 Religion-wise Patients")
religion_counts = filtered["Religion"].value_counts().reset_index()
religion_counts.columns = ["Religion", "Count"]
fig = px.pie(religion_counts, names="Religion", values="Count", hole=0.4)
fig.update_layout(title="Religion Breakdown", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# 6. Marital Status by Department (Stacked)
st.markdown("### 💑 Marital Status per Department")
ms_group = filtered.groupby(["Department", "Marital Status"]).size().reset_index(name="Count")
fig = px.bar(ms_group, x="Department", y="Count", color="Marital Status", barmode="stack")
fig.update_layout(title="Marital Status by Department", template="plotly_dark", xaxis_tickangle=-45)
st.plotly_chart(fig, use_container_width=True)

# 7. Heatmap
st.markdown("### 🔥 Heatmap: Dept vs Blood Group")
heat_df = pd.crosstab(filtered["Department"], filtered["Blood Group"])
fig = px.imshow(heat_df, text_auto=True, color_continuous_scale='Viridis')
fig.update_layout(title="Heatmap of Departments and Blood Groups", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# ----------------- Admin Tabs -----------------
st.markdown("### 🗂️ Admin Department Overview")
tabs = st.tabs(["Finance", "HR", "Insurance"])

with tabs[0]:
    st.subheader("💰 Finance")
    df = admin_df.copy()
    fig = px.line(df, x="Month", y="Finance Expense (in Lakh ₹)", color="Department", markers=True)
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tabs[1]:
    st.subheader("👥 HR")
    df = admin_df.copy()
    fig = px.line(df, x="Month", y="HR Count", color="Department", markers=True)
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    st.subheader("🛡️ Insurance")
    df = admin_df.copy()
    fig = px.line(df, x="Month", y="Insurance Claims Processed", color="Department", markers=True)
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ----------------- END -----------------
