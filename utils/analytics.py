import pandas as pd

# -------------------------
# Workforce Summary
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
    if "Department" not in df.columns or df.empty:
        return pd.Series(dtype=int)
    return df["Department"].value_counts().sort_index()

# -------------------------
# Gender Ratio
# -------------------------
def gender_ratio(df: pd.DataFrame) -> pd.Series:
    if "Gender" not in df.columns or df.empty:
        return pd.Series(dtype=int)
    return df["Gender"].value_counts().reindex(["Male","Female"], fill_value=0)

# -------------------------
# Average Salary by Department
# -------------------------
def average_salary_by_dept(df: pd.DataFrame) -> pd.Series:
    if "Department" not in df.columns or "Salary" not in df.columns or df.empty:
        return pd.Series(dtype=float)
    return df.groupby("Department")["Salary"].mean().sort_values(ascending=False)
