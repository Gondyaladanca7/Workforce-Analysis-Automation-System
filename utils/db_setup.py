import sqlite3
import os

# Create data folder if not exists
if not os.path.exists("data"):
    os.makedirs("data")
    print("✅ Created 'data' folder")

# Connect to SQLite database file
db_path = "data/workforce.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("🛠️ Connected to DB:", db_path)

# Create tables
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

print("✅ Database & tables successfully created!")
# utils/db_setup.py
# Run this once to create the database and tables

import sqlite3

DB_PATH = "data/workforce.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create employees table
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
    print("🛠️ Connected to DB:", DB_PATH)
    print("✅ Database & tables successfully created!")

if __name__ == "__main__":
    create_database()
