# utils/database.py

import sqlite3
import pandas as pd
from typing import Optional
from datetime import date
import os

DB_PATH = "data/workforce.db"
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)  # ensure data folder exists

# -----------------------------
# Database Initialization
# -----------------------------
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            Emp_ID INTEGER PRIMARY KEY,
            Name TEXT,
            Age INTEGER,
            Gender TEXT,
            Department TEXT,
            Role TEXT,
            Skills TEXT,
            Join_Date TEXT,
            Resign_Date TEXT,
            Status TEXT,
            Salary REAL,
            Location TEXT
        )
    """)
    conn.commit()
    conn.close()

def initialize_mood_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            mood TEXT,
            log_date TEXT,
            remarks TEXT
        )
    """)
    conn.commit()
    conn.close()

def initialize_task_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            emp_id INTEGER,
            assigned_by TEXT,
            due_date TEXT,
            status TEXT,
            remarks TEXT
        )
    """)
    conn.commit()
    conn.close()

def initialize_user_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

# -----------------------------
# Employee Functions
# -----------------------------
def add_employee(emp: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO employees (
            Emp_ID, Name, Age, Gender, Department, Role, Skills,
            Join_Date, Resign_Date, Status, Salary, Location
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        emp.get("Emp_ID"),
        emp.get("Name"),
        emp.get("Age"),
        emp.get("Gender"),
        emp.get("Department"),
        emp.get("Role"),
        emp.get("Skills"),
        emp.get("Join_Date"),
        emp.get("Resign_Date"),
        emp.get("Status"),
        emp.get("Salary"),
        emp.get("Location")
    ))
    conn.commit()
    conn.close()

def fetch_employees() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

def delete_employee(emp_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mood_logs WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM tasks WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()

# -----------------------------
# Mood Functions
# -----------------------------
def add_mood_entry(emp_id: int, mood: str, remarks: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO mood_logs (emp_id, mood, log_date, remarks)
        VALUES (?, ?, ?, ?)
    """, (emp_id, mood, date.today().isoformat(), remarks))
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
def add_task(task_name: str, emp_id: int, assigned_by: str,
             due_date: str, remarks: str = "", status: str = "Pending"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, status, remarks)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task_name, emp_id, assigned_by, due_date, status, remarks))
    conn.commit()
    conn.close()

def fetch_tasks() -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    return df

# -----------------------------
# User Functions (Login)
# -----------------------------
def get_user_by_username(username: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT username, password, role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"username": row[0], "password": row[1], "role": row[2]}
    return None

def add_user(username: str, password: str, role: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, (username, password, role))
    conn.commit()
    conn.close()

# -----------------------------
# Initialize all tables & default users
# -----------------------------
def initialize_all_tables():
    """
    Creates all tables, then resets default users with hashed passwords.
    Import hash_password here (local import) to avoid circular import at module import time.
    """
    initialize_database()
    initialize_mood_table()
    initialize_task_table()
    initialize_user_table()

    # Clear existing users and insert default users (hashed)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users")
        conn.commit()
    except Exception:
        # If users table doesn't exist or deletion fails, ignore and continue
        pass
    conn.close()

    # local import to avoid circular import at module load
    try:
        from utils.auth import hash_password
    except Exception:
        # fallback to a safe local hash if import fails (shouldn't happen if utils/auth.py exists)
        import hashlib
        def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

    add_user("admin", hash_password("admin123"), "Admin")
    add_user("manager", hash_password("manager123"), "Manager")
    add_user("employee", hash_password("employee123"), "Employee")
