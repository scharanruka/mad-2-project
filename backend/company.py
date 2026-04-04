from datetime import datetime

from flask import jsonify, request, Blueprint
from models import db, User, Student, Company, JobPosition, Application
from flask_jwt_extended import jwt_required, get_jwt_identity

from helpers import save_file

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


# ------------------------
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
        status="Approved",
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
    applicant_count = Application.query.filter_by(job_id=JobPosition.id).count() | 0
    return jsonify(
        [
            {
                "id": j.id,
                "title": j.title,
                "status": j.status,
                "applicant_count": applicant_count,
            }
            for j in jobs
        ]
    )


@company_bp.route("/company/application/<int:app_id>/status", methods=["POST"])
@company_required
def update_app_status(app_id):
    data = request.json  # Expecting {"status": "Shortlisted", "feedback": "..."}
    application = Application.query.get_or_404(app_id)
    application.status = data["status"]
    # TODO: Feedback here
    db.session.commit()
    return jsonify({"msg": f"Application marked as {application.status}"})


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


# Close or Re-open a Job Drive
@company_bp.route("/company/job/<int:job_id>/toggle-status", methods=["POST"])
@company_required
def toggle_job_status(job_id):
    job = JobPosition.query.get_or_404(job_id)

    job.status = "Closed" if job.status == "Approved" else "Approved"
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

    if "logo" in request.files:
        # Assuming you add a 'logo_path' column to Company model
        path = save_file(request.files["logo"], "logos")
        company.logo_path = path

    db.session.commit()
    return jsonify({"msg": "Company profile updated"})
