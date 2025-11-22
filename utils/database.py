# utils/database.py
import sqlite3
import pandas as pd
import datetime
import hashlib
import os
from typing import Optional, Dict, Any

DB_PATH = "data/workforce.db"

def ensure_data_folder():
    if not os.path.exists("data"):
        os.makedirs("data")

def connect_db():
    ensure_data_folder()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def initialize_all_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # employees
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        Emp_ID INTEGER PRIMARY KEY AUTOINCREMENT,
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

    # tasks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT,
        emp_id INTEGER,
        assigned_by TEXT,
        due_date TEXT,
        status TEXT DEFAULT 'Pending',
        remarks TEXT,
        created_date TEXT
    )
    """)

    # mood logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_logs (
        mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER,
        mood TEXT,
        remarks TEXT,
        log_date TEXT
    )
    """)

    # feedback
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        message TEXT,
        rating INTEGER,
        log_date TEXT
    )
    """)

    conn.commit()

    # seed default users
    defaults = [
        ("admin", "admin123", "Admin"),
        ("manager", "manager123", "Manager"),
        ("employee", "employee123", "Employee")
    ]
    for uname, pwd, role in defaults:
        cursor.execute("SELECT 1 FROM users WHERE username=?", (uname,))
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (uname, hash_password(pwd), role)
            )
    conn.commit()

    # seed small employees if empty
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] == 0:
        sample_employees = [
            ("John Doe", 30, "Male", "IT", "Developer", "Python;SQL", "2022-01-01", "", "Active", 50000, "Delhi"),
            ("Jane Smith", 28, "Female", "HR", "HR Executive", "Communication;Excel", "2021-06-15", "", "Active", 45000, "Mumbai"),
            ("Alice Johnson", 35, "Female", "Finance", "Accountant", "Excel;Accounting", "2020-03-20", "", "Active", 60000, "Bangalore"),
        ]
        cursor.executemany("""
            INSERT INTO employees
            (Name, Age, Gender, Department, Role, Skills, Join_Date, Resign_Date, Status, Salary, Location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_employees)
        conn.commit()

    conn.close()

# -------------------------
# Users
# -------------------------
def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "password": row[2], "role": row[3]}
    return None

def add_user(username: str, password: str, role: str = "Employee"):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (username, password, role) VALUES (?, ?, ?)",
                   (username, hash_password(password), role))
    conn.commit()
    conn.close()

# -------------------------
# Employees
# -------------------------
def fetch_employees() -> pd.DataFrame:
    conn = connect_db()
    try:
        df = pd.read_sql("SELECT * FROM employees", conn)
    finally:
        conn.close()
    return df

def add_employee(emp_dict: Dict[str, Any]):
    conn = connect_db()
    cursor = conn.cursor()
    if emp_dict.get("Emp_ID") is not None:
        # allow explicit ID insert/replace
        columns = ", ".join(emp_dict.keys())
        placeholders = ", ".join("?" for _ in emp_dict)
        sql = f"INSERT OR REPLACE INTO employees ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(emp_dict.values()))
    else:
        d = {k: v for k, v in emp_dict.items() if k != "Emp_ID"}
        columns = ", ".join(d.keys())
        placeholders = ", ".join("?" for _ in d)
        sql = f"INSERT INTO employees ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(d.values()))
    conn.commit()
    conn.close()

def delete_employee(emp_id: int):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mood_logs WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM tasks WHERE emp_id=?", (emp_id,))
    cursor.execute("DELETE FROM feedback WHERE receiver_id=? OR sender_id=?", (emp_id, emp_id))
    cursor.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()

# -------------------------
# Tasks
# -------------------------
def fetch_tasks() -> pd.DataFrame:
    conn = connect_db()
    try:
        df = pd.read_sql("SELECT * FROM tasks", conn)
    finally:
        conn.close()
    return df

def add_task(task: Optional[Dict[str, Any]] = None, **kwargs):
    if task is None:
        task = kwargs
    conn = connect_db()
    cursor = conn.cursor()
    created_date = datetime.datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, status, remarks, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        task.get("task_name", "Untitled Task"),
        task.get("emp_id"),
        task.get("assigned_by", ""),
        task.get("due_date", ""),
        task.get("status", "Pending"),
        task.get("remarks", ""),
        created_date
    ))
    conn.commit()
    conn.close()

# -------------------------
# Mood logs
# -------------------------
def fetch_mood_logs() -> pd.DataFrame:
    conn = connect_db()
    try:
        df = pd.read_sql("SELECT * FROM mood_logs", conn)
    finally:
        conn.close()
    return df

def add_mood_entry(emp_id: int, mood: str, remarks: str = ""):
    conn = connect_db()
    cursor = conn.cursor()
    log_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO mood_logs (emp_id, mood, remarks, log_date)
        VALUES (?, ?, ?, ?)
    """, (emp_id, mood, remarks, log_date))
    conn.commit()
    conn.close()

# -------------------------
# Feedback
# -------------------------
def fetch_feedback() -> pd.DataFrame:
    conn = connect_db()
    try:
        df = pd.read_sql("SELECT * FROM feedback", conn)
    finally:
        conn.close()
    return df

def add_feedback(sender_id: int, receiver_id: int, message: str, rating: int):
    conn = connect_db()
    cursor = conn.cursor()
    log_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO feedback (sender_id, receiver_id, message, rating, log_date)
        VALUES (?, ?, ?, ?, ?)
    """, (sender_id, receiver_id, message, rating, log_date))
    conn.commit()
    conn.close()
