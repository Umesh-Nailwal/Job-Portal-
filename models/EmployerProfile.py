from extensions import db
class EmployerProfile(db.Model):
    __tablename__="employer_profile"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    company_name = db.Column(db.String(150)) 
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    user = db.relationship(
        "User",
        back_populates="employer_profile"
    )

    job = db.relationship(
        "Job",
        back_populates="employer",
        cascade="all, delete-orphan"
    )