import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal
from models import Sentence, Token, User
from main import app

class TestSimultaneousExpertAssignmentsAndPersistence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        # Reset any sentences modified during tests back to pending
        cls.db.query(Sentence).filter(
            Sentence.sentence_position >= 1001,
            Sentence.sentence_position <= 7000,
            Sentence.status.in_(["verified", "in_progress"])
        ).update({
            "status": "pending",
            "verified_by": None,
            "verified_at": None,
            "annotation_note": None
        }, synchronize_session=False)
        cls.db.commit()
        cls.db.close()

    def test_01_user3_login_and_workspace_range(self):
        """When user3 logs in, their sentence range is 2,001–3,000."""
        res = self.client.post("/api/auth/login", json={"username": "user3", "password": "password123"})
        self.assertEqual(res.status_code, 200)
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Request next sentence without passing workspace param (defaults to user3)
        res_next = self.client.get("/api/dataset/sentences/next", headers=headers)
        self.assertEqual(res_next.status_code, 200)
        s = res_next.json()
        self.assertGreaterEqual(s["sentence_position"], 2001)
        self.assertLessEqual(s["sentence_position"], 3000)
        print(f"\n[PASS] User 3 login: Loaded sentence #{s['sentence_position']} in range 2,001-3,000")

    def test_02_dropdown_switching_to_user2_and_user4(self):
        """Dropdown menu switches workspace to User 2 (1001-2000) and User 4 (3001-4000)."""
        res = self.client.post("/api/auth/login", json={"username": "user1", "password": "password123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Switch dropdown to User 2
        res_u2 = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res_u2.status_code, 200)
        s2 = res_u2.json()
        self.assertGreaterEqual(s2["sentence_position"], 1001)
        self.assertLessEqual(s2["sentence_position"], 2000)
        print(f"[PASS] Dropdown User 2: Loaded sentence #{s2['sentence_position']} in range 1,001-2,000")

        # 2. Switch dropdown to User 4
        res_u4 = self.client.get("/api/dataset/sentences/next?workspace=user4", headers=headers)
        self.assertEqual(res_u4.status_code, 200)
        s4 = res_u4.json()
        self.assertGreaterEqual(s4["sentence_position"], 3001)
        self.assertLessEqual(s4["sentence_position"], 4000)
        print(f"[PASS] Dropdown User 4: Loaded sentence #{s4['sentence_position']} in range 3,001-4,000")

        # 3. Switch dropdown to User 7
        res_u7 = self.client.get("/api/dataset/sentences/next?workspace=user7", headers=headers)
        self.assertEqual(res_u7.status_code, 200)
        s7 = res_u7.json()
        self.assertGreaterEqual(s7["sentence_position"], 6001)
        self.assertLessEqual(s7["sentence_position"], 7000)
        print(f"[PASS] Dropdown User 7: Loaded sentence #{s7['sentence_position']} in range 6,001-7,000")

    def test_03_database_persistence_on_save_and_next(self):
        """Save & Next persists verified tags into database and advances to next sentence."""
        res = self.client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Fetch pending sentence for User 2
        res_curr = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        s = res_curr.json()
        ann_id = s["annotation_id"]
        pos = s["sentence_position"]

        # Prepare tokens with valid tags
        token_payload = []
        for t in s["tokens"]:
            token_payload.append({
                "token_id": t["token_id"],
                "gold_sanskrit_tag": "N" if t["upos"] in ["NOUN", "PROPN"] else "AVN"
            })

        # Submit verification (Save & Next)
        res_verify = self.client.post(
            f"/api/annotations/{ann_id}/verify?workspace=user2",
            headers=headers,
            json={"tokens": token_payload, "note": "Verified by expert simultaneously"}
        )
        self.assertEqual(res_verify.status_code, 200)

        # Check in DB that sentence status is verified
        self.db.expire_all()
        db_sentence = self.db.query(Sentence).filter(Sentence.annotation_id == ann_id).first()
        self.assertEqual(db_sentence.status, "verified")
        self.assertEqual(db_sentence.verified_by, "User 2")
        self.assertIsNotNone(db_sentence.verified_at)

        # Verify next pending sentence advances to pos + 1
        res_next = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res_next.status_code, 200)
        s_next = res_next.json()
        self.assertEqual(s_next["sentence_position"], pos + 1)
        print(f"[PASS] Save & Next verified sentence #{pos} and immediately advanced to sentence #{s_next['sentence_position']}!")

    def test_04_stats_reflect_saved_changes(self):
        """Database stats for User 2 reflect verified sentence."""
        res = self.client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res_stats = self.client.get("/api/dataset/stats?workspace=user2", headers=headers)
        self.assertEqual(res_stats.status_code, 200)
        stats = res_stats.json()
        self.assertEqual(stats["total_sentences"], 1000)
        self.assertEqual(stats["assigned_sentences"], 1000)
        self.assertGreaterEqual(stats["verified_sentences"], 1)
        self.assertEqual(stats["is_completed"], False)
        print(f"[PASS] User 2 Stats: {stats['verified_sentences']} verified, {stats['pending_sentences']} pending out of 1,000 sentences. is_completed=False")

    def test_05_test_a_user2_pending_never_shows_completion(self):
        """Test A: User 2 has pending sentences -> loads eligible sentence, NOT congratulations."""
        res = self.client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res_next = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res_next.status_code, 200)
        data = res_next.json()
        self.assertIn("sentence_position", data)
        self.assertGreaterEqual(data["sentence_position"], 1001)
        self.assertLessEqual(data["sentence_position"], 2000)
        print(f"[PASS Test A] User 2 pending sentences exist: returned sentence #{data['sentence_position']}, NOT completion")

    def test_06_test_b_user2_in_progress_resumes_correctly(self):
        """Test B: When User 2 has in-progress draft, Resume Annotation returns the draft, NOT completion."""
        res = self.client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Save sentence 1005 as in_progress
        s_1005 = self.db.query(Sentence).filter(Sentence.sentence_position == 1005).first()
        s_1005.status = "in_progress"
        self.db.commit()

        res_resume = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res_resume.status_code, 200)
        data = res_resume.json()
        self.assertEqual(data["sentence_position"], 1005)
        self.assertEqual(data["status"], "in_progress")
        print(f"[PASS Test B] User 2 resumed in-progress draft #{data['sentence_position']}, NOT completion")

        # Reset 1005 back to pending
        s_1005.status = "pending"
        self.db.commit()

    def test_07_test_c_genuine_completion_only_when_1000_verified(self):
        """Test C: Completion 404 is ONLY returned when all 1,000 sentences are genuinely verified."""
        res = self.client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Temporarily mark all 1,000 sentences in range 1001-2000 as verified
        self.db.query(Sentence).filter(
            Sentence.sentence_position >= 1001,
            Sentence.sentence_position <= 2000
        ).update({"status": "verified"}, synchronize_session=False)
        self.db.commit()

        # Check stats shows is_completed = True
        res_stats = self.client.get("/api/dataset/stats?workspace=user2", headers=headers)
        self.assertEqual(res_stats.status_code, 200)
        self.assertEqual(res_stats.json()["is_completed"], True)
        self.assertEqual(res_stats.json()["verified_sentences"], 1000)

        # Check next endpoint returns 404 with COMPLETED message
        res_next = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res_next.status_code, 404)
        self.assertIn("COMPLETED", res_next.json()["detail"])
        print("[PASS Test C] When all 1,000 sentences are verified: genuine completion confirmed")

        # Revert back to pending
        self.db.query(Sentence).filter(
            Sentence.sentence_position >= 1001,
            Sentence.sentence_position <= 2000
        ).update({"status": "pending"}, synchronize_session=False)
        self.db.commit()

    def test_08_test_d_discrepancy_returns_409_never_completion(self):
        """Test D: If sentences are missing or not all verified, return 409 Conflict, NEVER false completion."""
        res = self.client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Simulate invalid status on remaining pending sentences so neither in_progress nor pending match
        self.db.query(Sentence).filter(
            Sentence.sentence_position >= 1001,
            Sentence.sentence_position <= 2000
        ).update({"status": "corrupted_status"}, synchronize_session=False)
        self.db.commit()

        # Check next endpoint returns 409 CONFLICT, NOT 404 or completion
        res_next = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res_next.status_code, 409)
        self.assertIn("Assignment discrepancy", res_next.json()["detail"])
        print(f"[PASS Test D] Database discrepancy returned 409 Conflict ({res_next.json()['detail']}), NOT false completion")

        # Revert back to pending
        self.db.query(Sentence).filter(
            Sentence.sentence_position >= 1001,
            Sentence.sentence_position <= 2000
        ).update({"status": "pending"}, synchronize_session=False)
        self.db.commit()

    def test_09_test_f_database_integrity_all_seven_users(self):
        """Test F: Database integrity: 7 distinct 1,000-sentence slices, no overlaps, no gaps."""
        total = self.db.query(Sentence).count()
        self.assertEqual(total, 7000)

        for u_num in range(1, 8):
            start = (u_num - 1) * 1000 + 1
            end = u_num * 1000
            count = self.db.query(Sentence).filter(
                Sentence.sentence_position >= start,
                Sentence.sentence_position <= end
            ).count()
            self.assertEqual(count, 1000, f"User {u_num} does not have exactly 1,000 sentences")
        print("[PASS Test F] Database integrity: 7,000 sentences strictly partitioned into 7 x 1,000 slices")


if __name__ == "__main__":
    unittest.main()
