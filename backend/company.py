from flask import jsonify, request, Blueprint
from models import db, User, Student, Company, PlacementDrive, Application
from flask_jwt_extended import jwt_required, get_jwt_identity


company_bp = Blueprint("company", __name__)


# DECORATORS --------------------------------------------------------------------------
def company_required(fn):
    @jwt_required()
    def wrapper(*args, **kwargs):
        if request.method == "OPTIONS":
            return fn(*args, **kwargs)

        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))

        if not user or user.role != "company":
            return jsonify({"msg": "Company access required"}), 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


# ------------------------
