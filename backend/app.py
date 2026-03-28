from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    # jwt_required,
    # get_jwt_identity,
)

from models import db  # , User, Student, Company, Application, PlacementDrive
from auth import auth_bp
from admin import admin_bp
# from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret-key"
jwt = JWTManager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["CORS_HEADERS"] = "Content-Type"

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "mysecretkey"


db.init_app(app)


@app.route("/", methods=["GET"])
def hello():
    return jsonify("Hello!")


if __name__ == "__main__":
    app.run(debug=True)

# ------------------------------------
# Admin


# def admin_required(fn):
#     @jwt_required()
#     def wrapper(*args, **kwargs):
#         # get_jwt_identity() now returns the user_id string
#         user_id = get_jwt_identity()
#         user = User.query.get(int(user_id))

#         if not user or user.role != "admin":
#             return jsonify({"msg": "Admin access required"}), 403
#         return fn(*args, **kwargs)

#     wrapper.__name__ = fn.__name__
#     return wrapper


# @app.route("/admin/stats", methods=["GET"])
# @admin_required
# def get_stats():

#     return jsonify(
#         {
#             "total_students": Student.query.count(),
#             "total_companies": Company.query.count(),
#             "total_jobs": PlacementDrive.query.count(),
#             "total_applications": Application.query.count(),
#         }
#     )


# @app.route("/admin/companies", methods=["GET"])
# @admin_required
# def get_all_companies():  # search
#     search = request.args.get("search", "")
#     query = Company.query
#     if search:
#         query = query.filter(
#             (Company.name.contains(search) | (Company.industry.contains(search)))
#         )
#     companies = [
#         {
#             "id": c.id,
#             "name": c.name,
#             "industry": c.industry,
#             "is_approved": c.is_approved,
#         }
#         for c in query.all()
#     ]
#     return jsonify(companies)


# @app.route("/admin/approve-company/<int:company_id>", methods=["POST"])
# @admin_required
# def approve_company(company_id):
#     company = Company.query.get_or_404(company_id)
#     company.is_approved = True
#     db.session.commit()
#     return jsonify({"msg": f"Company {company.name} approved"})


# @app.route("/admin/user/<int:user_id>/toggle_status", methods=["POST"])
# @admin_required
# def toggle_user_status(user_id):
#     user = User.query.get_or_404(user_id)
#     # Admin can't deactive themselves
#     if user.role == "admin":
#         return jsonify({"msg": "Cannot deactive admin"}), 400

#     user.is_active = not user.is_active
#     db.session.commit()
#     status = "activated" if user.is_active else "blacklisted"
#     return jsonify({"msg": f"User {user.email} has been {status}"})


# @app.route("/admin/jobs/pending", methods=["GET"])
# @admin_required
# def get_pending_jobs():
#     jobs = PlacementDrive.query.filter_by(status="Pending").all()
#     return jsonify(
#         [
#             {
#                 "id": j.id,
#                 "company": j.company.name,
#                 "title": j.title,
#                 "salary": j.salary,
#             }
#             for j in jobs
#         ]
#     )


# @app.route("/admin/job/<int:job_id>/approve", methods=["POST"])
# @admin_required
# def approve_job(job_id):
#     job = PlacementDrive.query.get_or_404(job_id)
#     job.status = "Approved"
#     db.session.commit()
#     return jsonify({"msg": "Job posting approved"})


# if __name__ == "__main__":
#     app.run(debug=True)


# # Search students by name, ID, or username
# @app.route("/admin/students", methods=["GET"])
# @admin_required
# def get_admin_students():
#     search = request.args.get("search", "")
#     query = Student.query.join(User).filter(
#         (Student.full_name.contains(search))
#         | (User.username.contains(search))
#         | (User.id.contains(search))
#     )
#     return jsonify(
#         [
#             {
#                 "id": s.user.id,
#                 "name": s.full_name,
#                 "username": s.user.username,
#                 "is_active": s.user.is_active,
#             }
#             for s in query.all()
#         ]
#     )


# # Blacklist any user
# @app.route("/admin/user/<int:user_id>/toggle-active", methods=["POST"])
# @admin_required
# def toggle_active(user_id):
#     user = User.query.get_or_404(user_id)
#     if user.role == "admin":
#         return jsonify({"msg": "Admin cannot be deactivated"}), 400

#     user.is_active = not user.is_active
#     db.session.commit()
#     return jsonify({"msg": "Status updated", "is_active": user.is_active})


# # View all Job Postings and Applications
# @app.route("/admin/all-applications", methods=["GET"])
# @admin_required
# def get_all_applications():
#     apps = Application.query.all()
#     return jsonify(
#         [
#             {
#                 "id": a.id,
#                 "student": a.student.full_name,
#                 "job_title": a.job.title,
#                 "company": a.job.company.name,
#                 "status": a.status,
#                 "date": a.date_applied.strftime("%Y-%m-%d"),
#             }
#             for a in apps
#         ]
#     )
