from extensions import db
from datetime import datetime
class User(db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # job_seeker, employer, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    employer_profile = db.relationship(
        "EmployerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    jobseeker_profile= db.relationship(
    "JobSeekerProfile",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan"
    )

    applications = db.relationship(
        "Application",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    bookmarks = db.relationship(
        "Bookmark",
        back_populates="user",
        cascade="all, delete-orphan"
    )
     