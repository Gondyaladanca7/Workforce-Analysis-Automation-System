

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

    def generate_realistic_employees(n=100):
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
        skills_pool = ["Python","Excel","SQL","PowerPoint","Communication","Management","Leadership","JavaScript"]
        names_male = ["John","Alex","Michael","David","Robert","James","William","Daniel","Joseph","Mark"]
        names_female = ["Anna","Emily","Sophia","Olivia","Linda","Grace","Chloe","Emma","Sarah","Laura"]

        for i in range(1,n+1):
            gender = random.choices(["Male","Female"], weights=[0.65,0.35])[0]
            name = random.choice(names_male if gender=="Male" else names_female)
            dept = random.choice(departments)
            role_choice = random.choice(roles_by_dept[dept])
            if "Manager" in role_choice: age=random.randint(35,60)
            elif "Executive" in role_choice: age=random.randint(25,35)
            else: age=random.randint(22,30)

            join_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(365,365*10))
            status = random.choices(["Active","Resigned"], weights=[random.randint(80,88), random.randint(12,20)])[0]

            if status=="Resigned":
                min_days = 180
                max_days = (datetime.datetime.now()-join_date).days
                resign_date = join_date + datetime.timedelta(days=random.randint(min_days,max_days)) if max_days>min_days else ""
            else: resign_date = ""

            salary_ranges = {
                "Manager":(90000,150000),
                "Executive":(30000,70000),
                "Developer":(40000,100000),
                "SysAdmin":(40000,90000),
                "Accountant":(35000,80000)
            }
            key = "Manager" if "Manager" in role_choice else ("Executive" if "Executive" in role_choice else role_choice)
            sal_min, sal_max = salary_ranges.get(key,(30000,100000))
            salary = random.randint(sal_min,sal_max)

            location = random.choice(["Delhi","Mumbai","Bangalore","Chennai","Hyderabad"])
            skills = ", ".join(random.sample(skills_pool,k=random.randint(2,4)))

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

    df_generated = generate_realistic_employees(100)
    for _, row in df_generated.iterrows():
        db.add_employee(row.to_dict())
    df = db.fetch_employees()
    st.success("✅ Realistic workforce data generated and added to the database.")

# -------------------------
# Sidebar Filters
# -------------------------
st.sidebar.header("Filters")
def safe_options(df_local, col):
    return ["All"]+sorted(df_local[col].dropna().unique().tolist()) if col in df_local.columns else ["All"]

selected_dept = st.sidebar.selectbox("Department", safe_options(df,"Department"))
selected_status = st.sidebar.selectbox("Status", safe_options(df,"Status"))
selected_gender = st.sidebar.selectbox("Gender", ["All","Male","Female"])
selected_role = st.sidebar.selectbox("Role", safe_options(df,"Role"))
selected_skills = st.sidebar.selectbox("Skills", safe_options(df,"Skills"))

# -------------------------
# CSV Upload (Admin/Manager)
# -------------------------
if role in ("Admin","Manager"):
    st.sidebar.header("📁 Import CSV")
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)
            required_cols = {
                "Emp_ID": None,"Name":"NA","Age":0,"Gender":"Male","Department":"NA",
                "Role":"NA","Skills":"NA","Join_Date":"","Resign_Date":"",
                "Status":"Active","Salary":0.0,"Location":"NA"
            }
            for col, default in required_cols.items():
                if col not in df_uploaded.columns:
                    df_uploaded[col] = default

            existing_ids = set(df["Emp_ID"].dropna().astype(int).tolist()) if not df.empty else set()
            next_id = max(existing_ids)+1 if existing_ids else 1

            for _, row in df_uploaded.iterrows():
                eid = int(row.get("Emp_ID")) if pd.notna(row.get("Emp_ID")) else next_id
                if eid in existing_ids: eid = next_id; next_id+=1
                emp = {col: row.get(col, default) for col, default in required_cols.items()}
                emp["Emp_ID"]=int(eid)
                db.add_employee(emp)
                existing_ids.add(emp["Emp_ID"])
            st.success("CSV processed and employees added.")
            st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger",False)
        except Exception as e:
            st.error("Failed to process CSV.")
            st.exception(e)

# -------------------------
# Apply Filters
# -------------------------
filtered_df = df.copy()
if selected_dept!="All": filtered_df=filtered_df[filtered_df["Department"]==selected_dept]
if selected_status!="All": filtered_df=filtered_df[filtered_df["Status"]==selected_status]
if selected_gender!="All": filtered_df=filtered_df[filtered_df["Gender"]==selected_gender]
if selected_role!="All": filtered_df=filtered_df[filtered_df["Role"]==selected_role]
if selected_skills!="All": filtered_df=filtered_df[filtered_df["Skills"]==selected_skills]

# -------------------------
# Employee Records Table
# -------------------------
st.title("👩‍💼 Workforce Analytics System")
st.header("1. Employee Records")

search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
display_df = filtered_df.copy()
if search_term:
    cond = pd.Series(False, index=display_df.index)
    for col in ["Name","Emp_ID","Skills","Role"]:
        if col in display_df.columns:
            cond |= display_df[col].astype(str).str.contains(search_term, case=False, na=False)
    display_df = display_df[cond]

sort_col_options = [c for c in ["Emp_ID","Name","Age","Salary","Join_Date","Department","Role","Skills"] if c in display_df.columns]
sort_col = st.selectbox("Sort by", sort_col_options, index=0)
ascending = st.radio("Order", ["Ascending","Descending"], horizontal=True)=="Ascending"
try: display_df = display_df.sort_values(sort_col, ascending=ascending)
except: pass

cols_to_show = [c for c in ["Emp_ID","Name","Department","Role","Join_Date","Status"] if c in display_df.columns]
st.dataframe(display_df[cols_to_show], height=420)

# -------------------------
# Workforce Summary Metrics
# -------------------------
st.header("2. Workforce Summary")
summary = get_summary(filtered_df) if not filtered_df.empty else {"total":0,"active":0,"resigned":0}

# Show metrics as numbers (avoid Streamlit missing value issue)
st.metric("Total Employees", int(summary.get("total",0)))
st.metric("Active Employees", int(summary.get("active",0)))
st.metric("Resigned Employees", int(summary.get("resigned",0)))
