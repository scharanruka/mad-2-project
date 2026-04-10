import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from models import db

from auth import auth_bp
from admin import admin_bp
from company import company_bp
from student import student_bp

from extensions import cache
from celery.result import AsyncResult

base_dir = os.path.abspath(os.path.dirname(__file__))
template_dir = os.path.join(base_dir, "templates")

app = Flask(__name__, template_folder=template_dir)
app.config["JWT_SECRET_KEY"] = "secret-key"
cache.init_app(app)


jwt = JWTManager(app)

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

# File uploads
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/task-status/<task_id>", methods=["GET"])
def get_task_status(task_id):
    from tasks import celery

    # This works globally for any task triggered in the app
    result = AsyncResult(task_id, app=celery)

    response = {
        "task_id": task_id,
        "status": result.status,  # PENDING, STARTED, SUCCESS, FAILURE
        "result": result.result if result.status == "SUCCESS" else None,
    }

    # Return 200 even if pending, as the frontend expects a valid JSON status
    return jsonify(response), 200


if __name__ == "__main__":
    app.run(debug=True)
