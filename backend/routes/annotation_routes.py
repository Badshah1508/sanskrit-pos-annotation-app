from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import cast, Integer
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
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Saves expert's token tags and sentence notes as a draft without marking it verified."""
    return save_sentence_draft(
        annotation_id=annotation_id,
        token_inputs=payload.tokens,
        note=payload.note,
        user=current_user,
        db=db,
        workspace=workspace
    )

@router.post("/{annotation_id}/verify", response_model=SentenceDetailResponse)
def verify_sentence(
    annotation_id: str,
    payload: SentenceVerifyRequest,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Validates completeness of tags, saves all tokens in an atomic transaction,
    and updates sentence status to verified in the database.
    """
    return verify_sentence_annotation(
        annotation_id=annotation_id,
        token_inputs=payload.tokens,
        note=payload.note,
        user=current_user,
        db=db,
        workspace=workspace
    )

@router.get("/pending", response_model=List[SentenceDetailResponse])
def get_pending_sentences(
    limit: int = 20,
    offset: int = 0,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a paginated list of pending sentences within the expert's assigned sentence_position range."""
    from routes.dataset_routes import resolve_sentence_position_range
    start_pos, end_pos, _ = resolve_sentence_position_range(workspace, current_user)

    return (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(
            Sentence.status == "pending",
            Sentence.sentence_position >= start_pos,
            Sentence.sentence_position <= end_pos
        )
        .order_by(Sentence.sentence_position.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

@router.get("/verified", response_model=List[SentenceDetailResponse])
def get_verified_sentences(
    limit: int = 20,
    offset: int = 0,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns a paginated list of expert-verified sentences within the expert's assigned sentence_position range."""
    from routes.dataset_routes import resolve_sentence_position_range
    start_pos, end_pos, _ = resolve_sentence_position_range(workspace, current_user)

    return (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(
            Sentence.status == "verified",
            Sentence.sentence_position >= start_pos,
            Sentence.sentence_position <= end_pos
        )
        .order_by(Sentence.sentence_position.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


