# utils/database.py
import sqlite3
import pandas as pd
import datetime

DB_PATH = "data/workforce.db"

# -------------------------
# Generic helpers
def connect_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Employees
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

    # Tasks
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

    # Mood logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_logs (
        mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER,
        mood TEXT,
        remarks TEXT,
        log_date TEXT
    )
    """)

    # Feedback
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
    conn.close()

# -------------------------
# Employee functions
def fetch_employees():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM employees", conn)
    conn.close()
    return df

def add_employee(emp_dict):
    conn = connect_db()
    cursor = conn.cursor()
    columns = ", ".join(emp_dict.keys())
    placeholders = ", ".join("?" for _ in emp_dict)
    sql = f"INSERT INTO employees ({columns}) VALUES ({placeholders})"
    cursor.execute(sql, tuple(emp_dict.values()))
    conn.commit()
    conn.close()

def delete_employee(emp_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()

# -------------------------
# Tasks functions
def fetch_tasks():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM tasks", conn)
    conn.close()
    return df

def add_task(task_name, emp_id, assigned_by, due_date, remarks=""):
    conn = connect_db()
    cursor = conn.cursor()
    created_date = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, remarks, created_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (task_name, emp_id, assigned_by, due_date, remarks, created_date))
    conn.commit()
    conn.close()

# -------------------------
# Mood functions
def fetch_mood_logs():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM mood_logs", conn)
    conn.close()
    return df

def add_mood_entry(emp_id, mood, remarks=""):
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
# Feedback functions
def fetch_feedback():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM feedback", conn)
    conn.close()
    return df

def add_feedback(sender_id, receiver_id, message, rating):
    conn = connect_db()
    cursor = conn.cursor()
    log_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO feedback (sender_id, receiver_id, message, rating, log_date)
        VALUES (?, ?, ?, ?, ?)
    """, (sender_id, receiver_id, message, rating, log_date))
    conn.commit()
    conn.close()
