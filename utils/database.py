# pages/dashboard.py
"""
Professional Workforce Dashboard
- Role-based access (Admin, Manager, Employee)
- Employee Management
- Task Management
- Mood Tracker
- Feedback System
- Analytics / Summary
"""

import streamlit as st
import pandas as pd
import datetime

from utils.auth import require_login, show_role_badge, logout_user
from utils import database as db

# --------------------------
# Helper Functions
# --------------------------
def role_allowed(allowed_roles):
    """Check if current user role is allowed for a module"""
    role = st.session_state.get("role", "Employee")
    return role in allowed_roles

def format_emp_options(emp_df):
    """Format employees for dropdown"""
    if emp_df.empty:
        return []
    return (emp_df["Emp_ID"].astype(str) + " - " + emp_df["Name"]).tolist()

def get_employee_name(emp_df, emp_id):
    """Get employee name by ID"""
    if emp_df.empty or emp_id not in emp_df["Emp_ID"].values:
        return str(emp_id)
    return emp_df.loc[emp_df["Emp_ID"]==emp_id, "Name"].values[0]

# --------------------------
# Dashboard Main
# --------------------------
def show():
    require_login()
    show_role_badge()
    logout_user()

    role = st.session_state.get("role", "Employee")
    username = st.session_state.get("user", "Unknown")

    st.title("🏢 Workforce Analysis Automation System")

    # Load Data
    try: emp_df = db.fetch_employees()
    except: emp_df = pd.DataFrame(); st.error("Failed to load employees")

    try: tasks_df = db.fetch_tasks()
    except: tasks_df = pd.DataFrame(); st.error("Failed to load tasks")

    try: mood_df = db.fetch_mood_logs()
    except: mood_df = pd.DataFrame(); st.error("Failed to load mood logs")

    try: feedback_df = db.fetch_feedback()
    except: feedback_df = pd.DataFrame(); st.error("Failed to load feedback")

    # --------------------------
    # Sidebar Navigation
    # --------------------------
    tabs = []
    if role in ["Admin", "Manager"]: tabs.append("Employees")
    tabs.extend(["Tasks", "Mood Tracker", "Feedback", "Analytics"])
    page = st.sidebar.selectbox("🔹 Navigation", tabs)

    # --------------------------
    # Employees Module (Admin/Manager)
    # --------------------------
    if page == "Employees" and role_allowed(["Admin","Manager"]):
        st.subheader("🧾 Employee Management")

        # Add Employee
        with st.expander("➕ Add Employee"):
            with st.form("add_emp", clear_on_submit=True):
                col1, col2 = st.columns(2)
                name = col1.text_input("Full Name")
                age = col2.number_input("Age", min_value=18, max_value=100, value=25)
                gender = col1.selectbox("Gender", ["Male","Female","Other"])
                dept = col2.text_input("Department")
                role_in = col1.text_input("Role / Title")
                skills = col2.text_input("Skills (comma separated)")
                join_date = col1.date_input("Join Date", value=datetime.date.today())
                status = col2.selectbox("Status", ["Active","Resigned"])
                salary = col1.number_input("Salary", min_value=0.0, step=500.0, format="%.2f")
                location = col2.text_input("Location")
                submitted = st.form_submit_button("Add Employee")

                if submitted:
                    if not name.strip(): st.error("Name is required")
                    else:
                        emp_dict = {
                            "Name": name.strip(),
                            "Age": int(age),
                            "Gender": gender,
                            "Department": dept or "NA",
                            "Role": role_in or "NA",
                            "Skills": skills or "",
                            "Join_Date": join_date.strftime("%Y-%m-%d"),
                            "Resign_Date": "" if status=="Active" else join_date.strftime("%Y-%m-%d"),
                            "Status": status,
                            "Salary": float(salary),
                            "Location": location or ""
                        }
                        try: db.add_employee(emp_dict); st.success(f"Employee '{name}' added."); st.experimental_rerun()
                        except Exception as e: st.error("Failed to add employee"); st.exception(e)

        # Edit/Delete Employee
        if not emp_df.empty:
            st.subheader("✏️ Edit / Delete Employee")
            emp_options = format_emp_options(emp_df)
            sel = st.selectbox("Select Employee", emp_options, key="edit_emp_select")
            if sel:
                emp_id = int(sel.split(" - ")[0])
                emp_row = emp_df[emp_df["Emp_ID"]==emp_id].iloc[0].to_dict()
                with st.form("edit_emp"):
                    col1, col2 = st.columns(2)
                    e_name = col1.text_input("Full Name", value=emp_row.get("Name",""))
                    e_age = col2.number_input("Age", min_value=18, max_value=100, value=int(emp_row.get("Age",25)))
                    e_gender = col1.selectbox("Gender", ["Male","Female","Other"], index=0 if emp_row.get("Gender","Male")=="Male" else 1)
                    e_dept = col2.text_input("Department", value=emp_row.get("Department",""))
                    e_role = col1.text_input("Role / Title", value=emp_row.get("Role",""))
                    e_skills = col2.text_input("Skills", value=emp_row.get("Skills",""))
                    e_join = col1.date_input("Join Date", value=pd.to_datetime(emp_row.get("Join_Date")).date())
                    e_status = col2.selectbox("Status", ["Active","Resigned"], index=0 if emp_row.get("Status","Active")=="Active" else 1)
                    e_salary = col1.number_input("Salary", value=float(emp_row.get("Salary",0.0)), step=500.0)
                    e_location = col2.text_input("Location", value=emp_row.get("Location",""))
                    update_btn = st.form_submit_button("Save Changes")
                    delete_btn = st.form_submit_button("Delete Employee")

                    if update_btn:
                        updates = {
                            "Name": e_name.strip(),
                            "Age": int(e_age),
                            "Gender": e_gender,
                            "Department": e_dept or "NA",
                            "Role": e_role or "NA",
                            "Skills": e_skills or "",
                            "Join_Date": e_join.strftime("%Y-%m-%d"),
                            "Resign_Date": "" if e_status=="Active" else e_join.strftime("%Y-%m-%d"),
                            "Status": e_status,
                            "Salary": float(e_salary),
                            "Location": e_location or ""
                        }
                        try: db.update_employee(emp_id, updates); st.success("Employee updated"); st.experimental_rerun()
                        except Exception as e: st.error("Failed to update employee"); st.exception(e)

                    if delete_btn:
                        try: db.delete_employee(emp_id); st.success("Employee deleted"); st.experimental_rerun()
                        except Exception as e: st.error("Failed to delete employee"); st.exception(e)

    # --------------------------
    # Tasks Module
    # --------------------------
    if page == "Tasks":
        st.subheader("🗂️ Task Management")
        # Assign Task
        with st.expander("➕ Assign Task"):
            with st.form("assign_task"):
                task_title = st.text_input("Task title")
                assignee_options = format_emp_options(emp_df)
                assignee = st.selectbox("Assign to", assignee_options)
                due_date = st.date_input("Due date", value=datetime.date.today())
                priority = st.selectbox("Priority", ["Low","Medium","High"])
                remarks = st.text_area("Remarks")
                submit = st.form_submit_button("Assign Task")
                if submit:
                    if not task_title or not assignee: st.error("Task title and assignee required")
                    else:
                        emp_id = int(assignee.split(" - ")[0])
                        try: db.add_task({
                            "task_name": task_title.strip(),
                            "emp_id": emp_id,
                            "assigned_by": username,
                            "due_date": due_date.strftime("%Y-%m-%d"),
                            "priority": priority,
                            "status": "Pending",
                            "remarks": remarks
                        }); st.success("Task assigned"); st.experimental_rerun()
                        except Exception as e: st.error("Failed to assign task"); st.exception(e)

        # Edit/Delete Task
        if not tasks_df.empty:
            st.subheader("✏️ Edit / Delete Tasks")
            task_options = tasks_df["task_id"].astype(str).tolist()
            sel_task = st.selectbox("Select Task ID", task_options)
            if sel_task:
                task_row = tasks_df[tasks_df["task_id"]==int(sel_task)].iloc[0].to_dict()
                with st.form("edit_task"):
                    e_title = st.text_input("Task Title", value=task_row.get("task_name",""))
                    e_assignee = st.selectbox("Assign To", format_emp_options(emp_df), index=0)
                    e_due = st.date_input("Due Date", value=pd.to_datetime(task_row.get("due_date")).date())
                    e_priority = st.selectbox("Priority", ["Low","Medium","High"], index=["Low","Medium","High"].index(task_row.get("priority","Low")))
                    e_status = st.selectbox("Status", ["Pending","In-Progress","Completed"], index=["Pending","In-Progress","Completed"].index(task_row.get("status","Pending")))
                    e_remarks = st.text_area("Remarks", value=task_row.get("remarks",""))
                    update_btn = st.form_submit_button("Save Changes")
                    delete_btn = st.form_submit_button("Delete Task")

                    if update_btn:
                        emp_id_new = int(e_assignee.split(" - ")[0])
                        db.update_task(int(sel_task), {
                            "task_name": e_title.strip(),
                            "emp_id": emp_id_new,
                            "due_date": e_due.strftime("%Y-%m-%d"),
                            "priority": e_priority,
                            "status": e_status,
                            "remarks": e_remarks
                        })
                        st.success("Task updated"); st.experimental_rerun()
                    if delete_btn:
                        db.delete_task(int(sel_task)); st.success("Task deleted"); st.experimental_rerun()

    # --------------------------
    # Mood Tracker
    # --------------------------
    if page == "Mood Tracker":
        st.subheader("😃 Employee Mood Tracker")
        if role == "Employee":
            with st.form("add_mood"):
                mood = st.selectbox("Your Mood", ["Happy","Neutral","Sad","Stressed"])
                submit = st.form_submit_button("Log Mood")
                if submit:
                    db.add_mood(st.session_state.get("emp_id",0), mood)
                    st.success("Mood logged"); st.experimental_rerun()
        else:
            st.info("Admins/Managers can view analytics only")

    # --------------------------
    # Feedback
    # --------------------------
    if page == "Feedback":
        st.subheader("💬 Employee Feedback")
        with st.form("submit_feedback"):
            receiver_options = format_emp_options(emp_df)
            receiver = st.selectbox("Send Feedback To", receiver_options)
            message = st.text_area("Message")
            submit = st.form_submit_button("Submit Feedback")
            if submit:
                sender_id = int(st.session_state.get("emp_id",0))
                receiver_id = int(receiver.split(" - ")[0])
                db.add_feedback(sender_id, receiver_id, message)
                st.success("Feedback submitted"); st.experimental_rerun()

        if role in ["Admin","Manager"]:
            st.subheader("📊 Feedback Analytics")
            if not feedback_df.empty:
                feedback_df["Receiver"] = feedback_df["to_emp"].map(lambda x: get_employee_name(emp_df,x))
                feedback_df["Sender"] = feedback_df["from_emp"].map(lambda x: get_employee_name(emp_df,x))
                st.dataframe(feedback_df[["feedback_id","Sender","Receiver","feedback","date"]])
            else:
                st.info("No feedback available")

    # --------------------------
    # Analytics
    # --------------------------
    if page == "Analytics":
        st.subheader("📊 Dashboard Analytics")
        if not tasks_df.empty: st.bar_chart(tasks_df["status"].value_counts())
        if not mood_df.empty: st.bar_chart(mood_df["mood"].value_counts())
        if not feedback_df.empty: st.bar_chart(feedback_df["feedback"].apply(len))
