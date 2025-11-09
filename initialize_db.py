# initialize_db.py
import random
from datetime import datetime, timedelta, date
from utils import database as db
import sqlite3

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# -------------------------
# Employee data pools
# -------------------------
departments = ["HR", "IT", "Sales", "Finance", "Marketing", "Support"]
roles_by_dept = {
    "HR": ["HR Manager", "HR Executive"],
    "IT": ["Developer", "SysAdmin", "IT Manager"],
    "Sales": ["Sales Executive", "Sales Manager"],
    "Finance": ["Accountant", "Finance Manager"],
    "Marketing": ["Marketing Executive", "Marketing Manager"],
    "Support": ["Support Executive", "Support Manager"]
}
skills_pool = ["Python", "Excel", "SQL", "PowerPoint", "Communication", "Management", "Leadership", "JavaScript"]
names_male = ["John","Alex","Michael","David","Robert","James","William","Daniel","Joseph","Mark"]
names_female = ["Anna","Emily","Sophia","Olivia","Linda","Grace","Chloe","Emma","Sarah","Laura"]
locations = ["Delhi","Mumbai","Bangalore","Chennai","Hyderabad"]

# -------------------------
# Realistic employee generator
# -------------------------
def generate_realistic_employees(n=1000):
    employees = []
    for i in range(1, n+1):
        gender = random.choices(["Male","Female"], weights=[0.65,0.35])[0]
        name = random.choice(names_male if gender=="Male" else names_female)
        dept = random.choice(departments)
        role = random.choice(roles_by_dept[dept])

        # Age correlated with role
        if "Manager" in role:
            age = random.randint(35,60)
        elif "Executive" in role:
            age = random.randint(25,35)
        else:
            age = random.randint(22,30)

        join_date = datetime.now() - timedelta(days=random.randint(365, 365*10))
        status = random.choices(["Active","Resigned"], weights=[0.75,0.25])[0]

        if status == "Resigned":
            min_days = 180
            max_days = (datetime.now() - join_date).days
            resign_date = join_date + timedelta(days=random.randint(min_days, max_days)) if max_days>min_days else join_date
        else:
            resign_date = ""

        # Salary realistic per role
        salary_ranges = {
            "Manager": (90000,150000),
            "Executive": (30000,70000),
            "Developer": (40000,100000),
            "SysAdmin": (40000,90000),
            "Accountant": (35000,80000)
        }
        key = "Manager" if "Manager" in role else ("Executive" if "Executive" in role else role)
        sal_min, sal_max = salary_ranges.get(key, (30000,100000))
        salary = random.randint(sal_min,sal_max)

        location = random.choice(locations)
        skills = ", ".join(random.sample(skills_pool, k=random.randint(2,4)))

        emp = {
            "Emp_ID": i,
            "Name": name,
            "Age": age,
            "Gender": gender,
            "Department": dept,
            "Role": role,
            "Skills": skills,
            "Join_Date": join_date.strftime("%Y-%m-%d"),
            "Resign_Date": resign_date.strftime("%Y-%m-%d") if resign_date else "",
            "Status": status,
            "Salary": salary,
            "Location": location
        }
        employees.append(emp)

    return employees

# -------------------------
# Insert into database
# -------------------------
if __name__ == "__main__":
    db.initialize_all_tables()

    # Clear existing employees
    conn = sqlite3.connect(db.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM employees")
    conn.commit()
    conn.close()

    employees = generate_realistic_employees(1000)
    for emp in employees:
        db.add_employee(emp)

    print("✅ 1000 realistic employees generated successfully!")
    print("Default users: admin/admin123 | manager/manager123 | employee/employee123")
