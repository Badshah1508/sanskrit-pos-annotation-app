import sys
import os

# Add parent directory to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
from config import settings
from services.csv_importer import import_sanskrit_csv

def main():
    print("==========================================================")
    print("Sanskrit POS Dataset Importer (70% Stanza-Annotated Queue)")
    print("==========================================================")
    
    # Ensure database schema is created
    Base.metadata.create_all(bind=engine)
    
    csv_path = settings.DATASET_CSV_PATH
    print(f"Target CSV Path: {csv_path}")

    # Safety check: Verify that path does not point to 30% unassigned test split
    if "30_percent" in csv_path:
        print("CRITICAL ERROR: The specified CSV path contains '30_percent'.")
        print("As per research methodology, the 30% portion must remain untouched.")
        sys.exit(1)

    if not os.path.exists(csv_path):
        print(f"ERROR: Dataset CSV file not found at: {csv_path}")
        sys.exit(1)

    db = SessionLocal()
    try:
        print("Reading CSV, validating tokens, and importing sentences...")
        results = import_sanskrit_csv(csv_path, db)
        print("\n--- Import Summary ---")
        print(f"Documents Imported: {results['documents_imported']}")
        print(f"Sentences Imported: {results['sentences_imported']}")
        print(f"Tokens Imported:    {results['tokens_imported']}")
        print(f"Skipped Sentences:  {results['skipped_sentences']} (already in database)")
        print("\nImport completed successfully.")
    except Exception as e:
        print(f"Import failed with error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()
