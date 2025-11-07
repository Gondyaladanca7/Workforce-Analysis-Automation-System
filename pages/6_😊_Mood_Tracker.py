# pages/6_😊_Mood_Tracker.py
import streamlit as st
import pandas as pd
from datetime import date
from utils import database as db

st.set_page_config(page_title="Mood Tracker", page_icon="😊", layout="wide")
st.title("😊 Employee Mood Tracker")

# Fetch data
employees_df = db.fetch_employees()
mood_df = db.fetch_mood_logs()

# -------------------------
# Log Mood
st.header("➕ Log Your Mood")
with st.form("mood_form"):
    employee_name = st.selectbox("Select Employee", employees_df["Name"].tolist())
    mood = st.selectbox("Mood", ["Happy", "Neutral", "Sad", "Angry"])
    log_date = st.date_input("Date", value=date.today())
    submit = st.form_submit_button("Log Mood")
    
    if submit:
        emp_id = int(employees_df[employees_df["Name"]==employee_name]["Emp_ID"].values[0])
        db.add_mood_entry(emp_id=emp_id, mood=mood, log_date=str(log_date))
        st.success(f"Mood '{mood}' logged for {employee_name}")
        st.experimental_rerun()

# -------------------------
# View Mood Logs
st.header("📊 Mood Logs Overview")
if not mood_df.empty:
    mood_summary = mood_df.groupby(["log_date","mood"]).size().unstack(fill_value=0)
    st.bar_chart(mood_summary)
else:
    st.info("No mood logs yet.")
