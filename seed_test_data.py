"""
Creates 5 test employer accounts, each with a company profile and 6-7 posted jobs.
Run from the project root (same folder as app.py):

    python seed_test_data.py

Safe to re-run: it skips any employer whose username already exists.
"""
import random
from datetime import date, timedelta

from app import app
from extensions import db
from models.User import User
from models.EmployerProfile import EmployerProfile
from models.Job import Job
from werkzeug.security import generate_password_hash

EMPLOYERS = [
    {"company_name": "Acme Corp",      "industry": "Software",      "location": "Bengaluru, India"},
    {   "company_name": "Globex Inc",     "industry": "Fintech",        "location": "Mumbai, India"},
    {"company_name": "Initech",        "industry": "IT Services",    "location": "Noida, India"},
    { "company_name": "Umbrella Labs",  "industry": "Biotech",        "location": "Hyderabad, India"},
    {"company_name": "Stark Systems",  "industry": "Hardware",       "location": "Pune, India"},
]

JOB_TITLES = [
    "Backend Developer", "Frontend Developer", "Full Stack Engineer",
    "DevOps Engineer", "QA Engineer", "Product Manager",
    "Data Analyst", "UI/UX Designer",
]
EMPLOYMENT_TYPES = ["Full_Time", "Part_Time", "Remote", "Internship"]


def make_job(profile, title):
    min_sal = random.choice([20000, 30000, 40000, 50000])
    return Job(
        employer_id=profile.id,
        title=title,
        # Company name always comes from the employer's own profile,
        # never typed in on the job-post form - keeps it consistent
        # everywhere the job is displayed.
        company=profile.company_name,
        location=profile.location,
        employment_type=random.choice(EMPLOYMENT_TYPES),
        salary_min=min_sal,
        salary_max=min_sal + random.choice([10000, 20000, 30000]),
        description=f"We're looking for a {title} to join {profile.company_name}.",
        vacancies=random.randint(1, 5),
        deadline=date.today() + timedelta(days=random.randint(15, 60)),
        is_active=True,
    )


def run():
    with app.app_context():
        for data in EMPLOYERS:
            name=data["company_name"].replace(" ","")
            email=f"{name}@example.com"
            existing = User.query.filter_by(email=email).first()
            if existing:
                print(f"Skipping {data['company_name']} - already exists")
                continue

            user = User(
                email=email,
                password=generate_password_hash("test123"),
                role="Employer",
            )
            db.session.add(user)
            db.session.flush()  # get user.id before creating the profile

            profile = EmployerProfile(
                user_id=user.id,
                company_name=data["company_name"],
                industry=data["industry"],
                location=data["location"],
                website=f"https://{data['company_name'].lower().replace(' ', '')}.example.com",
                description=f"{data['company_name']} is a {data['industry']} company.",
            )
            db.session.add(profile)
            db.session.flush()  # get profile.id before creating jobs

            num_jobs = random.randint(6, 7)
            titles = random.sample(JOB_TITLES, num_jobs)
            for title in titles:
                db.session.add(make_job(profile, title))

            db.session.commit()
            print(f"Created  {name} with {num_jobs} jobs")

        print("Done. Login with any of the usernames above and password: TestPassword123")


if __name__ == "__main__":
    run()
