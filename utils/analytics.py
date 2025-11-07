import pandas as pd

# -----------------------------
# Analytics Functions
# -----------------------------

def get_summary(df: pd.DataFrame) -> dict:
    """
    Returns summary metrics:
    total employees, active employees, resigned employees
    """
    total = len(df)
    active = len(df[df["Status"] == "Active"]) if "Status" in df.columns else total
    resigned = len(df[df["Status"] == "Resigned"]) if "Status" in df.columns else 0
    return {
        "total": total,
        "active": active,
        "resigned": resigned
    }

def department_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Returns counts of employees per department
    """
    if "Department" in df.columns:
        return df["Department"].value_counts()
    else:
        return pd.Series(dtype=int)

def gender_ratio(df: pd.DataFrame) -> pd.Series:
    """
    Returns counts of employees per gender
    """
    if "Gender" in df.columns:
        return df["Gender"].value_counts()
    else:
        return pd.Series(dtype=int)

def average_salary_by_dept(df: pd.DataFrame) -> pd.Series:
    """
    Returns average salary per department
    """
    if "Department" in df.columns and "Salary" in df.columns:
        return df.groupby("Department")["Salary"].mean()
    else:
        return pd.Series(dtype=float)

def skills_distribution(df: pd.DataFrame) -> pd.Series:
    """
    Returns counts of all skills across employees
    """
    if "Skills" in df.columns:
        skills_series = df["Skills"].dropna().str.split(",", expand=True).stack()
        return skills_series.value_counts()
    else:
        return pd.Series(dtype=int)
