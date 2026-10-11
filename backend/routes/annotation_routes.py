from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Sentence, User
from schemas import SentenceDetailResponse, SentenceDraftRequest, SentenceVerifyRequest
from dependencies import get_current_user
from services.annotation_service import save_sentence_draft, verify_sentence_annotation

router = APIRouter(prefix="/annotations", tags=["Annotations"])

@router.put("/{annotation_id}/draft", response_model=SentenceDetailResponse)
def save_draft(
    annotation_id: str,
    payload: SentenceDraftRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Saves expert's token tags and sentence notes as a draft without marking it verified."""
    return save_sentence_draft(
        annotation_id=annotation_id,
        token_inputs=payload.tokens,
        note=payload.note,
        user=current_user,
        db=db
    )

@router.post("/{annotation_id}/verify", response_model=SentenceDetailResponse)
def verify_sentence(
    annotation_id: str,
    payload: SentenceVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validates completeness of tags, saves all tokens in an atomic transaction,
    and updates sentence status to verified.
    """
    return verify_sentence_annotation(
        annotation_id=annotation_id,
        token_inputs=payload.tokens,
        note=payload.note,
        user=current_user,
        db=db
    )

@router.get("/pending", response_model=List[SentenceDetailResponse])
def get_pending_sentences(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a paginated list of pending sentences."""
    return (
        db.query(Sentence)
        .filter(Sentence.status == "pending")
        .offset(offset)
        .limit(limit)
        .all()
    )

@router.get("/verified", response_model=List[SentenceDetailResponse])
def get_verified_sentences(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a paginated list of expert-verified sentences."""
    return (
        db.query(Sentence)
        .filter(Sentence.status == "verified")
        .offset(offset)
        .limit(limit)
        .all()
    )
