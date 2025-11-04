import sqlite3
import pandas as pd

DB_PATH = "data/workforce.db"

# ---------------- Employee Table ----------------
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            Emp_ID INTEGER PRIMARY KEY,
            Name TEXT DEFAULT 'NA',
            Age INTEGER DEFAULT 0,
            Gender TEXT DEFAULT 'NA',
            Department TEXT DEFAULT 'NA',
            Role TEXT DEFAULT 'NA',
            Skills TEXT DEFAULT 'NA',
            Join_Date TEXT DEFAULT '',
            Resign_Date TEXT DEFAULT '',
            Status TEXT DEFAULT 'Active',
            Salary REAL DEFAULT 0.0,
            Location TEXT DEFAULT 'NA'
        )
    ''')
    conn.commit()
    conn.close()

def add_employee(emp):
    # Ensure only Male/Female
    if emp.get('Gender') not in ["Male", "Female"]:
        emp['Gender'] = "Male"
    defaults = {
        'Emp_ID': None,'Name': "NA",'Age': 0,'Gender': "Male",'Department': "NA",
        'Role': "NA",'Skills': "NA",'Join_Date': "",'Resign_Date': "",
        'Status': "Active",'Salary': 0.0,'Location': "NA"
    }
    for key, value in defaults.items():
        if key not in emp or emp[key] is None:
            emp[key] = value
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO employees
        (Emp_ID, Name, Age, Gender, Department, Role, Skills, Join_Date, Resign_Date, Status, Salary, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        emp['Emp_ID'], emp['Name'], emp['Age'], emp['Gender'], emp['Department'],
        emp['Role'], emp['Skills'], emp['Join_Date'], emp['Resign_Date'],
        emp['Status'], emp['Salary'], emp['Location']
    ))
    conn.commit()
    conn.close()

def fetch_employees():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

def delete_employee(emp_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Delete mood logs first
    c.execute("DELETE FROM mood_logs WHERE emp_id=?", (emp_id,))
    # Then delete employee
    c.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()

# ---------------- Mood Tracker ----------------
def initialize_mood_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            mood TEXT,
            log_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_mood_entry(emp_id: int, mood: str, log_date: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mood_logs (emp_id, mood, log_date) VALUES (?, ?, ?)",
        (emp_id, mood, log_date)
    )
    conn.commit()
    conn.close()

def fetch_mood_logs():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM mood_logs", conn)
    conn.close()
    return df
