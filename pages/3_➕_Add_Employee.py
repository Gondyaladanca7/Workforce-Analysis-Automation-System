# pages/3_➕_Add_Employee.py
"""
Add Employee — Workforce Analytics System
Provides a form to add a new employee to the database.
Integrates with utils.database.
"""

import streamlit as st
import pandas as pd
from utils import database as db
import datetime

# -------------------------
st.set_page_config(page_title="Add Employee", page_icon="➕", layout="wide")
st.title("➕ Add New Employee")

# -------------------------
# Load existing data to get next Emp_ID
try:
    df = db.fetch_employees()
    next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
except Exception:
    next_emp_id = 1
    df = pd.DataFrame(columns=[
        "Emp_ID","Name","Age","Gender","Department","Role",
        "Skills","Join_Date","Resign_Date","Status","Salary","Location"
    ])

# -------------------------
# Employee Add Form
st.header("1️⃣ Employee Details Form")
with st.form("add_employee_form"):
    emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d")
    emp_name = st.text_input("Name")
    age = st.number_input("Age", step=1, format="%d")
    gender_val = st.selectbox("Gender", ["Male", "Female", "Other"])
    department = st.selectbox("Department", sorted(df["Department"].dropna().unique().tolist())) if ("Department" in df.columns and not df["Department"].dropna().empty) else st.text_input("Department")
    role = st.text_input("Role")
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date", value=datetime.date.today())
    status = st.selectbox("Status", ["Active", "Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)", value=datetime.date.today())
    if status == "Active":
        resign_date = ""
    salary = st.number_input("Salary", step=1000, format="%d")
    location = st.text_input("Location")

    submit = st.form_submit_button("Add Employee")
    if submit:
        new_row = {
            "Emp_ID": int(emp_id),
            "Name": emp_name or "NA",
            "Age": int(age),
            "Gender": gender_val or "NA",
            "Department": department or "NA",
            "Role": role or "NA",
            "Skills": skills or "NA",
            "Join_Date": str(join_date),
            "Resign_Date": str(resign_date) if status == "Resigned" else "",
            "Status": status,
            "Salary": float(salary),
            "Location": location or "NA"
        }
        try:
            db.add_employee(new_row)
            st.success(f"Employee {emp_name} added successfully!")
            st.experimental_rerun()
        except Exception as e:
            st.error("Failed to add employee.")
            st.exception(e)
