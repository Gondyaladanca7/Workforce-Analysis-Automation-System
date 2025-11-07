# utils/database.py (only these functions)

def add_task(self, task_name, emp_id, due_date=None, remarks=""):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (task_name, emp_id, due_date, remarks)
        VALUES (?, ?, ?, ?)
    """, (task_name, emp_id, due_date, remarks))
    conn.commit()
    conn.close()

def fetch_tasks(self, emp_id=None):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    if emp_id:
        cursor.execute("SELECT * FROM tasks WHERE emp_id=?", (emp_id,))
    else:
        cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return rows



# Mood
def log_mood(self, emp_id, mood, remarks=None):
    conn = self.connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO mood (emp_id, mood, remarks) VALUES (?, ?, ?)",
        (emp_id, mood, remarks)
    )
    conn.commit()
    conn.close()

def fetch_mood(self, emp_id):
    conn = self.connect()
    df = pd.read_sql_query("SELECT * FROM mood WHERE emp_id=?", conn, params=(emp_id,))
    conn.close()
    return df

def fetch_all_mood(self):
    conn = self.connect()
    df = pd.read_sql_query("SELECT * FROM mood", conn)
    conn.close()
    return df
