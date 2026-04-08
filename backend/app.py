from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from models import db

from auth import auth_bp
from admin import admin_bp
from company import company_bp
from student import student_bp

from extensions import cache

app = Flask(__name__)
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


if __name__ == "__main__":
    app.run(debug=True)
