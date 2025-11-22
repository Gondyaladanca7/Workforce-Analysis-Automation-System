# pages/7_Feedback.py
import streamlit as st
import pandas as pd
import datetime

from utils.auth import require_login, show_role_badge, logout_user
from utils import database as db

def show():
    require_login()
    show_role_badge()
    logout_user()

    role = st.session_state.get("role", "Employee")
    username = st.session_state.get("user", "unknown")

    st.title("💬 Employee Feedback System")

    # Load employees and feedback
    try:
        emp_df = db.fetch_employees()
    except Exception as e:
        st.error("Failed to load employees.")
        st.exception(e)
        emp_df = pd.DataFrame()

    try:
        feedback_df = db.fetch_feedback()
    except Exception as e:
        st.error("Failed to load feedback.")
        st.exception(e)
        feedback_df = pd.DataFrame()

    # -----------------------
    # Add Feedback
    # -----------------------
    st.subheader("➕ Submit Feedback")
    with st.form("add_feedback", clear_on_submit=True):
        receiver_options = (emp_df["Emp_ID"].astype(str) + " - " + emp_df["Name"]).tolist() if not emp_df.empty else []
        receiver = st.selectbox("Select Employee to Give Feedback", receiver_options)
        message = st.text_area("Message")
        rating = st.slider("Rating (1-5)", min_value=1, max_value=5, value=5)
        submit = st.form_submit_button("Submit Feedback")
        if submit:
            if not receiver or not message.strip():
                st.error("Please select a receiver and write a message.")
            else:
                receiver_id = int(receiver.split(" - ")[0])
                sender_user = db.get_user_by_username(username)
                sender_id = sender_user["id"] if sender_user else None
                try:
                    db.add_feedback(sender_id, receiver_id, message.strip(), rating)
                    st.success("Feedback submitted successfully.")
                    st.experimental_rerun()
                except Exception as e:
                    st.error("Failed to submit feedback.")
                    st.exception(e)

    st.markdown("---")

    # -----------------------
    # Search & View Feedback
    # -----------------------
    st.subheader("🔎 View Feedback")
    search_text = st.text_input("Search (message, sender, receiver)").lower().strip()
    feedback_display = feedback_df.copy()

    if not feedback_display.empty and emp_df.shape[0] > 0:
        emp_map = emp_df.set_index("Emp_ID")["Name"].to_dict()
        feedback_display["Sender"] = feedback_display["sender_id"].map(emp_map).fillna(feedback_display["sender_id"].astype(str))
        feedback_display["Receiver"] = feedback_display["receiver_id"].map(emp_map).fillna(feedback_display["receiver_id"].astype(str))

        if search_text:
            mask = (
                feedback_display["message"].str.lower().str.contains(search_text, na=False) |
                feedback_display["Sender"].str.lower().str.contains(search_text, na=False) |
                feedback_display["Receiver"].str.lower().str.contains(search_text, na=False)
            )
            feedback_display = feedback_display[mask]

    st.dataframe(
        feedback_display[["feedback_id","Sender","Receiver","message","rating","log_date"]],
        height=300
    )

    st.markdown("---")

    # -----------------------
    # Edit / Delete Feedback
    # -----------------------
    if not feedback_display.empty:
        st.subheader("✏️ Edit / Delete Feedback")
        feedback_ids = feedback_display["feedback_id"].astype(str).tolist()
        sel_feedback = st.selectbox("Select Feedback ID", feedback_ids)

        if sel_feedback:
            feedback_row = feedback_display[feedback_display["feedback_id"] == int(sel_feedback)].iloc[0].to_dict()
            with st.form("edit_feedback"):
                e_message = st.text_area("Message", value=feedback_row.get("message",""))
                e_rating = st.slider("Rating (1-5)", min_value=1, max_value=5, value=int(feedback_row.get("rating",5)))
                update_btn = st.form_submit_button("Update Feedback")
                delete_btn = st.form_submit_button("Delete Feedback")

                if update_btn:
                    try:
                        db.add_feedback(feedback_row["sender_id"], feedback_row["receiver_id"], e_message.strip(), e_rating)
                        # optional: delete old feedback to simulate update
                        db.delete_feedback(int(sel_feedback))
                        st.success("Feedback updated successfully.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Failed to update feedback.")
                        st.exception(e)

                if delete_btn:
                    try:
                        db.delete_feedback(int(sel_feedback))
                        st.success("Feedback deleted successfully.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error("Failed to delete feedback.")
                        st.exception(e)

    st.markdown("---")

    # -----------------------
    # Feedback Analytics
    # -----------------------
    st.subheader("📊 Feedback Analytics")
    if not feedback_df.empty:
        rating_counts = feedback_df["rating"].value_counts().sort_index()
        st.bar_chart(rating_counts)
    else:
        st.info("No feedback available yet.")

    # -----------------------
    # Upcoming Features / To-Do
    # -----------------------
    st.markdown("🔮 **Upcoming Features / To-Do**")
    st.markdown("""
    - Allow anonymous feedback option.
    - Add monthly/weekly trend analysis.
    - Dashboard-style charts: Top-rated employees, frequent feedback givers.
    - Export feedback reports as PDF/CSV.
    - Integrate feedback with performance reviews & task completion.
    - Enable notifications when new feedback is received.
    """)
