from extensions import db
class JobSeekerProfile(db.Model):
    __tablename__="jobseekerprofile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    full_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    linkedin = db.Column(db.String(255))
    github = db.Column(db.String(255))
    
    user = db.relationship(
        "User",
        back_populates="jobseeker_profile",
        uselist=False
    )
    
