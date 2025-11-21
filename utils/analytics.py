# utils/analytics.py
import pandas as pd

# -------------------------
# Employee Summary Functions
# -------------------------
def get_summary(df):
    """
    Returns total, active, and resigned employee counts.
    """
    if df.empty:
        return {"total": 0, "active": 0, "resigned": 0}
    
    total = int(len(df))
    active = int(len(df[df.get("Status")=="Active"])) if "Status" in df.columns else 0
    resigned = int(len(df[df.get("Status")=="Resigned"])) if "Status" in df.columns else 0
    return {"total": total, "active": active, "resigned": resigned}

def department_distribution(df):
    if df.empty or "Department" not in df.columns:
        return pd.Series(dtype=int)
    return df["Department"].value_counts()

def gender_ratio(df):
    if df.empty or "Gender" not in df.columns:
        return pd.Series(dtype=int)
    return df["Gender"].value_counts()

def average_salary_by_dept(df):
    if df.empty or "Department" not in df.columns or "Salary" not in df.columns:
        return pd.Series(dtype=float)
    return df.groupby("Department")["Salary"].mean()

# -------------------------
# Feedback Analytics
# -------------------------
def feedback_summary(feedback_df, employee_df):
    if feedback_df.empty or employee_df.empty:
        return pd.DataFrame(columns=["Employee", "Avg_Rating", "Feedback_Count"])
    summary = feedback_df.groupby("receiver_id").agg(
        Avg_Rating=("rating", "mean"),
        Feedback_Count=("rating", "count")
    ).reset_index()
    emp_map = employee_df.set_index("Emp_ID")["Name"].to_dict()
    summary["Employee"] = summary["receiver_id"].map(emp_map)
    summary = summary[["Employee", "Avg_Rating", "Feedback_Count"]]
    return summary

# -------------------------
# Skill & Role Analytics
# -------------------------
def skill_inventory(df):
    if df.empty or "Skills" not in df.columns:
        return pd.Series(dtype=int)
    skill_list = []
    for s in df["Skills"].dropna():
        skill_list.extend([skill.strip() for skill in s.split(";") if skill.strip()])
    return pd.Series(skill_list).value_counts()

def role_distribution(df):
    if df.empty or "Role" not in df.columns:
        return pd.Series(dtype=int)
    return df["Role"].value_counts()

# -------------------------
# Employee & Task Analytics
# -------------------------
def tasks_summary(tasks_df):
    if tasks_df.empty or "status" not in tasks_df.columns:
        return pd.Series(dtype=int)
    return tasks_df["status"].value_counts()

def overdue_tasks(tasks_df):
    if tasks_df.empty or "due_date" not in tasks_df.columns:
        return pd.DataFrame()
    tasks_df["due_date_parsed"] = pd.to_datetime(tasks_df["due_date"], errors="coerce").dt.date
    today = pd.Timestamp.today().date()
    tasks_df["overdue"] = tasks_df["due_date_parsed"].apply(lambda d: d<today if pd.notna(d) else False)
    return tasks_df[tasks_df["overdue"]]

# -------------------------
# Utility for employee selection
# -------------------------
def employee_options(df):
    if df.empty:
        return []
    return df["Emp_ID"].astype(str) + " - " + df["Name"]
