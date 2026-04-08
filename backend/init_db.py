import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from models import User, Student, Company, JobPosition, Application
from app import app, db


def seed_data():
    print("Seeding database....")
    with app.app_context():
        password = generate_password_hash("password123")

        # Create Companies (Some approved, some pending)
        google_user = User(email="hr@google.com", password=password, role="company")
        meta_user = User(email="hr@meta.com", password=password, role="company")
        startup_user = User(email="hr@startup.io", password=password, role="company")

        db.session.add_all([google_user, meta_user, startup_user])
        db.session.flush()

        google = Company(
            id=google_user.id,
            name="Google",
            industry="IT",
            website="google.com",
            is_approved=True,
        )
        meta = Company(
            id=meta_user.id,
            name="Meta",
            industry="Social Media",
            website="meta.com",
            is_approved=True,
        )
        startup = Company(
            id=startup_user.id, name="FastAI Startup", industry="AI", is_approved=False
        )

        db.session.add_all([google, meta, startup])
        # -----------------
        # Create Students
        student1_u = User(email="sai@student.com", password=password, role="student")
        student2_u = User(email="rahul@student.com", password=password, role="student")
        db.session.add_all([student1_u, student2_u])
        db.session.flush()

        s1 = Student(
            id=student1_u.id,
            full_name="Sai",
            cgpa=9.5,
            branch="Data Science",
            skills="Python, Flask, VueJS",
        )
        s2 = Student(
            id=student2_u.id,
            full_name="John Doe",
            cgpa=7.2,
            branch="Computer Science",
            skills="Java, SQL",
        )
        db.session.add_all([s1, s2])

        # Create Job Positions (Placement Drives)
        job1 = JobPosition(
            company_id=google.id,
            title="Software Engineer - L3",
            description="Looking for proficient backend developers.",
            salary="24 LPA",
            deadline=datetime.now() + timedelta(days=10),
            min_cgpa=8.0,
            status="ongoing",
        )
        job2 = JobPosition(
            company_id=meta.id,
            title="Data Scientist",
            description="Work on large scale recommendation engines.",
            salary="18 LPA",
            deadline=datetime.now() + timedelta(days=5),
            min_cgpa=7.0,
            status="ongoing",
        )

        db.session.add_all([job1, job2])
        db.session.commit()

        print("Database seeded successfully with Admin, Companies, Students, and Jobs!")


def create_admin():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(role="Admin").first():
            print("Admin user not found, creating one...")
            admin = User(
                email="admin@iitm.ac.in",
                password=generate_password_hash("admin123", method="pbkdf2:sha256"),
                role="admin",
                is_active=True,
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")


if __name__ == "__main__":
    create_admin()
    seed_data()
    print("Database Initialized...")
