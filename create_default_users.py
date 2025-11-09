from utils import database as db
from utils.auth import hash_password

# Define default users
default_users = [
    {"username": "admin", "password": "admin123", "role": "Admin"},
    {"username": "manager", "password": "manager123", "role": "Manager"},
    {"username": "employee", "password": "employee123", "role": "Employee"},
]

# Make sure the users table exists
db.initialize_user_table()

# Add users to the database
for user in default_users:
    try:
        hashed_pw = hash_password(user["password"])
        db.add_user(user["username"], hashed_pw, user["role"])
        print(f"User '{user['username']}' added successfully.")
    except Exception as e:
        print(f"Failed to add {user['username']}: {e}")
