from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Sentence, Token, User
from schemas import DatasetStatsResponse, SentenceDetailResponse
from dependencies import get_current_user, get_current_admin
from services.csv_importer import import_sanskrit_csv
from config import settings

router = APIRouter(prefix="/dataset", tags=["Dataset"])

@router.get("/stats", response_model=DatasetStatsResponse)
def get_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Computes real-time annotation statistics for the 70% corpus."""
    total_sentences = db.query(Sentence).count()
    pending = db.query(Sentence).filter(Sentence.status == "pending").count()
    in_progress = db.query(Sentence).filter(Sentence.status == "in_progress").count()
    verified = db.query(Sentence).filter(Sentence.status == "verified").count()
    total_tokens = db.query(Token).count()

    completion_pct = (verified / total_sentences * 100.0) if total_sentences > 0 else 0.0

    expert_verified = (
        db.query(Sentence)
        .filter(Sentence.verified_by == current_user.username)
        .count()
    )

    return {
        "total_sentences": total_sentences,
        "pending_sentences": pending,
        "in_progress_sentences": in_progress,
        "verified_sentences": verified,
        "total_tokens": total_tokens,
        "completion_percentage": round(completion_pct, 2),
        "expert_verified": expert_verified
    }

@router.get("/sentences/next", response_model=SentenceDetailResponse)
def get_next_sentence(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Returns the next pending or in-progress sentence for the expert to annotate.
    Prioritizes in-progress drafts by this expert, then any pending sentence.
    """
    # 1. First check if user has an unfinished draft
    draft = (
        db.query(Sentence)
        .filter(Sentence.status == "in_progress")
        .order_by(Sentence.id)
        .first()
    )
    if draft:
        return draft

    # 2. Otherwise return the earliest pending sentence
    pending = (
        db.query(Sentence)
        .filter(Sentence.status == "pending")
        .order_by(Sentence.id)
        .first()
    )
    if pending:
        return pending

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No pending sentences remaining in the 70% annotation queue!"
    )

@router.get("/sentences/{annotation_id}", response_model=SentenceDetailResponse)
def get_sentence_by_id(annotation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Fetch a specific sentence by its unique annotation_id."""
    sentence = db.query(Sentence).filter(Sentence.annotation_id == annotation_id).first()
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sentence '{annotation_id}' not found."
        )
    return sentence

@router.post("/import")
def trigger_import(file_path: str = None, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """
    Admin endpoint to trigger or re-trigger dataset import from the configured 70% CSV path.
    Idempotent and safe to run multiple times.
    """
    target_path = file_path or settings.DATASET_CSV_PATH
    try:
        result = import_sanskrit_csv(target_path, db)
        return {
            "status": "success",
            "message": "Dataset imported successfully",
            "details": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Import failed: {str(e)}"
        )
