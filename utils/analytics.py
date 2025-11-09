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
def department_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Returns department-wise counts as a Series.
    """
    if "Department" not in df.columns or df.empty:
        return pd.Series(dtype=int)
    
    dept_counts = df["Department"].value_counts().sort_index()
    return dept_counts

# -------------------------
# Gender Ratio
# -------------------------
def gender_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Returns male/female counts as a Series.
    """
    if "Gender" not in df.columns or df.empty:
        return pd.Series(dtype=int)
    
    gender_counts = df["Gender"].value_counts().reindex(["Male", "Female"], fill_value=0)
    return gender_counts

# -------------------------
# Average Salary by Department
# -------------------------
def average_salary_by_dept(df: pd.DataFrame) -> pd.Series:
    """
    Returns a Series: index=Department, values=average Salary.
    Always a single Series for plotting in Seaborn.
    """
    if "Department" not in df.columns or "Salary" not in df.columns or df.empty:
        return pd.Series(dtype=float)
    
    avg_salary = df.groupby("Department")["Salary"].mean().sort_values(ascending=False)
    return avg_salary
