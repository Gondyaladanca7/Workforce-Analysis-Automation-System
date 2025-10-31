# pages/3_➕_Add_Employee.py
"""
Add Employee — Workforce Analytics System
Allows HR/Manager to add new employee records with validation and confirmation.
Integrates with utils.database.
"""

import streamlit as st
import pandas as pd
from utils import database as db

# -------------------------
st.set_page_config(page_title="Add Employee", page_icon="➕", layout="wide")
st.title("➕ Add New Employee")

# -------------------------
# Load existing employee data
try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to fetch employee data from database.")
    st.exception(e)
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role",
                               "Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Form for adding employee
st.header("Add Employee Form")

with st.form("add_employee_form"):
    # Auto-generate next Emp_ID
    try:
        next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
    except Exception:
        next_emp_id = 1

    emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d", disabled=True)
    emp_name = st.text_input("Name *")
    age = st.number_input("Age", min_value=18, max_value=100, step=1, format="%d")
    gender_val = st.selectbox("Gender", ["Male", "Female", "Other"])
    
    # Department & Dynamic Role
    departments = sorted(df["Department"].dropna().unique().tolist()) if not df.empty else []
    department = st.selectbox("Department *", options=departments) if departments else st.text_input("Department *")
    
    # Roles filtered by department
    roles = df[df["Department"] == department]["Role"].dropna().unique().tolist() if not df.empty else []
    role = st.selectbox("Role *", options=roles) if roles else st.text_input("Role *")
    
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date")
    status = st.selectbox("Status", ["Active", "Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)")
    if status == "Active":
        resign_date = ""
    salary = st.number_input("Salary *", min_value=0, step=1000, format="%d")
    location = st.text_input("Location")
    
    submit = st.form_submit_button("Add Employee")
    
    if submit:
        # Validation
        missing_fields = []
        for field_name, value in [("Name", emp_name), ("Department", department), ("Role", role), ("Salary", salary)]:
            if value in [None, "", 0]:
                missing_fields.append(field_name)
        
        if missing_fields:
            st.warning(f"Please fill required fields: {', '.join(missing_fields)}")
        else:
            # Prepare employee record
            new_emp = {
                "Emp_ID": int(emp_id),
                "Name": emp_name.strip(),
                "Age": int(age),
                "Gender": gender_val,
                "Department": department.strip(),
                "Role": role.strip(),
                "Skills": skills.strip(),
                "Join_Date": str(join_date),
                "Resign_Date": str(resign_date) if status == "Resigned" else "",
                "Status": status,
                "Salary": float(salary),
                "Location": location.strip() if location else "NA"
            }
            
            # Add to DB
            try:
                db.add_employee(new_emp)
                st.success(f"✅ Employee {emp_name} added successfully!")
                
                # Show summary
                st.subheader("Employee Summary")
                st.write(pd.DataFrame([new_emp]).T.rename(columns={0: "Details"}))
            except Exception as e:
                st.error("Failed to add employee.")
                st.exception(e)
