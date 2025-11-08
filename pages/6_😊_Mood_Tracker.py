# pages/6_😊_Mood_Tracker.py
import streamlit as st
import datetime
import pandas as pd
from utils import database as db

st.title("😊 Employee Mood Tracker")

# Fetch employees
try:
    df = db.fetch_employees()
except Exception:
    df = pd.DataFrame(columns=["Emp_ID","Name"])

# Select employee
emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"] if not df.empty else []
emp_choice = st.selectbox("Select Employee", emp_opts)
emp_id = int(emp_choice.split(" - ")[0]) if emp_choice else None

# Log mood
mood_choice = st.radio("Today's Mood", ["😊 Happy","😐 Neutral","😔 Sad","😡 Angry"], horizontal=True)
remarks = st.text_input("Optional remarks")
if st.button("Log Mood"):
    if emp_id:
        try:
            db.add_mood_entry(emp_id=emp_id, mood=mood_choice, remarks=remarks or "")
            st.success(f"Mood '{mood_choice}' logged for {emp_choice.split(' - ')[1]}")
            st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)
    else:
        st.warning("Select an employee first.")

# View mood history
st.subheader("Mood History")
try:
    mood_df = db.fetch_mood_logs()
    if not mood_df.empty and not df.empty:
        emp_map = df.set_index("Emp_ID")["Name"].to_dict()
        mood_df["Employee"] = mood_df["emp_id"].map(emp_map).fillna(mood_df["emp_id"].astype(str))
        mood_df["log_date_parsed"] = pd.to_datetime(mood_df["log_date"], errors="coerce")
        st.dataframe(mood_df[["Employee","mood","remarks","log_date_parsed"]].sort_values("log_date_parsed", ascending=False).rename(columns={"log_date_parsed":"log_date"}), height=360)
    else:
        st.info("No mood logs yet.")
except Exception as e:
    st.error("Failed to fetch mood history.")
    st.exception(e)
