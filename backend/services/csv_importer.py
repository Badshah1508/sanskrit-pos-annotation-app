import os
import pandas as pd
from typing import Dict, Any
from sqlalchemy.orm import Session
from models import Sentence, Token
from config import settings

REQUIRED_COLUMNS = [
    "doc_id", "sentence_id", "annotation_id", "sentence_text",
    "token_id", "token", "lemma", "upos", "stanza_upos", "xpos", "feats"
]

def import_sanskrit_csv(file_path: str, db: Session) -> Dict[str, Any]:
    """
    Safely imports the 70% automatically annotated Sanskrit POS CSV into the database.
    - Strictly validates required columns.
    - Groups tokens by sentence (annotation_id).
    - Preserves exact token_id sequence.
    - Idempotent: Skips already existing sentences to prevent duplicate records.
    - Never modifies the original 30% unassigned test dataset.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configured dataset file not found at: {file_path}")

    # Read CSV using UTF-8 encoding
    try:
        df = pd.read_csv(file_path, encoding="utf-8", dtype=str)
    except Exception as e:
        raise ValueError(f"Could not read CSV file: {str(e)}")

    # Validate columns
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset CSV: {', '.join(missing_cols)}")

    # Fill NaN values with empty string or sensible default
    df = df.fillna("")

    # Check for empty dataset
    if df.empty:
        return {
            "documents_imported": 0,
            "sentences_imported": 0,
            "tokens_imported": 0,
            "skipped_sentences": 0
        }

    # Fetch existing annotation_ids in database to guarantee idempotency
    existing_ids = set(
        x[0] for x in db.query(Sentence.annotation_id).all()
    )

    imported_docs = set()
    sentences_count = 0
    tokens_count = 0
    skipped_count = 0

    # Group dataframe by annotation_id
    grouped = df.groupby("annotation_id", sort=False)

    for annotation_id, group in grouped:
        annotation_id = str(annotation_id).strip()
        if not annotation_id:
            continue

        if annotation_id in existing_ids:
            skipped_count += 1
            continue

        first_row = group.iloc[0]
        doc_id = str(first_row["doc_id"]).strip()
        try:
            sentence_id = int(first_row["sentence_id"])
        except ValueError:
            sentence_id = 1
            
        sentence_text = str(first_row["sentence_text"]).strip()

        # Create sentence record
        new_sentence = Sentence(
            annotation_id=annotation_id,
            doc_id=doc_id,
            sentence_id=sentence_id,
            sentence_text=sentence_text,
            status="pending"
        )
        db.add(new_sentence)
        db.flush()  # obtain new_sentence.id

        imported_docs.add(doc_id)
        sentences_count += 1

        # Add tokens in order
        # Sort group by token_id if possible
        try:
            group_sorted = group.copy()
            group_sorted["token_id_int"] = pd.to_numeric(group_sorted["token_id"], errors="coerce").fillna(0).astype(int)
            group_sorted = group_sorted.sort_values(by="token_id_int")
        except Exception:
            group_sorted = group

        for _, row in group_sorted.iterrows():
            try:
                t_id = int(row["token_id"])
            except ValueError:
                t_id = 1

            token_obj = Token(
                sentence_id=new_sentence.id,
                token_id=t_id,
                token=str(row["token"]).strip(),
                lemma=str(row["lemma"]).strip() or None,
                upos=str(row["upos"]).strip() or None,
                stanza_upos=str(row["stanza_upos"]).strip() or None,
                xpos=str(row["xpos"]).strip() or None,
                feats=str(row["feats"]).strip() or None,
                gold_sanskrit_tag=None  # Explicitly unassigned initially
            )
            db.add(token_obj)
            tokens_count += 1

        # Periodic commit to prevent large memory spikes
        if sentences_count % 500 == 0:
            db.commit()

    db.commit()

    return {
        "documents_imported": len(imported_docs),
        "sentences_imported": sentences_count,
        "tokens_imported": tokens_count,
        "skipped_sentences": skipped_count
    }
