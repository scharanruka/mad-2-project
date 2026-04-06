from flask import jsonify, request, Blueprint
from models import db, User, Student, Company, JobPosition, Application
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import joinedload

admin_bp = Blueprint("admin", __name__)


# DECORATORS --------------------------------------------------------------------------
def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return fn(*args, **kwargs)
        # get_jwt_identity() now returns the user_id string
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user or user.role != "admin":
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


# Basic GET Functions ------------------------------------------------------------


@admin_bp.route("/admin/stats", methods=["GET"])
@admin_required
def get_stats():

    return jsonify(
        {
            "total_students": Student.query.count(),
            "total_companies": Company.query.count(),
            "total_jobs": JobPosition.query.filter(
                JobPosition.status == "ongoing"
            ).count(),
            "total_applications": Application.query.count(),
        }
    )


@admin_bp.route("/admin/companies", methods=["GET"])
@admin_required
def get_companies():  # search
    search = request.args.get("search", "")
    query = Company.query.join(User)
    if search:
        query = query.filter(
            (Company.name.contains(search) | (Company.industry.contains(search)))
        )
    companies = [
        {
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "is_approved": c.is_approved,
            "is_active": c.user.is_active,
        }
        for c in query.all()
    ]
    return jsonify(companies)


@admin_bp.route("/admin/students", methods=["GET"])
@admin_required
def get_students():
    search = request.args.get("search", "")
    query = Student.query.join(User).filter(
        (Student.full_name.contains(search)) | (User.id.contains(search))
    )
    return jsonify(
        [
            {
                "id": s.id,
                "name": s.full_name,
                "branch": s.branch,
                "is_active": s.user.is_active,
            }
            for s in query.all()
        ]
    )


@admin_bp.route("/admin/postings", methods=["GET"])
@admin_required
def get_ongoing_postings():
    query = JobPosition.query.filter(JobPosition.status != "closed")
    return jsonify(
        [{"id": d.id, "title": d.title, "status": d.status} for d in query.all()]
    )


@admin_bp.route("/admin/applications", methods=["GET"])
@admin_required
def get_all_applications():
    query = Application.query.options(
        joinedload(Application.job_position).joinedload(JobPosition.company),
        joinedload(Application.student),
    )
    return jsonify(
        [
            {
                "id": a.id,
                "sname": a.student.full_name,
                "date_applied": a.date_applied,
                "posting": a.job_position.title,
                "company": a.job_position.company.name,
            }
            for a in query.all()
        ]
    )


# --------------------------------------------------------------------------------------------
# Blacklist and Approve Companies


@admin_bp.route("/admin/companies/approve", methods=["POST", "OPTIONS"])
@admin_required
def approve_company():
    company_id = request.args.get("id", type=int)

    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    return jsonify({"msg": f"Company {company.name} approved"})


# Blacklist any user
@admin_bp.route("/admin/user/blacklist", methods=["POST", "OPTIONS"])
@admin_required
def toggle_active():
    user_id = request.args.get("id", type=int)
    user = User.query.get_or_404(user_id)
    if user.role == "admin":
        return jsonify({"msg": "Admin cannot be deactivated"}), 400

    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({"msg": "Status updated", "is_active": user.is_active})


# ----------------------------------------------------------------------------------


@admin_bp.route("/admin/jobs/pending", methods=["GET"])
@admin_required
def get_pending_jobs():
    jobs = JobPosition.query.filter_by(status="Pending").all()
    return jsonify(
        [
            {
                "id": j.id,
                "company": j.company.name,
                "title": j.title,
                "salary": j.salary,
            }
            for j in jobs
        ]
    )


@admin_bp.route("/admin/job/<int:job_id>/approve", methods=["POST"])
@admin_required
def approve_job(job_id):
    job = JobPosition.query.get_or_404(job_id)
    job.status = "Approved"
    db.session.commit()
    return jsonify({"msg": "Job posting approved"})


@admin_bp.route("/admin/postings/<int:posting_id>/details", methods=["GET"])
@admin_required
def get_posting_details(posting_id):
    posting = JobPosition.query.get_or_404(posting_id)
    return jsonify(
        {
            "id": posting.id,
            "title": posting.title,
            "description": posting.description,
            "salary": posting.salary,
        }
    )


@admin_bp.route("/admin/postings/<int:posting_id>/complete", methods=["POST"])
@admin_required
def mark_posting_complete(posting_id):
    posting = JobPosition.query.get_or_404(posting_id)
    posting.status = "closed"
    db.session.commit()
    return jsonify({"msg": "Job posting marked complete"})


@admin_bp.route("/admin/postings/<int:posting_id>/toggle_status", methods=["POST"])
@admin_required
def toggle_posting(posting_id):
    posting = JobPosition.query.get_or_404(posting_id)
    posting.status = "rejected" if posting.status != "rejected" else "ongoing"
    db.session.commit()
    return jsonify({"msg": "Job posting status toggled"})


@admin_bp.route("/admin/applications/<int:appl_id>/details", methods=["GET"])
@admin_required
def get_application_details(appl_id):
    appl = Application.query.get_or_404(appl_id)
    student = Student.query.get_or_404(appl.student_id)
    job_position = JobPosition.query.get_or_404(appl.job_id)
    return jsonify(
        {
            "id": appl.id,
            "sname": student.full_name,
            "branch": student.branch,
            "posting_id": job_position.id,
            "posting_title": job_position.title,
        }
    )
