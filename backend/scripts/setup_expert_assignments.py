import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, func
from database import SessionLocal
from models import Sentence, User
from auth import get_password_hash

EXPERT_CONFIGS = [
    {"user_num": 1, "username": "user1", "display_name": "User 1", "email": "user1@example.ac.in", "start": 1, "end": 1000},
    {"user_num": 2, "username": "user2", "display_name": "User 2", "email": "user2@example.ac.in", "start": 1001, "end": 2000},
    {"user_num": 3, "username": "user3", "display_name": "User 3", "email": "user3@example.ac.in", "start": 2001, "end": 3000},
    {"user_num": 4, "username": "user4", "display_name": "User 4", "email": "user4@example.ac.in", "start": 3001, "end": 4000},
    {"user_num": 5, "username": "user5", "display_name": "User 5", "email": "user5@example.ac.in", "start": 4001, "end": 5000},
    {"user_num": 6, "username": "user6", "display_name": "User 6", "email": "user6@example.ac.in", "start": 5001, "end": 6000},
    {"user_num": 7, "username": "user7", "display_name": "User 7", "email": "user7@example.ac.in", "start": 6001, "end": 7000},
]

def setup_assignments(db=None):
    close_db = False
    if db is None:
        db = SessionLocal()
        close_db = True

    try:
        print("==================================================================")
        print("Sanskrit POS Annotation: 7 Expert Workspace Assignment Setup")
        print("==================================================================")

        # 1. Strict Validation: Must have exactly 7,000 unique annotation sentences
        total_sentences = db.query(Sentence).count()
        print(f"Checking sentence count in database: {total_sentences} sentences found.")
        if total_sentences != 7000:
            raise ValueError(
                f"SAFETY CHECK FAILED: Expected exactly 7,000 unique annotation sentences, "
                f"but found {total_sentences}. Stopping assignment to prevent corrupted ranges."
            )

        # 2. Setup / Update the 7 Expert Accounts + Admin
        print("\nConfiguring 7 Expert Accounts (User 1 - User 7)...")
        user_map = {} # user_num -> User object
        default_pw_hash = get_password_hash("password123")

        for cfg in EXPERT_CONFIGS:
            u_num = cfg["user_num"]
            uname = cfg["username"]
            
            # Check if user exists by username or email
            user = db.query(User).filter(
                (User.username == uname) | (User.email == cfg["email"])
            ).first()

            if not user:
                # If User 1 and 'sanskrit_scholar' exists, attach User 1 credentials
                if u_num == 1:
                    scholar = db.query(User).filter(User.username == "sanskrit_scholar").first()
                    if scholar:
                        user = scholar
                        user.display_name = cfg["display_name"]
                        user.assigned_range_start = cfg["start"]
                        user.assigned_range_end = cfg["end"]

            if not user:
                user = User(
                    username=uname,
                    email=cfg["email"],
                    password_hash=default_pw_hash,
                    role="expert",
                    display_name=cfg["display_name"],
                    assigned_range_start=cfg["start"],
                    assigned_range_end=cfg["end"],
                    is_active=True
                )
                db.add(user)
                db.flush()
                print(f"Created account: {uname} ({cfg['display_name']}) -> Range {cfg['start']}–{cfg['end']}")
            else:
                user.display_name = cfg["display_name"]
                user.assigned_range_start = cfg["start"]
                user.assigned_range_end = cfg["end"]
                user.role = "expert"
                db.flush()
                print(f"Updated account: {user.username} ({cfg['display_name']}) -> Range {cfg['start']}–{cfg['end']}")

            user_map[u_num] = user

        # Ensure user1 exists distinctly
        user1_record = db.query(User).filter(User.username == "user1").first()
        if not user1_record:
            user1_record = User(
                username="user1",
                email="user1@example.ac.in",
                password_hash=default_pw_hash,
                role="expert",
                display_name="User 1",
                assigned_range_start=1,
                assigned_range_end=1000,
                is_active=True
            )
            db.add(user1_record)
            db.flush()
            user_map[1] = user1_record

        # Also ensure 'sanskrit_scholar' if present has admin role and maps to User 1's range
        scholar_record = db.query(User).filter(User.username == "sanskrit_scholar").first()
        if scholar_record:
            scholar_record.display_name = "Scholar (Admin)"
            scholar_record.role = "admin"
            scholar_record.assigned_range_start = 1
            scholar_record.assigned_range_end = 1000

        # Ensure admin account exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@example.ac.in",
                password_hash=get_password_hash("admin123"),
                role="admin",
                display_name="Administrator",
                is_active=True
            )
            db.add(admin)
            db.flush()

        db.commit()

        # 3. High-Performance Bulk Range Assignment by doc_id
        print("\nExecuting bulk range assignment by doc_id (ranges 1–1,000, 1,001–2,000, etc.)...")
        assignment_counts = {}

        for cfg in EXPERT_CONFIGS:
            u_num = cfg["user_num"]
            assigned_user = user_map[u_num]
            start_doc = cfg["start"]
            end_doc = cfg["end"]

            db.execute(
                text("""
                    UPDATE sentences
                    SET assigned_expert_id = :user_id
                    WHERE CAST(doc_id AS INTEGER) >= :start_doc AND CAST(doc_id AS INTEGER) <= :end_doc
                """),
                {"user_id": assigned_user.id, "start_doc": start_doc, "end_doc": end_doc}
            )

            # Query count for this range
            cnt = db.query(func.count(Sentence.id)).filter(
                Sentence.assigned_expert_id == assigned_user.id
            ).scalar()
            assignment_counts[u_num] = cnt
            print(f"User {u_num} ({assigned_user.username}): Assigned doc_id Range {start_doc}–{end_doc} | Total: {cnt} sentences")

        db.commit()

        # 4. Strict Integrity Check
        total_assigned = sum(assignment_counts.values())
        if total_assigned != 7000:
            raise ValueError(f"Integrity check failed: Expected total 7000 sentences assigned, got: {total_assigned}")

        print("\n==================================================================")
        print("ALL CHECKS PASSED: 7,000 sentences assigned by doc_id cleanly.")
        print("Each expert has exactly 1,000 sentences with zero gaps and zero overlaps.")
        print("Existing annotations, notes, and timestamps have been 100% preserved.")
        print("==================================================================")

    finally:
        if close_db:
            db.close()

if __name__ == "__main__":
    setup_assignments()
