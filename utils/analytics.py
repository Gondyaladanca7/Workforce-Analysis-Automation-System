# utils/analytics.py

import pandas as pd
import matplotlib.pyplot as plt

# -------------------------
# Summary
# -------------------------
def get_summary(df: pd.DataFrame):
    total = len(df)
    active = len(df[df["Status"]=="Active"]) if "Status" in df.columns else 0
    resigned = len(df[df["Status"]=="Resigned"]) if "Status" in df.columns else 0
    return {"total": total, "active": active, "resigned": resigned}

# -------------------------
# Department Distribution
# -------------------------
def department_distribution(df: pd.DataFrame):
    if "Department" not in df.columns or df.empty:
        return pd.Series()
    dept_counts = df["Department"].value_counts()
    
    # Matplotlib figure for dashboard & PDF
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(dept_counts.index, dept_counts.values, color=plt.cm.Set3.colors)
    ax.set_ylabel("Number of Employees")
    ax.set_xlabel("Department")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig, dept_counts

# -------------------------
# Gender Ratio
# -------------------------
def gender_ratio(df: pd.DataFrame):
    if "Gender" not in df.columns or df.empty:
        return pd.Series()
    gender_counts = df["Gender"].value_counts()
    
    fig, ax = plt.subplots(figsize=(4,4))
    ax.pie(gender_counts.values, labels=gender_counts.index, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    
    return fig, gender_counts

# -------------------------
# Average Salary by Department
# -------------------------
def average_salary_by_dept(df: pd.DataFrame):
    if "Department" not in df.columns or "Salary" not in df.columns or df.empty:
        return pd.Series()
    salary_df = df.groupby("Department")["Salary"].mean()
    
    fig, ax = plt.subplots(figsize=(6,4))
    ax.bar(salary_df.index, salary_df.values, color=plt.cm.Pastel2.colors)
    ax.set_ylabel("Average Salary")
    ax.set_xlabel("Department")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return fig, salary_df
