# utils/database.py
import sqlite3
import pandas as pd
from typing import Optional
from datetime import date

DB_PATH = "data/workforce.db"

# -----------------------------
# Database Initialization
# -----------------------------
def initialize_database():
    """Create employees table if not exists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            Emp_ID INTEGER PRIMARY KEY,
            Name TEXT DEFAULT 'NA',
            Age INTEGER DEFAULT 0,
            Gender TEXT DEFAULT 'Male',
            Department TEXT DEFAULT 'NA',
            Role TEXT DEFAULT 'NA',
            Skills TEXT DEFAULT 'NA',
            Join_Date TEXT DEFAULT '',
            Resign_Date TEXT DEFAULT '',
            Status TEXT DEFAULT 'Active',
            Salary REAL DEFAULT 0.0,
            Location TEXT DEFAULT 'NA'
        )
    """)
    conn.commit()
    conn.close()

def initialize_mood_table():
    """Create mood table (compatible with pages)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood (
            mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER NOT NULL,
            mood TEXT NOT NULL,
            remarks TEXT DEFAULT '',
            log_date TEXT DEFAULT (date('now'))
        )
    """)
    conn.commit()
    conn.close()

def initialize_task_table():
    """Create tasks table (compatible with pages)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            emp_id INTEGER NOT NULL,
            assigned_by TEXT,
            due_date TEXT,
            remarks TEXT DEFAULT '',
            status TEXT DEFAULT 'Pending',
            created_date TEXT DEFAULT (date('now'))
        )
    """)
    conn.commit()
    conn.close()

# -----------------------------
# Employee Functions
# -----------------------------
def fetch_employees() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM employees", conn)
    except Exception:
        df = pd.DataFrame(columns=[
            "Emp_ID","Name","Age","Gender","Department","Role",
            "Skills","Join_Date","Resign_Date","Status","Salary","Location"
        ])
    conn.close()
    return df

def add_employee(emp_dict: dict) -> int:
    """Add a new employee and return Emp_ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(Emp_ID) FROM employees")
    max_id = cursor.fetchone()[0]
    new_id = (max_id or 0) + 1

    cursor.execute("""
        INSERT INTO employees (Emp_ID, Name, Age, Gender, Department, Role, Skills, Join_Date, Resign_Date, Status, Salary, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        new_id,
        emp_dict.get("Name", "NA"),
        emp_dict.get("Age", 0),
        emp_dict.get("Gender", "Male"),
        emp_dict.get("Department", "NA"),
        emp_dict.get("Role", "NA"),
        emp_dict.get("Skills", "NA"),
        emp_dict.get("Join_Date", ""),
        emp_dict.get("Resign_Date", ""),
        emp_dict.get("Status", "Active"),
        emp_dict.get("Salary", 0.0),
        emp_dict.get("Location", "NA")
    ))
    conn.commit()
    conn.close()
    return new_id

def delete_employee(emp_id: int):
    """Delete employee and cascade to mood and tasks"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mood WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM tasks WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()

# -----------------------------
# Mood Functions (consistent names)
# -----------------------------
def add_mood_entry(emp_id: int, mood: str, log_date: str = None, remarks: str = ""):
    """
    Log mood for an employee. Replaces same-day entry if exists.
    log_date expected 'YYYY-MM-DD'. If None, uses today's date.
    """
    if log_date is None:
        log_date = date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT mood_id FROM mood WHERE emp_id=? AND log_date=?", (emp_id, log_date))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE mood SET mood=?, remarks=? WHERE mood_id=?", (mood, remarks, existing[0]))
    else:
        cursor.execute("INSERT INTO mood (emp_id, mood, remarks, log_date) VALUES (?, ?, ?, ?)", (emp_id, mood, remarks, log_date))
    conn.commit()
    conn.close()

# Backwards-compatible alias used by some pages
def log_mood(emp_id: int, mood: str, remarks: str = None):
    add_mood_entry(emp_id=emp_id, mood=mood, remarks=(remarks or ""))


def fetch_mood_logs() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query("SELECT * FROM mood", conn)
    except Exception:
        df = pd.DataFrame(columns=["mood_id","emp_id","mood","remarks","log_date"])
    conn.close()
    return df

# Backwards compatible alias used on older pages
def fetch_mood(emp_id: Optional[int] = None) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        if emp_id is None:
            df = pd.read_sql_query("SELECT * FROM mood", conn)
        else:
            df = pd.read_sql_query("SELECT * FROM mood WHERE emp_id=?", conn, params=(emp_id,))
    except Exception:
        df = pd.DataFrame(columns=["mood_id","emp_id","mood","remarks","log_date"])
    conn.close()
    return df

# -----------------------------
# Task Functions
# -----------------------------
def add_task(task_name: str, emp_id: int, assigned_by: str = None,
             due_date: Optional[str] = None, status: str = "Pending",
             remarks: str = "", created_date: Optional[str] = None):
    """Insert a new task. created_date default is today."""
    if not created_date:
        created_date = date.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, remarks, status, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task_name, emp_id, assigned_by, due_date, remarks, status, created_date))
    conn.commit()
    conn.close()

def fetch_tasks(emp_id: Optional[int] = None) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        if emp_id is None:
            df = pd.read_sql_query("SELECT * FROM tasks", conn)
        else:
            df = pd.read_sql_query("SELECT * FROM tasks WHERE emp_id=?", conn, params=(emp_id,))
    except Exception:
        df = pd.DataFrame(columns=["task_id","task_name","emp_id","assigned_by","due_date","remarks","status","created_date"])
    conn.close()
    return df

def update_task_status(task_id: int, new_status: str, remarks: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status=?, remarks=? WHERE task_id=?", (new_status, remarks, task_id))
    conn.commit()
    conn.close()

# -----------------------------
# Initialize all tables
# -----------------------------
# keep idempotent (safe to call)
initialize_database()
initialize_mood_table()
initialize_task_table()
