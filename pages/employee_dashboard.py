# pages/employee_dashboard.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from utils.auth import require_login
from utils import database as db

def show():
    require_login()
    if st.session_state.get("role") != "Employee":
        st.warning("Access denied. Employees only.")
        st.stop()

    username = st.session_state.get("user", "Employee")
    st.title("👤 Employee Dashboard")

    # Load employees
    try:
        df = db.fetch_employees()
    except:
        df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills",
                                   "Join_Date","Resign_Date","Status","Salary","Location"])

    # determine emp_id
    emp_id = st.session_state.get("my_emp_id")
    if emp_id is None:
        emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"]
        emp_sel = st.selectbox("Select yourself", emp_opts)
        emp_id = int(emp_sel.split(" - ")[0])
        st.session_state["my_emp_id"] = emp_id

    my_data = df[df["Emp_ID"]==emp_id]
    st.subheader("1️⃣ Your Info")
    if not my_data.empty:
        st.table(my_data)
    else:
        st.info("Your profile not found in employee table.")

    # Tasks
    st.header("2️⃣ Your Tasks")
    try:
        tasks_df = db.fetch_tasks()
    except:
        tasks_df = pd.DataFrame()
    my_tasks = tasks_df[tasks_df["emp_id"]==emp_id] if not tasks_df.empty else pd.DataFrame()
    if not my_tasks.empty:
        my_tasks["due_date_parsed"] = pd.to_datetime(my_tasks["due_date"], errors="coerce").dt.date
        today = pd.Timestamp.today().date()
        my_tasks["overdue"] = my_tasks["due_date_parsed"].apply(lambda d: d<today if pd.notna(d) else False)
        st.dataframe(my_tasks[["task_id","task_name","assigned_by","due_date","status","overdue"]], height=300)
    else:
        st.info("No tasks assigned.")

    # Mood logging
    st.header("3️⃣ Log Your Mood")
    mood_choice = st.radio("Mood today", ["😊 Happy","😐 Neutral","😔 Sad","😡 Angry"], horizontal=True)
    if st.button("Log Mood"):
        try:
            db.add_mood_entry(emp_id, mood_choice, "")
            st.success("Mood logged successfully!")
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)

    # Mood history
    st.header("4️⃣ Mood History & Analytics")
    try:
        mood_df = db.fetch_mood_logs()
    except:
        mood_df = pd.DataFrame()
    my_moods = mood_df[mood_df["emp_id"]==emp_id] if not mood_df.empty else pd.DataFrame()
    if not my_moods.empty:
        st.dataframe(my_moods[["mood","log_date"]].sort_values(by="log_date", ascending=False), height=300)
    else:
        st.info("No mood logs available.")

    # small export personal PDF
    st.markdown("---")
    st.header("5️⃣ Export My Summary PDF")
    if st.button("Download My PDF"):
        try:
            buf = io.BytesIO()
            # personal df and personal mood logs
            generate_df = my_data
            generate_mood = my_moods
            from utils.pdf_export import generate_summary_pdf
            generate_summary_pdf(buf, len(generate_df), int(generate_df["Status"].eq("Active").sum()) if not generate_df.empty else 0, int(generate_df["Status"].eq("Resigned").sum()) if not generate_df.empty else 0,
                                 generate_df, mood_df=generate_mood, dept_fig=None, gender_fig=None, salary_fig=None, title=f"{username} - Employee Summary")
            st.download_button("📥 Download My Summary (PDF)", buf, file_name=f"{username}_summary.pdf", mime="application/pdf")
        except Exception as e:
            st.error("Failed to generate PDF.")
            st.exception(e)

    try:
        plt.close('all')
    except:
        pass
