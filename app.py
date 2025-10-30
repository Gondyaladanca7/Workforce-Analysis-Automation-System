# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import streamlit_authenticator as stauth
import base64
import datetime
from utils.pdf_export import generate_summary_pdf
from utils.analytics import *
from utils import database as db
import random
from faker import Faker

# -------------------------
# Page config
# -------------------------
st.set_page_config(page_title="Workforce Analytics System", page_icon="👩‍💼", layout="wide")

# -------------------------
# Authentication setup
# -------------------------
credentials = {"usernames": {}}
try:
    GOVIND_PLAIN_PASSWORD = "LADU"
    govind_hashed = stauth.Hasher([GOVIND_PLAIN_PASSWORD]).generate()[0]
    credentials["usernames"]["GOVIND"] = {
        "name": "Govind Lad",
        "password": govind_hashed,
        "role": "admin"
    }
except Exception as e:
    # Streamlit isn't running yet? show error in app when it is.
    st.error("Error generating GOVIND's password hash.")
    st.exception(e)

authenticator = stauth.Authenticate(
    credentials=credentials,
    cookie_name='workforce_dashboard',
    key='abcdef',
    cookie_expiry_days=1
)

# -------------------------
# Login form
# -------------------------
name, authentication_status, username = authenticator.login(form_name='Login', location='main')
if authentication_status:
    st.success(f"Welcome {name}")
elif authentication_status is False:
    st.error("Incorrect username or password")
elif authentication_status is None:
    st.warning("Enter your credentials")

# -------------------------
# Logged-in dashboard
# -------------------------
if authentication_status:
    authenticator.logout("Logout", location="sidebar", key="logout-btn")
    st.sidebar.success(f"Welcome {name} 👋")
    st.title("👩‍💼 Workforce Analytics System")

    # Ensure DB initialized
    db.initialize_database()

    # --- Load data from DB ---
    try:
        df = db.fetch_employees()
    except Exception as e:
        st.error("Failed to load employee data from database.")
        st.exception(e)
        df = pd.DataFrame(columns=["Emp_ID","Name","Age","Gender","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"])

    # --- CSV Upload (optional, robust) ---
    st.sidebar.header("📁 Import Employee Data from CSV")
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        try:
            df_uploaded = pd.read_csv(uploaded_file)

            # required columns and defaults
            required_cols = {
                "Emp_ID": None,  # special handling
                "Name": "NA",
                "Age": 0,
                "Gender": "NA",
                "Department": "NA",
                "Role": "NA",
                "Skills": "NA",
                "Join_Date": "",
                "Resign_Date": "",
                "Status": "Active",
                "Salary": 0.0,
                "Location": "NA"
            }

            # Add missing columns with defaults (except Emp_ID handled below)
            for col, default in required_cols.items():
                if col not in df_uploaded.columns and col != "Emp_ID":
                    df_uploaded[col] = default

            # If Emp_ID missing, create sequential IDs starting after current max
            existing_ids = set(df['Emp_ID'].dropna().astype(int).tolist()) if not df.empty else set()
            next_id = max(existing_ids) + 1 if existing_ids else 1
            if "Emp_ID" not in df_uploaded.columns:
                df_uploaded["Emp_ID"] = [None] * len(df_uploaded)

            # Insert rows into DB safely
            for _, row in df_uploaded.iterrows():
                row_dict = row.to_dict()

                # Assign Emp_ID if None or nan or duplicate
                try:
                    eid = int(row_dict.get("Emp_ID")) if pd.notna(row_dict.get("Emp_ID")) else None
                except Exception:
                    eid = None

                if eid is None or eid in existing_ids:
                    eid = next_id
                    next_id += 1

                # Build employee dict with safe defaults
                emp = {
                    "Emp_ID": int(eid),
                    "Name": str(row_dict.get("Name")) if pd.notna(row_dict.get("Name")) else required_cols["Name"],
                    "Age": int(row_dict.get("Age")) if pd.notna(row_dict.get("Age")) else required_cols["Age"],
                    "Gender": str(row_dict.get("Gender")) if pd.notna(row_dict.get("Gender")) else required_cols["Gender"],
                    "Department": str(row_dict.get("Department")) if pd.notna(row_dict.get("Department")) else required_cols["Department"],
                    "Role": str(row_dict.get("Role")) if pd.notna(row_dict.get("Role")) else required_cols["Role"],
                    "Skills": str(row_dict.get("Skills")) if pd.notna(row_dict.get("Skills")) else required_cols["Skills"],
                    "Join_Date": str(row_dict.get("Join_Date")) if pd.notna(row_dict.get("Join_Date")) else required_cols["Join_Date"],
                    "Resign_Date": str(row_dict.get("Resign_Date")) if pd.notna(row_dict.get("Resign_Date")) else required_cols["Resign_Date"],
                    "Status": str(row_dict.get("Status")) if pd.notna(row_dict.get("Status")) else required_cols["Status"],
                    "Salary": float(row_dict.get("Salary")) if pd.notna(row_dict.get("Salary")) else required_cols["Salary"],
                    "Location": str(row_dict.get("Location")) if pd.notna(row_dict.get("Location")) else required_cols["Location"],
                }

                db.add_employee(emp)
                existing_ids.add(emp["Emp_ID"])

            st.success("CSV uploaded successfully and added to database!")
            st.experimental_rerun()

        except Exception as e:
            st.error("Failed to process CSV")
            st.exception(e)

    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filter Employee Data")
    dept_options = sorted(df['Department'].dropna().unique().tolist()) if 'Department' in df.columns else []
    selected_dept = st.sidebar.selectbox("Department", ["All"] + dept_options)

    status_options = sorted(df['Status'].dropna().unique().tolist()) if 'Status' in df.columns else []
    selected_status = st.sidebar.selectbox("Status", ["All"] + status_options)

    gender_options = sorted(df['Gender'].dropna().unique().tolist()) if 'Gender' in df.columns else []
    selected_gender = st.sidebar.selectbox("Gender", ["All"] + gender_options)

    role_options = sorted(df['Role'].dropna().unique().tolist()) if 'Role' in df.columns else []
    selected_role = st.sidebar.selectbox("Role", ["All"] + role_options)

    skills_options = sorted(df['Skills'].dropna().unique().tolist()) if 'Skills' in df.columns else []
    selected_skills = st.sidebar.selectbox("Skills", ["All"] + skills_options)

    # --- Apply filters ---
    filtered_df = df.copy()
    if selected_dept != "All" and 'Department' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
    if selected_status != "All" and 'Status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    if selected_gender != "All" and 'Gender' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Gender'] == selected_gender]
    if selected_role != "All" and 'Role' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Role'] == selected_role]
    if selected_skills != "All" and 'Skills' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Skills'] == selected_skills]

    # --- Employee Table: Search, Sort, Highlight, Delete ---
    st.header("1️⃣ Raw Employee Data")
    search_term = st.text_input("Search by Name, ID, Skills, or Role").strip()
    filtered_search_df = filtered_df.copy()
    if search_term:
        cond = pd.Series([False]*len(filtered_search_df), index=filtered_search_df.index)
        for col in ['Name','Emp_ID','Skills','Role']:
            if col in filtered_search_df.columns:
                cond = cond | filtered_search_df[col].astype(str).str.contains(search_term, case=False, na=False)
        filtered_search_df = filtered_search_df[cond]

    # Sorting
    sort_options = [c for c in ["Emp_ID","Name","Age","Salary","Join_Date","Department","Role","Skills"] if c in filtered_search_df.columns]
    if not sort_options:
        sort_options = filtered_search_df.columns.tolist()
    sort_col = st.selectbox("Sort by", options=sort_options, index=0)
    ascending_order = st.radio("Order", ["Ascending","Descending"], horizontal=True)
    if sort_col in filtered_search_df.columns:
        try:
            filtered_search_df = filtered_search_df.sort_values(by=sort_col, ascending=(ascending_order=="Ascending"))
        except Exception:
            # fallback if column dtype mixed
            filtered_search_df = filtered_search_df.sort_values(by=sort_col, key=lambda s: s.astype(str), ascending=(ascending_order=="Ascending"))

    # Plain white background + black text for table display
    try:
        styled_df = filtered_search_df.style.set_properties(**{'background-color': 'white', 'color': 'black'})
    except Exception:
        styled_df = filtered_search_df  # fallback

    # Delete employee
    st.subheader("🗑️ Delete Employee")
    delete_id = st.number_input("Enter Employee ID to delete", step=1, format="%d")
    if st.button("Delete Employee"):
        try:
            if 'Emp_ID' in df.columns and int(delete_id) in df['Emp_ID'].astype(int).values:
                db.delete_employee(int(delete_id))
                st.success(f"Employee ID {delete_id} deleted successfully!")
                st.experimental_rerun()
            else:
                st.warning(f"No employee found with ID {delete_id}")
        except Exception as e:
            st.error("Failed to delete employee.")
            st.exception(e)

    # Display table
    # If styled_df is a Styler, Streamlit can render it; otherwise render DataFrame
    if hasattr(styled_df, "render"):
        st.dataframe(styled_df, height=420)
    else:
        st.dataframe(styled_df, height=420)

    # --- Summary Section ---
    st.header("2️⃣ Summary")
    try:
        total, active, resigned = get_summary(filtered_df) if not filtered_df.empty else (0,0,0)
        st.write(f"Total Employees: {total}")
        st.write(f"Active Employees: {active}")
        st.write(f"Resigned Employees: {resigned}")
    except Exception as e:
        st.error("Error computing summary.")
        st.exception(e)

    # --- Charts ---
    st.header("3️⃣ Department-wise Employee Count")
    try:
        if not filtered_df.empty and 'Department' in filtered_df.columns:
            st.bar_chart(department_distribution(filtered_df))
        else:
            st.info("Department chart requires 'Department' column in data.")
    except Exception as e:
        st.error("Error plotting department distribution.")
        st.exception(e)

    st.header("4️⃣ Gender Ratio")
    try:
        if not filtered_df.empty and 'Gender' in filtered_df.columns:
            gender = gender_ratio(filtered_df)
            fig, ax = plt.subplots()
            ax.pie(gender, labels=gender.index, autopct='%1.1f%%')
            st.pyplot(fig)
        else:
            st.info("Gender ratio requires 'Gender' column in data.")
    except Exception as e:
        st.error("Error creating gender ratio plot.")
        st.exception(e)

    st.header("5️⃣ Average Salary by Department")
    try:
        if not filtered_df.empty and 'Department' in filtered_df.columns and 'Salary' in filtered_df.columns:
            st.bar_chart(average_salary_by_dept(filtered_df))
        else:
            st.info("Average salary chart requires 'Department' and 'Salary' columns.")
    except Exception as e:
        st.error("Error plotting average salary by department.")
        st.exception(e)

    # --- Add New Employee Form ---
    st.sidebar.header("➕ Add New Employee")
    with st.sidebar.form("add_employee_form"):
        # If DB has Emp_ID column and existing rows, suggest next id; else allow manual
        next_emp_id = int(df['Emp_ID'].max()) + 1 if ('Emp_ID' in df.columns and not df['Emp_ID'].empty) else 1
        emp_id = st.number_input("Employee ID", value=next_emp_id, step=1, format="%d")
        emp_name = st.text_input("Name")
        age = st.number_input("Age", step=1, format="%d")
        gender_val = st.selectbox("Gender", ["Male","Female","Other"])
        department = st.selectbox("Department", sorted(df['Department'].dropna().unique().tolist())) if 'Department' in df.columns and not df['Department'].dropna().empty else st.text_input("Department")
        role = st.text_input("Role")
        skills = st.text_input("Skills")
        join_date = st.date_input("Join Date")
        status = st.selectbox("Status", ["Active","Resigned"])
        resign_date = st.date_input("Resign Date (if resigned)")
        if status=="Active":
            resign_date = ""
        salary = st.number_input("Salary", step=1000, format="%d")
        location = st.text_input("Location")

        submit = st.form_submit_button("Add Employee")
        if submit:
            new_row = {
                'Emp_ID': int(emp_id),
                'Name': emp_name or "NA",
                'Age': int(age),
                'Gender': gender_val or "NA",
                'Department': department or "NA",
                'Role': role or "NA",
                'Skills': skills or "NA",
                'Join_Date': str(join_date),
                'Resign_Date': str(resign_date) if status == "Resigned" else "",
                'Status': status,
                'Salary': float(salary),
                'Location': location or "NA"
            }
            try:
                db.add_employee(new_row)
                st.success(f"Employee {emp_name} added successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error("Failed to add employee.")
                st.exception(e)

    # --- Export PDF ---
    st.subheader("📄 Export Summary Report")
    if st.button("Download Summary PDF"):
        try:
            pdf_path = "summary_report.pdf"
            generate_summary_pdf(pdf_path, total, active, resigned)
            with open(pdf_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode("utf-8")
                href = f'<a href="data:application/pdf;base64,{base64_pdf}" download="summary_report.pdf">📥 Click here to download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error("Failed to generate PDF.")
            st.exception(e)
