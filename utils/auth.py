import streamlit as st
from utils.database import get_user_by_username, hash_password

# -------------------------
# Login
# -------------------------
def login(username, password):
    user = get_user_by_username(username)
    if not user:
        return False, "User not found"

    if hash_password(password) == user["password"]:
        st.session_state["logged_in"] = True
        st.session_state["user"] = user["username"]
        st.session_state["role"] = user["role"]
        st.session_state["user_id"] = user["id"]
        # Trigger refresh after login
        st.session_state["login_trigger"] = not st.session_state.get("login_trigger", False)
        return True, "Login successful"
    return False, "Invalid password"

# -------------------------
# Require login
# -------------------------
def require_login():
    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        st.warning("⚠️ Please login to access this page.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            success, msg = login(username, password)
            if success:
                st.success(msg)
                # Stop script to refresh with new session state
                st.stop()
            else:
                st.error(msg)
        st.stop()

# -------------------------
# Logout
# -------------------------
def logout_user():
    if st.sidebar.button("Logout"):
        for key in ["logged_in","user","role","user_id","my_emp_id","login_trigger"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun_safe()

# -------------------------
# Safe rerun replacement
# -------------------------
def st_experimental_rerun_safe():
    # Streamlit newer versions: just stop, reload occurs naturally
    st.stop()

# -------------------------
# Show role badge
# -------------------------
def show_role_badge():
    role = st.session_state.get("role", "Employee")
    st.sidebar.markdown(f"**Role:** {role}")
