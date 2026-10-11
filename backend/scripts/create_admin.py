import sys
import os
import getpass

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models import User
from auth import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        print("=== Create Sanskrit POS Application Administrator ===")
        username = input("Enter admin username [default: admin]: ").strip() or "admin"
        email = input("Enter admin email [default: admin@example.ac.in]: ").strip() or "admin@example.ac.in"
        password = getpass.getpass("Enter password [default: admin123]: ").strip() or "admin123"

        existing = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing:
            print(f"User '{username}' or email '{email}' already exists. Updating role to admin...")
            existing.role = "admin"
            existing.password_hash = get_password_hash(password)
            db.commit()
            print("Admin user updated successfully.")
            return

        admin = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"Administrator account '{username}' created successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
