# auth.py
"""
Authentication and Role-based Access Control
"""

import streamlit as st
import bcrypt

# -------------------------
# Predefined users
# Passwords stored in plaintext for simplicity (replace with hashed in production)
USERS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "manager": {"password": "manager123", "role": "Manager"},
    "employee": {"password": "employee123", "role": "Employee"},
}

# -------------------------
# Password hashing functions
def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)

# -------------------------
# Login / Logout
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
            st.experimental_rerun()
        else:
            st.error("Invalid credentials. Please try again.")

def logout_user():
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.experimental_rerun()

# -------------------------
# Require login decorator
def require_login(func):
    """
    Decorator to protect pages: user must be logged in
    """
    def wrapper(*args, **kwargs):
        if "logged_in" not in st.session_state or not st.session_state.logged_in:
            login_user()
            st.stop()
        return func(*args, **kwargs)
    return wrapper

# -------------------------
# Sidebar Role Badge
def show_role_badge():
    """Show logged-in user and role in sidebar"""
    if "username" in st.session_state and "role" in st.session_state:
        st.sidebar.info(f"👤 Logged in as: **{st.session_state.username.title()} ({st.session_state.role})**")
