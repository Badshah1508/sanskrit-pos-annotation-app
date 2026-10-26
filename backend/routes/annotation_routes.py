from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import cast, Integer
from database import get_db
from models import Sentence, User
from schemas import (
    SentenceDetailResponse, SentenceDraftRequest, SentenceVerifyRequest,
    SentenceSkipRequest, SkipSentenceResponse
)
from dependencies import get_current_user
from services.annotation_service import (
    save_sentence_draft, verify_sentence_annotation,
    skip_sentence_annotation, resume_skipped_sentence, get_next_sentence_after_skip
)

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


@router.post("/{annotation_id}/skip", response_model=SkipSentenceResponse)
def skip_sentence(
    annotation_id: str,
    payload: Optional[SentenceSkipRequest] = None,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marks the given sentence as skipped for this expert, preserves any partial annotations,
    and returns the next eligible sentence in the workspace.
    """
    from routes.dataset_routes import resolve_sentence_position_range
    start_pos, end_pos, _ = resolve_sentence_position_range(workspace, current_user)

    tokens = payload.tokens if payload else None
    note = payload.note if payload else None

    skipped_sent = skip_sentence_annotation(
        annotation_id=annotation_id,
        token_inputs=tokens,
        note=note,
        user=current_user,
        db=db,
        workspace=workspace
    )

    next_sent = get_next_sentence_after_skip(
        current_pos=skipped_sent.sentence_position,
        start_pos=start_pos,
        end_pos=end_pos,
        db=db
    )

    return SkipSentenceResponse(
        message=f"Sentence #{skipped_sent.sentence_position} skipped. You can annotate it later.",
        skipped_sentence_id=skipped_sent.id,
        skipped_annotation_id=skipped_sent.annotation_id,
        next_sentence=next_sent
    )


@router.post("/skip", response_model=SkipSentenceResponse)
def skip_sentence_alt(
    annotation_id: str = Query(..., description="Unique annotation_id of the sentence to skip"),
    payload: Optional[SentenceSkipRequest] = None,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alternative POST endpoint accepting annotation_id as query parameter."""
    return skip_sentence(
        annotation_id=annotation_id,
        payload=payload,
        workspace=workspace,
        db=db,
        current_user=current_user
    )


@router.get("/skipped", response_model=List[SentenceDetailResponse])
def get_skipped_sentences(
    limit: int = 50,
    offset: int = 0,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Returns all skipped sentences strictly within the expert's assigned sentence_position range."""
    from routes.dataset_routes import resolve_sentence_position_range
    start_pos, end_pos, _ = resolve_sentence_position_range(workspace, current_user)

    return (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(
            Sentence.status == "skipped",
            Sentence.sentence_position >= start_pos,
            Sentence.sentence_position <= end_pos
        )
        .order_by(Sentence.sentence_position.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post("/{annotation_id}/resume", response_model=SentenceDetailResponse)
def resume_sentence(
    annotation_id: str,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reopens a skipped sentence and transitions its status to in_progress so the scholar can complete it.
    """
    return resume_skipped_sentence(
        annotation_id=annotation_id,
        user=current_user,
        db=db,
        workspace=workspace
    )


@router.post("/resume/{sentence_id}", response_model=SentenceDetailResponse)
def resume_sentence_by_id(
    sentence_id: int,
    workspace: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reopens a skipped sentence by numeric sentence primary key."""
    from routes.dataset_routes import resolve_sentence_position_range
    start_pos, end_pos, target_label = resolve_sentence_position_range(workspace, current_user)

    sentence = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(Sentence.id == sentence_id)
        .first()
    )
    if not sentence:
        raise HTTPException(
            status_code=404,
            detail=f"Sentence with id {sentence_id} not found."
        )

    pos = sentence.sentence_position or 0
    if pos < start_pos or pos > end_pos:
        raise HTTPException(
            status_code=400,
            detail=f"Sentence with id {sentence_id} (position #{pos}) is outside {target_label} range ({start_pos:,}–{end_pos:,})."
        )

    return resume_skipped_sentence(
        annotation_id=sentence.annotation_id,
        user=current_user,
        db=db,
        workspace=workspace
    )



