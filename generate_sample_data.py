# generate_sample_data.py
# Generates 200 sample employee records for testing the Workforce Analytics System.
# Saves the data as data/workforce_data.csv

import pandas as pd
import random
from faker import Faker

# Initialize Faker for random names, cities, and dates
fake = Faker()

# Possible departments and roles
departments = ["IT", "HR", "Finance", "Marketing", "Operations"]
roles = ["Developer", "Analyst", "Manager", "Recruiter", "Accountant"]

# Skills mapped by department
skills_dict = {
    "IT": ["Python", "Java", "SQL", "C++", "JavaScript"],
    "HR": ["Recruitment", "Communication", "Training"],
    "Finance": ["Excel", "Accounting", "Taxation"],
    "Marketing": ["SEO", "Content", "Ads", "Social Media"],
    "Operations": ["Logistics", "Planning", "Coordination"]
}

data = []

# Generate 200 employee records
for emp_id in range(1, 201):
    dept = random.choice(departments)
    role = random.choice(roles)
    skills = ";".join(random.sample(skills_dict.get(dept, ["General"]), k=2))  # pick 2 random skills
    name = fake.name()
    age = random.randint(22, 45)
    join_date = fake.date_between(start_date='-5y', end_date='today')  # joined in last 5 years
    status = random.choice(["Active"]*8 + ["Resigned"]*2)  # ~20% resigned
    resign_date = fake.date_between(start_date=join_date, end_date='today') if status=="Resigned" else ""
    salary = random.randint(40000, 120000)
    location = fake.city()
    
    data.append([emp_id, name, age, dept, role, skills, join_date, resign_date, status, salary, location])

# Convert list to pandas DataFrame
df = pd.DataFrame(
    data, 
    columns=["Emp_ID","Name","Age","Department","Role","Skills","Join_Date","Resign_Date","Status","Salary","Location"]
)

# Save CSV file in data/ folder
df.to_csv("data/workforce_data.csv", index=False)

print("✅ 200 sample employees generated at data/workforce_data.csv")
