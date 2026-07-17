from flask import Flask, render_template, url_for, session , Blueprint, request , redirect, flash, abort
from datetime import datetime, timedelta, date
from extensions import db
from models.User import User
from models.Job import Job
from models.Application import Application 
from models.EmployerProfile import EmployerProfile
from Auth.routes import login_required, employer_required
emp_bp=Blueprint("emp",__name__)

APPLICATION_STATUSES = ["Applied", "Under Review", "Shortlisted", "Rejected"]

@emp_bp.route("/post_job", methods=["GET","POST"])
@login_required
@employer_required
def post_job():

    # jobs under someone else's company.
    profile = EmployerProfile.query.filter_by(user_id=session.get("user_id")).first()
    if profile is None:
        flash("Please create your company profile first")
        return redirect(url_for("emp.create_emp_profile"))

    if request.method=="POST":
        job_title=request.form.get("Job_title")
        job_location=request.form.get("Job_location")
        min_salary=request.form.get("min_salary")
        max_salary=request.form.get("max_salary")
        job_mode=request.form.get("Job_mode")
        vacancies =request.form.get("vacancies")
        description =request.form.get("description")
        company = profile.company_name
        
        deadline_raw = request.form.get("deadline")
        if deadline_raw:
            try:
                deadline = datetime.strptime(deadline_raw, "%Y-%m-%d").date()
                if deadline < date.today():
                    flash("Invalid deadline. No past dates allowed. Defaulting to today.")
                    deadline = date.today()
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.")
                return render_template("employer/post_job.html", profile=profile)
            else:
                flash("Deadline is required.")
                return render_template("employer/post_job.html", profile=profile)
    

        new_job=Job(
        employer_id=profile.id,
        title = job_title, 
        company =company,
        location= job_location,
        employment_type =job_mode,
        salary_min= int(min_salary) if min_salary else None,
        salary_max= int(max_salary) if max_salary else None,
        vacancies= int(vacancies) if vacancies else None,
        deadline= deadline,
        description=description)
        
        db.session.add(new_job)
        db.session.commit()
        flash("Job added successfully")
        return redirect(url_for("home"))
    return render_template("employer/post_job.html", profile=profile)

@emp_bp.route("/create_emp_profile", methods=["GET","POST"])
@login_required
@employer_required
def create_emp_profile():
    existing = EmployerProfile.query.filter_by(user_id=session.get("user_id")).first()
    if existing and request.method == "GET":
        return redirect(url_for("emp.emp_profile"))

    if request.method =="POST":
        
        company_name=request.form.get("company_name")
        website =request.form.get("website")
        industry=request.form.get("industry")
        location =request.form.get("location")
        description =request.form.get("description")
        
            #save profile to the database
        new_profile=EmployerProfile(
        user_id=session.get("user_id"),
        company_name=company_name,
        website=website,
        industry=industry,
        location=location,
        description=description)
        
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for("emp.emp_profile"))
    return render_template("employer/create_emp_profile.html")
        
@emp_bp.route("/emp_profile", methods=["GET"])
@login_required
@employer_required
def emp_profile():
    profile = EmployerProfile.query.filter_by(user_id=session.get("user_id")).first()
    if profile is None:
        flash("Please create your company profile first")
        return redirect(url_for("emp.create_emp_profile"))
    return render_template("employer/emp_profile.html", profile=profile, jobs=profile.job)

@emp_bp.route("/edit_emp_profile", methods=["GET","POST"])
@login_required
@employer_required
def edit_emp_profile():
    profile = EmployerProfile.query.filter_by(user_id=session.get("user_id")).first()
    
    if profile is None:
        flash("Please create your company profile first")
        return redirect(url_for("emp.create_emp_profile"))
        
    if request.method=="POST":
        website= request.form.get("website")
        industry =request.form.get("industry")
        location=request.form.get("location")
        description =request.form.get("description")
    
        profile.description=description 
    
        if website:
            profile.website=website
        if industry:
            profile.industry=industry
        if location:
            profile.location =location 
        
        db.session.commit()
        return redirect(url_for("emp.emp_profile"))
    return render_template("employer/edit_emp_profile.html", profile=profile)

@emp_bp.route("/manage_job",methods=["GET","POST"])
@login_required
@employer_required
def manage_job():
    user_id=session.get("user_id")
   
    profile = EmployerProfile.query.filter_by(user_id=session.get("user_id")).first()
    
    if not profile:
        flash("Please create your company profile first")
        return redirect(url_for("emp.create_emp_profile"))
    
    query = Job.query.filter_by(employer_id=profile.id)
    
    keyword=request.args.get("q","").strip()
    location = request.args.get("location","").strip()
    job_mode=request.args.get("job_mode")
    salary=request.args.get("min_salary")
    min_salary=int(salary) if salary else None
    
    if keyword:
        query=query.filter(Job.title.ilike(f"%{keyword}%"))
    if location:
        query=query.filter(Job.location.ilike(f"%{location}%"))
    if job_mode:
        query=query.filter(Job.employment_type.ilike(f"%{job_mode}%"))
    if min_salary is not None:
        query=query.filter(Job.salary_min>=min_salary)
        
    jobs = query.order_by(Job.created_at.desc()).all()
    user_name=profile.company_name
    
   
    return render_template("employer/manage_job.html",jobs=jobs, username=user_name,filters={"q": keyword,
    "location":location, "job_mode": job_mode,
    "min_salary": min_salary} )
    


# edit job details 
@emp_bp.route("/edit_job/<int:job_id>",methods=["GET", "POST"])
@employer_required
def edit_job(job_id):
    user_id = session.get("user_id")
    job_details = Job.query.get_or_404(job_id) # Safer lookup
    if job_details is None:
        abort(404)
       
   #check current login user owned the job
    current_user=db.session.get(User, user_id)
    if  job_details.employer_id != current_user.employer_profile.id:
        abort(403)
    
    if request.method == "POST":
        job_title = request.form.get("Job_title")
        job_location = request.form.get("Job_location")
        min_salary = request.form.get("min_salary")
        max_salary = request.form.get("max_salary")
        job_mode = request.form.get("Job_mode")
        vacancies = request.form.get("vacancies")
        
        # 1. Get the deadline raw string safely
        deadline_raw = request.form.get("deadline")
        
        description = request.form.get("description")
        
        # Apply updates if they are provided
        if job_title:
            job_details.title = job_title
        if job_location:
            job_details.location = job_location
        if job_mode:
            job_details.employment_type = job_mode
        if description:
            job_details.description = description
            
        
        job_details.salary_min = int(min_salary) if min_salary else None
        job_details.salary_max = int(max_salary) if max_salary else None
        job_details.vacancies = int(vacancies) if vacancies else None
        
        # 2. Safely parse and update the deadline
        if deadline_raw:
            try:
                deadline=datetime.strptime(deadline_raw, "%Y-%m-%d").date()
                if deadline<date.today():
                    flash("Invalid deadline deadline set for today. No past dates allowed")
                    deadline=date.today()
                job_details.deadline = deadline 
            except ValueError:
                flash("Invalid date format. Please use YYYY-MM-DD.")
                return render_template("employer/edit_job.html", job_details=job_details)

        # Save changes to the database
        db.session.commit()
        
        flash("Job details edited successfully")
        return redirect(url_for("emp.manage_job"))
    
    return render_template("employer/edit_job.html", job_details=job_details)
    
@emp_bp.route("/delete_jobs/<int:job_id>", methods=["POST"])
@employer_required
def employer_delete_job(job_id):
    job=db.session.get(Job,job_id)
   
    if job is None:
       abort(404)
       
   #check current login user owned the job
    current_user=db.session.get(User, session.get("user_id"))
    if  job.employer_id != current_user.employer_profile.id:
        abort(403)
   #delete the job
    db.session.delete(job)
    db.session.commit()
    flash("Job successfully deleted")
    return redirect(url_for("emp.manage_job"))

@emp_bp.route("/archive_jobs/<int:job_id>", methods=["POST"])
@employer_required
def toggle_archive(job_id):
    job=db.session.get(Job,job_id)
   
    if job is None:
        abort(404)
       
    #check current login user owned the job
    current_user=db.session.get(User, session.get("user_id"))
    if  job.employer_id != current_user.employer_profile.id:
        abort(403)
   #delete the job
    job.is_archived=not job.is_archived
    db.session.commit()
    if job.is_archived:
        flash("Job successfully archived")
    else: 
        flash("Job successfully Unarchived")
    return redirect(url_for("emp.manage_job"))

@emp_bp.route("/toggle_hiring/<int:job_id>", methods=["POST"])
@employer_required
def toggle_hiring(job_id):
    job=db.session.get(Job,job_id)
   
    if job is None:
        abort(404)
       
    #check current login user owned the job
    current_user=db.session.get(User, session.get("user_id"))
    if  job.employer_id != current_user.employer_profile.id:
        abort(403)
   #delete the job
    job.is_filled=not job.is_filled
    db.session.commit()
    if job.is_filled:
        flash("Stopped Hiring")
    else:
        flash("Active hiring")
    return redirect(url_for("emp.manage_job"))
   
# --- APPLICATIONS PIPELINE ---
@emp_bp.route("/applicants", methods=["GET"])
@employer_required
def applicants():
    profile = EmployerProfile.query.filter_by(user_id=session.get("user_id")).first()
    if profile is None:
        flash("Please create your company profile first")
        return redirect(url_for("emp.create_emp_profile"))

    query = Application.query.join(Job).filter(Job.employer_id == profile.id)

    keyword = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    job_id = request.args.get("job_id", "").strip()

    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))
    if status:
        query = query.filter(Application.status == status)
    if job_id.isdigit():
        query = query.filter(Application.job_id == int(job_id))

    applications = query.order_by(Application.applied_at.desc()).all()
    jobs = Job.query.filter_by(employer_id=profile.id).order_by(Job.title).all()

    return render_template(
        "employer/applications.html",
        applications=applications,
        jobs=jobs,
        statuses=APPLICATION_STATUSES,
        filters={"q": keyword, "status": status, "job_id": job_id},
    )


@emp_bp.route("/applications/<int:app_id>/status", methods=["POST"])
@employer_required
def update_application_status(app_id):
    application = db.session.get(Application, app_id)
    if application is None:
        abort(404)

    # check the application belongs to a job posted by the current employer
    current_user = db.session.get(User, session.get("user_id"))
    profile = current_user.employer_profile
    if profile is None or application.job.employer_id != profile.id:
        abort(403)

    new_status = request.form.get("status")
    if new_status not in APPLICATION_STATUSES:
        flash("Invalid status")
    else:
        application.status = new_status
        db.session.commit()
        flash("Application status updated")

    return redirect(url_for(
        "emp.applicants",
        q=request.form.get("q", ""),
        status=request.form.get("status_filter", ""),
        job_id=request.form.get("job_id_filter", ""),
    ))
    
       