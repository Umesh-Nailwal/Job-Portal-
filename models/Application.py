from extensions import db
from datetime import datetime
class Application(db.Model):
    __tablename__="application"
    id = db.Column(db.Integer, primary_key=True)

    job_id = db.Column(db.Integer, db.ForeignKey("job.id"))

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    resume = db.Column(db.String(255))

    status = db.Column(db.String(30), default="Applied")

    applied_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship(
        "User",
        back_populates="applications"
    )

    job = db.relationship(
        "Job",
        back_populates="applications"
    )