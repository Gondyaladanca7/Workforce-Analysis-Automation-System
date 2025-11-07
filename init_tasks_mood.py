# init_tasks_mood.py
import sqlite3
import os

# -------------------------
# Ensure data folder exists
# -------------------------
DB_FOLDER = "data"
DB_PATH = os.path.join(DB_FOLDER, "workforce.db")
os.makedirs(DB_FOLDER, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# -------------------------
# Create tasks table (if not exists)
# -------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    emp_id INTEGER NOT NULL,
    due_date TEXT,
    remarks TEXT,
    status TEXT DEFAULT 'Pending'
)
""")

# -------------------------
# Create mood table (if not exists)
# -------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS mood (
    mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    mood TEXT NOT NULL,
    remarks TEXT,
    log_date TEXT DEFAULT (date('now'))
)
""")

conn.commit()
conn.close()
print("Tasks and Mood tables initialized successfully!")
