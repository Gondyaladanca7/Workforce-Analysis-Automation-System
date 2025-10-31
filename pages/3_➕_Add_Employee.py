# Add Employee Page
"""
Add Employee — Workforce Analytics System
Provides a form to add new employees directly into the database.
Integrates with utils.database for persistence.
"""

import streamlit as st
import pandas as pd
from utils import database as db
from datetime import date

# -------------------------
st.set_page_config(page_title="Add Employee", page_icon="➕", layout="wide")
st.title("➕ Add New Employee")

# -------------------------
# Load employee data to determine next ID
try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to fetch employee data from database.")
    st.exception(e)
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role",
                               "Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
st.header("1️⃣ Add Employee Form")

with st.form("add_employee_form"):
    try:
        next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
    except Exception:
        next_emp_id = 1

    emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d")
    emp_name = st.text_input("Name")
    age = st.number_input("Age", step=1, format="%d")
    gender_val = st.selectbox("Gender", ["Male", "Female", "Other"])
    department = st.text_input("Department")
    role = st.text_input("Role")
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date", value=date.today())
    status = st.selectbox("Status", ["Active", "Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)", value=date.today())
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
            "Resign_Date": str(resign_date) if status=="Resigned" else "",
            "Status": status,
            "Salary": float(salary),
            "Location": location or "NA"
        }

        try:
            db.add_employee(new_row)
            st.success(f"Employee {emp_name} added successfully!")
        except Exception as e:
            st.error("Failed to add employee.")
            st.exception(e)

# -------------------------
# Optional: Show last 5 added employees
st.header("2️⃣ Recently Added Employees")
try:
    recent_df = df.sort_values(by="Emp_ID", ascending=False).head(5)
    st.dataframe(recent_df[["Emp_ID","Name","Department","Role","Join_Date","Status"]])
except Exception:
    st.info("No employee data to display.")
