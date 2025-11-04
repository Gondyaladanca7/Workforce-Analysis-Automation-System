from fpdf import FPDF
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from utils import database as db

sns.set_style("whitegrid")

def fig_to_image_bytes(fig):
    buf = BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    return buf

def generate_summary_pdf(pdf_path: str, total: int, active: int, resigned: int, df: pd.DataFrame):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Workforce Summary Report", ln=True, align="C")
    pdf.ln(5)

    # Employee summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Total Employees: {total}", ln=True)
    pdf.cell(0, 8, f"Active Employees: {active}", ln=True)
    pdf.cell(0, 8, f"Resigned Employees: {resigned}", ln=True)
    pdf.ln(5)

    # Department distribution
    if not df.empty and "Department" in df.columns:
        dept_counts = df['Department'].value_counts()
        fig, ax = plt.subplots(figsize=(6,3))
        sns.barplot(x=dept_counts.index, y=dept_counts.values, palette="viridis", ax=ax)
        ax.set_ylabel("Employees")
        ax.set_xlabel("Department")
        ax.set_title("Employees per Department")
        img_buf = fig_to_image_bytes(fig)
        pdf.image(img_buf, x=15, w=180)
        pdf.ln(5)

    # Gender ratio
    if not df.empty and "Gender" in df.columns:
        gender_counts = df['Gender'].value_counts()
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=90, colors=sns.color_palette("pastel"))
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig.gca().add_artist(centre_circle)
        ax.set_title("Gender Ratio")
        img_buf = fig_to_image_bytes(fig)
        pdf.image(img_buf, x=50, w=100)
        pdf.ln(5)

    # Average salary by department
    if not df.empty and "Salary" in df.columns and "Department" in df.columns:
        avg_salary = df.groupby("Department")["Salary"].mean().sort_values()
        fig, ax = plt.subplots(figsize=(6,3))
        sns.barplot(x=avg_salary.values, y=avg_salary.index, palette="magma", ax=ax)
        ax.set_xlabel("Average Salary")
        ax.set_ylabel("Department")
        ax.set_title("Average Salary by Department")
        img_buf = fig_to_image_bytes(fig)
        pdf.image(img_buf, x=15, w=180)
        pdf.ln(5)

    # Mood Analytics
    mood_df = db.fetch_mood_logs()
    if not mood_df.empty:
        merged = pd.merge(mood_df, df[["Emp_ID","Name"]], left_on="emp_id", right_on="Emp_ID", how="left")
        merged['Mood_Label'] = merged['mood'].replace({
            "😊 Happy":"Happy","😐 Neutral":"Neutral","😔 Sad":"Sad","😡 Angry":"Angry"
        })
        # Set integer values
        mood_score_map = {"Happy":5,"Neutral":3,"Sad":2,"Angry":1}
        merged['Mood_Score'] = merged['Mood_Label'].map(mood_score_map)

        # Average mood per employee
        avg_mood = merged.groupby("Name")["Mood_Score"].mean().round().astype(int).sort_values()
        fig, ax = plt.subplots(figsize=(6,3))
        sns.barplot(x=avg_mood.values, y=avg_mood.index, palette="coolwarm", ax=ax)
        for i, v in enumerate(avg_mood.values):
            ax.text(v+0.1, i, str(v), color='black', va='center')
        ax.set_xlabel("Average Mood Score (1-5)")
        ax.set_ylabel("Employee")
        ax.set_title("Average Mood per Employee")
        img_buf = fig_to_image_bytes(fig)
        pdf.image(img_buf, x=15, w=180)
        pdf.ln(5)

        # Overall mood distribution
        mood_counts = merged['Mood_Label'].value_counts()
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(mood_counts, labels=mood_counts.index, autopct="%1.0f%%", startangle=90, colors=sns.color_palette("Set2"))
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig.gca().add_artist(centre_circle)
        ax.set_title("Overall Team Mood")
        img_buf = fig_to_image_bytes(fig)
        pdf.image(img_buf, x=50, w=100)
        pdf.ln(5)

        # Mood trend over time
        fig, ax = plt.subplots(figsize=(6,3))
        for name, group in merged.groupby("Name"):
            group_sorted = group.sort_values(by="log_date")
            ax.plot(group_sorted["log_date"], group_sorted["Mood_Score"], marker='o', label=name)
        ax.set_xlabel("Date")
        ax.set_ylabel("Mood Score (1-5)")
        ax.set_title("Mood Trend Over Time")
        ax.legend(fontsize=6)
        plt.xticks(rotation=45)
        img_buf = fig_to_image_bytes(fig)
        pdf.image(img_buf, x=15, w=180)
        pdf.ln(5)

    pdf.output(pdf_path)
