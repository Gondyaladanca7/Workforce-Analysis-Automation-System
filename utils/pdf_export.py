# utils/pdf_export.py
from fpdf import FPDF
import pandas as pd
from utils import database as db

def generate_summary_pdf(pdf_path: str, total: int, active: int, resigned: int, df: pd.DataFrame):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Workforce Summary Report", ln=True, align="C")
    pdf.ln(5)

    # Employee Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, f"Total Employees: {total}", ln=True)
    pdf.cell(0, 8, f"Active Employees: {active}", ln=True)
    pdf.cell(0, 8, f"Resigned Employees: {resigned}", ln=True)
    pdf.ln(5)

    # Department distribution
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Department Distribution:", ln=True)
    pdf.set_font("Arial", '', 11)
    if "Department" in df.columns and not df.empty:
        for dept, count in df['Department'].value_counts().items():
            pdf.cell(0, 7, f"{dept}: {count}", ln=True)
    else:
        pdf.cell(0, 7, "No department data available.", ln=True)
    pdf.ln(5)

    # Average Salary by Department
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Average Salary by Department:", ln=True)
    pdf.set_font("Arial", '', 11)
    if "Department" in df.columns and "Salary" in df.columns and not df.empty:
        avg_salary = df.groupby("Department")["Salary"].mean()
        for dept, sal in avg_salary.items():
            pdf.cell(0, 7, f"{dept}: ₹{sal:,.2f}", ln=True)
    else:
        pdf.cell(0, 7, "No salary data available.", ln=True)
    pdf.ln(5)

    # Mood Tracker Logs
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, "Employee Mood Logs:", ln=True)
    pdf.set_font("Arial", '', 11)
    mood_df = db.fetch_mood_logs()
    if not mood_df.empty:
        merged = pd.merge(mood_df, df[["Emp_ID","Name"]], left_on="emp_id", right_on="Emp_ID", how="left")
        merged_sorted = merged.sort_values(by="log_date", ascending=False)
        for _, row in merged_sorted.iterrows():
            pdf.cell(0, 7, f"{row['log_date']} - {row['Name']} ({row['emp_id']}): {row['mood']}", ln=True)
    else:
        pdf.cell(0, 7, "No mood logs found.", ln=True)

    # Save PDF
    pdf.output(pdf_path)
