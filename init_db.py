# init_db.py
from utils import database as db

if __name__ == "__main__":
    print("🛠️ Initializing database...")
    db.initialize_database()
    print("✅ Database initialized successfully!")
