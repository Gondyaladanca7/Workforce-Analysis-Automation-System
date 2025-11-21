import streamlit as st
import pandas as pd
from utils import database as db

st.title("➕ Add New Employee")

# Fetch current employees
try:
    df = db.fetch_employees()
except Exception:
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"])

with st.form("add_employee_form", clear_on_submit=True):
    try:
        next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
    except Exception:
        next_emp_id = 1

    emp_id = st.number_input("Employee ID", value=next_emp_id, step=1)
    emp_name = st.text_input("Name")
    age = st.number_input("Age", step=1)
    gender_val = st.selectbox("Gender", ["Male","Female"])
    department = st.text_input("Department")
    role_input = st.text_input("Role")
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date")
    status = st.selectbox("Status", ["Active","Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)")
    if status == "Active":
        resign_date = ""
    salary = st.number_input("Salary", step=1000)
    location = st.text_input("Location")

    submit = st.form_submit_button("Add Employee")

    if submit:
        new_row = {
            "Emp_ID": int(emp_id),
            "Name": emp_name or "NA",
            "Age": int(age),
            "Gender": gender_val,
            "Department": department or "NA",
            "Role": role_input or "NA",
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
            # session-state rerun
            st.session_state["login_trigger"] = not st.session_state.get("login_trigger", False)
        except Exception as e:
            st.error("Failed to add employee to database.")
            st.exception(e)
