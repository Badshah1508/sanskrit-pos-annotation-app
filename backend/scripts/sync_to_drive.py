"""
Automated Google Drive Sync for Verified Sanskrit POS Dataset.
Exports the latest gold-standard verified sentences from the database
and syncs them to Google Drive (deleting previous version and replacing with the latest).
"""

import os
import sys
import json
import logging
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("DriveSync")

# Ensure backend root is on sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import SessionLocal
from models import Sentence
from services.export_service import generate_verified_csv

DEFAULT_WEBHOOK_URL = os.getenv(
    "GDRIVE_WEBHOOK_URL",
    "https://script.google.com/macros/s/AKfycbwDyCGka8Tk6hPgOkqZLY3kA5csxtewPlJo2kWN2Hvv02deKPtfL-a6dqWvpqwsat-P/exec"
)


def sync_via_apps_script_webhook(webhook_url: str, csv_bytes: bytes, verified_count: int) -> dict:
    """
    Uploads the CSV to Google Drive via the Google Apps Script Webhook.
    Runs under the user's personal Google account, overwriting/replacing previous files.
    """
    logger.info(f"Syncing to Google Drive via Apps Script Webhook: {webhook_url[:50]}...")

    try:
        import requests
        response = requests.post(
            webhook_url,
            data=csv_bytes,
            headers={"Content-Type": "text/csv; charset=utf-8"},
            timeout=90
        )
        if response.status_code == 200:
            try:
                result = response.json()
            except Exception:
                result = {"status": "success", "raw_response": response.text}
        else:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

    except ImportError:
        import urllib.request
        import urllib.error
        req = urllib.request.Request(
            webhook_url,
            data=csv_bytes,
            headers={"Content-Type": "text/csv; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = resp.read().decode("utf-8")
            try:
                result = json.loads(body)
            except Exception:
                result = {"status": "success", "raw_response": body}

    logger.info("==================================================================")
    logger.info("✓ SUCCESS: Uploaded latest verified dataset to Google Drive!")
    logger.info(f"✓ Verified Sentences in File: {verified_count}")
    if "url" in result:
        logger.info(f"✓ View Link: {result['url']}")
    if "fileId" in result:
        logger.info(f"✓ File ID: {result['fileId']}")
    logger.info("==================================================================")
    return result


def sync_verified_dataset(
    webhook_url: Optional[str] = None,
    force: bool = False
) -> dict:
    """
    Main entry point for syncing verified Sanskrit POS dataset to Google Drive.
    """
    db = SessionLocal()
    try:
        verified_count = db.query(Sentence).filter(Sentence.status == "verified").count()
        total_count = db.query(Sentence).count()
        logger.info(f"Database status: {verified_count:,} verified sentences out of {total_count:,} total.")

        if verified_count == 0 and not force:
            logger.info("No verified sentences in database yet. Skipping sync (use --force to override).")
            return {
                "status": "skipped",
                "verified_count": 0,
                "reason": "No verified sentences to export"
            }

        logger.info("Generating UTF-8 gold-standard CSV dataset...")
        csv_buffer = generate_verified_csv(db)
        csv_bytes = csv_buffer.getvalue().encode("utf-8")
        file_size_kb = len(csv_bytes) / 1024
        logger.info(f"Generated CSV ({file_size_kb:.2f} KB) with {verified_count} verified sentences.")
    finally:
        db.close()

    target_webhook = webhook_url or DEFAULT_WEBHOOK_URL
    return sync_via_apps_script_webhook(target_webhook, csv_bytes, verified_count)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sync verified Sanskrit POS dataset to Google Drive.")
    parser.add_argument("--force", action="store_true", help="Force upload even if 0 verified sentences.")
    parser.add_argument("--webhook", type=str, default=None, help="Google Apps Script Webhook URL.")
    args = parser.parse_args()

    try:
        sync_verified_dataset(webhook_url=args.webhook, force=args.force)
    except Exception as exc:
        logger.error(f"Sync failed: {exc}", exc_info=True)
        sys.exit(1)
