from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required

from models import db, User, Student, Company
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secret-key"
jwt = JWTManager(app)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "mysecretkey"

db.init_app(app)


@app.route("/", methods=["GET"])
def hello():
    return jsonify("Hello!")


@app.route("/register/student", methods=["POST"])
def register_student():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Username already exists"}), 400

    hashed_pw = generate_password_hash(data["password"])
    new_user = User(email=data["email"], password=hashed_pw, role="student")
    db.session.add(new_user)
    db.session.flush()

    new_student = Student(id=new_user.id, full_name=data["full_name"])
    db.session.add(new_student)
    db.session.commit()
    return jsonify({"msg": "Student registered successfully"}), 201


@app.route("/register/company", methods=["POST"])
def register_company():
    data = request.json
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Username already exists"}), 400

    hashed_pw = generate_password_hash(data["password"])
    new_user = User(email=data["email"], password=hashed_pw, role="company")
    db.session.add(new_user)
    db.session.flush()

    print("---")
    print(data)
    print("---")

    new_company = Company(
        id=new_user.id,
        name=data["name"],
        industry=data["industry"],
        # is_approved=False,
    )
    db.session.add(new_company)
    db.session.commit()
    return jsonify({"msg": "Registration successful. Awaiting Admin approval."}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
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


if __name__ == "__main__":
    app.run()
