# pages/manager_dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import io

from utils.auth import require_login
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept, employee_options

def show():
    require_login()
    if st.session_state.get("role") != "Manager":
        st.warning("Access denied. Managers only.")
        st.stop()

    username = st.session_state.get("user", "Manager")
    st.title("📊 Manager Dashboard")

    # Load employees
    try:
        df = db.fetch_employees()
    except:
        df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills",
                                   "Join_Date","Resign_Date","Status","Salary","Location"])

    # manager may filter by department
    st.header("1️⃣ Employee Records")
    depts = ["All"] + sorted(df["Department"].dropna().unique().tolist()) if not df.empty else ["All"]
    dept_filter = st.selectbox("Filter Department", depts)
    filtered_df = df.copy()
    if dept_filter != "All":
        filtered_df = df[filtered_df["Department"]==dept_filter]

    st.dataframe(filtered_df[["Emp_ID","Name","Department","Role","Status"]], height=250)

    # Task assignment
    st.header("2️⃣ Task Management")
    st.subheader("Assign Task")
    with st.form("assign_task_form"):
        task_name = st.text_input("Task title")
        emp_opts = employee_options(filtered_df)
        emp_choice = st.selectbox("Assign To", emp_opts)
        emp_id_for_task = int(emp_choice.split(" - ")[0]) if emp_choice else None
        due_date = st.date_input("Due Date", value=datetime.date.today())
        remarks = st.text_area("Remarks")
        submit_task = st.form_submit_button("Assign Task")

        if submit_task:
            if not task_name or emp_id_for_task is None:
                st.warning("Task title and assignee are required.")
            else:
                try:
                    db.add_task({
                        "task_name": task_name,
                        "emp_id": emp_id_for_task,
                        "assigned_by": username,
                        "due_date": due_date.strftime("%Y-%m-%d"),
                        "status": "Pending",
                        "remarks": remarks or ""
                    })
                    st.success("Task assigned successfully!")
                except Exception as e:
                    st.error("Failed to assign task.")
                    st.exception(e)

    # View tasks by manager
    st.subheader("Tasks Overview")
    try:
        tasks_df = db.fetch_tasks()
    except:
        tasks_df = pd.DataFrame()
    if not tasks_df.empty:
        tasks_df = tasks_df[tasks_df["assigned_by"]==username]
        tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
        today = pd.Timestamp.today().date()
        tasks_df["overdue"] = tasks_df["due_date_parsed"].apply(lambda d: d<today if pd.notna(d) else False)
        emp_map = df.set_index("Emp_ID")["Name"].to_dict()
        tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map).fillna(tasks_df["emp_id"].astype(str))
        st.dataframe(tasks_df[["task_id","task_name","Employee","due_date","status","overdue"]], height=300)
    else:
        st.info("No tasks found.")

    # Task analytics
    if not tasks_df.empty and "status" in tasks_df.columns:
        status_counts = tasks_df["status"].value_counts()
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie(status_counts.values, labels=[f"{s} ({c})" for s,c in zip(status_counts.index, status_counts.values)], startangle=90)
        ax.axis("equal")
        st.subheader("Task Analytics")
        st.pyplot(fig)

    st.markdown("---")
    # Mood tracker for selected employee
    st.header("3️⃣ Employee Mood Tracker")
    emp_opts = employee_options(filtered_df)
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

    # Mood history & average
    try:
        mood_df = db.fetch_mood_logs()
    except:
        mood_df = pd.DataFrame()

    if not mood_df.empty:
        mood_merged = pd.merge(mood_df, filtered_df[["Emp_ID","Name"]], left_on="emp_id", right_on="Emp_ID", how="left")
        mood_display = mood_merged[["Name","mood","log_date"]].sort_values(by="log_date", ascending=False)
        st.dataframe(mood_display, height=300)

        mood_map = {"😊 Happy":5,"😐 Neutral":3,"😔 Sad":2,"😡 Angry":1}
        mood_merged["score"] = mood_merged["mood"].map(mood_map)
        avg_mood = mood_merged.groupby("Name")["score"].mean().sort_values()
        if not avg_mood.empty:
            st.subheader("Average Mood per Employee")
            fig2, ax2 = plt.subplots(figsize=(6,3))
            ax2.barh(avg_mood.index, avg_mood.values)
            ax2.set_xlabel("Avg Mood Score")
            st.pyplot(fig2)
    else:
        st.info("No mood logs available.")

    try:
        plt.close('all')
    except:
        pass
