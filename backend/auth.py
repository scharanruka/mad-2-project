from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Student, Company

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email already exists!"}), 400

    new_user = User(
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="Student",
        is_approved=True,
    )

    db.session.add(new_user)
    db.session.flush()

    new_student = Student(id=new_user.id, full_name=data["full_name"])
    db.session.add(new_student)
    db.session.commit()

    return jsonify({"msg": "Student registered"}), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json()
    # Companies need Admin approval
    new_user = User(
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="Company",
        is_approved=False,  # Approval
    )
    db.session.add(new_user)
    db.session.flush()

    new_company = Company(id=new_user.id, name=data["name"], industry=data["industry"])
    db.session.add(new_company)
    db.session.commit()

    return jsonify({"msg": "Company registered, awaiting admin approval"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    print(data)
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"msg": "Bad credentials"}), 401

    if not user.is_approved:
        return jsonify({"msg": "Account pending approval by Admin"}), 403

    # Include role in the token for Vue-side redirection
    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify(access_token=access_token, role=user.role), 200
