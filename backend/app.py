import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

from models import db, Application, Student, JobPosition, User

from auth import auth_bp
from admin import admin_bp
from company import company_bp
from student import student_bp

from extensions import cache
from celery.result import AsyncResult

from dotenv import load_dotenv
from flask_mail import Mail

load_dotenv()


base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, "templates")

app = Flask(__name__, template_folder=template_dir)
app.config["JWT_SECRET_KEY"] = "secret-key"
cache.init_app(app)


jwt = JWTManager(app)


# SMTP configuration -----
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("SENDER_EMAIL")
app.config["MAIL_PASSWORD"] = os.getenv("GOOGLE_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("SENDER_EMAIL")
app.config["MAIL_DEBUG"] = True
app.config["MAIL_SUPPRESS_SEND"] = False
app.config["MAIL_DEBUG"] = True
app.config["TESTING"] = False

mail = Mail(app)


app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(company_bp)
app.register_blueprint(student_bp)

# enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})
app.config["CORS_HEADERS"] = "Content-Type"

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "mysecretkey"


db.init_app(app)

# File uploads ----
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/task-status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    from tasks import celery

    result = AsyncResult(task_id, app=celery)

    response = {
        "task_id": task_id,
        "status": result.status,  # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result if result.status == "SUCCESS" else None,
    }
    return jsonify(response), 200


@app.route("/view-resume/<int:student_id>", methods=["GET"])
@jwt_required()
def get_resume(student_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    student = Student.query.get_or_404(student_id)

    if not student.resume_path:
        return jsonify({"msg": "Resume not uploaded"}), 404

    if user.role == "admin":
        return send_resume_file(student.resume_path)

    if user.role == "company":
        application = (
            Application.query.join(JobPosition)
            .filter(
                Application.student_id == student_id, JobPosition.company_id == user.id
            )
            .first()
        )

        if application:
            return send_resume_file(student.resume_path)
        return jsonify({"msg": "Unauthorized: No application found"}), 403

    return jsonify({"msg": "Unauthorized"}), 403


def send_resume_file(path):
    directory = os.path.dirname(path)
    filename = os.path.basename(path)
    return send_from_directory(directory, filename)


if __name__ == "__main__":
    app.run(debug=True)
