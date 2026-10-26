import unittest
import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from config import settings
from services.annotation_service import APPROVED_TAG_SET, save_sentence_draft, verify_sentence_annotation
from services.export_service import generate_verified_csv
from database import SessionLocal
from models import Sentence, Token, User
from schemas import TokenAnnotationInput

class TestPUTagSupport(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_pu_in_approved_tag_list(self):
        """PU must be in settings.APPROVED_SANSKRIT_TAGS and APPROVED_TAG_SET."""
        self.assertIn("PU", settings.APPROVED_SANSKRIT_TAGS, "PU must be in settings.APPROVED_SANSKRIT_TAGS")
        self.assertIn("PU", APPROVED_TAG_SET, "PU must be in APPROVED_TAG_SET")
        self.assertEqual(len(settings.APPROVED_SANSKRIT_TAGS), 24, "Total approved tags should be 24 (23 + PU)")

    def test_02_draft_and_verify_with_pu_tag(self):
        """Ensure PU can be saved as a draft and verified, persisted, and exported."""
        admin_user = self.db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            self.skipTest("Admin user not found in test db")

        # Pick test sentence #1 in workspace 1
        sent = self.db.query(Sentence).filter(Sentence.sentence_position == 1).first()
        if not sent:
            self.skipTest("Sentence #1 not found")

        original_status = sent.status
        original_verified_by = sent.verified_by
        original_verified_at = sent.verified_at
        original_tags = {t.token_id: t.gold_sanskrit_tag for t in sent.tokens}

        try:
            # 1. Test saving draft with PU for the final punctuation/token
            tokens_draft = []
            for idx, t in enumerate(sent.tokens):
                # Assign PU to the last token or any punctuation token
                tag = "PU" if (idx == len(sent.tokens) - 1 or t.token in ["।", "॥", ",", ".", "?", "!"]) else "N"
                tokens_draft.append(TokenAnnotationInput(token_id=t.token_id, gold_sanskrit_tag=tag))

            updated_draft = save_sentence_draft(
                annotation_id=sent.annotation_id,
                token_inputs=tokens_draft,
                note="Test PU draft note",
                user=admin_user,
                db=self.db,
                workspace="user1"
            )

            # Check that draft persisted PU tag in database
            pu_tokens = [t for t in updated_draft.tokens if t.gold_sanskrit_tag == "PU"]
            self.assertTrue(len(pu_tokens) > 0, "At least one token must have PU tag saved")
            self.assertEqual(pu_tokens[0].gold_sanskrit_tag, "PU")

            # 2. Test verifying sentence with PU
            updated_verified = verify_sentence_annotation(
                annotation_id=sent.annotation_id,
                token_inputs=tokens_draft,
                note="Test PU verified note",
                user=admin_user,
                db=self.db,
                workspace="user1"
            )

            self.assertEqual(updated_verified.status, "verified")

            # 3. Test CSV export preserves PU
            csv_file = generate_verified_csv(self.db)
            csv_content = csv_file.getvalue()
            self.assertIn(",PU,", csv_content, "CSV export must contain the PU tag in gold_sanskrit_tag column")

        finally:
            # Revert changes to restore database to original state
            sent.status = original_status
            sent.verified_by = original_verified_by
            sent.verified_at = original_verified_at
            for t in sent.tokens:
                t.gold_sanskrit_tag = original_tags.get(t.token_id)
            self.db.commit()

if __name__ == "__main__":
    unittest.main()
