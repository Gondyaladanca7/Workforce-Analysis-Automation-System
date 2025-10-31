import sqlite3
import pandas as pd

DB_PATH = "data/workforce.db"

def initialize_database():
    """Create the employees table if it doesn't exist."""
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
    """Add a single employee dict to the database."""
    defaults = {
        'Emp_ID': None, 'Name': "NA", 'Age': 0, 'Gender': "NA",
        'Department': "NA", 'Role': "NA", 'Skills': "NA",
        'Join_Date': "", 'Resign_Date': "", 'Status': "Active",
        'Salary': 0.0, 'Location': "NA"
    }
    for k, v in defaults.items():
        if k not in emp or emp[k] is None:
            emp[k] = v
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
    try:
        df = pd.read_sql_query("SELECT * FROM employees", conn)
    except Exception:
        columns = ["Emp_ID","Name","Age","Gender","Department","Role","Skills",
                   "Join_Date","Resign_Date","Status","Salary","Location"]
        df = pd.DataFrame(columns=columns)
    conn.close()
    return df

def delete_employee(emp_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()

# -------------------------
# Mood Tracker Functions
# -------------------------
def initialize_mood_table():
    """Create mood_logs table if not exists."""
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
