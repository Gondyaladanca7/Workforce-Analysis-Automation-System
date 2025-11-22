# pages/admin_dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import io

from utils.auth import require_login
from utils import database as db
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept, employee_options
from utils.pdf_export import generate_summary_pdf

sns.set_style("whitegrid")

def show():
    require_login()
    if st.session_state.get("role") != "Admin":
        st.warning("Access denied. Admins only.")
        st.stop()

    username = st.session_state.get("user", "Admin")
    st.set_page_config(page_title="Admin Dashboard", page_icon="🛠️", layout="wide")
    st.title("🛠️ Admin Dashboard")

    # Load employees
    try:
        df = db.fetch_employees()
    except Exception:
        df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills",
                                   "Join_Date","Resign_Date","Status","Salary","Location"])

    # Search & display
    st.header("1️⃣ Employee Records")
    search_term = st.text_input("Search employees by Name, ID, Role or Skills").strip()
    display_df = df.copy()
    if search_term:
        cond = pd.Series(False, index=display_df.index)
        for col in ["Name","Emp_ID","Role","Skills"]:
            if col in display_df.columns:
                cond |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
        display_df = display_df[cond]

    cols_to_show = [c for c in ["Emp_ID","Name","Department","Role","Join_Date","Status"] if c in display_df.columns]
    st.dataframe(display_df[cols_to_show], height=300)

    # Metrics
    st.header("📊 Workforce Summary Metrics")
    summary = get_summary(display_df)
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees", summary["total"])
    col2.metric("Active Employees", summary["active"])
    col3.metric("Resigned Employees", summary["resigned"])

    st.markdown("---")
    # Add employee form
    st.subheader("➕ Add New Employee")
    with st.form("add_employee_form", clear_on_submit=True):
        emp_name = st.text_input("Name")
        age = st.number_input("Age", step=1, min_value=18, max_value=100, value=25)
        gender_val = st.selectbox("Gender", ["Male","Female"])
        department = st.text_input("Department")
        role_input = st.text_input("Role")
        skills = st.text_input("Skills (semicolon separated)")
        join_date = st.date_input("Join Date", value=datetime.date.today())
        status = st.selectbox("Status", ["Active","Resigned"])
        resign_date = st.date_input("Resign Date (if resigned)", value=datetime.date.today())
        if status=="Active":
            resign_date = ""
        salary = st.number_input("Salary", step=1000.0, value=30000.0)
        location = st.text_input("Location")
        submit = st.form_submit_button("Add Employee")

        if submit:
            new_emp = {
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

    st.markdown("---")
    # Delete employee
    st.subheader("🗑️ Delete Employee")
    delete_id = st.number_input("Enter Employee ID", step=1, key="del_emp")
    if st.button("Delete Employee"):
        try:
            db.delete_employee(int(delete_id))
            st.success(f"Employee {delete_id} deleted successfully.")
        except Exception as e:
            st.error("Failed to delete employee.")
            st.exception(e)

    st.markdown("---")
    # Task management
    st.header("2️⃣ Task Management")
    st.subheader("Assign Task")
    with st.form("assign_task_form"):
        task_name = st.text_input("Task title")
        emp_opts = employee_options(df)
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

    # View tasks
    st.subheader("All Tasks")
    try:
        tasks_df = db.fetch_tasks()
    except Exception:
        tasks_df = pd.DataFrame()
    if not tasks_df.empty:
        tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
        today = pd.Timestamp.today().date()
        tasks_df["overdue"] = tasks_df["due_date_parsed"].apply(lambda d: d<today if pd.notna(d) else False)
        emp_map = df.set_index("Emp_ID")["Name"].to_dict()
        tasks_df["Employee"] = tasks_df["emp_id"].map(emp_map).fillna(tasks_df["emp_id"].astype(str))
        display_cols = ["task_id","task_name","Employee","assigned_by","due_date","status","overdue"]
        st.dataframe(tasks_df[display_cols], height=250)
    else:
        st.info("No tasks found.")

    st.markdown("---")
    # Mood tracker
    st.header("3️⃣ Employee Mood Tracker")
    emp_opts = employee_options(df)
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

    st.markdown("---")
    # Charts area
    st.header("4️⃣ Analytics Charts")
    # Department distribution
    dept_fig = None
    if not display_df.empty and "Department" in display_df.columns:
        try:
            dept_ser = department_distribution(display_df)
            fig1, ax1 = plt.subplots(figsize=(8,4))
            dept_fig = fig1
            sns.barplot(x=dept_ser.index, y=dept_ser.values, ax=ax1, palette="pastel")
            ax1.set_xlabel("Department")
            ax1.set_ylabel("Count")
            ax1.set_title("Department Distribution")
            plt.xticks(rotation=45)
            st.pyplot(fig1, use_container_width=True)
        except Exception:
            st.info("Unable to render Department chart.")
    else:
        st.info("No Department data available.")

    # Gender ratio
    gender_fig = None
    if not display_df.empty and "Gender" in display_df.columns:
        try:
            gender_ser = gender_ratio(display_df)
            fig2, ax2 = plt.subplots(figsize=(5,5))
            gender_fig = fig2
            ax2.pie(gender_ser.values, labels=gender_ser.index, autopct="%1.1f%%", startangle=90)
            ax2.axis("equal")
            ax2.set_title("Gender Ratio")
            st.pyplot(fig2, use_container_width=True)
        except Exception:
            st.info("Unable to render Gender chart.")
    else:
        st.info("No Gender data available.")

    # Salary by dept
    salary_fig = None
    if not display_df.empty and "Salary" in display_df.columns and "Department" in display_df.columns:
        try:
            avg_salary = average_salary_by_dept(display_df)
            fig3, ax3 = plt.subplots(figsize=(8,4))
            salary_fig = fig3
            sns.barplot(x=avg_salary.index, y=avg_salary.values, ax=ax3, palette="pastel")
            ax3.set_xlabel("Department")
            ax3.set_ylabel("Average Salary")
            ax3.set_title("Average Salary by Department")
            plt.xticks(rotation=45)
            st.pyplot(fig3, use_container_width=True)
        except Exception:
            st.info("Unable to render Salary chart.")
    else:
        st.info("No Salary data available.")

    st.markdown("---")
    # PDF export (uses current display_df)
    st.header("5️⃣ Export PDF Report")
    if st.button("Generate & Download PDF"):
        try:
            buf = io.BytesIO()
            # pass the same figures used above; if None, pdf_export will skip
            generate_summary_pdf(buf, summary["total"], summary["active"], summary["resigned"],
                                 display_df, mood_df=db.fetch_mood_logs(),
                                 gender_fig=gender_fig, salary_fig=salary_fig, dept_fig=dept_fig)
            st.download_button("📥 Download Report (PDF)", buf, file_name="workforce_summary.pdf", mime="application/pdf")
        except Exception as e:
            st.error("Failed to generate PDF.")
            st.exception(e)
    # close figures to free memory
    try:
        plt.close('all')
    except:
        pass
