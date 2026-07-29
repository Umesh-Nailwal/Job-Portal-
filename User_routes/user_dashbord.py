from flask import Flask , render_template, redirect , url_for , Blueprint, request, session , flash
from extensions import db
from models.User import User
from models.Job import Job
from models.JobSeekerProfile import JobSeekerProfile
from Auth.routes import jobseeker_required
from models.Application import Application 
from services.jobs_services import application_service
user_bp=Blueprint("user",__name__)
    
@user_bp.route("/bookmark",methods=["GET","POST"])
@jobseeker_required
def bookmark():
     return render_template("user/bookmark.html")

@user_bp.route("/applications", methods=["GET"])
@jobseeker_required
def applications():
    applications, filters ,user= application_service()
    return render_template("user/applications.html", applications=applications, filters=filters ,user=user)

@user_bp.route("/user_profile",methods=["GET","POST"])
@jobseeker_required
def user_profile():
    user_id=session.get("user_id")
    profile=JobSeekerProfile.query.filter_by(user_id=user_id).first()
    
    if profile is None:
        return redirect(url_for("user.create_user_profile"))
    return render_template("user/user_profile.html",profile=profile)
    
@user_bp.route("/create_user_profile",methods=["GET","POST"])
@jobseeker_required
def create_user_profile():
    user_id=session.get("user_id")
    existing=JobSeekerProfile.query.filter_by(user_id= user_id).first()
    
    if existing and request.method=="GET":
        return redirect(url_for("user.user_profile"))
    
    if request.method =="POST":
        full_name=request.form.get("name")
        location = request.form.get("location")
        linkedin=request.form.get("linkedin")
        github=request.form.get("github")
        bio=request.form.get("bio")
        
        new_profile=JobSeekerProfile(
        user_id =user_id,
        full_name=full_name,
        location=location,
        linkedin=linkedin,
        github=github,
        bio=bio)
        
        db.session.add(new_profile)
        db.session.commit()
        return redirect(url_for("user.user_profile"))
    return render_template("user/create_user_profile.html")

@user_bp.route("/edit_user_profile",methods=["GET","POST"])
@jobseeker_required
def edit_user_profile():
    user_id=session.get("user_id")
    profile= JobSeekerProfile.query.filter_by(user_id= user_id).first()
    
    if request.method=="POST":
        linkedin=request.form.get("linkedin")
        github=request.form.get("github")
        location =request.form.get("location")
        bio=request.form.get("bio")
        
        profile.bio=bio
        if linkedin:
            profile.linkedin=linkedin
        if github:
            profile.github=github
        if location:
            profile.location =location 
        
        db.session.commit()
        return redirect(url_for("user.user_profile"))
                      
    return render_template("user/edit_user_profile.html", profile=profile)
    

