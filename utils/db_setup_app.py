# utils/db_setup_app.py
# Run this to create the app-specific employee table

import sqlite3

DB_PATH = "data/workforce.db"

def create_app_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create detailed employees table
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
    print("✅ App-specific tables successfully created!")

if __name__ == "__main__":
    create_app_tables()

