
from models.User import  User
from extensions import db
from werkzeug.security import generate_password_hash

def create_admin():
    email="admin@example.com"
    admin = User(
        
        email=email,
     password=generate_password_hash("admin123"),
        role="admin" )
    if not User.query.filter_by(email=email).first():

        db.session.add(admin)
        db.session.commit()

   