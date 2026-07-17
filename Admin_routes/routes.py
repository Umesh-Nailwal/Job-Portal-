from flask import Flask, render_template, url_for, session , Blueprint, request , redirect, flash, abort
from Auth.routes import login_required, admin_required
from extensions import db
from sqlalchemy import select, func
from models.Job import Job
from models.User import User
from models.Application import Application 
from models.JobSeekerProfile import JobSeekerProfile
from models.EmployerProfile import EmployerProfile
from datetime import date


admin_bp=Blueprint("admin",__name__,url_prefix="/admin")

@admin_bp.route("/home",methods=["GET"])
@admin_required
def admin_home():

    total_user= db.session.scalar(select(func.count()).select_from(User))

    total_employers=db.session.scalar(select(func.count()).select_from(EmployerProfile))

    total_jobseeker=db.session.scalar(select(func.count()).select_from(JobSeekerProfile))

    total_application=db.session.scalar(select(func.count()).select_from(Application))


    active_jobs=db.session.scalar(select(func.count()).select_from(Job).where(Job.is_active==True))

    expired_jobs=db.session.scalar(select(func.count()).select_from(Job).where(Job.is_active==False))

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()

    return render_template("admin/admin_home.html", total_user=total_user, total_employers=total_employers, total_jobseeker=total_jobseeker,
    total_application=total_application,
    active_jobs=active_jobs,
    expired_jobs=expired_jobs,
    recent_users=recent_users,
    recent_jobs=recent_jobs)


@admin_bp.route("/users",methods=["GET"])
@admin_required
def manage_users():
    keyword = request.args.get("q","").strip()
    role = request.args.get("role","").strip()

    query = User.query
    if keyword:
        query = query.filter(User.email.ilike(f"%{keyword}%"))
    if role:
        query = query.filter(User.role==role)

    users = query.order_by(User.created_at.desc()).all()
    return render_template("admin/admin_users.html", users=users, filters={"q":keyword,"role":role})


@admin_bp.route("/users/<int:user_id>/toggle_active",methods=["POST"])
@admin_required
def toggle_user_active(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.role=="admin":
        flash("Admin accounts cannot be deactivated")
        return redirect(url_for("admin.manage_users"))

    user.is_active = not user.is_active
    db.session.commit()
    flash(f"{user.email} {'activated' if user.is_active else 'deactivated'}")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/users/<int:user_id>/delete",methods=["POST"])
@admin_required
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if user is None:
        abort(404)
    if user.role=="admin":
        flash("Admin accounts cannot be deleted")
        return redirect(url_for("admin.manage_users"))

    db.session.delete(user)
    db.session.commit()
    flash("User deleted")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/employers",methods=["GET"])
@admin_required
def manage_employers():
    keyword = request.args.get("q","").strip()

    query = EmployerProfile.query
    if keyword:
        query = query.filter(EmployerProfile.company_name.ilike(f"%{keyword}%"))

    employers = query.order_by(EmployerProfile.id.desc()).all()
    return render_template("admin/admin_employers.html", employers=employers, filters={"q":keyword})


@admin_bp.route("/jobs",methods=["GET"])
@admin_required
def manage_jobs():
    keyword = request.args.get("q","").strip()
    status = request.args.get("status","").strip()
    company = request.args.get("company","").strip()

    query = Job.query
    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))
    if company:
        query = query.filter(Job.company==company)
    if status=="active":
        query = query.filter(Job.is_approved==True)
    elif status=="inactive":
        query = query.filter(Job.is_approved==False)

    jobs = query.order_by(Job.created_at.desc()).all()
    return render_template("admin/admin_jobs.html", jobs=jobs, filters={"q":keyword,"status":status,"company":company})


@admin_bp.route("/jobs/<int:job_id>/toggle_active",methods=["POST"])
@admin_required
def toggle_job_approved(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        abort(404)
    job.is_approved = not job.is_approved
    db.session.commit()
    flash(f"Job {'approved' if job.is_approved else 'Dismissed'}")
    return redirect(url_for("admin.manage_jobs"))


@admin_bp.route("/jobs/<int:job_id>/delete",methods=["POST"])
@admin_required
def delete_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        abort(404)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted")
    return redirect(url_for("admin.manage_jobs"))


@admin_bp.route("/applications",methods=["GET"])
@admin_required
def manage_applications():
    keyword = request.args.get("q","").strip()
    status = request.args.get("status","").strip()

    query = Application.query.join(Job)
    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))
    if status:
        query = query.filter(Application.status==status)

    applications = query.order_by(Application.applied_at.desc()).all()
    return render_template("admin/admin_applications.html", applications=applications, filters={"q":keyword,"status":status})
    
    
# manage jobs deadlined jobs that are active

@admin_bp.route("/deadline_jobs",methods=["GET"])
@admin_required
def manage_deadline_jobs():
    keyword = request.args.get("q","").strip()
    status = request.args.get("status","").strip()
    company = request.args.get("company","").strip()

    query = Job.query
    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))
    if company:
        query = query.filter(Job.company==company)
    if status=="active":
        query = query.filter(Job.is_active==True)
    elif status=="inactive":
        query = query.filter(Job.is_active==False)
    today =date.today()

    jobs = query.filter(Job.deadline<today).order_by(Job.created_at.desc()).all()
    return render_template("admin/deadlined_jobs.html", jobs=jobs, filters={"q":keyword,"status":status,"company":company})


@admin_bp.route("/deadline_jobs/<int:job_id>/toggle_active",methods=["POST"])
@admin_required
def toggle_job_active(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        abort(404)
    job.is_active = not job.is_active
    db.session.commit()
    flash(f"Job {'activate' if job.is_approved else 'deactivate'}")
    return redirect(url_for("admin.manage_deadline_jobs"))


@admin_bp.route("/deadline_jobs/<int:job_id>/delete",methods=["POST"])
@admin_required
def delete_deadline_job(job_id):
    job = db.session.get(Job, job_id)
    if job is None:
        abort(404)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted")
    return redirect(url_for("admin.manage_deadline_jobs"))
    
    