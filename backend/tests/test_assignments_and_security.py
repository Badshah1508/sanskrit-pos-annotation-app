import os
import sys
import unittest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal
from models import Sentence, User
from main import app

class TestExpertAssignmentsAndSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_exact_7000_sentences(self):
        """Requirement: Exact 7,000 unique annotation sentences in the database."""
        count = self.db.query(Sentence).count()
        self.assertEqual(count, 7000, f"Expected 7,000 sentences, found {count}")

    def test_02_expert_accounts_exist(self):
        """Requirement: Exactly 7 expert accounts with configured ranges."""
        for i in range(1, 8):
            username = f"user{i}"
            expected_start = (i - 1) * 1000 + 1
            expected_end = i * 1000
            user = self.db.query(User).filter(User.username == username).first()
            self.assertIsNotNone(user, f"User '{username}' does not exist")
            self.assertEqual(user.role, "expert")
            self.assertEqual(user.assigned_range_start, expected_start)
            self.assertEqual(user.assigned_range_end, expected_end)

    def test_03_expert_sentence_distribution_exact_1000(self):
        """Requirement: Each expert has exactly 1,000 assigned sentences."""
        for i in range(1, 8):
            username = f"user{i}"
            user = self.db.query(User).filter(User.username == username).first()
            count = self.db.query(Sentence).filter(Sentence.assigned_expert_id == user.id).count()
            self.assertEqual(count, 1000, f"{username} has {count} sentences instead of 1,000")

    def test_04_no_unassigned_sentences(self):
        """Requirement: Zero unassigned sentences."""
        unassigned = self.db.query(Sentence).filter(Sentence.assigned_expert_id.is_(None)).count()
        self.assertEqual(unassigned, 0, f"Found {unassigned} unassigned sentences")

    def test_05_auth_login_all_users(self):
        """Requirement: Login with user1..user7 and admin succeeds."""
        # Test expert logins
        for i in range(1, 8):
            res = self.client.post("/api/auth/login", json={"username": f"user{i}", "password": "password123"})
            self.assertEqual(res.status_code, 200, f"Login failed for user{i}: {res.text}")
            data = res.json()
            self.assertIn("access_token", data)
            self.assertEqual(data["user"]["username"], f"user{i}")

        # Test admin login
        res_admin = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        self.assertEqual(res_admin.status_code, 200, f"Admin login failed: {res_admin.text}")

    def test_06_expert_access_own_workspace(self):
        """Requirement: User 1 can access their own workspace and get next sentence in range 1-1000."""
        login_res = self.client.post("/api/auth/login", json={"username": "user1", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Next sentence for user1
        res = self.client.get("/api/dataset/sentences/next?workspace=user1", headers=headers)
        self.assertEqual(res.status_code, 200)
        s = res.json()
        self.assertLessEqual(s["sentence_position"], 1000)
        self.assertGreaterEqual(s["sentence_position"], 1)

    def test_07_expert_cross_workspace_rejected_403(self):
        """Requirement: User 1 requesting User 2's workspace MUST be rejected with HTTP 403 Forbidden."""
        login_res = self.client.post("/api/auth/login", json={"username": "user1", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # User 1 requests User 2's next sentence
        res = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res.status_code, 403, f"Expected 403 Forbidden, got {res.status_code}")
        self.assertIn("Access denied", res.json()["detail"])

        # User 1 requests User 2's stats
        res_stats = self.client.get("/api/dataset/stats?workspace=user2", headers=headers)
        self.assertEqual(res_stats.status_code, 403, f"Expected 403 Forbidden, got {res_stats.status_code}")

    def test_08_expert_cross_sentence_rejected_403(self):
        """Requirement: User 1 cannot access, draft, or verify a sentence belonging to User 2."""
        login_res = self.client.post("/api/auth/login", json={"username": "user1", "password": "password123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Find a sentence in User 2's range (e.g. position 1005)
        u2_sentence = self.db.query(Sentence).filter(Sentence.sentence_position == 1005).first()
        self.assertIsNotNone(u2_sentence)

        # GET sentence by ID
        res_get = self.client.get(f"/api/dataset/sentences/{u2_sentence.annotation_id}", headers=headers)
        self.assertEqual(res_get.status_code, 403)

        # PUT draft
        res_draft = self.client.put(
            f"/api/annotations/{u2_sentence.annotation_id}/draft",
            headers=headers,
            json={"tokens": [], "note": "Hacking attempt"}
        )
        self.assertEqual(res_draft.status_code, 403)

        # POST verify
        res_verify = self.client.post(
            f"/api/annotations/{u2_sentence.annotation_id}/verify",
            headers=headers,
            json={"tokens": [], "note": "Hacking attempt"}
        )
        self.assertEqual(res_verify.status_code, 403)

    def test_09_admin_can_access_any_workspace(self):
        """Requirement: Admin can access any workspace."""
        login_res = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Admin inspects User 2
        res_u2 = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=headers)
        self.assertEqual(res_u2.status_code, 200)
        s2 = res_u2.json()
        self.assertGreaterEqual(s2["sentence_position"], 1001)
        self.assertLessEqual(s2["sentence_position"], 2000)

        # Admin inspects User 7
        res_u7 = self.client.get("/api/dataset/sentences/next?workspace=user7", headers=headers)
        self.assertEqual(res_u7.status_code, 200)
        s7 = res_u7.json()
        self.assertGreaterEqual(s7["sentence_position"], 6001)
        self.assertLessEqual(s7["sentence_position"], 7000)

    def test_10_csv_export_endpoint(self):
        """Requirement: Admin can export verified CSV."""
        login_res = self.client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/export/verified.csv", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue("text/csv" in res.headers.get("content-type", ""))

if __name__ == "__main__":
    unittest.main()
