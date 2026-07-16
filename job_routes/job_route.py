from flask import Flask, render_template, redirect, url_for, Blueprint, request, session, flash, abort
from datetime import date, datetime
from Auth.routes import jobseeker_required, login_required, employer_required
from extensions import db
from models.Job import Job
from models.User import User
from models.Application import Application 

job_bp = Blueprint("job", __name__)

# --- JOB SEARCH PAGE ---
@job_bp.route("/jobs", methods=["GET"])
def jobs():
    today = date.today()
    query = Job.query.filter(
        Job.is_active == True,
        Job.deadline >= today, 
        Job.is_approved == True, 
        Job.is_filled == False, 
        Job.is_archived == False
    )

    # text search - job title (from the homepage search bar)
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
    min_salary = request.args.get("salary", "").strip()
    if min_salary.isdigit():
        query = query.filter(Job.salary_max >= int(min_salary))

    jobs = query.order_by(Job.created_at.desc()).all()

    if "user_id" in session:
        user_id = session.get("user_id")
        user = db.session.get(User, user_id)
    else: 
        user = "Guest"
   
    return render_template(
        "job/jobs.html",
        user=user,
        jobs=jobs,
        filters={"q": keyword, "location": location, "job_mode": job_mode, "min_salary": min_salary},
    )

# --- JOB DETAILS PAGE ---
@job_bp.route("/job_details/<int:job_id>", methods=["GET", "POST"])
def job_details(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        abort(404)
        
    user_id = session.get("user_id")
    applied_job_ids = set()
    
    if user_id:
        applied_job_ids = {
            a[0] for a in db.session.query(Application.job_id).filter_by(user_id=user_id).all()
        }
        
    return render_template("job/job_detail.html", job=job, applied_job_ids=applied_job_ids)

# --- APPLY FOR JOB ---
@job_bp.route("/apply_job", methods=["POST"])
@jobseeker_required
def apply_job():
    job_id = request.form.get("job_id")
    user_id = session.get("user_id")
    today = date.today()

    #Check for valid job to apply
    job = Job.query.filter(
        Job.id == job_id,
        Job.is_active == True, 
        Job.is_approved == True, 
        Job.deadline >= today, 
        ~Job.is_archived, 
        ~Job.is_filled
    ).first()
    
    if job is None:
        flash("This job is no longer available to apply or does not exist.")
        return redirect(url_for("job.jobs"))

    # Check for duplicate application
    already_applied = Application.query.filter_by(
        user_id=user_id, job_id=job_id
    ).first()
    
    if already_applied:
        flash("Already Applied")
        return redirect(url_for("job.job_details", job_id=job_id))

    # Save application
    applicant = Application(job_id=job_id, user_id=user_id, resume=None)
    db.session.add(applicant)
    db.session.commit()
    
    flash("Applied successfully")
    return redirect(url_for("job.job_details", job_id=job_id))
    