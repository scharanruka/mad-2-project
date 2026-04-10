import os
from datetime import datetime

from flask import jsonify, request, Blueprint, send_from_directory, send_file
from models import db, User, Student, Company, JobPosition, Application
from flask_jwt_extended import jwt_required, get_jwt_identity

# from helpers import save_file
from extensions import cache


student_bp = Blueprint("student", __name__)


# DECORATORS --------------------------------------------------------------------------
def student_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return fn(*args, **kwargs)

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user or user.role != "student":
            return jsonify({"msg": "Student access required"}), 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


# ______________________________________


@student_bp.route("/student/jobs", methods=["GET"])
@cache.cached(timeout=300, query_string=True)
@student_required
def get_available_jobs():
    user_id = get_jwt_identity()
    search = request.args.get("search", "")
    # Only show 'Approved' jobs that haven't passed the deadline and company approved
    query = JobPosition.query.join(Company, JobPosition.company_id == Company.id).join(
        User, Company.id == User.id
    )

    query = query.filter(
        JobPosition.status == "ongoing",
        JobPosition.deadline > datetime.now(),
        User.is_active,
        Company.is_approved,
    )
    if search:
        query = query.filter(
            (JobPosition.title.contains(search))
            | (JobPosition.description.contains(search))
            | (Company.name.contains(search))
        )

    jobs = query.all()
    return jsonify(
        [
            {
                "id": j.id,
                "title": j.title,
                "company_name": j.company.name,
                "salary": j.salary,
                "min_cgpa": j.min_cgpa,
                "deadline": j.deadline.strftime("%Y-%m-%d"),
                "description": j.description,
                "has_applied": True
                if Application.query.filter(Application.student_id == user_id)
                .filter(Application.job_id == j.id)
                .all()
                else False,
            }
            for j in jobs
        ]
    )


@student_bp.route("/student/details", methods=["GET"])
@student_required
def get_student_details():
    user_id = get_jwt_identity()
    student = Student.query.get_or_404(int(user_id))
    return jsonify(
        {
            "full_name": student.full_name,
            "branch": student.branch,
            "skills": student.skills,
            "resume_path": student.resume_path,
        }
    )


@student_bp.route("/student/apply/<int:job_id>", methods=["POST"])
@student_required
def apply_to_job(job_id):
    user_id = get_jwt_identity()
    student = Student.query.get(int(user_id))
    job = JobPosition.query.get_or_404(job_id)

    # 1. Check for duplicate application
    existing = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
    if existing:
        return jsonify({"msg": "You have already applied to this drive"}), 400

    # 2. Eligibility Check (CGPA)
    if student.cgpa < job.min_cgpa:
        return jsonify(
            {"msg": f"Ineligible: Minimum CGPA required is {job.min_cgpa}"}
        ), 403

    new_app = Application(student_id=student.id, job_id=job_id, status="Applied")
    db.session.add(new_app)
    db.session.commit()
    return jsonify({"msg": "Application submitted successfully!"}), 201


# Applications -----------------------------------------------------------------
@student_bp.route("/student/applications", methods=["GET"])
# @cache.cached(timeout=3600)
@student_required
def get_my_applications():
    user_id = get_jwt_identity()
    appls = (
        Application.query.join(JobPosition)
        .join(Company)
        .filter(Application.student_id == user_id)
    )
    appls = appls.all()
    data = [
        {
            "id": a.id,
            "status": a.status,
            "feedback": a.feedback,
            "job_title": a.job_position.title,
            "company": a.job_position.company.name,
        }
        for a in appls
    ]
    return jsonify(data)


@student_bp.route(
    "/student/applications/<int:appl_id>/generate-offer", methods=["POST"]
)
@student_required
def trigger_offer_pdf(appl_id):
    application = Application.query.get_or_404(appl_id)
    if application.status != "selected":
        return jsonify({"msg": "Offer letter not available"}), 403

    from tasks import generate_offer_letter_pdf

    task = generate_offer_letter_pdf.delay(appl_id)
    return jsonify({"task_id": task.id, "msg": "Generating your offer letter..."}), 202


@student_bp.route("/student/download-offer/<int:app_id>", methods=["GET"])
@student_required
def download_offer(app_id):
    return send_from_directory("exports", f"offer_{app_id}.pdf", as_attachment=True)


# Profile Editing ----------------------------------------------------------------------------------


@student_bp.route("/student/profile", methods=["PUT"])
@student_required
def update_student_profile():
    from app import app

    user_id = get_jwt_identity()
    student = Student.query.get(int(user_id))

    # Handle text data
    student.full_name = request.form.get("full_name", student.full_name)
    student.skills = request.form.get("skills", student.skills)
    student.branch = request.form.get("branch", student.branch)

    # Handle Resume Upload
    if "resume" in request.files:
        file = request.files["resume"]
        filename = f"resume_std_{student.id}.pdf"
        upload_dir = os.path.join(app.config["UPLOAD_FOLDER"], "resumes", filename)

        os.makedirs(upload_dir, exist_ok=True)

        path = os.path.join(upload_dir, filename)

        file.save(path)
        student.resume_path = path
        # Trigger background OCR
        # from tasks import process_resume_ocr

        # process_resume_ocr.delay(student.id, path)

    db.session.commit()
    return jsonify({"msg": "Profile updated successfully"})


# -------------------------


# Async Tasks ------------------------
@student_bp.route("/student/export-applications", methods=["POST"])
@student_required
def trigger_export():
    user_id = get_jwt_identity()
    from tasks import export_applications_csv

    task = export_applications_csv.delay(user_id)
    return jsonify(
        {"msg": "Export started. You will be notified when ready.", "task_id": task.id}
    ), 202


@student_bp.route("/student/download-export/<task_id>", methods=["GET"])
@student_required
def download_export(task_id):
    # Retrieve the student ID from JWT to ensure they only download their own files
    user_id = get_jwt_identity()
    filename = f"applications_student_{user_id}.csv"

    # Check if file exists in your exports volume
    if not os.path.exists(os.path.join("exports", filename)):
        return jsonify({"msg": "File not found"}), 404

    return send_from_directory("exports", filename, as_attachment=True)
