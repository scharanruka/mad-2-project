from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # (Admin, Company, Student)
    is_approved = db.Column(db.Boolean, default=False)  # for Admin approval

    # Relationships
    student_profile = db.relationship("Student", backref="user", uselist=False)
    company_profile = db.relationship("Company", backref="user", uselist=False)


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float)
    branch = db.Column(db.String(50))
    resume_path = db.Column(db.String(255))  # Local path for Docker volume
    resume_text = db.Column(db.Text)  # For AI/OCR extraction results
    skills = db.Column(db.String(500))  # Comma separated for keyword matching
    placement_probability = db.Column(db.Float)  # For ML Prediction storage
    applications = db.relationship("Application", backref="student", lazy=True)


class Company(db.Model):
    __tablename__ = "company"
    id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    industry = db.Column(db.String(100))
    website = db.Column(db.String(150))
    description = db.Column(db.Text)
    drives = db.relationship("PlacementDrive", backref="company", lazy=True)


class PlacementDrive(db.Model):
    __tablename__ = "placement_drive"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text)
    salary = db.Column(db.String(50))
    deadline = db.Column(db.DateTime, nullable=False)
    min_cgpa = db.Column(db.Float, default=0.0)  # Eligibility validation
    status = db.Column(db.String(20), default="Pending")  # Pending/Approved/Closed
    applications = db.relationship("Application", backref="drive", lazy=True)


class Application(db.Model):
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    drive_id = db.Column(
        db.Integer, db.ForeignKey("placement_drive.id"), nullable=False
    )
    date_applied = db.Column(db.DateTime, default=datetime.now(ZoneInfo("localtime")))
    status = db.Column(db.String(50), default="Applied")  # Applied/Shortlisted/Rejected
    feedback = db.Column(db.Text)
