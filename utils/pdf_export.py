from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import io

def generate_summary_pdf(path, total, active, resigned, df, mood_df=None, gender_fig=None, salary_fig=None, dept_fig=None):
    doc = SimpleDocTemplate(path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        name="Title",
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=20
    )
    elements.append(Paragraph("Workforce Summary Report", title_style))

    # Summary metrics
    metrics_style = ParagraphStyle(name="Metrics", fontSize=12, leading=16, spaceAfter=10)
    elements.append(Paragraph(f"Total Employees: {total}", metrics_style))
    elements.append(Paragraph(f"Active Employees: {active}", metrics_style))
    elements.append(Paragraph(f"Resigned Employees: {resigned}", metrics_style))
    elements.append(Spacer(1, 12))

    # Employee Table
    if not df.empty:
        df_display = df.copy()
        cols_to_show = ["Emp_ID", "Name", "Department", "Role", "Join_Date", "Status"]
        df_display = df_display[cols_to_show]

        data = [cols_to_show] + df_display.values.tolist()

        # Pastel colors
        pastel_blue = colors.Color(173/255, 216/255, 230/255)
        pastel_green = colors.Color(198/255, 239/255, 206/255)
        pastel_grey = colors.Color(240/255, 240/255, 240/255)

        t = Table(data, hAlign='LEFT', repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), pastel_blue),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), pastel_grey),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

    # Mood logs table
    if mood_df is not None and not mood_df.empty:
        elements.append(Paragraph("Mood Logs", styles['Heading2']))
        mood_cols = ["Name", "log_date", "mood", "remarks"]  # matches DB column names
        mood_data = [mood_cols] + mood_df[mood_cols].values.tolist()
        t_mood = Table(mood_data, hAlign='LEFT', repeatRows=1)
        t_mood.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), pastel_green),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ]))
        elements.append(t_mood)
        elements.append(Spacer(1, 12))

    # Figures
    for fig, title in zip([dept_fig, gender_fig, salary_fig], ["Department Distribution", "Gender Ratio", "Average Salary by Department"]):
        if fig:
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight')
            buf.seek(0)
            elements.append(Paragraph(title, styles['Heading2']))
            elements.append(Image(buf, width=6*inch, height=3*inch))
            elements.append(Spacer(1, 12))

    doc.build(elements)
