from celery import Celery
from celery.schedules import crontab

from models import db, Student, Application, JobPosition
from app import app

import csv
import pytesseract
from pdf2image import convert_from_path

celery = Celery(
    "tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0"
)

# Scheduled Jobs -------
celery.conf.beat_schedule = {
    "send-daily-reminders": {
        "task": "tasks.send_interview_reminders",
        "schedule": crontab(housr=9, minute=0),  # 9AM
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


@celery.task
def export_applications_csv(student_id):
    with app.app_context():
        apps = Application.query.filter_by(student_id=student_id).all()
        filename = f"exports/applications_student_{student_id}.csv"

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Company", "Job Title", "Status", "Date Applied"])
            for a in apps:
                writer.writerow(
                    [a.job.company.name, a.job.title, a.status, a.date_applied]
                )

        # Here you would trigger a notification/alert
        return filename
