from utils import database as db

db.initialize_all_tables()
print("Database initialized with default users:")
print("admin / admin123, manager / manager123, employee / employee123")
