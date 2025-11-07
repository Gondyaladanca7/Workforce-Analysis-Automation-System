# utils/database.py (tasks & mood related functions)

import sqlite3
import pandas as pd
from datetime import date

DB_PATH = "data/workforce.db"

# -------------------------
# TASKS FUNCTIONS
# -------------------------
def add_task(task_name, emp_id, assigned_by=None, due_date=None, status="Pending", remarks=""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, status, remarks)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task_name, emp_id, assigned_by, due_date, status, remarks))
    conn.commit()
    conn.close()

def fetch_tasks(emp_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if emp_id is not None:
        cursor.execute("SELECT * FROM tasks WHERE emp_id=?", (emp_id,))
    else:
        cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    # Convert to DataFrame
    cols = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=cols)
    conn.close()
    return df

def update_task_status(task_id, new_status, new_remarks=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if new_remarks is not None:
        cursor.execute("UPDATE tasks SET status=?, remarks=? WHERE task_id=?", (new_status, new_remarks, task_id))
    else:
        cursor.execute("UPDATE tasks SET status=? WHERE task_id=?", (new_status, task_id))
    conn.commit()
    conn.close()

# -------------------------
# MOOD FUNCTIONS
# -------------------------
def log_mood(emp_id, mood, remarks=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mood (emp_id, mood, remarks, log_date)
        VALUES (?, ?, ?, ?)
    """, (emp_id, mood, remarks, date.today().strftime("%Y-%m-%d")))
    conn.commit()
    conn.close()

def fetch_mood(emp_id=None):
    conn = sqlite3.connect(DB_PATH)
    if emp_id is not None:
        df = pd.read_sql_query("SELECT * FROM mood WHERE emp_id=?", conn, params=(emp_id,))
    else:
        df = pd.read_sql_query("SELECT * FROM mood", conn)
    conn.close()
    return df
