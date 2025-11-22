import streamlit as st
import pandas as pd
import plotly.express as px

from utils.auth import require_login, show_role_badge, logout_user
from utils import database as db


def show():
    require_login()
    show_role_badge()
    logout_user()

    st.title("📊 Mood Analytics Dashboard")

    # Load mood data
    try:
        mood_df = db.fetch_mood()
    except Exception as e:
        st.error("Failed to load mood data.")
        st.exception(e)
        return

    if mood_df.empty:
        st.info("No mood entries available to analyze.")
        return

    # Convert date column
    mood_df["date"] = pd.to_datetime(mood_df["date"], errors="coerce")

    st.markdown("### 📅 Mood Trend Over Time")
    trend_fig = px.line(
        mood_df,
        x="date",
        y="mood",
        markers=True,
        title="Mood Trend Over Time",
    )
    st.plotly_chart(trend_fig, use_container_width=True)

    st.markdown("### 📊 Mood Distribution")
    dist_fig = px.histogram(
        mood_df,
        x="mood",
        nbins=10,
        title="Mood Distribution",
    )
    st.plotly_chart(dist_fig, use_container_width=True)

    st.markdown("### 🧍 Employee-wise Mood Comparison")
    box_fig = px.box(
        mood_df,
        x="username",
        y="mood",
        title="Mood Comparison by Employee",
    )
    st.plotly_chart(box_fig, use_container_width=True)

    st.markdown("---")

    st.markdown("### 🔍 Filter Mood Data")
    users = sorted(mood_df["username"].unique().tolist())
    selected_user = st.selectbox("Select Employee", ["All"] + users)

    if selected_user != "All":
        filtered_df = mood_df[mood_df["username"] == selected_user]
    else:
        filtered_df = mood_df.copy()

    st.dataframe(filtered_df.reset_index(drop=True), height=300)
