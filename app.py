"""
Workforce Analytics & Employee Management System
Single-entry app that routes by role (uses auth.py)
Features:
 - Role-based login (auth.py)
 - Employee management (add/delete)
 - Mood tracker + analytics
 - Task management (assign/update/overdue)
 - PDF export
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import datetime

# Local modules
from auth import require_login, logout_user, show_role_badge
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils.pdf_export import generate_summary_pdf

sns.set_style("whitegrid")

# -------------------------
# Streamlit page config
# -------------------------
st.set_page_config(page_title="Workforce Analytics System", page_icon="👩‍💼", layout="wide")

# -------------------------
# Require login
# -------------------------
require_login()
show_role_badge()
logout_user()

role = st.session_state.get("role", "Employee")
username = st.session_state.get("user", "unknown")

# -------------------------
# Initialize DB tables
# -------------------------
try:
    db.initialize_all_tables()  # ✅ initializes employees, moods, tasks, and default users
except Exception as e:
    st.error("Failed to initialize database tables.")
    st.exception(e)
    st.stop()

# -------------------------
# Load employee data
# -------------------------
try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to load employees from DB.")
    st.exception(e)
    df = pd.DataFrame(columns=[
        "Emp_ID","Name","Age","Gender","Department","Role","Skills",
        "Join_Date","Resign_Date","Status","Salary","Location"
    ])

# -------------------------
# Sidebar Controls
# -------------------------
st.sidebar.header("Controls")
st.sidebar.markdown(f"**Logged in as:** {username} — **{role}**")

def safe_options(df_local, col):
    return ["All"] + sorted(df_local[col].dropna().unique().tolist()) if col in df_local.columns else ["All"]

selected_dept = st.sidebar.selectbox("Department", safe_options(df, "Department"))
selected_status = st.sidebar.selectbox("Status", safe_options(df, "Status"))
selected_gender = st.sidebar.selectbox("Gender", ["All", "Male", "Female"])
selected_role = st.sidebar.selectbox("Role", safe_options(df, "Role"))
selected_skills = st.sidebar.selectbox("Skills", safe_options(df, "Skills"))

# -------------------------
# CSV Upload (Admin/Manager)
# -------------------------
if role in ("Admin", "Manager"):
    st.sidebar.header("📁 Import CSV")
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            required_cols = {
                "Emp_ID": None, "Name":"NA","Age":0,"Gender":"Male","Department":"NA",
                "Role":"NA","Skills":"NA","Join_Date":"","Resign_Date":"",
                "Status":"Active","Salary":0.0,"Location":"NA"
            }
            for col, default in required_cols.items():
                if col not in df_uploaded.columns:
                    df_uploaded[col] = default

            existing_ids = set(df["Emp_ID"].dropna().astype(int).tolist()) if not df.empty else set()
            next_id = max(existing_ids)+1 if existing_ids else 1

            for _, row in df_uploaded.iterrows():
                try:
                    eid = int(row.get("Emp_ID")) if pd.notna(row.get("Emp_ID")) else None
                except:
                    eid = None
                if eid is None or eid in existing_ids:
                    eid = next_id
                    next_id += 1

                emp = {col: row.get(col, default) for col, default in required_cols.items()}
                emp["Emp_ID"] = int(eid)
                db.add_employee(emp)
                existing_ids.add(emp["Emp_ID"])

            st.success("CSV processed and employees added.")
            st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
        except Exception as e:
            st.error("Failed to process CSV.")
            st.exception(e)

# -------------------------
# Apply Filters
# -------------------------
filtered_df = df.copy()
if selected_dept != "All":
    filtered_df = filtered_df[filtered_df["Department"]==selected_dept]
if selected_status != "All":
    filtered_df = filtered_df[filtered_df["Status"]==selected_status]
if selected_gender != "All":
    filtered_df = filtered_df[filtered_df["Gender"]==selected_gender]
if selected_role != "All":
    filtered_df = filtered_df[filtered_df["Role"]==selected_role]
if selected_skills != "All":
    filtered_df = filtered_df[filtered_df["Skills"]==selected_skills]

# -------------------------
# Employee Records
# -------------------------
st.title("👩‍💼 Workforce Analytics System")
st.header("1️⃣ Employee Records")

search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
display_df = filtered_df.copy()
if search_term:
    cond = pd.Series(False, index=display_df.index)
    for col in ["Name","Emp_ID","Skills","Role"]:
        if col in display_df.columns:
            cond |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

# Sorting
available_sort_cols = [c for c in ["Emp_ID","Name","Age","Salary","Join_Date","Department","Role","Skills"] if c in display_df.columns]
if not available_sort_cols:
    available_sort_cols = display_df.columns.tolist()
sort_col = st.selectbox("Sort by", available_sort_cols, index=0)
ascending = st.radio("Order", ["Ascending","Descending"], horizontal=True)=="Ascending"
try:
    display_df = display_df.sort_values(by=sort_col, ascending=ascending, key=lambda s: s.astype(str))
except Exception:
    pass

cols_to_show = [c for c in ["Emp_ID","Name","Department","Role","Join_Date","Status"] if c in display_df.columns]
st.dataframe(display_df[cols_to_show], height=420)

# -------------------------
# Delete Employee
# -------------------------
if role=="Admin":
    st.subheader("🗑️ Delete Employee")
    delete_id = st.number_input("Enter Employee ID", step=1, format="%d", key="del_emp")
    if st.button("Delete Employee"):
        try:
            if "Emp_ID" in df.columns and int(delete_id) in df["Emp_ID"].astype(int).values:
                db.delete_employee(int(delete_id))
                st.success(f"Employee {delete_id} deleted.")
                st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
            else:
                st.warning("Employee not found.")
        except Exception as e:
            st.error("Failed to delete employee.")
            st.exception(e)

# -------------------------
# Workforce Summary
# -------------------------
st.header("2️⃣ Workforce Summary")
summary = get_summary(filtered_df) if not filtered_df.empty else {"total":0,"active":0,"resigned":0}
st.metric("Total Employees", summary["total"])
st.metric("Active Employees", summary["active"])
st.metric("Resigned Employees", summary["resigned"])

# -------------------------
# Dashboard Charts (figures for PDF)
# -------------------------
st.header("3️⃣ Department Distribution")
dept_fig = None
if not filtered_df.empty:
    dept_fig, dept_ser = department_distribution(filtered_df)
    st.bar_chart(dept_ser)

st.header("4️⃣ Gender Ratio")
gender_fig = None
if not filtered_df.empty and "Gender" in filtered_df.columns:
    try:
        gender_fig, gender_ser = gender_ratio(filtered_df)
        st.pyplot(gender_fig)
    except Exception:
        st.info("Not enough data to plot gender ratio.")

st.header("5️⃣ Average Salary by Department")
salary_fig = None
if not filtered_df.empty and "Salary" in filtered_df.columns:
    salary_fig, salary_ser = average_salary_by_dept(filtered_df)
    st.bar_chart(salary_ser)

# -------------------------
# Add New Employee (Sidebar)
# -------------------------
if role in ("Admin", "Manager"):
    st.sidebar.header("➕ Add New Employee")
    with st.sidebar.form("add_employee_form", clear_on_submit=True):
        try:
            next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
        except Exception:
            next_emp_id = 1

        emp_id = st.number_input("Employee ID", value=next_emp_id, step=1)
        emp_name = st.text_input("Name")
        age = st.number_input("Age", step=1)
        gender_val = st.selectbox("Gender", ["Male", "Female"])
        department = st.text_input("Department")
        role_input = st.text_input("Role")
        skills = st.text_input("Skills")
        join_date = st.date_input("Join Date")
        status = st.selectbox("Status", ["Active", "Resigned"])
        resign_date = st.date_input("Resign Date (if resigned)")
        if status == "Active":
            resign_date = ""
        salary = st.number_input("Salary", step=1000)
        location = st.text_input("Location")
        submit = st.form_submit_button("Add Employee")

        if submit:
            try:
                new_emp = {
                    "Emp_ID": int(emp_id),
                    "Name": emp_name or "NA",
                    "Age": int(age),
                    "Gender": gender_val,
                    "Department": department or "NA",
                    "Role": role_input or "NA",
                    "Skills": skills or "NA",
                    "Join_Date": str(join_date),
                    "Resign_Date": str(resign_date) if status == "Resigned" else "",
                    "Status": status,
                    "Salary": float(salary),
                    "Location": location or "NA"
                }
                db.add_employee(new_emp)
                st.success("Employee added successfully.")
                st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
            except Exception as e:
                st.error("Failed to add employee.")
                st.exception(e)

# -------------------------
# Task Management
# -------------------------
st.header("6️⃣ Task Management")
if role in ("Admin", "Manager"):
    st.subheader("Assign Task")
    with st.form("assign_task_form"):
        task_name = st.text_input("Task title")
        emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"] if not df.empty else []
        emp_choice = st.selectbox("Assign To", emp_opts)
        emp_id_for_task = int(emp_choice.split(" - ")[0]) if emp_choice else None
        due_date = st.date_input("Due date", value=datetime.date.today())
        remarks = st.text_area("Remarks")
        assign_submit = st.form_submit_button("Assign Task")

        if assign_submit:
            if not task_name or emp_id_for_task is None:
                st.warning("Task title and assignee are required.")
            else:
                try:
                    db.add_task(task_name=task_name, emp_id=emp_id_for_task,
                                assigned_by=username, due_date=due_date.strftime("%Y-%m-%d"),
                                remarks=remarks or "")
                    st.success("Task assigned successfully.")
                    st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
                except Exception as e:
                    st.error("Failed to assign task.")
                    st.exception(e)

st.subheader("All Tasks")
try:
    tasks_df = db.fetch_tasks()
except Exception:
    tasks_df = pd.DataFrame()

if not tasks_df.empty:
    tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
    today = pd.Timestamp.today().date()
    tasks_df["overdue"] = tasks_df["due_date_parsed"].apply(lambda d: (d < today) if pd.notna(d) else False)
    emp_map = df.set_index("Emp_ID")["Name"].to_dict() if not df.empty else {}
    tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map).fillna(tasks_df["emp_id"].astype(str))
    display_cols = [c for c in ["task_id","task_name","Employee","assigned_by","due_date","status","remarks","overdue"] if c in tasks_df.columns]
    st.dataframe(tasks_df[display_cols], height=300)

    # Task Analytics
    st.subheader("Task Analytics")
    if "status" in tasks_df.columns:
        status_counts = tasks_df["status"].value_counts()
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie(status_counts.values, labels=[f"{s} ({c})" for s,c in zip(status_counts.index, status_counts.values)],
               startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
else:
    st.info("No tasks found.")

# -------------------------
# Mood Tracker
# -------------------------
st.header("7️⃣ Employee Mood (Pulse)")
emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"] if not df.empty else []

if role in ("Admin", "Manager"):
    emp_sel = st.selectbox("Select Employee", emp_opts)
    emp_mood_id = int(emp_sel.split(" - ")[0]) if emp_sel else None
else:
    emp_mood_id = st.session_state.get("my_emp_id", None)
    if emp_mood_id is None:
        emp_sel = st.selectbox("Select your Emp_ID", emp_opts)
        emp_mood_id = int(emp_sel.split(" - ")[0]) if emp_sel else None
        if emp_mood_id is not None:
            st.session_state["my_emp_id"] = emp_mood_id

mood_choice = st.radio("Mood today", ["😊 Happy","😐 Neutral","😔 Sad","😡 Angry"], horizontal=True)
if st.button("Log Mood"):
    if not emp_mood_id:
        st.warning("Select an employee before logging mood.")
    else:
        try:
            db.add_mood_entry(emp_mood_id, mood_choice, remarks="")
            st.success("Mood logged successfully.")
            st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)

# Mood History & Analytics
try:
    mood_df = db.fetch_mood_logs()
except Exception:
    mood_df = pd.DataFrame()

if not mood_df.empty and not df.empty:
    mood_merged = pd.merge(mood_df, df[["Emp_ID","Name"]], left_on="emp_id", right_on="Emp_ID", how="left")
    mood_display = mood_merged[["emp_id","Name","mood","log_date"]].sort_values(by="log_date", ascending=False)
    st.subheader("Mood History")
    st.dataframe(mood_display, height=300)

    mood_label_map = {"😊 Happy":"Happy","😐 Neutral":"Neutral","😔 Sad":"Sad","😡 Angry":"Angry"}
    mood_score_map = {"Happy":5,"Neutral":3,"Sad":2,"Angry":1}
    mood_merged["Mood_Label"] = mood_merged["mood"].replace(mood_label_map)
    mood_merged["Mood_Score"] = mood_merged["Mood_Label"].map(mood_score_map).fillna(0).astype(int)
    avg_mood = mood_merged.groupby("Name")["Mood_Score"].mean().round().astype(int).sort_values(ascending=True)

    if not avg_mood.empty:
        st.subheader("Average Mood per Employee")
        fig, ax = plt.subplots(figsize=(6,3))
        ax.barh(avg_mood.index, avg_mood.values)
        ax.set_xlabel("Avg Mood Score")
        st.pyplot(fig)
else:
    st.info("No mood logs to show.")

# -------------------------
# PDF Export
# -------------------------
st.header("📄 Export")
if st.button("Download Summary PDF"):
    pdf_path = "workforce_summary_report.pdf"
    try:
        generate_summary_pdf(
            pdf_path,
            summary["total"],
            summary["active"],
            summary["resigned"],
            mood_df=mood_df,
            gender_fig=gender_fig,
            salary_fig=salary_fig,
            dept_fig=dept_fig
        )
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="workforce_summary_report.pdf">📥 Download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.success("PDF generated successfully!")
    except Exception as e:
        st.error("Failed to generate PDF.")
        st.exception(e)
