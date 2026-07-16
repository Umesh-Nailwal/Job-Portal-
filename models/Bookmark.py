from extensions import db
class Bookmark(db.Model):
    __tablename__="savedjob"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id"))

    job_id = db.Column(db.Integer,
                       db.ForeignKey("job.id"))
    user = db.relationship(
        "User",
        back_populates="bookmarks"
    )

    job = db.relationship(
        "Job",
        back_populates="bookmarks"
    )