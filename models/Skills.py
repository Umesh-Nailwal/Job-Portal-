from extensions import db
class Skills(db.Model):
    __tablename__="skills"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    skill_name = db.Column(db.String(50))