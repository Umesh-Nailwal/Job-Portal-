from flask_sqlalchemy import SQLAlchemy
import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-fallback-key")
    SQLALCHEMY_DATABASE_URI = "sqlite:///job_portal.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False