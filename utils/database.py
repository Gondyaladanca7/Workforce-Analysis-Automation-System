import sqlite3
import pandas as pd
import datetime
import hashlib
import os

DB_PATH = "data/workforce.db"

# -------------------------
# Helpers
# -------------------------
def connect_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def hash_password(password):
    """Return SHA256 hash of password"""
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------
# Initialize all tables
# -------------------------
def initialize_all_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Employees table
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

    # Tasks table
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

    # Mood logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mood_logs (
        mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id INTEGER,
        mood TEXT,
        remarks TEXT,
        log_date TEXT
    )
    """)

    # Feedback table
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

    # -------------------------
    # Add default admin
    # -------------------------
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", hash_password("admin123"), "Admin")
        )
        conn.commit()
        print("✅ Default admin user created: username='admin', password='admin123'")
    else:
        print("ℹ️ Admin user already exists")

    conn.close()
    print("✅ All tables initialized successfully!")

# -------------------------
# Users functions
# -------------------------
def get_user_by_username(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "password": row[2], "role": row[3]}
    return None

def add_user(username, password, role="Employee"):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hash_password(password), role)
    )
    conn.commit()
    conn.close()

# -------------------------
# Employees
# -------------------------
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
    sql = f"INSERT OR REPLACE INTO employees ({columns}) VALUES ({placeholders})"
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
# Tasks
# -------------------------
def fetch_tasks():
    conn = connect_db()
    df = pd.read_sql("SELECT * FROM tasks", conn)
    conn.close()
    return df

def add_task(task_dict):
    conn = connect_db()
    cursor = conn.cursor()
    created_date = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, status, remarks, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        task_dict["task_name"],
        task_dict["emp_id"],
        task_dict.get("assigned_by",""),
        task_dict.get("due_date",""),
        task_dict.get("status","Pending"),
        task_dict.get("remarks",""),
        created_date
    ))
    conn.commit()
    conn.close()

# -------------------------
# Mood logs
# -------------------------
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
# Feedback
# -------------------------
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
