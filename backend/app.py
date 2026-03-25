from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    # create_access_token,
    jwt_required,
    get_jwt_identity,
)

from models import db, User, Student, Company, Application, PlacementDrive
from auth import auth_bp
# from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret-key"
jwt = JWTManager(app)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "mysecretkey"

app.register_blueprint(auth_bp)
db.init_app(app)


@app.route("/", methods=["GET"])
def hello():
    return jsonify("Hello!")


# @app.route("/register/student", methods=["POST"])
# def register_student():
#     data = request.json
#     if User.query.filter_by(email=data["email"]).first():
#         return jsonify({"msg": "Username already exists"}), 400

#     hashed_pw = generate_password_hash(data["password"])
#     new_user = User(email=data["email"], password=hashed_pw, role="student")
#     db.session.add(new_user)
#     db.session.flush()

#     new_student = Student(id=new_user.id, full_name=data["full_name"])
#     db.session.add(new_student)
#     db.session.commit()
#     return jsonify({"msg": "Student registered successfully"}), 201


# @app.route("/register/company", methods=["POST"])
# def register_company():
#     data = request.json
#     if User.query.filter_by(email=data["email"]).first():
#         return jsonify({"msg": "Username already exists"}), 400

#     hashed_pw = generate_password_hash(data["password"])
#     new_user = User(email=data["email"], password=hashed_pw, role="company")
#     db.session.add(new_user)
#     db.session.flush()

#     new_company = Company(
#         id=new_user.id,
#         name=data["name"],
#         industry=data["industry"],
#         # is_approved=False,
#     )
#     db.session.add(new_company)
#     db.session.commit()
#     return jsonify({"msg": "Registration successful. Awaiting Admin approval."}), 201


# @app.route("/login", methods=["POST"])
# def login():
#     data = request.json
#     user = User.query.filter_by(email=data["email"]).first()

#     if user and check_password_hash(user.password, data["password"]):
#         # If company, check if approved by admin
#         if user.role == "company":
#             company = Company.query.filter_by(id=user.id).first()
#             if not company.is_approved:
#                 return jsonify({"msg": "Company account pending admin approval"}), 403

#         access_token = create_access_token(
#             identity={"email": user.email, "role": user.role}
#         )
#         return jsonify(access_token=access_token, role=user.role), 200

#     return jsonify({"msg": "Bad Email or password"}), 401


# ------------------------------------
# Admin


def admin_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        if get_jwt_identity()["role"] != "admin":
            return jsonify({"msg": "Admin access required"}), 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


@app.route("/admin/stats", methods=["GET"])
@admin_required
def get_stats():
    print("get stats..........")
    return jsonify(
        {
            "total_students": Student.query.count(),
            "total_companies": Company.query.count(),
            "total_jobs": PlacementDrive.query.count(),
            "total_applications": Application.query.count(),
        }
    )


@app.route("/admin/companies", methods=["GET"])
@admin_required
def get_all_companies():  # search
    search = request.args.get("search", "")
    query = Company.query.filter(
        (Company.name.contains(search) | (Company.industry.contains(search)))
    )
    companies = [
        {
            "id": c.id,
            "name": c.name,
            "industry": c.industry,
            "is_approved": c.is_approved,
        }
        for c in query.all()
    ]
    return jsonify(companies)


@app.route("/admin/approve-company/<int:company_id>", methods=["POST"])
@admin_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    return jsonify({"msg": f"Company {company.name} approved"})


@app.route("/admin/user/<int:user_id>/toggle_status", methods=["POST"])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    # Admin can't deactive themselves
    if user.role == "admin":
        return jsonify({"msg": "Cannot deactive admin"}), 400

    user.is_active = not user.is_active
    db.session.commit()
    status = "activated" if user.is_active else "blacklisted"
    return jsonify({"msg": f"User {user.email} has been {status}"})


if __name__ == "__main__":
    app.run(debug=True)
