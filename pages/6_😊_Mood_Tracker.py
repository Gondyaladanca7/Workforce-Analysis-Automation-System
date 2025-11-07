# pages/6_😊_Mood_Tracker.py
import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from utils import database as db

st.set_page_config(page_title="Mood Tracker", page_icon="😊", layout="wide")
sns.set_style("whitegrid")

# -------------------------
# Session state trigger
# -------------------------
if "mood_refresh" not in st.session_state:
    st.session_state["mood_refresh"] = False

# -------------------------
# Load employee data
# -------------------------
try:
    employees = db.fetch_employees()
except Exception as e:
    st.error("Failed to load employees from DB.")
    st.exception(e)
    employees = pd.DataFrame(columns=["Emp_ID","Name"])

role = st.session_state.get("role", "Employee")
username = st.session_state.get("user", "unknown")

# -------------------------
# Select Employee for Mood
# -------------------------
st.header("Employee Mood Tracker")

if role in ("Admin", "Manager"):
    emp_opts = employees["Emp_ID"].astype(str) + " - " + employees["Name"]
    sel_emp = st.selectbox("Select Employee to Log Mood", emp_opts) if not employees.empty else None
    emp_id = int(sel_emp.split(" - ")[0]) if sel_emp else None
elif role == "Employee":
    emp_id = st.session_state.get("my_emp_id", None)
    if emp_id is None:
        st.warning("Please select your Emp_ID in the Tasks section first.")
        emp_opts = employees["Emp_ID"].astype(str) + " - " + employees["Name"] if not employees.empty else []
        emp_choice = st.selectbox("Select your Emp_ID (one-time)", emp_opts)
        if emp_choice:
            emp_id = int(emp_choice.split(" - ")[0])
            st.session_state["my_emp_id"] = emp_id

# -------------------------
# Log Mood Entry
# -------------------------
if emp_id:
    mood_choice = st.radio("How are you feeling today?", ["😊 Happy","😐 Neutral","😔 Sad","😡 Angry"], horizontal=True)
    if st.button("Log Mood"):
        try:
            db.log_mood(emp_id, mood_choice)
            st.success(f"Mood '{mood_choice}' logged for {employees.loc[employees['Emp_ID']==emp_id,'Name'].values[0]}")
            st.session_state["mood_refresh"] = not st.session_state["mood_refresh"]
        except Exception as e:
            st.error("Failed to log mood.")
            st.exception(e)

# -------------------------
# Display Mood History
# -------------------------
st.subheader("Mood History")

try:
    if role == "Employee":
        mood_df = db.fetch_mood(emp_id=emp_id)
    else:
        mood_df = db.fetch_mood()
except Exception as e:
    st.error("Failed to fetch mood logs.")
    st.exception(e)
    mood_df = pd.DataFrame(columns=["mood_id","emp_id","mood","log_date"])

if not mood_df.empty:
    # Merge with employee names
    mood_df = pd.merge(mood_df, employees[["Emp_ID","Name"]], left_on="emp_id", right_on="Emp_ID", how="left")
    mood_display = mood_df[["emp_id","Name","mood","log_date"]].sort_values(by="log_date", ascending=False)
    st.dataframe(mood_display, height=300)

    # Mood Analytics
    mood_label_map = {"😊 Happy":"Happy","😐 Neutral":"Neutral","😔 Sad":"Sad","😡 Angry":"Angry"}
    mood_score_map = {"Happy":5,"Neutral":3,"Sad":2,"Angry":1}
    mood_df["Mood_Label"] = mood_df["mood"].replace(mood_label_map)
    mood_df["Mood_Score"] = mood_df["Mood_Label"].map(mood_score_map)

    st.subheader("Average Mood per Employee")
    avg_mood = mood_df.groupby("Name")["Mood_Score"].mean().round().astype(int).sort_values()
    if not avg_mood.empty:
        fig, ax = plt.subplots(figsize=(6,3))
        sns.barplot(x=avg_mood.values, y=avg_mood.index, palette="coolwarm", ax=ax)
        for i, v in enumerate(avg_mood.values):
            ax.text(v+0.1, i, str(v), color="black", va="center")
        ax.set_xlabel("Average Mood Score")
        ax.set_ylabel("Employee")
        ax.set_title("Mood Analytics")
        st.pyplot(fig)

    st.subheader("Overall Mood Distribution")
    mood_counts = mood_df["Mood_Label"].value_counts()
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(mood_counts, labels=[f"{lab} ({cnt})" for lab,cnt in zip(mood_counts.index, mood_counts.values)], startangle=90, colors=sns.color_palette("Set2"))
    ax.set_title("Team Mood")
    st.pyplot(fig)

    st.subheader("Mood Trend Over Time")
    fig, ax = plt.subplots(figsize=(8,3))
    for name, group in mood_df.groupby("Name"):
        group_sorted = group.sort_values("log_date")
        ax.plot(group_sorted["log_date"], group_sorted["Mood_Score"], marker="o", label=name)
    ax.set_xlabel("Date")
    ax.set_ylabel("Mood Score")
    ax.set_ylim(0,5.5)
    ax.legend(fontsize=6)
    plt.xticks(rotation=45)
    st.pyplot(fig)
else:
    st.info("No mood logs yet.")
