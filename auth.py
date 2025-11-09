import streamlit as st
from utils import database as db
import hashlib

# -------------------------
# Helper: Password hashing
# -------------------------
def hash_password(password: str) -> str:
    """Return SHA256 hash of the password."""
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------
# Login
# -------------------------
def login_user(username: str, password: str) -> bool:
    """
    Attempt to log in a user.
    Returns True if successful, False otherwise.
    Sets session_state with user info.
    """
    try:
        user = db.get_user_by_username(username)
        if not user:
            return False

        stored_hash = user.get("password_hash", "")
        if hash_password(password) == stored_hash:
            st.session_state["logged_in"] = True
            st.session_state["user"] = username
            st.session_state["role"] = user.get("role", "Employee")
            st.session_state["my_emp_id"] = user.get("emp_id", None)
            return True
        else:
            return False
    except Exception as e:
        st.error("Login failed due to error.")
        st.exception(e)
        return False

# -------------------------
# Logout
# -------------------------
def logout_user():
    if st.sidebar.button("Logout"):
        for key in ["logged_in","user","role","my_emp_id"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

# -------------------------
# Require login decorator
# -------------------------
def require_login():
    """
    Call this at the top of any page that requires authentication.
    Shows login form if not logged in.
    """
    if not st.session_state.get("logged_in", False):
        st.warning("Please log in to access this page.")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if login_user(username, password):
                    st.success(f"Welcome, {username}!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid username or password.")
        st.stop()

# -------------------------
# Role badge display
# -------------------------
def show_role_badge():
    if st.session_state.get("logged_in"):
        role = st.session_state.get("role", "Employee")
        username = st.session_state.get("user", "User")
        st.sidebar.markdown(f"**Logged in as:** {username} — **{role}**")
