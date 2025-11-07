# app.py
"""
Workforce Analytics & Employee Management System
Single-entry app that routes by role (uses auth.py).
Features:
 - Role-based login (auth.py)
 - Employee management (add/delete)
 - Mood tracker + Mood analytics (integer scores)
 - Task management (assign/update/overdue)
 - PDF export (uses utils.pdf_export.generate_summary_pdf)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import datetime
from typing import Optional

# local modules (make sure these exist)
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
# Require login (auth.py)
# -------------------------
require_login()
show_role_badge()
logout_user()

role = st.session_state.get("role", "Employee")
username = st.session_state.get("username", "unknown")

# -------------------------
# Initialize DB (employees, mood table, tasks)
# -------------------------
try:
    db.initialize_database()
    # mood and tasks table initializers may be present in your utils.database
    if hasattr(db, "initialize_mood_table"):
        db.initialize_mood_table()
    if hasattr(db, "initialize_task_table"):
        db.initialize_task_table()
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
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"])

# -------------------------
# --- Sidebar Filters & Actions
# -------------------------
st.sidebar.header("Controls")
st.sidebar.markdown(f"**Logged in as:** {username} — **{role}**")

st.sidebar.header("Filters")
def safe_options(df_local: pd.DataFrame, col: str):
    if col in df_local.columns:
        opts = sorted(df_local[col].dropna().unique().tolist())
        return ["All"] + opts
    return ["All"]

selected_dept = st.sidebar.selectbox("Department", safe_options(df, "Department"))
selected_status = st.sidebar.selectbox("Status", safe_options(df, "Status"))
# Enforce gender choices
selected_gender = st.sidebar.selectbox("Gender", ["All", "Male", "Female"])
selected_role = st.sidebar.selectbox("Role", safe_options(df, "Role"))
selected_skills = st.sidebar.selectbox("Skills", safe_options(df, "Skills"))

# CSV upload (Admin/Manager)
if role in ("Admin", "Manager"):
    st.sidebar.header("📁 Import CSV (optional)")
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            # required cols & defaults
            required_cols = {
                "Emp_ID": None, "Name":"NA","Age":0,"Gender":"Male","Department":"NA","Role":"NA",
                "Skills":"NA","Join_Date":"","Resign_Date":"","Status":"Active","Salary":0.0,"Location":"NA"
            }
            # fill missing
            for col, default in required_cols.items():
                if col not in df_uploaded.columns:
                    df_uploaded[col] = default
            # assign Emp_IDs if missing/duplicate
            existing_ids = set(df["Emp_ID"].dropna().astype(int).tolist()) if not df.empty else set()
            next_id = max(existing_ids)+1 if existing_ids else 1
            if "Emp_ID" not in df_uploaded.columns:
                df_uploaded["Emp_ID"] = [None]*len(df_uploaded)
            for _, row in df_uploaded.iterrows():
                try:
                    eid = int(row.get("Emp_ID")) if pd.notna(row.get("Emp_ID")) else None
                except Exception:
                    eid = None
                if eid is None or eid in existing_ids:
                    eid = next_id
                    next_id += 1
                emp = {
                    "Emp_ID": int(eid),
                    "Name": str(row.get("Name")) if pd.notna(row.get("Name")) else required_cols["Name"],
                    "Age": int(row.get("Age")) if pd.notna(row.get("Age")) else required_cols["Age"],
                    "Gender": str(row.get("Gender")) if pd.notna(row.get("Gender")) else required_cols["Gender"],
                    "Department": str(row.get("Department")) if pd.notna(row.get("Department")) else required_cols["Department"],
                    "Role": str(row.get("Role")) if pd.notna(row.get("Role")) else required_cols["Role"],
                    "Skills": str(row.get("Skills")) if pd.notna(row.get("Skills")) else required_cols["Skills"],
                    "Join_Date": str(row.get("Join_Date")) if pd.notna(row.get("Join_Date")) else required_cols["Join_Date"],
                    "Resign_Date": str(row.get("Resign_Date")) if pd.notna(row.get("Resign_Date")) else required_cols["Resign_Date"],
                    "Status": str(row.get("Status")) if pd.notna(row.get("Status")) else required_cols["Status"],
                    "Salary": float(row.get("Salary")) if pd.notna(row.get("Salary")) else float(required_cols["Salary"]),
                    "Location": str(row.get("Location")) if pd.notna(row.get("Location")) else required_cols["Location"]
                }
                db.add_employee(emp)
                existing_ids.add(emp["Emp_ID"])
            st.success("CSV processed and employees added.")
            st.rerun()
        except Exception as e:
            st.error("Failed to process CSV.")
            st.exception(e)

# -------------------------
# Apply filters to dataframe
# -------------------------
filtered_df = df.copy()
if selected_dept != "All" and "Department" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Department"] == selected_dept]
if selected_status != "All" and "Status" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
if selected_gender != "All" and "Gender" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Gender"] == selected_gender]
if selected_role != "All" and "Role" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Role"] == selected_role]
if selected_skills != "All" and "Skills" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Skills"] == selected_skills]

# -------------------------
# Main area: Employee Table
# -------------------------
st.title("👩‍💼 Workforce Analytics System")
st.header("1️⃣ Employee Records")

search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
display_df = filtered_df.copy()
if search_term:
    cond = pd.Series([False]*len(display_df), index=display_df.index)
    for col in ["Name","Emp_ID","Skills","Role"]:
        if col in display_df.columns:
            cond |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

available_sort_cols = [c for c in ["Emp_ID","Name","Age","Salary","Join_Date","Department","Role","Skills"] if c in display_df.columns]
if not available_sort_cols:
    available_sort_cols = display_df.columns.tolist()
sort_col = st.selectbox("Sort by", available_sort_cols, index=0)
ascending = st.radio("Order", ["Ascending","Descending"], horizontal=True) == "Ascending"
try:
    display_df = display_df.sort_values(by=sort_col, ascending=ascending, key=lambda s: s.astype(str))
except Exception:
    pass

# Force simple display
st.dataframe(display_df, height=420)

# -------------------------
# Delete Employee (Admin only)
# -------------------------
if role == "Admin":
    st.subheader("🗑️ Delete Employee (Admin)")
    delete_id = st.number_input("Enter Employee ID to delete", step=1, format="%d", key="del_emp")
    if st.button("Delete Employee"):
        try:
            if "Emp_ID" in df.columns and int(delete_id) in df["Emp_ID"].astype(int).values:
                db.delete_employee(int(delete_id))  # should remove moods & tasks in db.delete_employee
                st.success(f"Employee ID {delete_id} and related data deleted.")
                st.rerun()
            else:
                st.warning(f"No employee found with ID {delete_id}")
        except Exception as e:
            st.error("Failed to delete employee.")
            st.exception(e)

# -------------------------
# Summary & Analytics (based on filtered_df)
# -------------------------
st.header("2️⃣ Workforce Summary")
total, active, resigned = get_summary(filtered_df) if not filtered_df.empty else (0,0,0)
st.metric("Total Employees", total)
st.metric("Active Employees", active)
st.metric("Resigned Employees", resigned)

st.header("3️⃣ Department Distribution")
if not filtered_df.empty and "Department" in filtered_df.columns:
    st.bar_chart(department_distribution(filtered_df))

st.header("4️⃣ Gender Ratio")
if not filtered_df.empty and "Gender" in filtered_df.columns:
    gender_ser = gender_ratio(filtered_df)
    fig, ax = plt.subplots()
    ax.pie(gender_ser, labels=gender_ser.index, autopct="%1.1f%%", colors=sns.color_palette("pastel"))
    ax.axis("equal")
    st.pyplot(fig)

st.header("5️⃣ Average Salary by Department")
if not filtered_df.empty and "Department" in filtered_df.columns and "Salary" in filtered_df.columns:
    st.bar_chart(average_salary_by_dept(filtered_df))

# -------------------------
# Add New Employee (Admin / Manager)
# -------------------------
if role in ("Admin", "Manager"):
    st.sidebar.header("➕ Add New Employee")
    with st.sidebar.form("add_employee_form", clear_on_submit=True):
        try:
            next_emp_id = int(df["Emp_ID"].max())+1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
        except Exception:
            next_emp_id = 1
        emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d")
        emp_name = st.text_input("Name")
        age = st.number_input("Age", step=1, format="%d")
        gender_val = st.selectbox("Gender", ["Male","Female"])
        department = st.text_input("Department")
        role_input = st.text_input("Role")
        skills = st.text_input("Skills (semicolon separated)")
        join_date = st.date_input("Join Date")
        status = st.selectbox("Status", ["Active","Resigned"])
        resign_date = st.date_input("Resign Date (if resigned)")
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
                st.rerun()
            except Exception as e:
                st.error("Failed to add employee.")
                st.exception(e)

# -------------------------
# -------------------------
# Task Management
# -------------------------
st.header("6️⃣ Task Management")

# Assign Task (Admin/Manager)
if role in ("Admin", "Manager"):
    st.subheader("Assign Task")
    with st.form("assign_task_form"):
        task_name = st.text_input("Task title")
        # select employee
        emp_select_opts = df["Emp_ID"].astype(str) + " - " + df["Name"]
        emp_choice = st.selectbox("Assign To (Employee)", options=emp_select_opts) if not df.empty else None
        if emp_choice:
            emp_id_for_task = int(emp_choice.split(" - ")[0])
        else:
            emp_id_for_task = None
        due_date = st.date_input("Due date", value=datetime.date.today())
        remarks = st.text_area("Remarks (optional)")
        assign_submit = st.form_submit_button("Assign Task")
        if assign_submit:
            if not task_name or emp_id_for_task is None:
                st.warning("Task title and assignee are required.")
            else:
                try:
                    db.add_task(task_name=task_name, emp_id=int(emp_id_for_task),
                                assigned_by=username, due_date=str(due_date), status="Pending", remarks=remarks or "")
                    st.success("Task assigned successfully.")
                    st.rerun()
                except Exception as e:
                    st.error("Failed to assign task.")
                    st.exception(e)

# View & Update Tasks (Admin/Manager/Employee)
st.subheader("All Tasks")
# fetch tasks (for employees, restrict to their emp_id after choosing)
tasks_df = pd.DataFrame()
try:
    if role == "Employee":
        # Ask employee to pick their Emp_ID (we don't have mapping between login username and Emp_ID)
        st.info("Select your Emp_ID to view/update your tasks (one-time selection).")
        emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"]
        emp_selected = st.selectbox("My Employee record", options=emp_opts)
        my_emp_id = int(emp_selected.split(" - ")[0])
        st.session_state["my_emp_id"] = my_emp_id
        tasks_df = db.fetch_tasks(emp_id=my_emp_id)
    else:
        # Admin/Manager see all tasks but can filter
        filter_emp = st.selectbox("Filter by Employee", ["All"] + (df["Emp_ID"].astype(str) + " - " + df["Name"]).tolist() if not df.empty else ["All"])
        if filter_emp and filter_emp != "All":
            fid = int(filter_emp.split(" - ")[0])
            tasks_df = db.fetch_tasks(emp_id=fid)
        else:
            tasks_df = db.fetch_tasks()
except Exception as e:
    st.error("Failed to fetch tasks.")
    st.exception(e)
    tasks_df = pd.DataFrame(columns=["task_id","task_name","emp_id","assigned_by","due_date","status","remarks","created_date"])

# Process tasks_df for visuals
if not tasks_df.empty:
    # Parse due dates
    tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
    today = datetime.date.today()
    tasks_df["overdue"] = tasks_df.apply(lambda r: (r["due_date_parsed"] < today) and (r["status"] != "Completed"), axis=1)
    # Merge employee name
    if "Emp_ID" in df.columns:
        emp_map = df.set_index("Emp_ID")["Name"].to_dict()
        tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map)
    else:
        tasks_df["Employee"] = tasks_df["emp_id"].astype(str)

    # Display tasks with overdue styling
    def highlight_overdue(row):
        return ['background-color: #ffdddd' if row.overdue else '' for _ in row.index]

    try:
        styled = tasks_df[["task_id","task_name","Employee","assigned_by","due_date","status","remarks","overdue"]].style.apply(lambda r: highlight_overdue(r), axis=1)
        st.dataframe(styled, height=300)
    except Exception:
        st.dataframe(tasks_df, height=300)

    # Task analytics
    st.subheader("Task Analytics")
    # Tasks per employee
    tasks_per_emp = tasks_df.groupby("Employee").size().sort_values(ascending=False)
    if not tasks_per_emp.empty:
        fig, ax = plt.subplots(figsize=(6,3))
        sns.barplot(x=tasks_per_emp.values, y=tasks_per_emp.index, ax=ax, palette="viridis")
        ax.set_xlabel("Number of Tasks")
        ax.set_ylabel("Employee")
        ax.set_title("Tasks per Employee")
        st.pyplot(fig)

    # Status distribution
    status_counts = tasks_df["status"].value_counts()
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(status_counts, labels=[f"{s} ({c})" for s,c in zip(status_counts.index, status_counts.values)], autopct=None, startangle=90, colors=sns.color_palette("pastel"))
    ax.set_title("Task Status Distribution")
    st.pyplot(fig)

    # Overdue count
    overdue_count = int(tasks_df["overdue"].sum())
    st.metric("Overdue Tasks", overdue_count)

    # Update tasks (Admin/Manager can update any; Employee can update only their tasks)
    st.subheader("Update Task Status / Remarks")
    task_ids = tasks_df["task_id"].astype(str).tolist()
    sel_task = st.selectbox("Select Task ID to update", options=["None"] + task_ids)
    if sel_task and sel_task != "None":
        trow = tasks_df[tasks_df["task_id"].astype(str) == sel_task].iloc[0]
        st.write(f"Task: **{trow['task_name']}** — Assigned to **{trow['Employee']}** — Current status: **{trow['status']}**")
        new_status = st.selectbox("New Status", ["Pending","In Progress","Completed"], index=["Pending","In Progress","Completed"].index(trow["status"]) if trow["status"] in ["Pending","In Progress","Completed"] else 0)
        new_remarks = st.text_area("Remarks (optional)", value=str(trow.get("remarks","")))
        if st.button("Apply Update to Task"):
            try:
                db.update_task_status(int(sel_task), new_status, new_remarks)
                st.success("Task updated.")
                st.rerun()
            except Exception as e:
                st.error("Failed to update task.")
                st.exception(e)
else:
    st.info("No tasks found.")

# -------------------------
# Mood Tracker (All roles)
# -------------------------
st.header("7️⃣ Employee Mood (Pulse)")

# Select employee (Admin/Manager) or use session employee (Employee)
if role in ("Admin", "Manager"):
    emp_opts_all = df["Emp_ID"].astype(str) + " - " + df["Name"]
    sel_emp_for_mood = st.selectbox("Select Employee to log mood", options=emp_opts_all) if not df.empty else None
    if sel_emp_for_mood:
        emp_mood_id = int(sel_emp_for_mood.split(" - ")[0])
    else:
        emp_mood_id = None
elif role == "Employee":
    emp_mood_id = st.session_state.get("my_emp_id", None)
    if emp_mood_id is None:
        st.warning("Please select your Emp_ID in the Tasks section to link your account to an employee record.")
        # don't block; allow selection below
        emp_opts_all = df["Emp_ID"].astype(str) + " - " + df["Name"] if not df.empty else []
        emp_choice = st.selectbox("Select your Emp_ID (one-time)", options=emp_opts_all)
        if emp_choice:
            emp_mood_id = int(emp_choice.split(" - ")[0])
            st.session_state["my_emp_id"] = emp_mood_id

# Log mood
if emp_mood_id is not None:
    mood_choice = st.radio("How is the employee feeling today?", ["😊 Happy","😐 Neutral","😔 Sad","😡 Angry"], horizontal=True)
    if st.button("Log Mood Entry"):
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        try:
            db.add_mood_entry(int(emp_mood_id), mood_choice, today_str)
            st.success("Mood logged.")
            st.rerun()
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)

# Display mood history and analytics
try:
    mood_logs = db.fetch_mood_logs()
except Exception as e:
    st.error("Failed to fetch mood logs.")
    st.exception(e)
    mood_logs = pd.DataFrame(columns=["id","emp_id","mood","log_date"])

if not mood_logs.empty:
    # merge with employee names
    mood_merged = pd.merge(mood_logs, df[["Emp_ID","Name"]], left_on="emp_id", right_on="Emp_ID", how="left")
    mood_merged_display = mood_merged[["emp_id","Name","mood","log_date"]].sort_values(by="log_date", ascending=False)
    st.subheader("Mood History")
    st.dataframe(mood_merged_display, height=300)

    # Analytics: convert mood to integer scores (as requested)
    mood_label_map = {"😊 Happy":"Happy","😐 Neutral":"Neutral","😔 Sad":"Sad","😡 Angry":"Angry"}
    mood_score_map = {"Happy":5,"Neutral":3,"Sad":2,"Angry":1}
    mood_merged["Mood_Label"] = mood_merged["mood"].replace(mood_label_map)
    mood_merged["Mood_Score"] = mood_merged["Mood_Label"].map(mood_score_map)

    st.subheader("Mood Analytics")
    # Average mood per employee (rounded to integer)
    avg_mood = mood_merged.groupby("Name")["Mood_Score"].mean().round().astype(int).sort_values()
    if not avg_mood.empty:
        fig, ax = plt.subplots(figsize=(6,3))
        sns.barplot(x=avg_mood.values, y=avg_mood.index, palette="coolwarm", ax=ax)
        for i, v in enumerate(avg_mood.values):
            ax.text(v + 0.1, i, str(v), color="black", va="center")
        ax.set_xlabel("Average Mood Score (integer)")
        ax.set_ylabel("Employee")
        ax.set_title("Average Mood per Employee")
        st.pyplot(fig)

    # Overall mood distribution
    mood_counts = mood_merged["Mood_Label"].value_counts()
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(mood_counts, labels=[f"{lab} ({cnt})" for lab,cnt in zip(mood_counts.index, mood_counts.values)], startangle=90, colors=sns.color_palette("Set2"))
    ax.set_title("Overall Team Mood")
    st.pyplot(fig)

    # Mood trend over time (per employee)
    st.subheader("Mood Trend Over Time")
    fig, ax = plt.subplots(figsize=(8,3))
    for name, group in mood_merged.groupby("Name"):
        gs = group.sort_values(by="log_date")
        ax.plot(gs["log_date"], gs["Mood_Score"], marker="o", label=name)
    ax.set_xlabel("Date")
    ax.set_ylabel("Mood Score")
    ax.set_ylim(0,5.5)
    ax.legend(fontsize=6)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("No mood logs yet.")

# -------------------------
# Export Summary PDF (for Admin/Manager)
# -------------------------
st.header("📄 Export")
if role in ("Admin", "Manager"):
    if st.button("Download Summary PDF"):
        try:
            pdf_path = "workforce_summary_report.pdf"
            # Use filtered_df so PDF reflects current filters as requested
            generate_summary_pdf(pdf_path, total, active, resigned, filtered_df)
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="workforce_summary_report.pdf">📥 Click here to download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error("Failed to generate PDF.")
            st.exception(e)
else:
    st.info("PDF export is available for Admin & Manager only.")

# -------------------------
# Footer / Future
# -------------------------
st.markdown("---")
st.info("Future: AI Skill Radar, Project Health Tracker, Burnout Prediction (coming soon).")
