# auth.py
import streamlit as st

# Example credentials (replace with your DB or secure method)
CREDENTIALS = {
    "admin": {"password": "admin123", "role": "Admin"},
    "manager": {"password": "manager123", "role": "Manager"},
    "employee": {"password": "employee123", "role": "Employee"}
}

# -------------------------
# Initialize triggers
# -------------------------
if "login_trigger" not in st.session_state:
    st.session_state["login_trigger"] = False

if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# -------------------------
# Login Function
# -------------------------
def login_user():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_btn = st.button("Login")
    
    if login_btn:
        user = CREDENTIALS.get(username)
        if user and user["password"] == password:
            st.session_state["user"] = username
            st.session_state["role"] = user["role"]
            st.session_state["login_trigger"] = not st.session_state["login_trigger"]
            st.success(f"Logged in as {username} ({user['role']})")
        else:
            st.error("Invalid credentials")

# -------------------------
# Logout Function
# -------------------------
def logout_user():
    if st.session_state.get("user"):
        if st.button("Logout"):
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.session_state["login_trigger"] = not st.session_state["login_trigger"]
            st.info("Logged out")

# -------------------------
# Require Login
# -------------------------
def require_login():
    if not st.session_state.get("user"):
        login_user()
        st.stop()

# -------------------------
# Display role badge
# -------------------------
def show_role_badge():
    role = st.session_state.get("role")
    if role:
        st.sidebar.markdown(f"**Role:** {role}")
