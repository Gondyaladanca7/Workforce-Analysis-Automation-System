"""
Professional PDF Export for Workforce Analytics System
Generates a full workforce summary PDF with charts and tables
"""

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph, Image, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import io
from datetime import datetime

def generate_summary_pdf(
    pdf_path,
    total,
    active,
    resigned,
    df,
    mood_df=None,
    gender_fig=None,
    salary_fig=None,
    dept_fig=None
):
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=landscape(A4), rightMargin=30,leftMargin=30, topMargin=30,bottomMargin=18)
    elements = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, alignment=1, spaceAfter=20)
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Heading2'], fontSize=16, spaceAfter=12)
    normal_style = styles['Normal']

    # Title
    elements.append(Paragraph("Workforce Analytics Summary", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 12))

    # Summary Metrics
    metrics_data = [
        ["Total Employees", total],
        ["Active Employees", active],
        ["Resigned Employees", resigned]
    ]
    metrics_table = Table(metrics_data, colWidths=[200, 100])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.pastelblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),12),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID',(0,0),(-1,-1),0.5,colors.grey)
    ]))
    elements.append(metrics_table)
    elements.append(Spacer(1, 20))

    # Charts
    def fig_to_image(fig):
        buf = io.BytesIO()
        fig.savefig(buf, format='PNG', bbox_inches='tight')
        buf.seek(0)
        return buf

    if dept_fig:
        elements.append(Paragraph("Department Distribution", subtitle_style))
        elements.append(Image(fig_to_image(dept_fig), width=400, height=250))
        elements.append(Spacer(1, 12))
    if gender_fig:
        elements.append(Paragraph("Gender Distribution", subtitle_style))
        elements.append(Image(fig_to_image(gender_fig), width=350, height=350))
        elements.append(Spacer(1, 12))
    if salary_fig:
        elements.append(Paragraph("Average Salary by Department", subtitle_style))
        elements.append(Image(fig_to_image(salary_fig), width=400, height=250))
        elements.append(Spacer(1, 20))

    # Employee Table
    elements.append(Paragraph("Employee Records", subtitle_style))
    table_data = [list(df.columns)]
    for _, row in df.iterrows():
        table_data.append([str(row[col]) for col in df.columns])
    
    col_widths = [70, 100, 70, 100, 80, 80, 80, 70, 70, 60, 70, 80]
    emp_table = Table(table_data, colWidths=col_widths)
    emp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#2E86C1")),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,-1),8),
        ('GRID',(0,0),(-1,-1),0.25,colors.grey),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')
    ]))
    elements.append(emp_table)
    elements.append(Spacer(1, 20))

    # Mood Logs Table (Optional)
    if mood_df is not None and not mood_df.empty:
        elements.append(Paragraph("Employee Mood Logs", subtitle_style))
        mood_cols = ["Name","Date","Mood"]
        mood_table_data = [mood_cols] + mood_df[mood_cols].values.tolist()
        mood_table = Table(mood_table_data, colWidths=[150,100,100])
        mood_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#27AE60")),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',(0,0),(-1,-1),8),
            ('GRID',(0,0),(-1,-1),0.25,colors.grey),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE')
        ]))
        elements.append(mood_table)

    # Build PDF
    doc.build(elements)
