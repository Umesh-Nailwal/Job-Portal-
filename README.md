# Job Portal

A Flask-based job portal where employers can post jobs and job seekers can browse, bookmark, and apply. Includes an admin panel for managing users, employers, jobs, and applications.

**Live demo:** https://job-portal-bu8x.onrender.com/
**Repo:** https://github.com/Umesh-Nailwal/Job-Portal-

---

## Features

- Role-based accounts: Job Seeker, Employer, Admin
- Employers can post, edit, archive, and delete jobs
- Job seekers can search jobs and apply
- Employers can review applicants and update application status
- Admin dashboard for managing users, employers, jobs, and applications

## Tech Stack

- **Backend:** Flask, Flask-SQLAlchemy
- **Database:** SQLite (dev), easily swappable for PostgreSQL in production
- **Auth:** Session-based, passwords hashed with Werkzeug
- **Deployment:** Gunicorn + Render

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Umesh-Nailwal/Job-Portal-.git
cd Job-Portal-
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set environment variables

Create a `.env` file in the project root (never commit this file — it's already in `.gitignore`):

```
SECRET_KEY=replace-with-a-long-random-string
FLASK_DEBUG=1
```

Generate a strong secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize the database

The app creates tables automatically on first run via `db.create_all()`. To also create an admin account:

```bash
python create_admin.py
```

Optionally load sample employers and jobs:

```bash
python seed_test_data.py
```

### 6. Run the app

```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

---

## Project Structure

```
Job portal/
├── app.py                  # App factory / entry point, landing route
├── config.py                # App configuration (reads from environment)
├── extensions.py             # Shared SQLAlchemy instance
├── create_admin.py           # One-off script to create an admin user
├── seed_test_data.py         # One-off script to load sample data
├── Auth/                     # Signup, login, logout, role decorators
├── Admin_routes/              # Admin dashboard routes
├── Employer_routes/           # Employer profile, job posting, applicants
├── User_routes/                # Job seeker profile, applications, bookmarks
├── job_routes/                 # Public job search and apply routes
├── models/                     # SQLAlchemy models
├── templates/                   # Jinja2 templates
└── static/                      # CSS
```

---

## Deploying to Render

1. Push your code to GitHub (make sure `.env` and `instance/*.db` are **not** committed).
2. Create a new Web Service on Render, connect your repo.
3. Set the build command: `pip install -r requirements.txt`
4. Set the start command: `gunicorn app:app` (already defined in `Procfile`)
5. Under **Environment**, add `SECRET_KEY` with a securely generated value. Leave `FLASK_DEBUG` unset (or `0`) in production.

---
## Known Limitations

- No automated tests yet
- Bookmark feature is a stub (`/bookmark` route exists but has no add/remove logic)
- No file upload for resumes or company logos

## License

Add your license of choice here (MIT is a common default for course projects).
