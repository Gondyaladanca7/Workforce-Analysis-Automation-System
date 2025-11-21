# pages/7_💬_Feedback.py
import streamlit as st
import pandas as pd
from utils import database as db
from utils.auth import require_login
from utils.analytics import feedback_summary
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
st.set_page_config(page_title="💬 Feedback", page_icon="💬", layout="wide")

# -------------------------
# Access Control
# -------------------------
require_login()
role = st.session_state.get("role", "")
username = st.session_state.get("user", "Unknown")
emp_id = st.session_state.get("my_emp_id", None)

st.title("💬 Employee Feedback System")

# -------------------------
# Fetch employees
# -------------------------
try:
    df_employees = db.fetch_employees()
except Exception:
    df_employees = pd.DataFrame(columns=["Emp_ID", "Name"])

# -------------------------
# Feedback Submission (Employee)
# -------------------------
if role == "Employee":
    st.header("1️⃣ Submit Feedback")

    if not df_employees.empty:
        emp_opts = df_employees[df_employees["Emp_ID"] != emp_id]["Emp_ID"].astype(str) + " - " + df_employees["Name"]
        receiver_choice = st.selectbox("Select Employee to Give Feedback", emp_opts)
        receiver_id = int(receiver_choice.split(" - ")[0]) if receiver_choice else None
    else:
        st.info("No other employees available.")
        receiver_id = None

    feedback_msg = st.text_area("Feedback Message")
    rating = st.slider("Rating (1-5)", min_value=1, max_value=5, value=3)
    submit_btn = st.button("Submit Feedback")

    if submit_btn:
        if receiver_id and feedback_msg.strip():
            try:
                db.add_feedback(sender_id=emp_id, receiver_id=receiver_id,
                                message=feedback_msg.strip(), rating=rating)
                st.success("✅ Feedback submitted successfully!")
                st.session_state["refresh_trigger"] = not st.session_state.get("refresh_trigger", False)
            except Exception as e:
                st.error("❌ Failed to submit feedback.")
                st.exception(e)
        else:
            st.warning("⚠️ Select an employee and write a feedback message.")

st.markdown("---")

# -------------------------
# Feedback Analytics (Admin/Manager)
# -------------------------
if role in ["Admin", "Manager"]:
    st.header("📊 Feedback Analytics")

    try:
        feedback_df = db.fetch_feedback()
        if not feedback_df.empty and not df_employees.empty:
            emp_map = df_employees.set_index("Emp_ID")["Name"].to_dict()
            feedback_df["Sender"] = feedback_df["sender_id"].map(emp_map).fillna(feedback_df["sender_id"].astype(str))
            feedback_df["Receiver"] = feedback_df["receiver_id"].map(emp_map).fillna(feedback_df["receiver_id"].astype(str))

            # Filters
            st.subheader("🔍 Filter Feedback")
            sender_filter = st.selectbox("Filter by Sender", ["All"] + sorted(feedback_df["Sender"].unique()))
            receiver_filter = st.selectbox("Filter by Receiver", ["All"] + sorted(feedback_df["Receiver"].unique()))
            rating_filter = st.selectbox("Filter by Rating", ["All", 1, 2, 3, 4, 5])

            filtered_df = feedback_df.copy()
            if sender_filter != "All":
                filtered_df = filtered_df[filtered_df["Sender"] == sender_filter]
            if receiver_filter != "All":
                filtered_df = filtered_df[filtered_df["Receiver"] == receiver_filter]
            if rating_filter != "All":
                filtered_df = filtered_df[filtered_df["rating"] == rating_filter]

            # Feedback table
            st.subheader("📋 Feedback Entries")
            st.dataframe(filtered_df[["Sender", "Receiver", "message", "rating", "log_date"]]
                         .sort_values(by="log_date", ascending=False), height=400)

            # -------------------------
            # Analytics Charts
            # -------------------------
            st.markdown("---")
            st.subheader("⭐ Average Rating per Employee")
            avg_rating = feedback_df.groupby("Receiver")["rating"].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(6,4))
            ax.barh(avg_rating.index, avg_rating.values, color=sns.color_palette("pastel"))
            ax.set_xlabel("Average Rating")
            ax.set_ylabel("Employee")
            st.pyplot(fig)

            st.subheader("📊 Rating Distribution")
            rating_counts = feedback_df["rating"].value_counts().sort_index()
            fig2, ax2 = plt.subplots(figsize=(6,4))
            ax2.bar(rating_counts.index.astype(str), rating_counts.values, color=sns.color_palette("pastel"))
            ax2.set_xlabel("Rating")
            ax2.set_ylabel("Count")
            st.pyplot(fig2)

            # Optional: Summary Table
            st.subheader("📈 Summary Table")
            summary_df = feedback_summary(feedback_df, df_employees)
            st.dataframe(summary_df.sort_values(by="Avg_Rating", ascending=False), height=300)

        else:
            st.info("No feedback available yet.")

    except Exception as e:
        st.error("Failed to fetch feedback.")
        st.exception(e)

# -------------------------
# Future Features / To-Do
# -------------------------
st.markdown("---")
st.header("🔮 Upcoming Features / To-Do")
st.markdown("""
- Allow **anonymous feedback** option.  
- Add **monthly/weekly trend analysis**.  
- Dashboard-style charts: Top-rated employees, frequent feedback givers.  
- Export feedback reports as **PDF/CSV**.  
- Integrate feedback with **performance reviews & task completion**.  
- Enable **notifications** when new feedback is received.
""")
