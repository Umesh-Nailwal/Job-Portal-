from flask import session, request
from models.Application import Application
from models.User import User
from models.Job import Job
from models.JobSeekerProfile import JobSeekerProfile
from extensions import db
from datetime import date , datetime
# Apply filters for jobs
def job_filters(query):
    keyword = request.args.get("q", "").strip()
    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))

    # location - typed or picked from a dropdown
    location = request.args.get("location", "").strip()
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    # employment type - exact match against one of the enum-like values
    job_mode = request.args.get("job_mode", "").strip()
    if job_mode:
        query = query.filter(Job.employment_type == job_mode)

    # minimum salary - only show jobs whose max salary clears this bar
    min_salary = request.args.get("min_salary", "").strip()
    if min_salary.isdigit():
        query = query.filter(Job.salary_max >= int(min_salary))
    filters={
    "q": keyword, "location": location, "job_mode": job_mode, "min_salary": min_salary
    }
    return query,filters

# Service for application route
def application_service():
     #shows the user applied jobs 
     applications =Application.query.join(Job).filter(Application.user_id==session.get("user_id"))
     #show username
     user_id= session.get("user_id")
     if "user_id" in session:
         user= db.session.query(JobSeekerProfile.full_name).filter_by(user_id=user_id).scalar()
     else:
         user="User"
     #apply filter 
     query,filters = job_filters(applications)
     applications= query
     return (applications , filters, user)
def show_jobs():
    today = date.today()
    query = Job.query.filter(
        Job.is_active == True,
        Job.deadline >= today, 
        Job.is_approved == True, 
        Job.is_filled == False, 
        Job.is_archived == False
    )
    query,filters= job_filters(query)
    jobs = query.order_by(Job.created_at.desc()).limit(10).offset(0).all()
    user_id= session.get("user_id")
    if "user_id" in session:
         user= db.session.query(JobSeekerProfile.full_name).filter_by(user_id=user_id).scalar()
    else:
         user="User"
    return (jobs, filters, user)
  
