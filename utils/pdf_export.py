# utils/pdf_export.py

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import matplotlib.pyplot as plt
import pandas as pd
import io

def generate_summary_pdf(file_path, total, active, resigned, mood_df=None, gender_df=None, salary_df=None, dept_df=None):
    ...

    """
    Generate a professional PDF report:
    - Total, Active, Resigned employees
    - Employee Mood table (latest logs)
    - Gender Ratio chart
    - Average Salary by Department chart
    - Department Distribution chart
    """

    doc = SimpleDocTemplate(file_path, pagesize=A4,
                            rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    styleH = styles['Heading1']
    styleH2 = styles['Heading2']
    styleN = styles['Normal']

    # Title
    elements.append(Paragraph("Workforce Summary Report", styleH))
    elements.append(Spacer(1, 20))

    # Summary metrics
    elements.append(Paragraph(f"<b>Total Employees:</b> {total}", styleN))
    elements.append(Paragraph(f"<b>Active Employees:</b> {active}", styleN))
    elements.append(Paragraph(f"<b>Resigned Employees:</b> {resigned}", styleN))
    elements.append(Spacer(1, 20))

    # Gender Ratio chart
    if gender_df is not None and not gender_df.empty:
        elements.append(Paragraph("Gender Ratio", styleH2))
        fig, ax = plt.subplots(figsize=(4,4))
        try:
            ax.pie(gender_df.values, labels=gender_df.index, autopct="%1.1f%%",
                   colors=plt.cm.Pastel1.colors)
            ax.axis("equal")
            buf = io.BytesIO()
            plt.savefig(buf, format="png")
            plt.close(fig)
            buf.seek(0)
            elements.append(Image(buf, width=200, height=200))
            elements.append(Spacer(1, 20))
        except Exception as e:
            elements.append(Paragraph(f"Failed to plot gender chart: {e}", styleN))

    # Average Salary chart
    if salary_df is not None and not salary_df.empty:
        elements.append(Paragraph("Average Salary by Department", styleH2))
        fig, ax = plt.subplots(figsize=(6,4))
        try:
            ax.bar(salary_df.index, salary_df.values, color=plt.cm.Pastel2.colors)
            ax.set_ylabel("Average Salary")
            ax.set_xlabel("Department")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            buf2 = io.BytesIO()
            plt.savefig(buf2, format="png")
            plt.close(fig)
            buf2.seek(0)
            elements.append(Image(buf2, width=400, height=200))
            elements.append(Spacer(1, 20))
        except Exception as e:
            elements.append(Paragraph(f"Failed to plot salary chart: {e}", styleN))

    # Department Distribution chart
    if dept_df is not None and not dept_df.empty:
        elements.append(Paragraph("Department Distribution", styleH2))
        fig, ax = plt.subplots(figsize=(6,4))
        try:
            ax.bar(dept_df.index, dept_df.values, color=plt.cm.Set3.colors)
            ax.set_ylabel("Number of Employees")
            ax.set_xlabel("Department")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            buf3 = io.BytesIO()
            plt.savefig(buf3, format="png")
            plt.close(fig)
            buf3.seek(0)
            elements.append(Image(buf3, width=400, height=200))
            elements.append(Spacer(1, 20))
        except Exception as e:
            elements.append(Paragraph(f"Failed to plot department chart: {e}", styleN))

    # Mood Table
    elements.append(Paragraph("Employee Mood (Latest Logs)", styleH2))
    elements.append(Spacer(1, 10))

    if mood_df is not None and not mood_df.empty:
        cols = [col for col in ["emp_id","Name","mood","log_date"] if col in mood_df.columns]
        if cols:
            mood_clean = mood_df[cols].dropna(how="all")
            if not mood_clean.empty:
                table_data = [["Emp_ID", "Name", "Mood", "Log Date"]]
                for _, row in mood_clean.head(50).iterrows():  # limit 50 rows
                    table_data.append([str(row.get("emp_id","")),
                                       row.get("Name",""),
                                       row.get("mood",""),
                                       str(row.get("log_date",""))])
                table = Table(table_data, colWidths=[60, 150, 80, 100])
                style = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                    ('TEXTCOLOR',(0,0),(-1,0),colors.black),
                    ('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 12),
                    ('BOTTOMPADDING', (0,0), (-1,0), 8),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.black)
                ])
                table.setStyle(style)
                elements.append(table)
            else:
                elements.append(Paragraph("No mood data available.", styleN))
        else:
            elements.append(Paragraph("No mood data columns found.", styleN))
    else:
        elements.append(Paragraph("No mood data available.", styleN))

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Generated by Workforce Analytics System", styles['Italic']))

    doc.build(elements)
