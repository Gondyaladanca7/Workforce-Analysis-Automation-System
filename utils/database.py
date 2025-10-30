# utils/database.py
import sqlite3
import os
import pandas as pd

DB_PATH = "data/workforce.db"

def initialize_database():
    """Create the employees table if it doesn't exist with all required columns."""
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
    # Insert or replace to avoid duplicate Emp_ID issues
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
    # Ensure all columns exist in query
    try:
        df = pd.read_sql_query("SELECT * FROM employees", conn)
    except Exception:
        # In case table exists but missing columns, return empty with all columns
        columns = ["Emp_ID","Name","Age","Gender","Department","Role","Skills",
                   "Join_Date","Resign_Date","Status","Salary","Location"]
        df = pd.DataFrame(columns=columns)
    conn.close()
    return df

def delete_employee(emp_id):
    """Delete employee by ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM employees WHERE Emp_ID=?", (emp_id,))
    conn.commit()
    conn.close()
