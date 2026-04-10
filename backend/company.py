from datetime import datetime

from flask import jsonify, request, Blueprint, send_from_directory, send_file
from models import db, User, Student, Company, JobPosition, Application
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions import cache
from sqlalchemy.orm import joinedload

company_bp = Blueprint("company", __name__)


# DECORATORS --------------------------------------------------------------------------
def company_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return fn(*args, **kwargs)

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user or user.role != "company":
            return jsonify({"msg": "Company access required"}), 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


# ------------------------------------------------------------------------------------
@company_bp.route("/company/details", methods=["GET", "POST"])
@company_required
def get_change_company_details():
    if request.method == "POST":
        # change details
        return jsonify({"msg": "Profile updated!"})
    else:
        user_id = get_jwt_identity()
        company = Company.query.filter_by(id=user_id).first()
        return jsonify(
            {"id": company.id, "name": company.name, "industry": company.industry}
        )


@company_bp.route("/company/jobs", methods=["POST"])
@company_required
def create_job():
    data = request.json
    user_id = get_jwt_identity()
    company = Company.query.filter_by(id=user_id).first()

    new_job = JobPosition(
        company_id=company.id,
        title=data["title"],
        description=data["description"],
        salary=data["salary"],
        min_cgpa=data.get("min_cgpa", 0.0),
        deadline=datetime.strptime(data["deadline"], "%Y-%m-%d"),
        status="ongoing",
    )
    db.session.add(new_job)
    db.session.commit()

    return jsonify({"msg": "Job posting created"}), 201


@company_bp.route("/company/jobs", methods=["GET"])
@company_required
def get_company_jobs():
    user_id = get_jwt_identity()
    company = Company.query.filter_by(id=user_id).first()
    jobs = JobPosition.query.filter_by(company_id=company.id).all()
    return jsonify(
        [
            {
                "id": j.id,
                "title": j.title,
                "status": j.status,
                "applicant_count": Application.query.filter_by(job_id=j.id).count(),
            }
            for j in jobs
        ]
    )


# APPLCIATIONS --------------------------------------------------------------------------
@company_bp.route("/company/application/<int:appl_id>/", methods=["GET"])
@company_required
def get_appl_details(appl_id):
    appl = Application.query.options(
        joinedload(Application.student),
        joinedload(Application.job_position).joinedload(JobPosition.company),
    ).get_or_404(appl_id)
    return jsonify(
        {
            "application_id": appl_id,
            "status": appl.status,
            "student_name": appl.student.full_name,
            "branch": appl.student.branch,
            "job_title": appl.job_position.title,
        }
    )


@company_bp.route("/company/application/<int:appl_id>/status", methods=["POST"])
@company_required
def update_appl_status(appl_id):
    data = request.json  # Expecting {"status": "Shortlisted", "feedback": "..."}
    application = Application.query.get_or_404(appl_id)
    application.status = data["status"]
    # TODO: Feedback here
    db.session.commit()
    return jsonify({"msg": f"Application marked as {application.status}"})


@company_bp.route("/company/application/<int:appl_id>/process", methods=["POST"])
@company_required
def process_application(appl_id):
    data = request.json
    # { "status": "Shortlisted", "feedback": "Great resume", "interview_date": "2026-04-15T10:00" }
    application = Application.query.get_or_404(appl_id)

    application.status = str(data.get("status", application.status)).lower()
    application.feedback = str(data.get("feedback", application.feedback)).lower()
    if data.get("interview_date"):
        application.interview_date = datetime.fromisoformat(data["interview_date"])

    db.session.commit()

    # TODO: Trigger an async notification task if you have it set up
    return jsonify({"msg": f"Application updated to {application.status}"})


@company_bp.route("/company/application/<int:appl_id>/offer", methods=["POST"])
@company_required
def generate_offer(appl_id):
    application = Application.query.get_or_404(appl_id)
    application.status = "selected"  # Final stage
    db.session.commit()
    # In a later milestone, you can hook this into a PDF generator
    return jsonify({"msg": "Offer extended to student"})


# -------------------------------------------------------------------------------------------


# View all applicants for a specific job
@company_bp.route("/company/job/<int:job_id>/applicants", methods=["GET"])
@company_required
def get_job_applicants(job_id):
    job = JobPosition.query.get_or_404(job_id)

    user_id = get_jwt_identity()
    if job.company.id != int(user_id):
        return jsonify({"msg": "Unauthorized"}), 403

    apps = Application.query.filter_by(job_id=job_id).all()
    return jsonify(
        [
            {
                "application_id": a.id,
                "student_name": a.student.full_name,
                "cgpa": a.student.cgpa,
                "status": a.status,
                "applied_on": a.date_applied.strftime("%Y-%m-%d"),
            }
            for a in apps
        ]
    )


# Secure Resume Viewing for Companies
@company_bp.route("/view-resume/<int:student_id>", methods=["GET"])
@jwt_required()
def view_resume(student_id):
    current_user = User.query.get(get_jwt_identity())
    student = Student.query.get_or_404(student_id)

    # Logic: Admin can see all; Company only if student applied
    if current_user.role == "admin":
        return send_file(student.resume_path)

    if current_user.role == "company":
        applied = Application.query.filter_by(
            student_id=student_id, job_id=JobPosition.company_id == current_user.id
        ).first()
        if applied:
            return send_file(student.resume_path)

    return jsonify({"msg": "Unauthorized"}), 403


# Close or Re-open a Job Drive
@company_bp.route("/company/job/<int:job_id>/toggle-status", methods=["POST"])
@company_required
def toggle_job_status(job_id):
    job = JobPosition.query.get_or_404(job_id)

    job.status = "closed" if job.status == "ongoing" else "ongoing"
    db.session.commit()
    return jsonify(
        {"msg": f"Job status updated to {job.status}", "new_status": job.status}
    )


# Profile Editing ---------------------------------------------
@company_bp.route("/company/profile", methods=["PUT"])
@company_required
def update_company_profile():
    user_id = get_jwt_identity()
    company = Company.query.get(int(user_id))

    company.name = request.form.get("name", company.name)
    company.description = request.form.get("description", company.description)

    db.session.commit()
    return jsonify({"msg": "Company profile updated"})


# Export History -------------------------------
@company_bp.route("/company/export-history", methods=["POST"])
@company_required
def trigger_company_export():
    print("Export history clicked!")
    user_id = get_jwt_identity()
    from tasks import export_company_history_csv

    task = export_company_history_csv.delay(int(user_id))
    return jsonify({"task_id": task.id, "msg": "Company export started..."}), 202


@company_bp.route("/company/download-export/<task_id>", methods=["GET"])
@company_required
def download_company_export(task_id):
    user_id = get_jwt_identity()
    filename = f"company_history_{user_id}.csv"
    return send_from_directory("exports", filename, as_attachment=True)
