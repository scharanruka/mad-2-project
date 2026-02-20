from flask import Flask

from models import db

app = Flask(__name__)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "mysecretkey"

db.init_app(app)
