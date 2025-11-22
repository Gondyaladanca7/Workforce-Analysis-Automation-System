import streamlit as st
import pandas as pd
import datetime

from utils.auth import require_login, show_role_badge, logout_user
from utils import database as db

def show():
    require_login()
    show_role_badge()
    logout_user()

    role = st.session_state.get("role", "Employee")
    if role not in ("Admin", "Manager"):
        st.warning("Access denied. Admin/Manager only.")
        st.stop()

    st.title("🧾 Employee Management (CRUD)")

    # Load employees
    try:
        df = db.fetch_employees()
    except Exception as e:
        st.error("Failed to load employee data.")
        st.exception(e)
        df = pd.DataFrame()

    # -----------------------
    # Add new employee
    # -----------------------
    st.subheader("➕ Add New Employee")
    with st.form("add_emp", clear_on_submit=True):
        col1, col2 = st.columns(2)
        name = col1.text_input("Full Name")
        age = col2.number_input("Age", min_value=18, max_value=100, value=25, step=1)
        gender = col1.selectbox("Gender", ["Male", "Female", "Other"])
        dept = col2.text_input("Department")
        role_in = col1.text_input("Role / Title")
        skills = col2.text_input("Skills (comma separated)")
        join_date = col1.date_input("Join Date", value=datetime.date.today())
        status = col2.selectbox("Status", ["Active", "Resigned"])
        salary = col1.number_input("Salary", min_value=0.0, step=500.0, format="%.2f")
        location = col2.text_input("Location")

        submitted = st.form_submit_button("Add Employee")
        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                emp = {
                    "Name": name.strip(),
                    "Age": int(age),
                    "Gender": gender,
                    "Department": dept or "NA",
                    "Role": role_in or "NA",
                    "Skills": skills or "",
                    "Join_Date": join_date.strftime("%Y-%m-%d"),
                    "Resign_Date": "" if status == "Active" else join_date.strftime("%Y-%m-%d"),
                    "Status": status,
                    "Salary": float(salary),
                    "Location": location or ""
                }
                try:
                    db.add_employee(emp)
                    st.success(f"Employee '{name}' added.")
                    st.session_state["refresh_flag"] = True
                    st.experimental_rerun()
                except Exception as e:
                    st.error("Failed to add employee.")
                    st.exception(e)

    st.markdown("---")

    # -----------------------
    # Edit employee
    # -----------------------
    st.subheader("✏️ Edit Employee")
    if df.empty:
        st.info("No employees to edit.")
    else:
        options = (df["Emp_ID"].astype(str) + " - " + df["Name"]).tolist()
        sel = st.selectbox("Select employee to edit", options)
        if sel:
            emp_id = int(sel.split(" - ")[0])
            emp_row = df[df["Emp_ID"] == emp_id].iloc[0].to_dict()

            with st.form("edit_emp"):
                col1, col2 = st.columns(2)
                e_name = col1.text_input("Full Name", value=emp_row.get("Name", ""))
                e_age = col2.number_input("Age", min_value=18, max_value=100,
                                          value=int(emp_row.get("Age") or 25), step=1)
                e_gender = col1.selectbox("Gender", ["Male","Female","Other"],
                                          index=0 if emp_row.get("Gender","Male")=="Male" else 1)
                e_dept = col2.text_input("Department", value=emp_row.get("Department",""))
                e_role = col1.text_input("Role / Title", value=emp_row.get("Role",""))
                e_skills = col2.text_input("Skills (comma separated)", value=emp_row.get("Skills",""))
                e_join = col1.date_input("Join Date",
                                         value=pd.to_datetime(emp_row.get("Join_Date", datetime.date.today())).date())
                e_status = col2.selectbox("Status", ["Active","Resigned"],
                                          index=0 if emp_row.get("Status","Active")=="Active" else 1)
                e_salary = col1.number_input("Salary", min_value=0.0,
                                             value=float(emp_row.get("Salary") or 0.0), step=500.0)
                e_location = col2.text_input("Location", value=emp_row.get("Location",""))

                updated = st.form_submit_button("Save changes")
                if updated:
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
                    try:
                        db.update_employee(emp_id, updates)
                        st.success("Employee updated.")
                        st.session_state["refresh_flag"] = True
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Failed to update employee.")
                        st.exception(e)

    st.markdown("---")

    # -----------------------
    # Delete employee
    # -----------------------
    st.subheader("🗑️ Delete Employee")
    if df.empty:
        st.info("No employees to delete.")
    else:
        del_sel = st.selectbox("Select employee to delete", options, key="del_emp_select")
        if del_sel:
            del_id = int(del_sel.split(" - ")[0])
            if st.button("Delete Employee"):
                try:
                    db.delete_employee(del_id)
                    st.success(f"Employee {del_sel} deleted.")
                    st.session_state["refresh_flag"] = True
                    st.experimental_rerun()
                except Exception as e:
                    st.error("Failed to delete employee.")
                    st.exception(e)

    st.markdown("---")

    # -----------------------
    # Quick search / table view
    # -----------------------
    st.subheader("🔎 Search / View Employees")
    q = st.text_input("Search (name, role, department, skills)")
    view_df = df.copy()
    if q:
        ql = q.lower().strip()
        mask = (
            view_df["Name"].astype(str).str.lower().str.contains(ql, na=False) |
            view_df["Role"].astype(str).str.lower().str.contains(ql, na=False) |
            view_df["Department"].astype(str).str.lower().str.contains(ql, na=False) |
            view_df["Skills"].astype(str).str.lower().str.contains(ql, na=False)
        )
        view_df = view_df[mask]
    st.dataframe(view_df.reset_index(drop=True), height=360)
