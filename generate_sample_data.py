# generate_sample_data.py
# Generates 200 sample employee records for testing the Workforce Analytics System

import pandas as pd
import random
from faker import Faker
from utils import database as db

# Initialize Faker
fake = Faker()

# Departments, roles, and skills mapping
departments = ["IT", "HR", "Finance", "Marketing", "Operations"]
roles = {
    "IT": ["Developer", "System Admin", "Data Analyst"],
    "HR": ["Recruiter", "HR Manager", "Trainer"],
    "Finance": ["Accountant", "Financial Analyst", "Auditor"],
    "Marketing": ["SEO Specialist", "Content Writer", "Marketing Manager"],
    "Operations": ["Logistics Coordinator", "Operations Manager", "Planner"]
}
skills_dict = {
    "IT": ["Python", "Java", "SQL", "C++", "JavaScript"],
    "HR": ["Recruitment", "Communication", "Training"],
    "Finance": ["Excel", "Accounting", "Taxation"],
    "Marketing": ["SEO", "Content", "Ads", "Social Media"],
    "Operations": ["Logistics", "Planning", "Coordination"]
}

# Ensure DB is initialized
db.initialize_database()

# Fetch existing employee IDs to avoid duplicates
existing_df = db.fetch_employees()
existing_ids = set(existing_df['Emp_ID'].tolist()) if not existing_df.empty else set()

data = []

for _ in range(200):
    emp_id = max(existing_ids) + 1 if existing_ids else 1
    existing_ids.add(emp_id)

    dept = random.choice(departments)
    role = random.choice(roles.get(dept, ["General"]))
    skills = ";".join(random.sample(skills_dict.get(dept, ["General"]), k=2))
    name = fake.name()
    age = random.randint(22, 45)
    gender = random.choice(["Male", "Female", "Other"])
    join_date = fake.date_between(start_date='-5y', end_date='today')
    status = random.choice(["Active"]*8 + ["Resigned"]*2)
    resign_date = fake.date_between(start_date=join_date, end_date='today') if status=="Resigned" else ""
    salary = random.randint(40000, 120000)
    location = fake.city()

    row = {
        'Emp_ID': emp_id,
        'Name': name,
        'Age': age,
        'Gender': gender,
        'Department': dept,
        'Role': role,
        'Skills': skills,
        'Join_Date': str(join_date),
        'Resign_Date': str(resign_date),
        'Status': status,
        'Salary': float(salary),
        'Location': location
    }
    
    data.append(row)
    db.add_employee(row)

# Optional: save to CSV
df = pd.DataFrame(data)
df.to_csv("data/workforce_data.csv", index=False)

print("✅ 200 sample employees generated and added to database & saved at data/workforce_data.csv")
