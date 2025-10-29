# utils/database.py
import sqlite3
import os

DB_PATH = "data/workforce.db"

def initialize_database():
    """Create the employees table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
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
    ''')
    conn.commit()
    conn.close()

def add_employee(emp):
    """Add a single employee dict to the database. Handles missing keys safely."""
    defaults = {
        'Emp_ID': None,
        'Name': "NA",
        'Age': 0,
        'Gender': "NA",
        'Department': "NA",
        'Role': "NA",
        'Skills': "NA",
        'Join_Date': "",
        'Resign_Date': "",
        'Status': "Active",
        'Salary': 0.0,
        'Location': "NA"
    }
    
    # Fill missing keys with defaults
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
    """Fetch all employees as a pandas DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

def delete_employee(emp_id):
    """Delete employee by ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()
