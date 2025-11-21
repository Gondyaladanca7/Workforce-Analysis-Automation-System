# utils/db_setup_app.py
import sqlite3
import os
import hashlib
import datetime

DB_PATH = "data/workforce.db"

# -------------------------
# Helpers
# -------------------------
def connect_db():
    conn = sqlite3.connect(DB_PATH)
    return conn

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

# -------------------------
# Create data folder
# -------------------------
if not os.path.exists("data"):
    os.makedirs("data")
    print("✅ Created 'data' folder")

# -------------------------
# Create all tables
# -------------------------
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
# Seed default admin
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

# -------------------------
# Optional: seed sample employees
# -------------------------
cursor.execute("SELECT COUNT(*) FROM employees")
if cursor.fetchone()[0] == 0:
    sample_employees = [
        (1, "John Doe", 30, "Male", "IT", "Developer", "Python,SQL", "2022-01-01", "", "Active", 50000, "Delhi"),
        (2, "Jane Smith", 28, "Female", "HR", "HR Executive", "Communication,Excel", "2021-06-15", "", "Active", 45000, "Mumbai"),
        (3, "Alice Johnson", 35, "Female", "Finance", "Accountant", "Excel,Accounting", "2020-03-20", "", "Active", 60000, "Bangalore")
    ]
    cursor.executemany("""
        INSERT INTO employees
        (Emp_ID, Name, Age, Gender, Department, Role, Skills, Join_Date, Resign_Date, Status, Salary, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sample_employees)
    conn.commit()
    print("✅ Sample employees added")
else:
    print("ℹ️ Employees already exist")

conn.close()
print("✅ Database setup completed successfully!")
