from flask import jsonify, request, Blueprint
from models import db, User, Student, Company, PlacementDrive, Application
from flask_jwt_extended import jwt_required, get_jwt_identity


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
            "total_jobs": PlacementDrive.query.count(),
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


# --------------------------------------------------------------------------------------------


@admin_bp.route("/admin/companies/approve", methods=["POST", "OPTIONS"])
@admin_required
def approve_company():
    company_id = request.args.get("id", type=int)

    company = Company.query.get_or_404(company_id)
    company.is_approved = not company.is_approved
    db.session.commit()
    return jsonify({"msg": f"Company {company.name} approved toggled"})


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


@admin_bp.route("/admin/jobs/pending", methods=["GET"])
@admin_required
def get_pending_jobs():
    jobs = PlacementDrive.query.filter_by(status="Pending").all()
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
    job = PlacementDrive.query.get_or_404(job_id)
    job.status = "Approved"
    db.session.commit()
    return jsonify({"msg": "Job posting approved"})


# View all Job Postings and Applications
@admin_bp.route("/admin/all-applications", methods=["GET"])
@admin_required
def get_all_applications():
    apps = Application.query.all()
    return jsonify(
        [
            {
                "id": a.id,
                "student": a.student.full_name,
                "job_title": a.job.title,
                "company": a.job.company.name,
                "status": a.status,
                "date": a.date_applied.strftime("%Y-%m-%d"),
            }
            for a in apps
        ]
    )
