# utils/auth.py
import streamlit as st
from utils import database as db

# -------------------------
# Login
# -------------------------
def login(username: str, password: str):
    try:
        user = db.get_user_by_username(username)
    except Exception as e:
        return False, f"DB error: {e}"

    if not user:
        return False, "User not found"

    hashed_input = db.hash_password(password)
    stored_hash = user.get("password")
    if hashed_input != stored_hash:
        return False, "Invalid password"

    # store session info
    st.session_state["logged_in"] = True
    st.session_state["user"] = user["username"]
    st.session_state["role"] = user["role"]
    st.session_state["user_id"] = user["id"]

    # map username to Emp_ID if present (optional)
    try:
        employees = db.fetch_employees()
        emp_row = employees[employees["Name"] == username]
        if not emp_row.empty:
            st.session_state["my_emp_id"] = int(emp_row.iloc[0]["Emp_ID"])
        else:
            # keep previous mapping if set, else None
            st.session_state.setdefault("my_emp_id", None)
    except Exception:
        st.session_state.setdefault("my_emp_id", None)

    return True, "Login successful"

# -------------------------
# Require login (used at top of pages)
# -------------------------
def require_login():
    if not st.session_state.get("logged_in", False):
        st.warning("⚠️ Please login to continue.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, msg = login(username, password)
            if success:
                st.success(msg)
                # rerun to load page with session set
                st.rerun()
            else:
                st.error(msg)
        st.stop()

# -------------------------
# Logout
# -------------------------
def logout_user():
    # put logout on sidebar to be consistent with app layout
    if st.sidebar.button("Logout"):
        for key in ["logged_in", "user", "role", "user_id", "my_emp_id"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

# -------------------------
# Show role badge
# -------------------------
def show_role_badge():
    role = st.session_state.get("role", "")
    if role:
        st.sidebar.markdown(f"**Role:** {role}")
