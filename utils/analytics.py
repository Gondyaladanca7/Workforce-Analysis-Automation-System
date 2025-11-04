import pandas as pd

# ------------------------- Summary Functions
def get_summary(df: pd.DataFrame):
    total = len(df)
    active = len(df[df["Status"]=="Active"])
    resigned = len(df[df["Status"]=="Resigned"])
    return total, active, resigned

# ------------------------- Department Distribution
def department_distribution(df: pd.DataFrame):
    if "Department" in df.columns and not df.empty:
        return df["Department"].value_counts()
    return pd.Series(dtype=int)

# ------------------------- Gender Ratio
def gender_ratio(df: pd.DataFrame):
    if "Gender" in df.columns and not df.empty:
        df = df[df["Gender"].isin(["Male","Female"])]  # Ensure only Male/Female
        return df["Gender"].value_counts()
    return pd.Series(dtype=int)

# ------------------------- Average Salary by Department
def average_salary_by_dept(df: pd.DataFrame):
    if "Department" in df.columns and "Salary" in df.columns and not df.empty:
        avg_salary = df.groupby("Department")["Salary"].mean().sort_values()
        return avg_salary
    return pd.Series(dtype=float)
