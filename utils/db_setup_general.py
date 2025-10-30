# utils/db_setup_general.py
# Run this once to create the basic database and general tables

import sqlite3
import os

# Create data folder if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")
    print("✅ Created 'data' folder")

# Connect to SQLite database file
DB_PATH = "data/workforce.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("🛠️ Connected to DB:", DB_PATH)

# Create general tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    department TEXT,
    gender TEXT,
    salary REAL,
    joining_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    date TEXT,
    status TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    task_name TEXT,
    status TEXT,
    deadline TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER,
    category TEXT,
    amount REAL,
    date TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

conn.commit()
conn.close()
print("✅ General database & tables successfully created!")
