import streamlit as st
import datetime
from utils import database as db

st.title("😊 Employee Mood Tracker")

# Fetch employees
try:
    df = db.fetch_employees()
except Exception:
    df = None

# -------------------------
# Select employee
# -------------------------
emp_opts = df["Emp_ID"].astype(str) + " - " + df["Name"] if df is not None else []
emp_choice = st.selectbox("Select Employee", emp_opts)
emp_id = int(emp_choice.split(" - ")[0]) if emp_choice else None

# -------------------------
# Log mood
# -------------------------
mood_choice = st.radio("Today's Mood", ["😊 Happy", "😐 Neutral", "😔 Sad", "😡 Angry"], horizontal=True)
if st.button("Log Mood"):
    if emp_id:
        try:
            db.log_mood(emp_id=emp_id, mood=mood_choice)
            st.success(f"Mood '{mood_choice}' logged for {emp_choice.split(' - ')[1]}")
            st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)

# -------------------------
# View mood history
# -------------------------
st.subheader("Mood History")
try:
    mood_df = db.fetch_mood()
    if not mood_df.empty and df is not None:
        emp_map = df.set_index("Emp_ID")["Name"].to_dict()
        mood_df["Employee"] = mood_df["emp_id"].map(emp_map)
        st.dataframe(mood_df[["Employee", "mood", "log_date"]].sort_values("log_date", ascending=False))
    else:
        st.info("No mood logs yet.")
except Exception as e:
    st.error("Failed to fetch mood history.")
    st.exception(e)
