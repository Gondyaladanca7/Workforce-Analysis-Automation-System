# pages/5_Tasks.py
import streamlit as st
import pandas as pd
import datetime
from utils import database as db
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("whitegrid")

st.set_page_config(page_title="Tasks", page_icon="📝", layout="wide")
st.title("📝 Task Management")

# Fetch employee list
try:
    df = db.fetch_employees()
except Exception:
    df = pd.DataFrame(columns=["Emp_ID", "Name"])

# Assign Task (Admin/Manager)
st.subheader("Assign Task")
with st.form("assign_task_form", clear_on_submit=True):
    task_name = st.text_input("Task Title")

    emp_list = []
    if not df.empty:
        emp_list = df["Emp_ID"].astype(str) + " - " + df["Name"]
        emp_list = emp_list.tolist()
    emp_choice = st.selectbox("Assign To", options=emp_list)

    emp_id_for_task = int(emp_choice.split(" - ")[0]) if emp_choice else None
    due_date = st.date_input("Due Date", value=datetime.date.today())
    remarks = st.text_area("Remarks (optional)")
    submit_task = st.form_submit_button("Assign Task")

    if submit_task:
        if not task_name or emp_id_for_task is None:
            st.warning("Task title and assignee are required.")
        else:
            try:
                db.add_task({
                    "task_name": task_name,
                    "emp_id": emp_id_for_task,
                    "assigned_by": st.session_state.get("user", "system"),
                    "due_date": due_date.strftime("%Y-%m-%d"),
                    "status": "Pending",
                    "remarks": remarks or ""
                })
                st.success("Task assigned successfully.")
                # trigger refresh
                st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
            except Exception as e:
                st.error("Failed to assign task.")
                st.exception(e)

# View Tasks
st.subheader("All Tasks")
try:
    tasks_df = db.fetch_tasks()
except Exception:
    tasks_df = pd.DataFrame(columns=[
        "task_id", "task_name", "emp_id", "assigned_by", "due_date",
        "status", "remarks", "created_date"
    ])

if not tasks_df.empty:
    # Ensure due_date parsed as dates
    tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
    today = pd.Timestamp.today().date()
    tasks_df["overdue"] = tasks_df["due_date_parsed"].apply(lambda d: d < today if pd.notna(d) else False)

    # Merge employee names
    emp_map = df.set_index("Emp_ID")["Name"].to_dict() if not df.empty else {}
    tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map).fillna(tasks_df["emp_id"].astype(str))

    display_cols = ["task_id", "task_name", "Employee", "assigned_by", "due_date", "status", "remarks", "overdue"]
    st.dataframe(tasks_df[display_cols], height=360)

    # Task Analytics
    st.subheader("Task Analytics")
    if "status" in tasks_df.columns and not tasks_df["status"].isna().all():
        status_counts = tasks_df["status"].value_counts()
        fig, ax = plt.subplots(figsize=(5,3))
        ax.pie(
            status_counts.values,
            labels=[f"{s} ({c})" for s,c in zip(status_counts.index, status_counts.values)],
            startangle=90,
            autopct='%1.0f%%'
        )
        ax.axis("equal")
        st.pyplot(fig)
    else:
        st.info("No task status data available for analytics.")
else:
    st.info("No tasks found.")
