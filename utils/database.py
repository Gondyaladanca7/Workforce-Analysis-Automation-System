# utils/database.py
import sqlite3
import pandas as pd

# -------------------------------
# Database connection
# -------------------------------
DB_PATH = "data/workforce.db"

def create_connection():
    """Create or connect to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    return conn

# -------------------------------
# Initialize database
# -------------------------------
def initialize_database():
    """Create the employees table if it doesn't exist."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            Emp_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Age INTEGER,
            Gender TEXT,
            Department TEXT,
            Join_Date TEXT,
            Resign_Date TEXT,
            Status TEXT,
            Salary REAL,
            Location TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Call to ensure table exists
initialize_database()

# -------------------------------
# CRUD Operations
# -------------------------------
def fetch_employees():
    """Fetch all employee records as a pandas DataFrame."""
    conn = create_connection()
    df = pd.read_sql_query("SELECT * FROM employees", conn)
    conn.close()
    return df

def add_employee(emp):
    """Add a new employee. emp should be a dict with keys matching column names."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO employees (Emp_ID, Name, Age, Gender, Department, Join_Date, Resign_Date, Status, Salary, Location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        emp['Emp_ID'], emp['Name'], emp['Age'], emp['Gender'], emp['Department'],
        emp['Join_Date'], emp['Resign_Date'], emp['Status'], emp['Salary'], emp['Location']
    ))
    conn.commit()
    conn.close()

def delete_employee(emp_id):
    """Delete an employee record by ID."""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees WHERE Emp_ID = ?", (emp_id,))
    conn.commit()
    conn.close()

def update_employee(emp_id, **kwargs):
    """
    Update employee details dynamically.
    Example: update_employee(1, Salary=90000, Status='Resigned')
    """
    if not kwargs:
        return
    conn = create_connection()
    cursor = conn.cursor()
    set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
    values = list(kwargs.values()) + [emp_id]
    cursor.execute(f"UPDATE employees SET {set_clause} WHERE Emp_ID = ?", values)
    conn.commit()
    conn.close()

# -------------------------------
# Import/Export Utilities
# -------------------------------
def import_from_csv(csv_path="data/workforce_data.csv"):
    """Import all data from an existing CSV file (run only once)."""
    conn = create_connection()
    df = pd.read_csv(csv_path)
    df.to_sql("employees", conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()

def export_to_csv(csv_path="data/exported_data.csv"):
    """Export all current employee data to a CSV."""
    df = fetch_employees()
    df.to_csv(csv_path, index=False)
