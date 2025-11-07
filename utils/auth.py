# auth.py
"""
Handles authentication and role-based access control
"""

import streamlit as st
import bcrypt

# ------------------------- Predefined user roles
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "manager": {"password": "manager123", "role": "Manager"},
    "employee": {"password": "employee123", "role": "Employee"},
}

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)

def login_user():
    st.title("🔐 Login — Workforce Analysis Automation System")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USERS and password == USERS[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = USERS[username]["role"]
            st.success(f"Welcome, {username.title()} ({st.session_state.role}) 🎉")
            st.rerun()  # modern Streamlit rerun (no experimental)
        else:
            st.error("Invalid credentials. Please try again.")

def logout_user():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

def require_login():
    """If not logged in, show login page"""
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        login_user()
        st.stop()

def show_role_badge():
    """Show role indicator in sidebar"""
    if "role" in st.session_state:
        st.sidebar.info(f"👤 Logged in as: **{st.session_state.username.title()} ({st.session_state.role})**")
