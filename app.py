"""
Workforce Analytics & Employee Management System
Single-entry app that routes by role (uses utils/auth.py)
Features:
 - Role-based login
 - Employee management (add/delete)
 - Mood tracker + analytics
 - Task management
 - PDF export (professional)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import random
from utils import database as db
from utils.auth import require_login, logout_user, show_role_badge
from utils.analytics import get_summary, department_distribution, gender_ratio, average_salary_by_dept
from utils.pdf_export import generate_summary_pdf

sns.set_style("whitegrid")

# -------------------------
# Streamlit page config
# -------------------------
st.set_page_config(page_title="Workforce Analytics System", page_icon="👩‍💼", layout="wide")

# -------------------------
# Initialize DB tables
# -------------------------
try:
    db.initialize_all_tables()
except Exception as e:
    st.error("Failed to initialize database tables.")
    st.exception(e)
    st.stop()

# -------------------------
# Require login
# -------------------------
require_login()
show_role_badge()
logout_user()

role = st.session_state.get("role", "Employee")
username = st.session_state.get("user", "unknown")

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
# Auto-generate realistic employees if DB empty
# -------------------------
if df.empty:
    st.info("No employees found. Generating realistic workforce data...")

    def generate_realistic_employees(n=1000):
        employees = []
        departments = ["HR", "IT", "Sales", "Finance", "Marketing", "Support"]
        roles_by_dept = {
            "HR": ["HR Manager", "HR Executive"],
            "IT": ["Developer", "SysAdmin", "IT Manager"],
            "Sales": ["Sales Executive", "Sales Manager"],
            "Finance": ["Accountant", "Finance Manager"],
            "Marketing": ["Marketing Executive", "Marketing Manager"],
            "Support": ["Support Executive", "Support Manager"]
        }
        skills_pool = ["Python", "Excel", "SQL", "PowerPoint", "Communication", "Management", "Leadership", "JavaScript"]

        names_male = ["John","Alex","Michael","David","Robert","James","William","Daniel","Joseph","Mark"]
        names_female = ["Anna","Emily","Sophia","Olivia","Linda","Grace","Chloe","Emma","Sarah","Laura"]

        for i in range(1, n+1):
            gender = random.choices(["Male","Female"], weights=[0.65,0.35])[0]
            name = random.choice(names_male if gender=="Male" else names_female)
            dept = random.choice(departments)
            role_choice = random.choice(roles_by_dept[dept])

            if "Manager" in role_choice:
                age = random.randint(35, 60)
            elif "Executive" in role_choice:
                age = random.randint(25, 35)
            else:
                age = random.randint(22, 30)

            join_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(365, 365*10))

            # Updated realistic status: ~84% active
            status = random.choices(["Active","Resigned"], weights=[0.84,0.16])[0]
            if status == "Resigned":
                min_days = 180
                max_days = (datetime.datetime.now() - join_date).days
                if max_days > min_days:
                    resign_date = join_date + datetime.timedelta(days=random.randint(min_days, max_days))
                else:
                    resign_date = ""
            else:
                resign_date = ""

            salary_ranges = {
                "Manager": (90000, 150000),
                "Executive": (30000, 70000),
                "Developer": (40000, 100000),
                "SysAdmin": (40000, 90000),
                "Accountant": (35000, 80000)
            }
            key = "Manager" if "Manager" in role_choice else ("Executive" if "Executive" in role_choice else role_choice)
            sal_min, sal_max = salary_ranges.get(key, (30000,100000))
            salary = random.randint(sal_min, sal_max)

            location = random.choice(["Delhi","Mumbai","Bangalore","Chennai","Hyderabad"])
            skills = ", ".join(random.sample(skills_pool, k=random.randint(2,4)))

            emp = {
                "Emp_ID": i,
                "Name": name,
                "Age": age,
                "Gender": gender,
                "Department": dept,
                "Role": role_choice,
                "Skills": skills,
                "Join_Date": join_date.strftime("%Y-%m-%d"),
                "Resign_Date": resign_date.strftime("%Y-%m-%d") if resign_date else "",
                "Status": status,
                "Salary": salary,
                "Location": location
            }
            employees.append(emp)
        return pd.DataFrame(employees)

    df_generated = generate_realistic_employees(1000)
    for _, row in df_generated.iterrows():
        db.add_employee(row.to_dict())
    df = db.fetch_employees()
    st.success("✅ Realistic workforce data generated and added to the database.")

# -------------------------
# Sidebar Controls
# -------------------------
st.sidebar.header("Filters & Controls")
st.sidebar.markdown(f"**Logged in as:** {username} — **{role}**")

def safe_options(df_local, col):
    return ["All"] + sorted(df_local[col].dropna().unique().tolist()) if col in df_local.columns else ["All"]

selected_dept = st.sidebar.selectbox("Department", safe_options(df, "Department"))
selected_status = st.sidebar.selectbox("Status", safe_options(df, "Status"))
selected_gender = st.sidebar.selectbox("Gender", ["All", "Male", "Female"])
selected_role = st.sidebar.selectbox("Role", safe_options(df, "Role"))
selected_skills = st.sidebar.multiselect("Skills", sorted(df["Skills"].dropna().unique().tolist()) if "Skills" in df.columns else [])

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
if selected_skills:
    filtered_df = filtered_df[filtered_df["Skills"].apply(lambda x: any(skill in x for skill in selected_skills))]

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

available_sort_cols = [c for c in ["Emp_ID","Name","Age","Salary","Join_Date","Department","Role","Skills"] if c in display_df.columns]
if not available_sort_cols:
    available_sort_cols = display_df.columns.tolist()
sort_col = st.selectbox("Sort by", available_sort_cols, index=0)
ascending = st.radio("Order", ["Ascending","Descending"], horizontal=True)=="Ascending"
if sort_col in ["Emp_ID","Age","Salary"]:
    display_df = display_df.sort_values(by=sort_col, ascending=ascending)
else:
    display_df = display_df.sort_values(by=sort_col, ascending=ascending, key=lambda s: s.astype(str))

cols_to_show = [c for c in ["Emp_ID","Name","Department","Role","Join_Date","Status"] if c in display_df.columns]
st.dataframe(display_df[cols_to_show], height=420)

st.markdown("---")

# -------------------------
# Workforce Summary
# -------------------------
st.header("2️⃣ Workforce Summary")
summary = get_summary(filtered_df) if not filtered_df.empty else {"total":0,"active":0,"resigned":0}
st.metric("Total Employees", summary["total"])
st.metric("Active Employees", summary["active"])
st.metric("Resigned Employees", summary["resigned"])

st.markdown("---")

# -------------------------
# Dashboard Charts
# -------------------------
def plot_bar_chart(series, title, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(6,4))
    sns.barplot(x=series.index, y=series.values, palette="pastel", ax=ax)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

st.header("3️⃣ Department Distribution")
dept_fig = None
if not filtered_df.empty and "Department" in filtered_df.columns:
    dept_ser = department_distribution(filtered_df)
    dept_fig = plot_bar_chart(dept_ser, "Department-wise Employee Distribution", "Department", "Employees")
    st.pyplot(dept_fig, use_container_width=True)
else:
    st.info("No Department data available.")

st.markdown("---")

st.header("4️⃣ Gender Ratio")
gender_fig = None
if not filtered_df.empty and "Gender" in filtered_df.columns:
    try:
        gender_counts = gender_ratio(filtered_df)
        fig, ax = plt.subplots(figsize=(5,5))
        gender_fig = fig
        ax.pie(gender_counts.values, labels=gender_counts.index, autopct="%1.1f%%",
               startangle=90, colors=sns.color_palette("pastel"))
        ax.axis("equal")
        ax.set_title("Gender Distribution")
        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
    except Exception:
        st.info("Not enough data to plot gender ratio.")
else:
    st.info("No Gender data available.")

st.markdown("---")

st.header("5️⃣ Average Salary by Department")
salary_fig = None
if not filtered_df.empty and "Salary" in filtered_df.columns and "Department" in filtered_df.columns:
    avg_salary = average_salary_by_dept(filtered_df)
    salary_fig = plot_bar_chart(avg_salary, "Average Salary by Department", "Department", "Average Salary")
    st.pyplot(salary_fig, use_container_width=True)
else:
    st.info("No Salary or Department data available.")

st.markdown("---")

# -------------------------
# Add New Employee (Sidebar)
# -------------------------
if role in ("Admin", "Manager"):
    st.sidebar.header("➕ Add New Employee")
    with st.sidebar.form("add_employee_form", clear_on_submit=True):
        next_emp_id = int(df["Emp_ID"].max()) + 1 if ("Emp_ID" in df.columns and not df["Emp_ID"].empty) else 1
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
                    "Resign_Date": str(resign_date) if status=="Resigned" else "",
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
# PDF Export
# -------------------------
st.sidebar.header("📄 Export PDF Summary")
if st.sidebar.button("Download PDF"):
    try:
        pdf_path = "workforce_summary_report.pdf"
        mood_df = db.fetch_mood_logs()
        if not mood_df.empty:
            emp_names = df.set_index("Emp_ID")["Name"].to_dict()
            mood_df["Name"] = mood_df["emp_id"].map(emp_names)

        generate_summary_pdf(
            pdf_path,
            total=summary["total"],
            active=summary["active"],
            resigned=summary["resigned"],
            df=filtered_df,
            mood_df=mood_df,
            gender_fig=gender_fig,
            salary_fig=salary_fig,
            dept_fig=dept_fig
        )

        with open(pdf_path, "rb") as f:
            st.sidebar.download_button("📥 Download PDF", f, file_name="workforce_summary_report.pdf", mime="application/pdf")

    except Exception as e:
        st.error("Failed to generate PDF.")
        st.exception(e)
