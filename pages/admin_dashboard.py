import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import base64

from auth import require_login
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils.pdf_export import generate_summary_pdf

require_login()
if st.session_state.get("role") != "Admin":
    st.warning("Access denied. Admins only.")
    st.stop()

username = st.session_state.get("user", "Admin")

st.title("🛠️ Admin Dashboard")

# Load employee data
try:
    df = db.fetch_employees()
except:
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills",
                               "Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Employee Management
# -------------------------
st.header("1️⃣ Employee Records")

search_term = st.text_input("Search employees by Name, ID, Role or Skills").strip()
display_df = df.copy()
if search_term:
    cond = pd.Series(False, index=display_df.index)
    for col in ["Name","Emp_ID","Role","Skills"]:
        if col in display_df.columns:
            cond |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

cols_to_show = ["Emp_ID","Name","Department","Role","Join_Date","Status"]
st.dataframe(display_df[cols_to_show], height=400)

# Add Employee Form
st.subheader("➕ Add New Employee")
with st.form("add_employee_form", clear_on_submit=True):
    emp_name = st.text_input("Name")
    age = st.number_input("Age", step=1)
    gender_val = st.selectbox("Gender", ["Male","Female"])
    department = st.text_input("Department")
    role_input = st.text_input("Role")
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date")
    status = st.selectbox("Status", ["Active","Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)")
    if status=="Active":
        resign_date=""
    salary = st.number_input("Salary", step=1000)
    location = st.text_input("Location")
    submit = st.form_submit_button("Add Employee")

    if submit:
        new_emp = {
            "Emp_ID": int(df["Emp_ID"].max())+1 if not df.empty else 1,
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
            db.add_employee(new_emp)
            st.success(f"Employee {emp_name} added successfully!")
        except Exception as e:
            st.error("Failed to add employee.")
            st.exception(e)

# Delete Employee
st.subheader("🗑️ Delete Employee")
delete_id = st.number_input("Enter Employee ID", step=1, key="del_emp")
if st.button("Delete Employee"):
    try:
        db.delete_employee(int(delete_id))
        st.success(f"Employee {delete_id} deleted successfully.")
    except Exception as e:
        st.error("Failed to delete employee.")
        st.exception(e)

# -------------------------
# Task Management
# -------------------------
st.header("2️⃣ Task Management")

# Assign Task
st.subheader("Assign Task")
with st.form("assign_task_form"):
    task_name = st.text_input("Task title")
    emp_opts = df["Emp_ID"].astype(str)+" - "+df["Name"] if not df.empty else []
    emp_choice = st.selectbox("Assign To", emp_opts)
    emp_id_for_task = int(emp_choice.split(" - ")[0]) if emp_choice else None
    due_date = st.date_input("Due Date", value=datetime.date.today())
    remarks = st.text_area("Remarks")
    submit_task = st.form_submit_button("Assign Task")

    if submit_task:
        try:
            db.add_task(task_name, emp_id_for_task, username, due_date.strftime("%Y-%m-%d"), remarks or "")
            st.success("Task assigned successfully!")
        except Exception as e:
            st.error("Failed to assign task.")
            st.exception(e)

# View Tasks
st.subheader("All Tasks")
try:
    tasks_df = db.fetch_tasks()
except:
    tasks_df = pd.DataFrame()
if not tasks_df.empty:
    tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
    today = pd.Timestamp.today().date()
    tasks_df["overdue"] = tasks_df["due_date_parsed"].apply(lambda d: d<today if pd.notna(d) else False)
    emp_map = df.set_index("Emp_ID")["Name"].to_dict()
    tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map).fillna(tasks_df["emp_id"].astype(str))
    st.dataframe(tasks_df[["task_id","task_name","Employee","assigned_by","due_date","status","overdue"]], height=300)
else:
    st.info("No tasks found.")

# -------------------------
# Mood Tracker
# -------------------------
st.header("3️⃣ Employee Mood Tracker")
emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"] if not df.empty else []
emp_sel = st.selectbox("Select Employee", emp_opts)
emp_mood_id = int(emp_sel.split(" - ")[0]) if emp_sel else None
mood_choice = st.radio("Mood today", ["😊 Happy","😐 Neutral","😔 Sad","😡 Angry"], horizontal=True)
if st.button("Log Mood"):
    if emp_mood_id:
        try:
            db.add_mood_entry(emp_mood_id, mood_choice, "")
            st.success("Mood logged successfully!")
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)

# -------------------------
# Reports PDF
# -------------------------
st.header("4️⃣ Export PDF Report")
if st.button("Download Summary PDF"):
    try:
        summary = get_summary(df)
        gender_ser = gender_ratio(df)
        salary_ser = average_salary_by_dept(df)
        dept_ser = department_distribution(df)
        generate_summary_pdf("workforce_summary_report.pdf", summary["total"], summary["active"], summary["resigned"],
                            df, gender_ser, salary_ser, dept_ser)
        st.success("PDF generated!")
        with open("workforce_summary_report.pdf","rb") as f:
            st.download_button("📥 Download PDF", f, file_name="workforce_summary_report.pdf", mime="application/pdf")
    except Exception as e:
        st.error("Failed to generate PDF.")
        st.exception(e)
