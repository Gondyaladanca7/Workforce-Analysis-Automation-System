"""
preflight_check.py
-----------------
Checks for common errors before running Streamlit:
- Database connection and tables
- Required utils files
- Required columns in employee table
- Dummy data presence
- Streamlit version check
"""

import os
import sys
import sqlite3
import importlib.util
import pandas as pd
import streamlit as st

# -------------------------
# 1️⃣ Check required utils files
# -------------------------
required_utils = [
    "utils/auth.py",
    "utils/database.py",
    "utils/analytics.py",
    "utils/pdf_export.py"
]

print("Checking required utils files...")
for file in required_utils:
    if not os.path.exists(file):
        print(f"❌ Missing file: {file}")
    else:
        print(f"✅ Found: {file}")

# -------------------------
# 2️⃣ Check Streamlit version
# -------------------------
print("\nChecking Streamlit version...")
try:
    import streamlit as st
    ver = tuple(map(int, st.__version__.split(".")))
    if ver < (1, 24, 0):
        print(f"⚠️ Streamlit version is {st.__version__}. Recommended >= 1.24.0")
    else:
        print(f"✅ Streamlit version: {st.__version__}")
except Exception as e:
    print(f"❌ Streamlit not installed: {e}")

# -------------------------
# 3️⃣ Check database and tables
# -------------------------
DB_PATH = "data/workforce.db"
required_tables = ["employees", "moods", "tasks", "users"]

print("\nChecking database and tables...")
if not os.path.exists(DB_PATH):
    print(f"❌ Database not found at {DB_PATH}. Run initialize_db.py first.")
else:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        for table in required_tables:
            if table not in tables:
                print(f"❌ Missing table: {table}")
            else:
                print(f"✅ Found table: {table}")
        conn.close()
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

# -------------------------
# 4️⃣ Check employee table columns
# -------------------------
required_columns = [
    "Emp_ID","Name","Age","Gender","Department","Role","Skills",
    "Join_Date","Resign_Date","Status","Salary","Location"
]

print("\nChecking employee table columns and dummy data...")
if os.path.exists(DB_PATH):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM employees LIMIT 1", conn)
        for col in required_columns:
            if col not in df.columns:
                print(f"❌ Missing column in employees table: {col}")
            else:
                print(f"✅ Column exists: {col}")
        if df.empty:
            print("⚠️ Employees table is empty. Add dummy data or upload CSV.")
        else:
            print(f"✅ Employees table has {len(df)} record(s).")
        conn.close()
    except Exception as e:
        print(f"❌ Error reading employees table: {e}")

# -------------------------
# 5️⃣ Check authentication functions
# -------------------------
print("\nChecking auth.py functions...")
auth_file = "utils/auth.py"
functions = ["require_login", "logout_user", "show_role_badge"]
if os.path.exists(auth_file):
    spec = importlib.util.spec_from_file_location("auth", auth_file)
    auth = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(auth)
    for func in functions:
        if not hasattr(auth, func):
            print(f"❌ Missing function in auth.py: {func}")
        else:
            print(f"✅ Function exists: {func}")
else:
    print(f"❌ auth.py not found.")

print("\n✅ Pre-flight check complete!")
print("If all checks are ✅, Streamlit should run without critical errors.")
