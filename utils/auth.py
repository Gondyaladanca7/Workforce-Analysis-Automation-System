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
                # no rerun needed; session_state now has login info
            else:
                st.error(msg)
        st.stop()  # stop rendering page until login


# -------------------------
# Logout
# -------------------------
def logout_user():
    # put logout on sidebar
    if st.sidebar.button("Logout"):
        keys = ["logged_in", "user", "role", "user_id", "my_emp_id"]
        for k in keys:
            if k in st.session_state:
                del st.session_state[k]
        st.info("Logged out successfully.")
        st.experimental_set_query_params()  # resets query params, avoids rerun

# -------------------------
# Show role badge
# -------------------------
def show_role_badge():
    role = st.session_state.get("role", "")
    if role:
        st.sidebar.markdown(f"**Role:** {role}")
