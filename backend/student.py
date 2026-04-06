from datetime import datetime

from flask import jsonify, request, Blueprint
from models import db, User, Student, Company, JobPosition, Application
from flask_jwt_extended import jwt_required, get_jwt_identity
from helpers import save_file

# from tasks import export_applications_csv

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
@student_required
def get_available_jobs():
    search = request.args.get("search", "")
    # Only show 'Approved' jobs that haven't passed the deadline and company approved
    query = JobPosition.query.join(Company, JobPosition.company_id == Company.id).join(
        User, Company.id == User.id
    )

    query = query.filter(
        JobPosition.status == "Approved",
        JobPosition.deadline > datetime.now(),
        User.is_active,
        Company.is_approved,
    )
    if search:
        query = query.filter(
            (JobPosition.title.contains(search))
            | (JobPosition.description.contains(search))
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
            }
            for j in jobs
        ]
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


# Profile Editing ----------------------------------------------------------------------------------
@student_bp.route("/student/profile", methods=["PUT"])
@student_required
def update_student_profile():
    user_id = get_jwt_identity()
    student = Student.query.get(int(user_id))

    # Handle text data
    student.full_name = request.form.get("full_name", student.full_name)
    student.skills = request.form.get("skills", student.skills)
    student.branch = request.form.get("branch", student.branch)

    # Handle Resume Upload
    if "resume" in request.files:
        student.resume_path = save_file(request.files["resume"], "resumes")

    db.session.commit()
    return jsonify({"msg": "Profile updated successfully"})


# Async Tasks ------------------------
@student_bp.route("/student/export-applications", methods=["POST"])
@student_required
def trigger_export():
    user_id = get_jwt_identity()
    # Trigger Celery task asynchronously
    task = ""  # export_applications_csv.delay(int(user_id))
    return jsonify(
        {"msg": "Export started. You will be notified when ready.", "task_id": task.id}
    ), 202
