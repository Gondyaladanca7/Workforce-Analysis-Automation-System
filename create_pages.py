import os

# Pages folder name
pages_dir = "pages"

# Pages to create
files = {
    "1_📊_Dashboard.py": "# Dashboard Page\nimport streamlit as st\nst.title('📊 Workforce Dashboard')",
    "2_📄_Employee_Records.py": "# Employee Records Page\nimport streamlit as st\nst.title('📄 Employee Records')",
    "3_➕_Add_Employee.py": "# Add Employee Page\nimport streamlit as st\nst.title('➕ Add Employee')",
    "4_📁_Reports.py": "# Reports Page\nimport streamlit as st\nst.title('📁 Reports')",
    "5_📝_Tasks.py": "# Tasks Page\nimport streamlit as st\nst.title('📝 Tasks')",
    "6_😊_Mood_Tracker.py": "# Mood Tracker Page\nimport streamlit as st\nst.title('😊 Mood Tracker')",
    "admin_dashboard.py": "",
    "employee_dashboard.py": "",
    "manager_dashboard.py": ""
}

# Create pages folder if not exists
if not os.path.exists(pages_dir):
    os.makedirs(pages_dir)

# Create files if not exists
for file_name, content in files.items():
    file_path = os.path.join(pages_dir, file_name)
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

print("✅ All Streamlit pages are created (or already exist).")
