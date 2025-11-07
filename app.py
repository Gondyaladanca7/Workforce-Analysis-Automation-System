# app.py
"""
Workforce Analytics & Employee Management System
Single-entry app that routes by role (uses auth.py).
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import base64

from auth import require_login, logout_user, show_role_badge
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils.pdf_export import generate_summary_pdf

sns.set_style("whitegrid")

# -------------------------
# Streamlit config
# -------------------------
st.set_page_config(page_title="Workforce Analytics System", page_icon="👩‍💼", layout="wide")

# -------------------------
# Login
# -------------------------
require_login()
show_role_badge()

role = st.session_state.get("role", "Employee")
username = st.session_state.get("user", "unknown")

# -------------------------
# Initialize DB tables
# -------------------------
try:
    db.initialize_database()
except Exception as e:
    st.error("Failed to initialize database.")
    st.exception(e)
    st.stop()

# -------------------------
# Load Employees
# -------------------------
try:
    df = db.fetch_employees()
except:
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role",
                               "Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# Sidebar: Filters & CSV Import
# -------------------------
st.sidebar.header("Controls")
st.sidebar.markdown(f"**Logged in as:** {username} — **{role}**")

# Filters
selected_dept = st.sidebar.selectbox("Department", ["All"] + sorted(df["Department"].dropna().unique().tolist()) if not df.empty else ["All"])
selected_status = st.sidebar.selectbox("Status", ["All"] + sorted(df["Status"].dropna().unique().tolist()) if not df.empty else ["All"])
selected_gender = st.sidebar.selectbox("Gender", ["All","Male","Female"])
selected_role = st.sidebar.selectbox("Role", ["All"] + sorted(df["Role"].dropna().unique().tolist()) if not df.empty else ["All"])
selected_skills = st.sidebar.selectbox("Skills", ["All"] + sorted(df["Skills"].dropna().unique().tolist()) if not df.empty else ["All"])

# CSV Upload (Admin/Manager)
if role in ("Admin","Manager"):
    st.sidebar.header("📁 Import CSV (optional)")
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            for idx,row in df_uploaded.iterrows():
                emp = {col: row.get(col, "NA") for col in ["Emp_ID","Name","Age","Gender","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"]}
                db.add_employee(emp)
            st.success("CSV processed and employees added.")
            st.rerun()
        except Exception as e:
            st.error("Failed to process CSV")
            st.exception(e)

# -------------------------
# Apply filters
# -------------------------
filtered_df = df.copy()
if selected_dept != "All": filtered_df = filtered_df[filtered_df["Department"]==selected_dept]
if selected_status != "All": filtered_df = filtered_df[filtered_df["Status"]==selected_status]
if selected_gender != "All": filtered_df = filtered_df[filtered_df["Gender"]==selected_gender]
if selected_role != "All": filtered_df = filtered_df[filtered_df["Role"]==selected_role]
if selected_skills != "All": filtered_df = filtered_df[filtered_df["Skills"]==selected_skills]

# -------------------------
# Employee Table
# -------------------------
st.title("👩‍💼 Workforce Analytics System")
st.header("1️⃣ Employee Records")
search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
display_df = filtered_df.copy()
if search_term:
    cond = pd.Series([False]*len(display_df))
    for col in ["Name","Emp_ID","Skills","Role"]:
        if col in display_df.columns:
            cond |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

st.dataframe(display_df, height=400)

# -------------------------
# Delete Employee (Admin)
# -------------------------
if role=="Admin":
    st.subheader("🗑️ Delete Employee (Admin)")
    delete_id = st.number_input("Employee ID to delete", step=1, format="%d")
    if st.button("Delete Employee"):
        try:
            db.delete_employee(int(delete_id))
            st.success(f"Employee ID {delete_id} deleted.")
            st.rerun()
        except Exception as e:
            st.error("Failed to delete employee")
            st.exception(e)

# -------------------------
# Workforce Summary
# -------------------------
st.header("2️⃣ Workforce Summary")
total, active, resigned = get_summary(filtered_df) if not filtered_df.empty else (0,0,0)
st.metric("Total Employees", total)
st.metric("Active Employees", active)
st.metric("Resigned Employees", resigned)

st.header("3️⃣ Department Distribution")
st.bar_chart(department_distribution(filtered_df)) if not filtered_df.empty else st.info("No data")

st.header("4️⃣ Gender Ratio")
if not filtered_df.empty:
    gender_ser = gender_ratio(filtered_df)
    fig, ax = plt.subplots()
    ax.pie(gender_ser, labels=gender_ser.index, autopct="%1.1f%%", colors=sns.color_palette("pastel"))
    ax.axis("equal")
    st.pyplot(fig)

st.header("5️⃣ Average Salary by Department")
if not filtered_df.empty:
    st.bar_chart(average_salary_by_dept(filtered_df))

# -------------------------
# Add Employee (Admin/Manager)
# -------------------------
if role in ("Admin","Manager"):
    st.sidebar.header("➕ Add Employee")
    with st.sidebar.form("add_emp_form", clear_on_submit=True):
        emp_id = st.number_input("Employee ID", step=1, format="%d")
        emp_name = st.text_input("Name")
        age = st.number_input("Age", step=1)
        gender_val = st.selectbox("Gender", ["Male","Female"])
        dept = st.text_input("Department")
        role_input = st.text_input("Role")
        skills = st.text_input("Skills")
        join_date = st.date_input("Join Date")
        status = st.selectbox("Status", ["Active","Resigned"])
        resign_date = st.date_input("Resign Date") if status=="Resigned" else None
        salary = st.number_input("Salary", step=1000)
        location = st.text_input("Location")
        submit = st.form_submit_button("Add Employee")
        if submit:
            emp = {"Emp_ID":emp_id,"Name":emp_name,"Age":age,"Gender":gender_val,
                   "Department":dept,"Role":role_input,"Skills":skills,
                   "Join_Date":str(join_date),"Resign_Date":str(resign_date) if resign_date else "",
                   "Status":status,"Salary":salary,"Location":location}
            try:
                db.add_employee(emp)
                st.success(f"{emp_name} added")
                st.rerun()
            except Exception as e:
                st.error("Failed to add employee")
                st.exception(e)

# -------------------------
# Task Management
# -------------------------
st.header("6️⃣ Task Management")
if role in ("Admin","Manager"):
    st.subheader("Assign Task")
    with st.form("assign_task_form"):
        task_name = st.text_input("Task Title")
        emp_choice = st.selectbox("Assign To", df["Emp_ID"].astype(str)+" - "+df["Name"] if not df.empty else [])
        emp_id_for_task = int(emp_choice.split(" - ")[0]) if emp_choice else None
        due_date = st.date_input("Due Date", value=datetime.date.today())
        remarks = st.text_area("Remarks")
        submit_task = st.form_submit_button("Assign Task")
        if submit_task:
            if task_name and emp_id_for_task:
                try:
                    db.add_task(task_name, emp_id_for_task, str(due_date), remarks or "")
                    st.success("Task assigned")
                    st.rerun()
                except Exception as e:
                    st.error("Failed to assign task")
                    st.exception(e)

# Display tasks
tasks_df = pd.DataFrame()
try:
    tasks_df = db.fetch_tasks()
except:
    pass
st.subheader("All Tasks")
st.dataframe(tasks_df)

# -------------------------
# Mood Tracker
# -------------------------
st.header("7️⃣ Employee Mood (Pulse)")
emp_mood_id = st.selectbox("Select Employee", df["Emp_ID"].astype(str)+" - "+df["Name"] if not df.empty else [])
emp_id_val = int(emp_mood_id.split(" - ")[0]) if emp_mood_id else None
mood_choice = st.radio("Mood Today", ["😊 Happy","😐 Neutral","😔 Sad","😡 Angry"], horizontal=True)
if st.button("Log Mood"):
    try:
        db.log_mood(emp_id_val, mood_choice)
        st.success("Mood logged")
        st.rerun()
    except Exception as e:
        st.error("Failed to log mood")
        st.exception(e)

# Display Mood History
try:
    mood_logs = db.fetch_all_mood()
    st.subheader("Mood History")
    st.dataframe(mood_logs)
except:
    st.info("No mood logs")

# -------------------------
# Export PDF
# -------------------------
if role in ("Admin","Manager"):
    if st.button("Download Summary PDF"):
        try:
            pdf_path = "workforce_summary_report.pdf"
            generate_summary_pdf(pdf_path, total, active, resigned, filtered_df)
            with open(pdf_path,"rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            st.markdown(f'<a href="data:application/pdf;base64,{b64}" download="workforce_summary_report.pdf">📥 Download PDF</a>', unsafe_allow_html=True)
        except Exception as e:
            st.error("Failed to generate PDF")
            st.exception(e)
