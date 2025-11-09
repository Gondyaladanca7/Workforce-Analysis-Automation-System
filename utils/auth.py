# utils/auth.py
import streamlit as st
from utils import database as db
from hashlib import sha256

# -------------------------
# Password hashing
# -------------------------
def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()

# -------------------------
# Login
# -------------------------
def login_user(username: str, password: str) -> bool:
    try:
        user = db.get_user_by_username(username)
        if user and user["password"] == hash_password(password):
            st.session_state["user"] = username
            st.session_state["role"] = user["role"]
            return True
        else:
            return False
    except Exception as e:
        st.error(f"Login failed due to error: {e}")
        return False

# -------------------------
# Logout
# -------------------------
def logout_user():
    if st.sidebar.button("Logout"):
        for key in ["user", "role"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()


# -------------------------
# Require login decorator
# -------------------------
def require_login():
    if "user" not in st.session_state:
        st.warning("Please login to continue.")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
        st.stop()

# -------------------------
# Show role badge
# -------------------------
def show_role_badge():
    role = st.session_state.get("role", "")
    if role:
        st.sidebar.markdown(f"**Role:** {role}")
