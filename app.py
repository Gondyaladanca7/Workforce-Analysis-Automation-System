# app.py
"""
Workforce Analytics & Employee Management System
Includes: Employee management, Analytics, PDF export, Employee Mood Tracker with full charts.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import datetime
import bcrypt
from utils.pdf_export import generate_summary_pdf
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils import database as db

sns.set_style("whitegrid")

# ------------------------- Page config
st.set_page_config(page_title="Workforce Analytics System", page_icon="👩‍💼", layout="wide")

# ------------------------- Authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

PLAIN_USERNAME = "GOVIND"
PLAIN_PASSWORD = "LADU"
stored_hash = bcrypt.hashpw(PLAIN_PASSWORD.encode("utf-8"), bcrypt.gensalt())

def check_credentials(username: str, password: str) -> bool:
    if username is None or password is None:
        return False
    if username.strip().upper() != PLAIN_USERNAME:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash)
    except Exception:
        return False

def show_login():
    st.title("🔐 Login — Workforce Analytics System")
    st.write("Use dev credentials for local testing.")
    col1, col2 = st.columns(2)
    with col1:
        username_input = st.text_input("Username")
    with col2:
        password_input = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_credentials(username_input, password_input):
            st.session_state.logged_in = True
            st.session_state.user = username_input.strip().upper()
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")

if not st.session_state.logged_in:
    show_login()
    st.stop()

auth_user = st.session_state.user or PLAIN_USERNAME
st.sidebar.success(f"Welcome {auth_user} 👋")
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.experimental_rerun()

# ------------------------- Initialize DB & Mood table
try:
    db.initialize_database()
    db.initialize_mood_table()
except Exception as e:
    st.error("Failed to initialize database.")
    st.exception(e)
    st.stop()

# ------------------------- Load employee data
try:
    df = db.fetch_employees()
except Exception as e:
    st.error("Failed to load employee data.")
    st.exception(e)
    df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills",
                               "Join_Date","Resign_Date","Status","Salary","Location"])

# ------------------------- Sidebar Filters
st.sidebar.header("🔍 Filter Employee Data")
def safe_options(df_local, col):
    if col in df_local.columns:
        opts = sorted(df_local[col].dropna().unique().tolist())
        return ["All"] + opts
    return ["All"]

selected_dept = st.sidebar.selectbox("Department", safe_options(df, "Department"))
selected_status = st.sidebar.selectbox("Status", safe_options(df, "Status"))
selected_gender = st.sidebar.selectbox("Gender", ["All", "Male", "Female"])
selected_role = st.sidebar.selectbox("Role", safe_options(df, "Role"))
selected_skills = st.sidebar.selectbox("Skills", safe_options(df, "Skills"))

# Apply filters
filtered_df = df.copy()
if selected_dept != "All": filtered_df = filtered_df[filtered_df["Department"]==selected_dept]
if selected_status != "All": filtered_df = filtered_df[filtered_df["Status"]==selected_status]
if selected_gender != "All": filtered_df = filtered_df[filtered_df["Gender"]==selected_gender]
if selected_role != "All": filtered_df = filtered_df[filtered_df["Role"]==selected_role]
if selected_skills != "All": filtered_df = filtered_df[filtered_df["Skills"]==selected_skills]

# ------------------------- Employee Table
st.header("1️⃣ Employee Records")
search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
display_df = filtered_df.copy()
if search_term:
    cond = pd.Series([False]*len(display_df), index=display_df.index)
    for col in ["Name","Emp_ID","Skills","Role"]:
        if col in display_df.columns:
            cond |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

sort_col = st.selectbox("Sort by", options=[c for c in ["Emp_ID","Name","Age","Salary","Join_Date","Department","Role","Skills"] if c in display_df.columns], index=0)
ascending = st.radio("Order", ["Ascending","Descending"], horizontal=True) == "Ascending"
try:
    display_df = display_df.sort_values(by=sort_col, ascending=ascending, key=lambda s: s.astype(str))
except Exception:
    pass

st.dataframe(display_df, height=400)

# ------------------------- Delete Employee
st.subheader("🗑️ Delete Employee")
delete_id = st.number_input("Enter Employee ID to delete", step=1, format="%d")
if st.button("Delete Employee"):
    try:
        if "Emp_ID" in df.columns and int(delete_id) in df["Emp_ID"].astype(int).values:
            # Delete mood logs of employee
            conn = db.sqlite3.connect(db.DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM mood_logs WHERE emp_id=?", (delete_id,))
            conn.commit()
            conn.close()
            
            # Delete employee
            db.delete_employee(int(delete_id))
            st.success(f"Employee ID {delete_id} and their mood logs deleted successfully!")
            st.experimental_rerun()
        else:
            st.warning(f"No employee found with ID {delete_id}")
    except Exception as e:
        st.error("Failed to delete employee.")
        st.exception(e)

# ------------------------- Summary & Analytics
st.header("2️⃣ Workforce Summary")
total, active, resigned = get_summary(filtered_df) if not filtered_df.empty else (0,0,0)
st.write(f"Total Employees: **{total}**")
st.write(f"Active Employees: **{active}**")
st.write(f"Resigned Employees: **{resigned}**")

st.header("3️⃣ Department Distribution")
if not filtered_df.empty and "Department" in filtered_df.columns:
    st.bar_chart(department_distribution(filtered_df))

st.header("4️⃣ Gender Ratio")
if not filtered_df.empty and "Gender" in filtered_df.columns:
    gender = gender_ratio(filtered_df)
    fig, ax = plt.subplots()
    ax.pie(gender, labels=gender.index, autopct="%1.1f%%", colors=sns.color_palette("pastel"))
    st.pyplot(fig)

st.header("5️⃣ Average Salary by Department")
if not filtered_df.empty and "Department" in filtered_df.columns and "Salary" in filtered_df.columns:
    st.bar_chart(average_salary_by_dept(filtered_df))

# ------------------------- Add New Employee Form
st.sidebar.header("➕ Add New Employee")
with st.sidebar.form("add_employee_form"):
    next_emp_id = int(df["Emp_ID"].max())+1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
    emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d")
    emp_name = st.text_input("Name")
    age = st.number_input("Age", step=1, format="%d")
    gender_val = st.selectbox("Gender", ["Male","Female"])
    department = st.text_input("Department")
    role = st.text_input("Role")
    skills = st.text_input("Skills (semicolon separated)")
    join_date = st.date_input("Join Date")
    status = st.selectbox("Status", ["Active","Resigned"])
    resign_date = st.date_input("Resign Date (if resigned)")
    if status=="Active": resign_date=""
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
            "Role": role or "NA",
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
            st.experimental_rerun()
        except Exception as e:
            st.error("Failed to add employee.")
            st.exception(e)

# ------------------------- Mood Tracker
st.header("6️⃣ Employee Pulse Check (Mood Tracker)")
if not df.empty:
    emp_options = df["Emp_ID"].astype(str) + " - " + df["Name"]
    selected_emp = st.selectbox("Select Employee", options=emp_options)
    emp_id_selected = int(selected_emp.split(" - ")[0])

    mood = st.radio("How is the employee feeling today?", ["😊 Happy", "😐 Neutral", "😔 Sad", "😡 Angry"])
    if st.button("Log Mood"):
        today = datetime.date.today().strftime("%Y-%m-%d")
        db.add_mood_entry(emp_id_selected, mood, today)
        st.success(f"Mood for employee ID {emp_id_selected} logged successfully!")
        st.experimental_rerun()

    # Display mood history
    st.subheader("Mood History")
    mood_logs = db.fetch_mood_logs()
    if not mood_logs.empty:
        merged = pd.merge(mood_logs, df[["Emp_ID","Name"]], left_on="emp_id", right_on="Emp_ID", how="inner")
        merged_display = merged[["emp_id","Name","mood","log_date"]].sort_values(by="log_date", ascending=False)
        st.dataframe(merged_display, height=300)
    else:
        st.info("No mood logs found yet.")

    # ------------------------- Mood Analytics Charts
    st.subheader("Mood Analytics")
    if not mood_logs.empty:
        merged['Mood_Label'] = merged['mood'].replace({
            "😊 Happy": "Happy",
            "😐 Neutral": "Neutral",
            "😔 Sad": "Sad",
            "😡 Angry": "Angry"
        })
        mood_score_map = {"Happy":5,"Neutral":3,"Sad":2,"Angry":1}
        merged['Mood_Score'] = merged['Mood_Label'].map(mood_score_map)

        # Average mood per employee
        avg_mood = merged.groupby("Name")["Mood_Score"].mean().round().astype(int).sort_values()
        fig, ax = plt.subplots(figsize=(6,3))
        sns.barplot(x=avg_mood.values, y=avg_mood.index, palette="coolwarm", ax=ax)
        for i, v in enumerate(avg_mood.values):
            ax.text(v + 0.1, i, str(v), color='black', va='center')
        ax.set_xlabel("Average Mood Score")
        ax.set_ylabel("Employee")
        ax.set_title("Average Mood per Employee")
        st.pyplot(fig)

        # Overall mood distribution
        mood_counts = merged['Mood_Label'].value_counts()
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(mood_counts, labels=[f"{label} ({count})" for label, count in zip(mood_counts.index, mood_counts.values)],
               autopct=None, startangle=90, colors=sns.color_palette("Set2"))
        ax.set_title("Overall Team Mood")
        st.pyplot(fig)

        # Mood trend over time
        fig, ax = plt.subplots(figsize=(6,3))
        for name, group in merged.groupby("Name"):
            group_sorted = group.sort_values(by="log_date")
            ax.plot(group_sorted["log_date"], group_sorted["Mood_Score"], marker='o', label=name)
        ax.set_xlabel("Date")
        ax.set_ylabel("Mood Score")
        ax.set_title("Mood Trend Over Time")
        ax.legend(fontsize=6)
        plt.xticks(rotation=45)
        st.pyplot(fig)

# ------------------------- Export PDF
st.subheader("📄 Export Summary Report")
if st.button("Download Summary PDF"):
    try:
        pdf_path = "workforce_summary_report.pdf"
        generate_summary_pdf(pdf_path, total, active, resigned, filtered_df)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="workforce_summary_report.pdf">📥 Click here to download PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    except Exception as e:
        st.error("Failed to generate PDF.")
        st.exception(e)

# ------------------------- Future Placeholder Sections
st.header("7️⃣ Future Features")
st.info("AI Skill Radar, Project Health Tracker, and Burnout Prediction will be integrated here in future updates.")
