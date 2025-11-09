import os

base_path = os.getcwd()

folders = [
    "data",
    "utils",
    "pages",
    "assets",
    ".devcontainer"
]

files = {
    "utils/__init__.py": "",
    "utils/database.py": "# database.py placeholder\n",
    "utils/auth.py": "# auth.py placeholder\n",
    "initialize_db.py": (
        "# initialize all tables\n"
        "from utils import database as db\n\n"
        "db.initialize_all_tables()\n"
        "print('Database initialized')"
    ),
    "app.py": "# Main Streamlit app placeholder\n"
}

for folder in folders:
    os.makedirs(os.path.join(base_path, folder), exist_ok=True)

for filepath, content in files.items():
    path = os.path.join(base_path, filepath)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

print("✅ All folders and placeholder files created successfully.")
