from app import app
from models.User import  User
from extensions import db
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        
        email="admin@example.com",
        password=generate_password_hash("admin123"),
        role="admin"
    )

    db.session.add(admin)
    db.session.commit()

    print("Admin created successfully!")