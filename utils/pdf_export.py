# utils/pdf_export.py
from fpdf import FPDF
import pandas as pd
from utils.analytics import feedback_summary

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Workforce Summary Report", ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def generate_summary_pdf(file_path, total_employees, active_employees, resigned_employees,
                         employee_df, gender_series=None, salary_series=None,
                         dept_series=None, feedback_df=None):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # -------------------------
    # Key Metrics
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "1. Key Metrics", ln=True)  # Removed emoji
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f"Total Employees: {total_employees}", ln=True)
    pdf.cell(0, 8, f"Active Employees: {active_employees}", ln=True)
    pdf.cell(0, 8, f"Resigned Employees: {resigned_employees}", ln=True)
    pdf.ln(5)

    # -------------------------
    # Department Distribution
    if dept_series is not None and not dept_series.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "2. Department Distribution", ln=True)
        pdf.set_font("Arial", "", 11)
        for dept, count in dept_series.items():
            pdf.cell(0, 8, f"{dept}: {count} employees", ln=True)
        pdf.ln(5)

    # -------------------------
    # Gender Ratio
    if gender_series is not None and not gender_series.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "3. Gender Distribution", ln=True)
        pdf.set_font("Arial", "", 11)
        for gender, count in gender_series.items():
            pdf.cell(0, 8, f"{gender}: {count}", ln=True)
        pdf.ln(5)

    # -------------------------
    # Average Salary
    if salary_series is not None and not salary_series.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "4. Average Salary by Department", ln=True)
        pdf.set_font("Arial", "", 11)
        for dept, salary in salary_series.items():
            pdf.cell(0, 8, f"{dept}: ₹{salary:.2f}", ln=True)
        pdf.ln(5)

    # -------------------------
    # Feedback Summary
    if feedback_df is not None and not feedback_df.empty:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "5. Employee Feedback Summary", ln=True)
        pdf.set_font("Arial", "", 11)
        fb_summary = feedback_summary(feedback_df, employee_df)
        if fb_summary.empty:
            pdf.cell(0, 8, "No feedback available.", ln=True)
        else:
            for _, row in fb_summary.iterrows():
                pdf.cell(0, 8, f"{row['Employee']}: Avg Rating {row['Avg_Rating']:.2f} ({row['Feedback_Count']} feedbacks)", ln=True)
        pdf.ln(5)

    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, "Report generated automatically by Workforce Analytics System.", ln=True)
    pdf.output(file_path)
