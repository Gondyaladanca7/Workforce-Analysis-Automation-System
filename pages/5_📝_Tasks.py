import streamlit as st
import pandas as pd
import datetime
from utils import database as db
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style("whitegrid")

st.title("📝 Task Management")

# Fetch employee list
try:
    df = db.fetch_employees()
except Exception:
    df = pd.DataFrame(columns=["Emp_ID", "Name"])

# -------------------------
# Assign Task (Admin/Manager)
# -------------------------
st.subheader("Assign Task")
with st.form("assign_task_form"):
    task_name = st.text_input("Task Title")
    emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"] if not df.empty else []
    emp_choice = st.selectbox("Assign To", emp_opts)
    emp_id_for_task = int(emp_choice.split(" - ")[0]) if emp_choice else None
    due_date = st.date_input("Due Date", value=datetime.date.today())
    remarks = st.text_area("Remarks (optional)")
    submit_task = st.form_submit_button("Assign Task")

    if submit_task:
        if not task_name or emp_id_for_task is None:
            st.warning("Task title and assignee are required.")
        else:
            try:
                db.add_task(task_name=task_name, emp_id=emp_id_for_task,
                            assigned_by="Admin", due_date=str(due_date), remarks=remarks)
                st.success("Task assigned successfully.")
                st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
            except Exception as e:
                st.error("Failed to assign task.")
                st.exception(e)

# -------------------------
# View Tasks
# -------------------------
st.subheader("All Tasks")
try:
    tasks_df = db.fetch_tasks()
except Exception:
    tasks_df = pd.DataFrame(columns=["task_id", "task_name", "emp_id", "assigned_by", "due_date", "status", "remarks", "created_date"])

if not tasks_df.empty:
    # Merge employee names
    emp_map = df.set_index("Emp_ID")["Name"].to_dict() if not df.empty else {}
    tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map)
    tasks_df["Overdue"] = pd.to_datetime(tasks_df["due_date"], errors="coerce") < datetime.date.today()
    st.dataframe(tasks_df[["task_id", "task_name", "Employee", "assigned_by", "due_date", "status", "remarks", "Overdue"]])
else:
    st.info("No tasks found.")
