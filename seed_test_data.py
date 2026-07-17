"""
Creates 5 test employer accounts, each with a company profile and 6-7 posted jobs.
Safe to re-run: it skips any employer whose email already exists.
"""
import random
from datetime import date, timedelta

from extensions import db
from models.User import User
from models.EmployerProfile import EmployerProfile
from models.Job import Job
from werkzeug.security import generate_password_hash

EMPLOYERS = [
    {"company_name": "Acme Corp",      "industry": "Software",      "location": "Bengaluru, India"},
    {"company_name": "Globex Inc",     "industry": "Fintech",       "location": "Mumbai, India"},
    {"company_name": "Initech",        "industry": "IT Services",   "location": "Noida, India"},
    {"company_name": "Umbrella Labs",  "industry": "Biotech",       "location": "Hyderabad, India"},
    {"company_name": "Stark Systems",  "industry": "Hardware",      "location": "Pune, India"},
]

JOB_TITLES = [
    "Backend Developer", "Frontend Developer", "Full Stack Engineer",
    "DevOps Engineer", "QA Engineer", "Product Manager",
    "Data Analyst", "UI/UX Designer",
]
EMPLOYMENT_TYPES = ["Full_Time", "Part_Time", "Remote", "Internship"]

SEED_PASSWORD = "test123"


def make_job(profile, title):
    min_sal = random.choice([20000, 30000, 40000, 50000])
    return Job(
        employer_id=profile.id,
        title=title,
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


def run(app):
    with app.app_context():
        for data in EMPLOYERS:
            name = data["company_name"].replace(" ", "")
            email = f"{name}@example.com"
            existing = User.query.filter_by(email=email).first()
            if existing:
              
                continue

            user = User(
                email=email,
                password=generate_password_hash(SEED_PASSWORD),
                role="Employer",
            )
            db.session.add(user)
            db.session.flush()

            profile = EmployerProfile(
                user_id=user.id,
                company_name=data["company_name"],
                industry=data["industry"],
                location=data["location"],
                website=f"https://{data['company_name'].lower().replace(' ', '')}.example.com",
                description=f"{data['company_name']} is a {data['industry']} company.",
            )
            db.session.add(profile)
            db.session.flush()

            num_jobs = random.randint(6, 7)
            titles = random.sample(JOB_TITLES, num_jobs)
            for title in titles:
                db.session.add(make_job(profile, title))

            db.session.commit()
from app import app as flask_app
run(flask_app)