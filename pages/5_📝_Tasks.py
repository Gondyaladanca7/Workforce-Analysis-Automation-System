# pages/5_📝_Tasks.py
import streamlit as st
import pandas as pd
from datetime import date
from utils import database as db

st.set_page_config(page_title="Tasks", page_icon="📝", layout="wide")
st.title("📝 Task Management")

# -------------------------
# Fetch tasks & employees
tasks_df = db.fetch_tasks()
employees_df = db.fetch_employees()

# Sidebar: Filter
st.sidebar.header("🔍 Filter Tasks")
status_options = ["All"] + tasks_df["status"].dropna().unique().tolist() if not tasks_df.empty else ["All"]
selected_status = st.sidebar.selectbox("Status", status_options)

emp_options = ["All"] + employees_df["Name"].dropna().tolist() if not employees_df.empty else ["All"]
selected_employee = st.sidebar.selectbox("Employee", emp_options)

# Apply filters
filtered_tasks = tasks_df.copy()
if selected_status != "All":
    filtered_tasks = filtered_tasks[filtered_tasks["status"] == selected_status]
if selected_employee != "All":
    filtered_tasks = filtered_tasks[filtered_tasks["emp_id"].isin(employees_df[employees_df["Name"]==selected_employee]["Emp_ID"])]

st.header("📋 Tasks Table")
st.dataframe(filtered_tasks)

# -------------------------
# Add New Task
st.header("➕ Add New Task")
with st.form("add_task_form"):
    task_name = st.text_input("Task Name")
    employee_name = st.selectbox("Assign to", employees_df["Name"].tolist() if not employees_df.empty else [])
    due_date = st.date_input("Due Date", value=date.today())
    submit = st.form_submit_button("Add Task")
    
    if submit:
        if not task_name or not employee_name:
            st.warning("Task name and employee are required")
        else:
            emp_id = int(employees_df[employees_df["Name"]==employee_name]["Emp_ID"].values[0])
            db.add_task(task_name=task_name, emp_id=emp_id, assigned_by="Admin", due_date=str(due_date))
            st.success(f"Task '{task_name}' assigned to {employee_name}")
            st.experimental_rerun()
