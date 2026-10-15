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

client = TestClient(app)

def get_auth_token(username, password="password123"):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return resp.json()["access_token"]


class TestSentenceAssignments(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_all_seven_users_have_exactly_1000_assigned_sentences(self):
        """Verify each of the 7 users has exactly 1,000 sentences assigned by sentence_position."""
        expected_ranges = [
            ("user1", 1, 1000, 5),      # pos 1-4 verified, next is 5 (5_2)
            ("user2", 1001, 2000, 1001), # pos 1001 (869_3)
            ("user3", 2001, 3000, 2001), # pos 2001 (1139_0)
            ("user4", 3001, 4000, 3001), # pos 3001 (2139_3)
            ("user5", 4001, 5000, 4001), # pos 4001 (799_9)
            ("user6", 5001, 6000, 5001), # pos 5001 (936_2)
            ("user7", 6001, 7000, 6001), # pos 6001 (3318_2)
        ]

        for uname, start_pos, end_pos, expected_first_pos in expected_ranges:
            token = get_auth_token(uname)
            headers = {"Authorization": f"Bearer {token}"}

            # 1. Check stats endpoint for this user
            stats_res = client.get("/api/dataset/stats", headers=headers)
            self.assertEqual(stats_res.status_code, 200, f"Failed getting stats for {uname}")
            stats = stats_res.json()
            self.assertEqual(stats["total_sentences"], 1000, f"{uname} total_sentences != 1000")
            self.assertIn(f"{start_pos:,}–{end_pos:,}", stats["assigned_range"])

            # 2. Check next sentence endpoint
            next_res = client.get("/api/dataset/sentences/next", headers=headers)
            self.assertEqual(next_res.status_code, 200, f"Failed getting next sentence for {uname}")
            s = next_res.json()
            pos = s["sentence_position"]
            self.assertGreaterEqual(pos, start_pos, f"{uname} got sentence_position {pos} < {start_pos}")
            self.assertLessEqual(pos, end_pos, f"{uname} got sentence_position {pos} > {end_pos}")
            self.assertEqual(pos, expected_first_pos, f"{uname} expected initial pos {expected_first_pos}, got {pos}")

    def test_02_user3_resume_never_loads_user1_sentence(self):
        """User 3 clicking resume MUST load User 3's sentence (pos 2001), NEVER pos 5 (doc 5)."""
        token3 = get_auth_token("user3")
        headers3 = {"Authorization": f"Bearer {token3}"}

        res = client.get("/api/dataset/sentences/next", headers=headers3)
        self.assertEqual(res.status_code, 200)
        sent = res.json()

        # Must be position 2001 (annotation_id 1139_0)
        self.assertEqual(sent["sentence_position"], 2001)
        self.assertEqual(sent["annotation_id"], "1139_0")
        self.assertNotEqual(sent["annotation_id"], "5_2")
        self.assertNotEqual(sent["sentence_position"], 5)

    def test_03_dropdown_switching_loads_correct_ranges(self):
        """Header dropdown selection passes ?workspace=userX and loads that user's 1,000 range."""
        admin_token = get_auth_token("admin", "admin123")
        headers = {"Authorization": f"Bearer {admin_token}"}

        # Select User 3 from dropdown
        res_u3 = client.get("/api/dataset/sentences/next?workspace=user3", headers=headers)
        self.assertEqual(res_u3.status_code, 200)
        s3 = res_u3.json()
        self.assertEqual(s3["sentence_position"], 2001)
        self.assertEqual(s3["annotation_id"], "1139_0")

        # Select User 6 from dropdown
        res_u6 = client.get("/api/dataset/sentences/next?workspace=user6", headers=headers)
        self.assertEqual(res_u6.status_code, 200)
        s6 = res_u6.json()
        self.assertEqual(s6["sentence_position"], 5001)
        self.assertEqual(s6["annotation_id"], "936_2")

    def test_04_save_draft_and_save_next_persistence(self):
        """Save draft marks sentence in_progress and Save & Next marks verified in DB."""
        token3 = get_auth_token("user3")
        headers3 = {"Authorization": f"Bearer {token3}"}

        # 1. Get User 3's next sentence (pos 2001)
        res1 = client.get("/api/dataset/sentences/next?workspace=user3", headers=headers3)
        self.assertEqual(res1.status_code, 200)
        s = res1.json()
        ann_id = s["annotation_id"]
        tokens = s["tokens"]

        # 2. Save draft
        token_payload = [{"token_id": t["token_id"], "gold_sanskrit_tag": "N", "annotation_note": "draft note"} for t in tokens]
        res_draft = client.put(
            f"/api/annotations/{ann_id}/draft?workspace=user3",
            json={"tokens": token_payload, "note": "User 3 testing draft"},
            headers=headers3
        )
        self.assertEqual(res_draft.status_code, 200)
        self.assertEqual(res_draft.json()["status"], "in_progress")

        # 3. Next sentence should return the in_progress draft
        res_resume = client.get("/api/dataset/sentences/next?workspace=user3", headers=headers3)
        self.assertEqual(res_resume.status_code, 200)
        self.assertEqual(res_resume.json()["annotation_id"], ann_id)
        self.assertEqual(res_resume.json()["status"], "in_progress")

        # 4. Save & Next (verify)
        verify_payload = [{"token_id": t["token_id"], "gold_sanskrit_tag": "N"} for t in tokens]
        res_verify = client.post(
            f"/api/annotations/{ann_id}/verify?workspace=user3",
            json={"tokens": verify_payload, "note": "Verified by User 3"},
            headers=headers3
        )
        self.assertEqual(res_verify.status_code, 200)
        self.assertEqual(res_verify.json()["status"], "verified")

        # 5. Check next sentence advances to 2002
        res_adv = client.get("/api/dataset/sentences/next?workspace=user3", headers=headers3)
        self.assertEqual(res_adv.status_code, 200)
        self.assertEqual(res_adv.json()["sentence_position"], 2002)

        # 6. Revert pos 2001 back to pending for clean test state
        self.db.expire_all()
        s_db = self.db.query(Sentence).filter(Sentence.annotation_id == ann_id).first()
        s_db.status = "pending"
        s_db.verified_by = None
        s_db.verified_at = None
        s_db.annotation_note = None
        self.db.commit()


if __name__ == "__main__":
    unittest.main()
