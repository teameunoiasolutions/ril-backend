"""Create (or update) an admin account with a properly hashed password.

Usage:
    python create_admin.py <email> <password> ["Full Name"]

Example:
    python create_admin.py me@royaleisles.lk MyStr0ngPass "Sakna Perera"

If run with no arguments, it prompts for the details.
"""
import sys

from app.database.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models import Admin


def create_admin(email: str, password: str, full_name: str = "") -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        email = email.strip().lower()
        admin = db.query(Admin).filter(Admin.email == email).first()
        if admin is None:
            admin = Admin(email=email, hashed_password=hash_password(password), full_name=full_name)
            db.add(admin)
            action = "Created"
        else:
            admin.hashed_password = hash_password(password)
            if full_name:
                admin.full_name = full_name
            action = "Updated"
        db.commit()
        print(f"{action} admin: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        email_arg = sys.argv[1]
        password_arg = sys.argv[2]
        name_arg = sys.argv[3] if len(sys.argv) > 3 else ""
    else:
        email_arg = input("Admin email: ").strip()
        password_arg = input("Admin password: ").strip()
        name_arg = input("Full name (optional): ").strip()

    if not email_arg or not password_arg:
        print("Email and password are required.")
        sys.exit(1)

    create_admin(email_arg, password_arg, name_arg)
