
import os

# Pages folder name
pages_dir = "pages"

# Pages to create
files = {
    "1_📊_Dashboard.py": "# Dashboard Page\nimport streamlit as st\nst.title('📊 Workforce Dashboard')",
    "2_📄_Employee_Records.py": "# Employee Records Page\nimport streamlit as st\nst.title('📄 Employee Records')",
    "3_➕_Add_Employee.py": "# Add Employee Page\nimport streamlit as st\nst.title('➕ Add Employee')",
    "4_📁_Reports.py": "# Reports Page\nimport streamlit as st\nst.title('📁 Reports')"
}

# Create pages folder if not exists
if not os.path.exists(pages_dir):
    os.makedirs(pages_dir)

# Create files
for file, content in files.items():
    with open(os.path.join(pages_dir, file), "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Streamlit app pages created successfully!")
