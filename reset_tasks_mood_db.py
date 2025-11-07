import sqlite3

DB_PATH = "data/workforce.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Drop existing tables (reset)
cursor.execute("DROP TABLE IF EXISTS tasks")
cursor.execute("DROP TABLE IF EXISTS mood")

# Recreate tasks table
cursor.execute("""
CREATE TABLE tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_name TEXT NOT NULL,
    emp_id INTEGER NOT NULL,
    assigned_by TEXT,
    due_date TEXT,
    remarks TEXT,
    status TEXT DEFAULT 'Pending',
    created_date TEXT DEFAULT (date('now'))
)
""")

# Recreate mood table
cursor.execute("""
CREATE TABLE mood (
    mood_id INTEGER PRIMARY KEY AUTOINCREMENT,
    emp_id INTEGER NOT NULL,
    mood TEXT NOT NULL,
    remarks TEXT,
    log_date TEXT DEFAULT (date('now'))
)
""")

conn.commit()
conn.close()
print("Tasks and Mood tables reset successfully!")
