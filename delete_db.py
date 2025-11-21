import os
db_path = "data/workforce.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✅ Deleted {db_path}")
else:
    print(f"ℹ️ File {db_path} does not exist")
