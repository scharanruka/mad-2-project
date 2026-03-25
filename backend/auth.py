from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Student, Company

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="student",
    )
    db.session.add(new_user)
    db.session.flush()

    new_student = Student(id=new_user.id, full_name=data["full_name"])
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"msg": "Student registered successfully"}), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(
        email=data["email"],
        password=generate_password_hash(data["password"]),
        role="company",
    )
    db.session.add(new_user)
    db.session.flush()

    new_company = Company(
        id=new_user.id,
        name=data["name"],
        industry=data["industry"],
        # is_approved=False,
    )
    db.session.add(new_company)
    db.session.commit()
    return jsonify({"msg": "Registration successful. Awaiting Admin approval."}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    print(request.json)
    user = User.query.filter_by(email=data["email"]).first()

    if user and check_password_hash(user.password, data["password"]):
        # If company, check if approved by admin
        if user.role == "company":
            company = Company.query.filter_by(id=user.id).first()
            if not company.is_approved:
                return jsonify({"msg": "Company account pending admin approval"}), 403

        access_token = create_access_token(
            identity={"email": user.email, "role": user.role}
        )
        return jsonify(access_token=access_token, role=user.role), 200

    return jsonify({"msg": "Bad Email or password"}), 401
