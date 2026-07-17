from flask import Flask, render_template, url_for, session 
from create_admin import create_admin
from seed_test_data import run as seed_jobs
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from models.User import User
from models.Job import Job
from models.EmployerProfile import EmployerProfile 
from models.Application import Application 
from models.JobSeekerProfile import JobSeekerProfile
from models.Bookmark import Bookmark
from models.Skills import Skills
from config import Config
from extensions import db
from Auth.routes import auth_bp
from User_routes.user_dashbord import user_bp
from Admin_routes.routes import admin_bp
from Employer_routes.routes import emp_bp 
from job_routes.job_route import job_bp
from datetime import datetime, timedelta
#Create flask instance app and start database
app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)

# Set session timeout (e.g., 7 days)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


#Register the blueprints 
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(job_bp)
app.register_blueprint(emp_bp)
app.register_blueprint(admin_bp)
#Landing page routes
@app.route("/")
def home():
    id=session.get('user_id')
    if id:
        user=db.session.get(User,id)
    else:
        user="Guest"
    featured_jobs = Job.query.filter_by(is_active=True).limit(5).all()
    return render_template("index.html", user=user, jobs=featured_jobs)
    
@app.template_filter('format_date')
def format_date(value, format="%d %b"):
    if value is None:
        return ""
    return value.strftime(format)
#Create database id not exist 
with app.app_context():
    db.create_all()
    create_admin()
    seed_jobs()

#start the app
if __name__=="__main__":
    app.run()
