import sqlite3
import pandas as pd
from typing import Optional

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
    """Create mood_logs table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            mood TEXT,
            log_date TEXT,
            FOREIGN KEY(emp_id) REFERENCES employees(Emp_ID) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def initialize_task_table():
    """Create tasks table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            emp_id INTEGER,
            assigned_by TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            remarks TEXT DEFAULT '',
            created_date TEXT,
            FOREIGN KEY(emp_id) REFERENCES employees(Emp_ID) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# -----------------------------
# Employee Functions
# -----------------------------

def fetch_employees() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

def add_employee(emp_dict: dict):
    """
    Add employee.
    emp_dict keys: Name, Age, Gender, Department, Role, Skills, Join_Date, Resign_Date, Status, Salary, Location
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Auto-generate Emp_ID
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
    """Delete employee and cascade to mood_logs and tasks"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Delete moods
    cursor.execute("DELETE FROM mood_logs WHERE emp_id=?", (emp_id,))
    # Delete tasks
    cursor.execute("DELETE FROM tasks WHERE emp_id=?", (emp_id,))
    # Delete employee
    cursor.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()

# -----------------------------
# Mood Functions
# -----------------------------

def add_mood_entry(emp_id: int, mood: str, log_date: str):
    """
    Add mood entry
    mood: 'Happy', 'Neutral', 'Sad', 'Angry'
    log_date: 'YYYY-MM-DD'
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Optional: replace mood if already exists for the day
    cursor.execute("""
        SELECT id FROM mood_logs WHERE emp_id=? AND log_date=?
    """, (emp_id, log_date))
    existing = cursor.fetchone()
    if existing:
        cursor.execute("UPDATE mood_logs SET mood=? WHERE id=?", (mood, existing[0]))
    else:
        cursor.execute("INSERT INTO mood_logs (emp_id, mood, log_date) VALUES (?, ?, ?)",
                       (emp_id, mood, log_date))
    conn.commit()
    conn.close()

def fetch_mood_logs() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM mood_logs", conn)
    conn.close()
    return df

# -----------------------------
# Task Functions
# -----------------------------

def add_task(task_name: str, emp_id: int, assigned_by: str, due_date: str,
             status: str = "Pending", remarks: str = "", created_date: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, status, remarks, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (task_name, emp_id, assigned_by, due_date, status, remarks, created_date))
    conn.commit()
    conn.close()

def fetch_tasks(emp_id: Optional[int] = None) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    if emp_id is None:
        df = pd.read_sql_query("SELECT * FROM tasks", conn)
    else:
        df = pd.read_sql_query("SELECT * FROM tasks WHERE emp_id=?", conn, params=(emp_id,))
    conn.close()
    return df

def update_task_status(task_id: int, new_status: str, remarks: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tasks SET status=?, remarks=? WHERE task_id=?
    """, (new_status, remarks, task_id))
    conn.commit()
    conn.close()

# -----------------------------
# Initialize all tables
# -----------------------------
initialize_database()
initialize_mood_table()
initialize_task_table()
