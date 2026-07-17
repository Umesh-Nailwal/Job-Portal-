from flask import Flask , render_template, redirect , url_for , Blueprint, request, session , flash, abort
from models.User import User
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from extensions import db
from sqlalchemy import or_
auth_bp=Blueprint("auth",__name__)

@auth_bp.route("/signup",methods=["GET","POST"])
def signup():
    role_allowed=["Job_Seeker","Employer"]
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        role=request.form.get("role")
        
        if role not in role_allowed:
            flash("This role is not allowed")
            return redirect(url_for("auth.signup"))
        #Check if the username and email previously exists in the database 
        
        existing_email=User.query.filter_by(email=email).first()
        if existing_email:
            flash("This email is already exist")
            return render_template("signup.html")
        
        
        new_user=User(
        email=email, role=role, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        session.permanent=True
        session["user_id"]=new_user.id
        session["role"]=new_user.role
        flash("Signup successfully")
        if role=='Employer':
            return redirect(url_for("emp.create_emp_profile"))
        else:
            return redirect(url_for("user.create_user_profile"))
    return render_template("signup.html")
    
@auth_bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
       
        # if this profile exists or not in the database 
        existing_user=User.query.filter(
           ( User.email == email)
        ).first()
        if  existing_user is None:
            flash("Invalid email or password")
            return render_template("login.html")
           
        
        if not check_password_hash(existing_user.password, password):
            flash("Invalid email or password ")
            return render_template("login.html")
        
        
        if not  existing_user.is_active:
            flash("Your user account has been banned")
            return redirect(url_for("auth.login"))
        #Store user data in session 
        session.permanent=True
        session["user_id"]=existing_user.id
        session["role"]=existing_user.role
        
        if session.get("role")=="admin":
            return redirect(url_for("admin.admin_home"))
        elif session.get("role")== "Employer" or session.get("role")=="Job_Seeker":
            return redirect(url_for("home"))
            
    return render_template("login.html")
    
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Logout sucessfully")
    return redirect(url_for("home"))
    
    
    # login required decorator 
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Login required ")
            return redirect(url_for("auth.login"))
        return func(*args,**kwargs)
    return wrapper 
 #job seeker Decorator
def jobseeker_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
             flash("Login required")
             return redirect(url_for("auth.login"))
        if session["role"] != "Job_Seeker":
            flash("Access denied! Routes only for Job Seekers")
            abort(403)

        return func(*args, **kwargs)
    return wrapper
    #employer decorator 
def employer_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
             flash("Login required")
             return redirect(url_for("auth.login"))

        if session["role"] != "Employer":
            flash("Access denied! Employer only routes")
            abort(403)

        return func(*args, **kwargs)

    return wrapper
#admin required decorator 
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
             flash("Login required")
             return redirect(url_for("auth.login"))

        if session.get("role") != "admin":
            flash("Access denied for this route")
            abort(403)

        return f(*args, **kwargs)

    return wrapper