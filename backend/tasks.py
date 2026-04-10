import os
from datetime import datetime, timedelta
from celery import Celery, shared_task
from celery.schedules import crontab

from models import db, Student, Application, JobPosition, Company
from app import app

import csv
import pytesseract
from pdf2image import convert_from_path

# from sqlalchemy.orm import joinedload

from flask import render_template
from weasyprint import HTML

from flask_mail import Mail, Message

celery = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

# Scheduled Jobs -------
celery.conf.beat_schedule = {
    "send-daily-reminders": {
        "task": "tasks.send_interview_reminders",
        "schedule": crontab(hour=9, minute=0),  # 9AM
    },
    "monthly-placement-report": {
        "task": "tasks.generate_monthly_report",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),  # 1st of month
    },
}


@celery.task
def process_resume_ocr(student_id, file_path):
    with app.app_context():
        student = Student.query.get(student_id)
        try:
            # PDF -> Images
            images = convert_from_path(file_path)
            extracted_text = ""
            for img in images:
                extracted_text += pytesseract.image_to_string(img)
            student.resume_text = extracted_text
            db.session.commit()
        except Exception as e:
            return str(e)


@celery.task(name="tasks.send_interview_reminders")
def send_interview_reminders():
    with app.app_context():
        tomorrow = datetime.now() + timedelta(days=1)
        apps = Application.query.filter(
            Application.status == "accepted",
            db.func.date(Application.interview_date) == tomorrow.date(),
        ).all()

        for a in apps:
            msg = Message("Interview Reminder", recipients=[a.student.user.email])
            msg.body = f"Hi {a.student.full_name}, you have an interview for {a.job.title} at {a.job.company.name} tomorrow."
            mail.send(msg)


@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    with app.app_context():
        # Calculate stats for the previous month
        total_placed = Application.query.filter_by(status="selected").count()
        active_drives = JobPosition.query.filter_by(status="ongoing").count()

        # Simple HTML report
        report_html = f"<h1>Monthly Placement Report</h1><p>Students Placed: {total_placed}</p><p>Active Drives: {active_drives}</p>"
        msg = Message("Monthly Placement Activity", recipients=["admin@iitm.ac.in"])
        msg.html = report_html
        mail.send(msg)


@celery.task
def export_applications_csv(student_id):
    with app.app_context():
        apps = (
            Application.query.join(JobPosition)
            .join(Company)
            .join(Student)
            .filter(Application.student_id == student_id)
        ).all()
        filename = f"exports/applications_student_{student_id}.csv"

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Company", "Job Title", "Status", "Date Applied"])
            for a in apps:
                writer.writerow(
                    [
                        a.job_position.company.name,
                        a.job_position.title,
                        a.status,
                        a.date_applied,
                    ]
                )

        # Here you would trigger a notification/alert
        return filename


@celery.task
def export_company_history_csv(company_id):
    with app.app_context():
        jobs = JobPosition.query.filter_by(company_id=company_id).all()
        filename = f"exports/company_history_{company_id}.csv"

        os.makedirs("exports", exist_ok=True)

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Job Title", "Salary", "Status", "Min CGPA", "Total Applicants"]
            )
            for j in jobs:
                writer.writerow(
                    [
                        j.title,
                        j.salary,
                        j.status,
                        j.min_cgpa,
                        Application.query.filter_by(job_id=j.id).count(),
                    ]
                )

        return filename


# Generate Offer Letter --------------------------------------------
@celery.task
def generate_offer_letter_pdf(application_id):
    with app.app_context():
        appl = Application.query.get(application_id)
        appl = (
            Application.query.join(JobPosition)
            .join(Company)
            .join(Student)
            .filter(Application.id == application_id)
        ).first()
        if not appl or appl.status != "selected":
            return "Invalid application for offer letter"

        # Prepare data for the template TODO:
        data = {
            "interview_date": appl.interview_date,
            "student_name": appl.student.full_name,  # appl.student.full_name,
            "company_name": appl.job_position.company.name,  # appl.job.company.name,
            "job_title": appl.job_position.title,  # appl.job.title,
            "salary": appl.job_position.salary,  # appl.job.salary,
            "date": datetime.now().strftime("%d %B %Y"),
        }

        # Render HTML to String
        html_content = render_template("offer_letter_template.html", **data)

        # Save PDF to exports folder
        filepath = os.path.join("exports", f"offer_{application_id}.pdf")
        HTML(string=html_content).write_pdf(filepath)

        return filepath


# Email Service -------------------------------------------------------------------------------------------------------------
mail = Mail(app)
