from flask import Flask, render_template, redirect, url_for, Blueprint, request, session, flash, abort
from datetime import date, datetime
from Auth.routes import jobseeker_required, login_required, employer_required
from extensions import db
from models.Job import Job
from models.User import User
from models.Application import Application 
from services.jobs_services import show_jobs
job_bp = Blueprint("job", __name__)

# --- JOB SEARCH PAGE ---
@job_bp.route("/jobs", methods=["GET"])
def jobs():
    jobs , filters ,user= show_jobs()
    return render_template(
        "job/jobs.html",
        jobs=jobs,
        filters=filters,
        user=user
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
@jobseeker_required
@job_bp.route("/apply_job", methods=["POST"])
def apply_job():
    if not "user_id" in session:
        flash("Login to apply for the job","info")
        return redirect(url_for("auth.login"))
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
    
    flash("Applied successfully","success")
    return redirect(url_for("job.job_details", job_id=job_id))
    