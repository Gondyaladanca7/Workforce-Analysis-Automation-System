import sqlite3
import pandas as pd

DB_PATH = "data/workforce.db"

# -------------------- Database Initialization --------------------
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Employees table
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

def initialize_mood_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS mood_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            mood TEXT,
            log_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def initialize_task_table():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            emp_id INTEGER,
            assigned_by TEXT,
            due_date TEXT,
            status TEXT DEFAULT 'Pending',
            remarks TEXT DEFAULT '',
            created_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# -------------------- Employees CRUD --------------------
def add_employee(emp):
    defaults = {
        'Emp_ID': None,'Name': "NA",'Age': 0,'Gender': "NA",'Department': "NA",
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
    # Delete employee
    c.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    # Delete mood logs related
    c.execute("DELETE FROM mood_logs WHERE emp_id=?", (emp_id,))
    # Delete tasks related
    c.execute("DELETE FROM tasks WHERE emp_id=?", (emp_id,))
    conn.commit()
    conn.close()

# -------------------- Mood Tracker --------------------
def add_mood_entry(emp_id: int, mood: str, log_date: str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
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

# -------------------- Task Management --------------------
def add_task(task_name: str, emp_id: int, assigned_by: str, due_date: str, status="Pending", remarks=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    created_date = pd.Timestamp.today().strftime("%Y-%m-%d")
    c.execute('''
        INSERT INTO tasks (task_name, emp_id, assigned_by, due_date, status, remarks, created_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (task_name, emp_id, assigned_by, due_date, status, remarks, created_date))
    conn.commit()
    conn.close()

def fetch_tasks(emp_id=None):
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM tasks"
    if emp_id is not None:
        query += f" WHERE emp_id={emp_id}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_task_status(task_id: int, status: str, remarks=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        UPDATE tasks SET status=?, remarks=? WHERE task_id=?
    ''', (status, remarks, task_id))
    conn.commit()
    conn.close()
