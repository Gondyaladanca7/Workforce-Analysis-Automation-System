import io
from fpdf import FPDF
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# -----------------------------
# PDF Helper Class
# -----------------------------

class PDFExporter:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=15)
    
    def add_title(self, title):
        self.pdf.set_font("Arial", "B", 16)
        self.pdf.add_page()
        self.pdf.cell(0, 10, title, ln=True, align="C")
        self.pdf.ln(10)
    
    def add_table(self, df: pd.DataFrame, title: str = ""):
        if title:
            self.pdf.set_font("Arial", "B", 14)
            self.pdf.cell(0, 10, title, ln=True)
            self.pdf.ln(5)
        
        # Table header
        self.pdf.set_font("Arial", "B", 10)
        col_widths = [max(30, self.pdf.get_string_width(str(col)) + 4) for col in df.columns]
        for i, col in enumerate(df.columns):
            self.pdf.cell(col_widths[i], 8, str(col), border=1, align='C')
        self.pdf.ln()
        
        # Table rows
        self.pdf.set_font("Arial", "", 10)
        for _, row in df.iterrows():
            for i, col in enumerate(df.columns):
                text = str(row[col])
                self.pdf.cell(col_widths[i], 8, text, border=1)
            self.pdf.ln()
        self.pdf.ln(5)
    
    def add_chart(self, fig: plt.Figure, title: str = ""):
        """Convert Matplotlib figure to image and embed in PDF"""
        buf = io.BytesIO()
        fig.savefig(buf, format="PNG", bbox_inches='tight')
        buf.seek(0)
        self.pdf.ln(5)
        if title:
            self.pdf.set_font("Arial", "B", 14)
            self.pdf.cell(0, 10, title, ln=True)
        self.pdf.image(buf, x=None, y=None, w=180)
        plt.close(fig)
        self.pdf.ln(5)
    
    def save_pdf(self):
        self.pdf.output(self.pdf_path)

# -----------------------------
# Export Function
# -----------------------------

def generate_summary_pdf(pdf_path: str, total_employees: int, active_employees: int, resigned_employees: int, df: pd.DataFrame):
    """
    pdf_path: file to save PDF
    total_employees, active_employees, resigned_employees: summary numbers
    df: filtered employee/task/mood data
    """
    pdf = PDFExporter(pdf_path)
    pdf.add_title("Workforce Summary Report")
    
    # Add basic summary
    summary_df = pd.DataFrame({
        "Metric": ["Total Employees", "Active Employees", "Resigned Employees"],
        "Count": [total_employees, active_employees, resigned_employees]
    })
    pdf.add_table(summary_df, title="Summary")
    
    # Department distribution chart
    if "Department" in df.columns:
        dept_counts = df["Department"].value_counts()
        fig, ax = plt.subplots(figsize=(6,4))
        sns.barplot(x=dept_counts.index, y=dept_counts.values, palette="coolwarm", ax=ax)
        ax.set_title("Employees per Department")
        ax.set_ylabel("Count")
        ax.set_xlabel("Department")
        pdf.add_chart(fig, title="Department Distribution")
    
    # Gender ratio chart
    if "Gender" in df.columns:
        gender_counts = df["Gender"].value_counts()
        fig, ax = plt.subplots(figsize=(6,4))
        ax.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%', colors=sns.color_palette("Set2"))
        ax.set_title("Gender Ratio")
        pdf.add_chart(fig, title="Gender Ratio")
    
    # Skills distribution (if exists)
    if "Skills" in df.columns:
        skills_series = df["Skills"].dropna().str.split(",", expand=True).stack()
        skills_counts = skills_series.value_counts()
        if not skills_counts.empty:
            fig, ax = plt.subplots(figsize=(6,4))
            sns.barplot(x=skills_counts.values, y=skills_counts.index, palette="coolwarm", ax=ax)
            ax.set_xlabel("Count")
            ax.set_ylabel("Skill")
            ax.set_title("Skill Distribution")
            pdf.add_chart(fig, title="Skills Distribution")
    
    # Add employee table
    pdf.add_table(df, title="Employee Details / Tasks")
    
    # Save PDF
    pdf.save_pdf()
