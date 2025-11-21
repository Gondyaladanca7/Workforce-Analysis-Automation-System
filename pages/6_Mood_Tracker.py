# pages/6_Mood_Tracker.py
import streamlit as st
import datetime
import pandas as pd
from utils import database as db

st.set_page_config(page_title="Mood Tracker", page_icon="😊", layout="wide")
st.title("😊 Employee Mood Tracker")

# -------------------------
# Fetch employees
# -------------------------
try:
    employees_df = db.fetch_employees()
except Exception:
    employees_df = pd.DataFrame(columns=["Emp_ID", "Name"])

emp_list = []
if not employees_df.empty:
    emp_list = (employees_df["Emp_ID"].astype(str) + " - " + employees_df["Name"]).tolist()

emp_choice = st.selectbox("Select Employee", options=emp_list)
emp_id = int(emp_choice.split(" - ")[0]) if emp_choice else None

# -------------------------
# Log Mood
# -------------------------
mood_choice = st.radio(
    "Today's Mood", ["😊 Happy", "😐 Neutral", "😔 Sad", "😡 Angry"], horizontal=True
)
remarks = st.text_input("Optional remarks")

if st.button("Log Mood"):
    if emp_id:
        try:
            # FIX: Use correct datetime for log
            log_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.add_mood_entry(emp_id=emp_id, mood=mood_choice, remarks=remarks or "")
            st.success(f"Mood '{mood_choice}' logged for {emp_choice.split(' - ')[1]}")
            st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)
    else:
        st.warning("Select an employee first.")

# -------------------------
# View Mood History
# -------------------------
st.subheader("Mood History")
try:
    mood_df = db.fetch_mood_logs()
    if not mood_df.empty and not employees_df.empty:
        emp_map = employees_df.set_index("Emp_ID")["Name"].to_dict()
        mood_df["Employee"] = mood_df["emp_id"].map(emp_map).fillna(mood_df["emp_id"].astype(str))
        mood_df["log_date_parsed"] = pd.to_datetime(mood_df["log_date"], errors="coerce")
        st.dataframe(
            mood_df[["Employee", "mood", "remarks", "log_date_parsed"]]
            .sort_values("log_date_parsed", ascending=False)
            .rename(columns={"log_date_parsed": "log_date"}),
            height=360
        )
    else:
        st.info("No mood logs yet.")
except Exception as e:
    st.error("Failed to fetch mood history.")
    st.exception(e)
