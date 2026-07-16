from extensions import db
from datetime import datetime
class Job(db.Model):
    __tablename__="job"
    id = db.Column(db.Integer, primary_key=True)

    employer_id = db.Column(
        db.Integer,
        db.ForeignKey("employer_profile.id")
    )

    title = db.Column(db.String(150))
    company = db.Column(db.String(150))

    location = db.Column(db.String(100))

    employment_type = db.Column(db.String(30))
    # Full Time
    # Part Time
    # Internship
    # Remote

    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)

    description = db.Column(db.Text)


    vacancies = db.Column(db.Integer)

    deadline = db.Column(db.Date)

    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    is_archived = db.Column(db.Boolean, default=False)     
     # Employer action
    is_approved = db.Column(db.Boolean, default=True)       
    # Admin action
    is_filled = db.Column(db.Boolean,default=False)       # Position filled
    
    employer = db.relationship(
        "EmployerProfile",
        back_populates="job"
    )

    applications = db.relationship(
        "Application",
        back_populates="job",
        cascade="all, delete-orphan"
    )

    bookmarks = db.relationship(
        "Bookmark",
        back_populates="job",
        cascade="all, delete-orphan"
    )
    
    #function to find job posted since
    @property
    def age(self):
        diff = datetime.utcnow() - self.created_at

        if diff.days > 0:
            return f"{diff.days} day(s) ago"

        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours} hour(s) ago"

        minutes = diff.seconds // 60
        if minutes > 0:
            return f"{minutes} minute(s) ago"

        return "Just now"