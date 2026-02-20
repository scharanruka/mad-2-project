from app import app, db
from models import User
from werkzeug.security import generate_password_hash


def create_admin():
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(role="Admin").first():
            print("Admin user not found, creating one...")
            admin = User(
                email="admin@iitm.ac.in",
                password=generate_password_hash("admin123", method="pbkdf2:sha256"),
                role="Admin",
                is_approved=True,
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")


if __name__ == "__main__":
    create_admin()
    print("Database Initialized...")
