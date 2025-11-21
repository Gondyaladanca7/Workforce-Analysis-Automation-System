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
require_login()
role = st.session_state.get("role", "")
username = st.session_state.get("user", "Unknown")
emp_id = st.session_state.get("my_emp_id", None)

st.title("💬 Employee Feedback System")

# -------------------------
# Fetch employees
try:
    df_employees = db.fetch_employees()
except Exception:
    df_employees = pd.DataFrame(columns=["Emp_ID", "Name"])

# -------------------------
# Feedback Submission (Employee)
if role == "Employee":
    st.header("1️⃣ Submit Feedback")
    emp_opts = df_employees[df_employees["Emp_ID"] != emp_id]["Emp_ID"].astype(str) + " - " + df_employees["Name"] if not df_employees.empty else []
    emp_choice = st.selectbox("Select Employee to Give Feedback", emp_opts)
    receiver_id = int(emp_choice.split(" - ")[0]) if emp_choice else None

    feedback_msg = st.text_area("Feedback Message")
    rating = st.slider("Rating (1-5)", min_value=1, max_value=5, value=3)

    if st.button("Submit Feedback"):
        if receiver_id and feedback_msg.strip():
            try:
                db.add_feedback(sender_id=emp_id,
                                receiver_id=receiver_id,
                                message=feedback_msg.strip(),
                                rating=rating)
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
if role in ["Admin", "Manager"]:
    st.header("2️⃣ Feedback Analytics")
    try:
        feedback_df = db.fetch_feedback()
        if not feedback_df.empty and not df_employees.empty:
            emp_map = df_employees.set_index("Emp_ID")["Name"].to_dict()
            feedback_df["Receiver_Name"] = feedback_df["receiver_id"].map(emp_map)
            feedback_df["Sender_Name"] = feedback_df["sender_id"].map(emp_map)

            # Average rating per employee
            summary_df = feedback_summary(feedback_df, df_employees)
            st.subheader("⭐ Average Rating per Employee")
            st.dataframe(summary_df.sort_values(by="Avg_Rating", ascending=False), height=300)

            # Detailed Feedback Table
            st.subheader("📋 All Feedback Entries")
            st.dataframe(feedback_df[["Sender_Name","Receiver_Name","message","rating","log_date"]]
                         .sort_values(by="log_date", ascending=False), height=400)

            # Analytics Charts
            st.subheader("📊 Rating Distribution")
            rating_counts = feedback_df["rating"].value_counts().sort_index()
            fig, ax = plt.subplots(figsize=(6,4))
            ax.bar(rating_counts.index.astype(str), rating_counts.values, color=sns.color_palette("pastel"))
            ax.set_xlabel("Rating")
            ax.set_ylabel("Count")
            st.pyplot(fig)

        else:
            st.info("No feedback available yet.")
    except Exception as e:
        st.error("❌ Failed to fetch feedback.")
        st.exception(e)

# -------------------------
# Future Features (Placeholder)
st.markdown("---")
st.header("🔮 Upcoming Features / To-Do")
st.markdown("""
- Filter feedback by **Department**, **Role**, or **Date range**  
- Visualize **feedback trends** over time (charts/graphs)  
- Feedback **alerts** for low-rated employees or tasks  
- Export feedback analytics to **PDF/CSV**  
- Dashboard-style charts for top-rated employees & frequent feedback givers  
- Integrate feedback with performance reviews & task completion  
- Enable notifications when new feedback is received
""")
