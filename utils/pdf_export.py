# utils/pdf_export.py
from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
import io

def generate_summary_pdf(file_path, total, active, resigned, df: pd.DataFrame):
    """
    Generate a professional workforce summary PDF (fully in-memory plots).
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Workforce Summary Report", ln=True, align="C")
    pdf.ln(10)

    # --- Summary metrics ---
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, "1. Key Metrics", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, f"Total Employees: {total}", ln=True)
    pdf.cell(0, 6, f"Active Employees: {active}", ln=True)
    pdf.cell(0, 6, f"Resigned Employees: {resigned}", ln=True)
    pdf.ln(5)

    # --- Department distribution ---
    if "Department" in df.columns and not df.empty:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "2. Department-wise Count", ln=True)
        dept_counts = df["Department"].value_counts()
        pdf.set_font("Arial", "", 12)
        for dept, count in dept_counts.items():
            pdf.cell(0, 6, f"{dept}: {count}", ln=True)
        pdf.ln(5)

    # --- Gender ratio ---
    if "Gender" in df.columns and not df.empty:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "3. Gender Ratio", ln=True)
        gender_counts = df["Gender"].value_counts()
        fig, ax = plt.subplots(figsize=(4,4))
        ax.pie(gender_counts, labels=gender_counts.index, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        buf = io.BytesIO()
        plt.savefig(buf, format="PNG", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        pdf.image(buf, w=100)
        pdf.ln(5)

    # --- Average Salary by Department ---
    if "Department" in df.columns and "Salary" in df.columns and not df.empty:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "4. Average Salary by Department", ln=True)
        avg_salary = df.groupby("Department")["Salary"].mean().round(2)
        fig, ax = plt.subplots(figsize=(6,3))
        avg_salary.plot(kind="bar", ax=ax)
        ax.set_ylabel("Average Salary")
        ax.set_xlabel("Department")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="PNG", bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        pdf.image(buf, w=160)

    # --- Save PDF ---
    pdf.output(file_path)
