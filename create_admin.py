from utils.database import initialize_user_table, add_user

# Make sure the users table exists
initialize_user_table()

# Add a test admin user
add_user(username="admin", password="admin123", role="Admin")

print("Test admin user created: username=admin, password=admin123")
