import os
import sys
import unittest
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal
from models import Sentence, Token, User
from main import app

class TestSkipSentenceFeature(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.db = SessionLocal()

        # Login user1 and user2
        res1 = cls.client.post("/api/auth/login", json={"username": "user1", "password": "password123"})
        cls.user1_token = res1.json()["access_token"]
        cls.user1_headers = {"Authorization": f"Bearer {cls.user1_token}"}

        res2 = cls.client.post("/api/auth/login", json={"username": "user2", "password": "password123"})
        cls.user2_token = res2.json()["access_token"]
        cls.user2_headers = {"Authorization": f"Bearer {cls.user2_token}"}

    @classmethod
    def tearDownClass(cls):
        # Reset test sentences in range 1001-1005 back to pending
        cls.db.query(Sentence).filter(
            Sentence.sentence_position >= 1001,
            Sentence.sentence_position <= 1005
        ).update({
            "status": "pending",
            "skipped_at": None,
            "verified_by": None,
            "verified_at": None,
            "annotation_note": None
        }, synchronize_session=False)
        cls.db.commit()
        cls.db.close()

    def test_01_user2_skips_sentence_and_receives_next(self):
        """User 2 skips a sentence, draft data is preserved, and next sentence is returned."""
        # 1. Fetch next sentence for User 2
        res = self.client.get("/api/dataset/sentences/next?workspace=user2", headers=self.user2_headers)
        self.assertEqual(res.status_code, 200)
        s1 = res.json()
        s1_id = s1["annotation_id"]
        s1_pos = s1["sentence_position"]
        self.assertGreaterEqual(s1_pos, 1001)
        self.assertLessEqual(s1_pos, 2000)

        # 2. Skip this sentence with partial note and draft token
        tokens_payload = []
        if s1.get("tokens") and len(s1["tokens"]) > 0:
            tokens_payload.append({
                "token_id": s1["tokens"][0]["token_id"],
                "gold_sanskrit_tag": "N"
            })

        skip_res = self.client.post(
            f"/api/annotations/{s1_id}/skip?workspace=user2",
            json={
                "tokens": tokens_payload,
                "note": "Draft note before skipping"
            },
            headers=self.user2_headers
        )
        self.assertEqual(skip_res.status_code, 200, skip_res.text)
        skip_data = skip_res.json()
        self.assertEqual(skip_data["skipped_annotation_id"], s1_id)
        self.assertIsNotNone(skip_data["next_sentence"])

        next_s = skip_data["next_sentence"]
        self.assertNotEqual(next_s["annotation_id"], s1_id)
        self.assertGreaterEqual(next_s["sentence_position"], 1001)
        self.assertLessEqual(next_s["sentence_position"], 2000)

        # 3. Verify in database: status is 'skipped', skipped_at is set, note saved
        self.db.expire_all()
        db_s1 = self.db.query(Sentence).filter(Sentence.annotation_id == s1_id).first()
        self.assertEqual(db_s1.status, "skipped")
        self.assertIsNotNone(db_s1.skipped_at)
        self.assertEqual(db_s1.annotation_note, "Draft note before skipping")

        print(f"\n[PASS] User 2 skipped sentence #{s1_pos} and received next sentence #{next_s['sentence_position']}")

    def test_02_stats_and_skipped_list_endpoint(self):
        """Stats reflects skipped sentences and /annotations/skipped lists them."""
        # 1. Check stats
        stats_res = self.client.get("/api/dataset/stats?workspace=user2", headers=self.user2_headers)
        self.assertEqual(stats_res.status_code, 200)
        stats = stats_res.json()
        self.assertIn("skipped_sentences", stats)
        self.assertGreaterEqual(stats["skipped_sentences"], 1)
        self.assertFalse(stats["is_completed"])

        # 2. Check /api/annotations/skipped for User 2
        skipped_res = self.client.get("/api/annotations/skipped?workspace=user2", headers=self.user2_headers)
        self.assertEqual(skipped_res.status_code, 200)
        skipped_list = skipped_res.json()
        self.assertGreaterEqual(len(skipped_list), 1)
        for item in skipped_list:
            self.assertEqual(item["status"], "skipped")
            self.assertGreaterEqual(item["sentence_position"], 1001)
            self.assertLessEqual(item["sentence_position"], 2000)

        print(f"\n[PASS] Stats shows {stats['skipped_sentences']} skipped; /annotations/skipped returned {len(skipped_list)} items")

    def test_03_workspace_isolation_and_security(self):
        """User 1 cannot see or manipulate User 2's skipped sentence."""
        # Query User 1's skipped sentences -> should not contain User 2's sentences
        u1_skipped = self.client.get("/api/annotations/skipped?workspace=user1", headers=self.user1_headers).json()
        for s in u1_skipped:
            self.assertLessEqual(s["sentence_position"], 1000)

        # User 1 attempts to skip a sentence in User 2's range (1001)
        u2_sent = self.db.query(Sentence).filter(Sentence.sentence_position == 1001).first()
        cross_res = self.client.post(
            f"/api/annotations/{u2_sent.annotation_id}/skip",
            json={"tokens": [], "note": "Unauthorized skip"},
            headers=self.user1_headers
        )
        self.assertIn(cross_res.status_code, [400, 403], f"Expected 400 or 403 for cross-workspace skip, got {cross_res.status_code}")
        print(f"\n[PASS] Workspace security: User 1 correctly prevented from skipping User 2's sentence (HTTP {cross_res.status_code})")

    def test_04_resume_and_verify_skipped_sentence(self):
        """Resuming a skipped sentence transitions it to in_progress, and verifying it clears it."""
        # Find the skipped sentence from User 2
        u2_skipped = self.db.query(Sentence).filter(
            Sentence.sentence_position >= 1001,
            Sentence.sentence_position <= 2000,
            Sentence.status == "skipped"
        ).first()
        self.assertIsNotNone(u2_skipped)
        ann_id = u2_skipped.annotation_id

        # 1. Resume
        resume_res = self.client.post(
            f"/api/annotations/{ann_id}/resume?workspace=user2",
            headers=self.user2_headers
        )
        self.assertEqual(resume_res.status_code, 200)
        resumed_data = resume_res.json()
        self.assertEqual(resumed_data["status"], "in_progress")

        # Check DB
        self.db.expire_all()
        db_sent = self.db.query(Sentence).filter(Sentence.annotation_id == ann_id).first()
        self.assertEqual(db_sent.status, "in_progress")

        # Check that it's no longer in /annotations/skipped
        skipped_list = self.client.get("/api/annotations/skipped?workspace=user2", headers=self.user2_headers).json()
        self.assertNotIn(ann_id, [s["annotation_id"] for s in skipped_list])

        # 2. Verify sentence with valid tags
        tokens_verify = []
        for t in db_sent.tokens:
            tokens_verify.append({
                "token_id": t.token_id,
                "gold_sanskrit_tag": "N"
            })

        verify_res = self.client.post(
            f"/api/annotations/{ann_id}/verify?workspace=user2",
            json={"tokens": tokens_verify, "note": "Verified after resume"},
            headers=self.user2_headers
        )
        self.assertEqual(verify_res.status_code, 200)
        self.db.expire_all()
        db_sent_verified = self.db.query(Sentence).filter(Sentence.annotation_id == ann_id).first()
        self.assertEqual(db_sent_verified.status, "verified")

        print(f"\n[PASS] Resumed skipped sentence #{db_sent.sentence_position} -> in_progress -> verified")

if __name__ == "__main__":
    unittest.main()
