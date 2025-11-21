# utils/analytics.py
import pandas as pd

def get_summary(df: pd.DataFrame):
    """
    Return a dict with keys: total, active, resigned
    """
    if df is None or df.empty:
        return {"total": 0, "active": 0, "resigned": 0}
    total = len(df)
    active = int(len(df[df.get("Status", "") == "Active"])) if "Status" in df.columns else 0
    resigned = int(len(df[df.get("Status", "") == "Resigned"])) if "Status" in df.columns else 0
    return {"total": total, "active": active, "resigned": resigned}

def department_distribution(df: pd.DataFrame) -> pd.Series:
    if df is None or df.empty or "Department" not in df.columns:
        return pd.Series(dtype=int)
    return df["Department"].value_counts().sort_index()

def gender_ratio(df: pd.DataFrame) -> pd.Series:
    if df is None or df.empty or "Gender" not in df.columns:
        return pd.Series(dtype=int)
    return df["Gender"].value_counts().reindex(["Male","Female"], fill_value=0)

def average_salary_by_dept(df: pd.DataFrame) -> pd.Series:
    if df is None or df.empty or "Department" not in df.columns or "Salary" not in df.columns:
        return pd.Series(dtype=float)
    return df.groupby("Department")["Salary"].mean().sort_values(ascending=False)

# Feedback summary
def feedback_summary(feedback_df: pd.DataFrame, employee_df: pd.DataFrame):
    if feedback_df is None or feedback_df.empty or employee_df is None or employee_df.empty:
        return pd.DataFrame(columns=["Employee", "Avg_Rating", "Feedback_Count"])
    summary = feedback_df.groupby("receiver_id").agg(
        Avg_Rating=("rating", "mean"), Feedback_Count=("rating", "count")
    ).reset_index()
    emp_map = employee_df.set_index("Emp_ID")["Name"].to_dict()
    summary["Employee"] = summary["receiver_id"].map(emp_map)
    summary = summary[["Employee", "Avg_Rating", "Feedback_Count"]]
    return summary

# Utility to create selection list
def employee_options(df):
    if df is None or df.empty:
        return []
    return (df["Emp_ID"].astype(str) + " - " + df["Name"]).tolist()
