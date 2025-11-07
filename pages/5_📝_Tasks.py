# pages/5_📝_Tasks.py
import streamlit as st
import pandas as pd
from utils import database as db
import datetime

st.set_page_config(page_title="Task Management", page_icon="📝", layout="wide")

# -------------------------
# Initialize session triggers
# -------------------------
if "task_refresh" not in st.session_state:
    st.session_state["task_refresh"] = False

# -------------------------
# Load employee data
# -------------------------
try:
    employees = db.fetch_employees()
except Exception as e:
    st.error("Failed to load employees from DB.")
    st.exception(e)
    employees = pd.DataFrame(columns=["Emp_ID", "Name"])

# -------------------------
# Assign Task (Admin/Manager)
# -------------------------
st.header("Assign Task")
if st.session_state.get("role") in ("Admin", "Manager"):
    with st.form("assign_task_form"):
        task_name = st.text_input("Task Title")
        emp_options = employees["Emp_ID"].astype(str) + " - " + employees["Name"]
        emp_choice = st.selectbox("Assign To", emp_options) if not employees.empty else None
        emp_id = int(emp_choice.split(" - ")[0]) if emp_choice else None
        due_date = st.date_input("Due Date", value=datetime.date.today())
        remarks = st.text_area("Remarks (optional)")
        assign_submit = st.form_submit_button("Assign Task")
        
        if assign_submit:
            if not task_name or emp_id is None:
                st.warning("Task title and assignee are required.")
            else:
                try:
                    db.add_task(
                        task_name=task_name,
                        emp_id=emp_id,
                        assigned_by=st.session_state.get("user", "Admin"),
                        due_date=str(due_date),
                        status="Pending",
                        remarks=remarks or ""
                    )
                    st.success(f"Task '{task_name}' assigned to {emp_choice}")
                    st.session_state["task_refresh"] = not st.session_state["task_refresh"]
                except Exception as e:
                    st.error("Failed to assign task.")
                    st.exception(e)

# -------------------------
# View & Update Tasks
# -------------------------
st.header("All Tasks")
tasks_df = pd.DataFrame()
try:
    if st.session_state.get("role") == "Employee":
        # Employee selects their own Emp_ID
        st.info("Select your Emp_ID to view/update your tasks.")
        emp_opts = employees["Emp_ID"].astype(str) + " - " + employees["Name"]
        selected = st.selectbox("Select Employee", emp_opts)
        my_emp_id = int(selected.split(" - ")[0])
        st.session_state["my_emp_id"] = my_emp_id
        tasks_df = db.fetch_tasks(emp_id=my_emp_id)
    else:
        # Admin/Manager can filter tasks by employee
        filter_emp = st.selectbox("Filter by Employee", ["All"] + (employees["Emp_ID"].astype(str) + " - " + employees["Name"]).tolist() if not employees.empty else ["All"])
        if filter_emp != "All":
            fid = int(filter_emp.split(" - ")[0])
            tasks_df = db.fetch_tasks(emp_id=fid)
        else:
            tasks_df = db.fetch_tasks()
except Exception as e:
    st.error("Failed to fetch tasks.")
    st.exception(e)

# -------------------------
# Display tasks table
# -------------------------
if not tasks_df.empty:
    tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
    today = datetime.date.today()
    tasks_df["overdue"] = tasks_df.apply(lambda r: (r["due_date_parsed"] < today) and (r["status"] != "Completed"), axis=1)

    if "Emp_ID" in employees.columns:
        emp_map = employees.set_index("Emp_ID")["Name"].to_dict()
        tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map)
    else:
        tasks_df["Employee"] = tasks_df["emp_id"].astype(str)

    st.dataframe(tasks_df[["task_id","task_name","Employee","assigned_by","due_date","status","remarks","overdue"]], height=300)

    # Update Task Status / Remarks
    st.subheader("Update Task Status / Remarks")
    task_ids = tasks_df["task_id"].astype(str).tolist()
    sel_task = st.selectbox("Select Task ID", ["None"] + task_ids)
    if sel_task and sel_task != "None":
        trow = tasks_df[tasks_df["task_id"].astype(str) == sel_task].iloc[0]
        st.write(f"Task: **{trow['task_name']}** — Assigned to **{trow['Employee']}** — Current status: **{trow['status']}**")
        new_status = st.selectbox("New Status", ["Pending","In Progress","Completed"], index=["Pending","In Progress","Completed"].index(trow["status"]) if trow["status"] in ["Pending","In Progress","Completed"] else 0)
        new_remarks = st.text_area("Remarks (optional)", value=str(trow.get("remarks","")))
        if st.button("Apply Update"):
            try:
                db.update_task_status(int(sel_task), new_status, new_remarks)
                st.success("Task updated successfully.")
                st.session_state["task_refresh"] = not st.session_state["task_refresh"]
            except Exception as e:
                st.error("Failed to update task.")
                st.exception(e)
else:
    st.info("No tasks found.")
