from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, cast, Integer
from database import get_db
from models import Sentence, Token, User
from schemas import DatasetStatsResponse, SentenceDetailResponse, WorkspaceInfo
from dependencies import get_current_user, get_current_admin
from services.csv_importer import import_sanskrit_csv
from config import settings

router = APIRouter(prefix="/dataset", tags=["Dataset"])

# Fixed configuration for the 7 expert workspaces by sentence_position (1,000 sentences each)
WORKSPACE_DEFS = [
    {"num": 1, "key": "user1", "label": "User 1", "username": "user1", "start": 1, "end": 1000, "docs": 868, "sentences": 1000},
    {"num": 2, "key": "user2", "label": "User 2", "username": "user2", "start": 1001, "end": 2000, "docs": 874, "sentences": 1000},
    {"num": 3, "key": "user3", "label": "User 3", "username": "user3", "start": 2001, "end": 3000, "docs": 890, "sentences": 1000},
    {"num": 4, "key": "user4", "label": "User 4", "username": "user4", "start": 3001, "end": 4000, "docs": 883, "sentences": 1000},
    {"num": 5, "key": "user5", "label": "User 5", "username": "user5", "start": 4001, "end": 5000, "docs": 879, "sentences": 1000},
    {"num": 6, "key": "user6", "label": "User 6", "username": "user6", "start": 5001, "end": 6000, "docs": 866, "sentences": 1000},
    {"num": 7, "key": "user7", "label": "User 7", "username": "user7", "start": 6001, "end": 7000, "docs": 889, "sentences": 1000},
]


def resolve_sentence_position_range(workspace: Optional[str], current_user: User) -> tuple:
    """
    Resolves (start_pos, end_pos, label).
    If a specific workspace is requested via query param (e.g. user1..user7),
    returns the exact bounds for that expert workspace.
    If no workspace is specified, defaults to current_user's assigned range.
    """
    if workspace:
        clean_ws = workspace.strip().lower().replace(" ", "").replace("_", "")
        if clean_ws == "all":
            return 1, 7000, "All Workspaces (Administrator Overview)"
        for w in WORKSPACE_DEFS:
            if clean_ws in [w["key"], f"user{w['num']}", str(w["num"])]:
                return w["start"], w["end"], w["label"]

    # Fall back to authenticated user's assigned range
    start_pos = current_user.assigned_range_start or 1
    end_pos = current_user.assigned_range_end or 1000
    user_label = current_user.display_name or current_user.username
    return start_pos, end_pos, user_label


# Backwards compatibility alias
resolve_doc_id_range = resolve_sentence_position_range


def resolve_workspace_user(workspace: Optional[str], current_user: User, db: Session) -> Optional[User]:
    """Compatibility helper to find the target User model instance."""
    start_pos, _, _ = resolve_sentence_position_range(workspace, current_user)
    target = db.query(User).filter(User.assigned_range_start == start_pos).first()
    return target or current_user


@router.get("/workspaces", response_model=List[WorkspaceInfo])
def get_workspaces():
    """Returns the list of the 7 configured Sanskrit POS annotation expert workspaces."""
    return [
        WorkspaceInfo(
            id=w["num"],
            key=w["key"],
            label=w["label"],
            username=w["username"],
            range_label=f"Sentences {w['start']:,}–{w['end']:,}",
            range_start=w["start"],
            range_end=w["end"],
            total_documents=w["docs"],
            total_sentences=w["sentences"]
        )
        for w in WORKSPACE_DEFS
    ]


@router.get("/stats", response_model=DatasetStatsResponse)
def get_stats(
    workspace: Optional[str] = Query(None, description="Workspace key e.g. user1, user2"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Computes real-time annotation statistics for the requested sentence_position range.
    Calculates document counts and sentence counts separately.
    """
    start_pos, end_pos, label = resolve_sentence_position_range(workspace, current_user)
    base_filter = (Sentence.sentence_position >= start_pos) & (Sentence.sentence_position <= end_pos)

    # Status counts for sentences in this sentence_position range
    counts = (
        db.query(Sentence.status, func.count(Sentence.id))
        .filter(base_filter)
        .group_by(Sentence.status)
        .all()
    )
    counts_dict = dict(counts)
    pending = counts_dict.get("pending", 0)
    in_progress = counts_dict.get("in_progress", 0)
    verified = counts_dict.get("verified", 0)
    total_sentences = pending + in_progress + verified

    # Count distinct unique documents in this sentence range
    total_documents = (
        db.query(func.count(func.distinct(Sentence.doc_id)))
        .filter(base_filter)
        .scalar() or 0
    )

    # Count distinct verified documents in this sentence range
    verified_documents = (
        db.query(func.count(func.distinct(Sentence.doc_id)))
        .filter(base_filter, Sentence.status == "verified")
        .scalar() or 0
    )

    completion_pct = (verified / total_sentences * 100.0) if total_sentences > 0 else 0.0

    # Token count for sentences in this range
    token_count = (
        db.query(func.count(Token.id))
        .join(Sentence, Token.sentence_id == Sentence.id)
        .filter(base_filter)
        .scalar() or 0
    )

    return {
        "total_documents": total_documents,
        "total_sentences": total_sentences,
        "pending_sentences": pending,
        "in_progress_sentences": in_progress,
        "verified_sentences": verified,
        "verified_documents": verified_documents,
        "total_tokens": token_count,
        "completion_percentage": round(completion_pct, 2),
        "expert_verified": verified,
        "workspace_label": label,
        "assigned_range": f"Sentences {start_pos:,}–{end_pos:,}"
    }


@router.get("/sentences/next", response_model=SentenceDetailResponse)
def get_next_sentence(
    workspace: Optional[str] = Query(None, description="Workspace key e.g. user1, user2"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the next pending or in-progress sentence strictly within the sentence_position range
    assigned to the requested expert workspace.
    Ordered stably by Sentence.sentence_position.asc().
    """
    start_pos, end_pos, label = resolve_sentence_position_range(workspace, current_user)

    # 1. First check if user has an unfinished draft in their sentence_position range
    draft = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(
            Sentence.sentence_position >= start_pos,
            Sentence.sentence_position <= end_pos,
            Sentence.status == "in_progress"
        )
        .order_by(Sentence.sentence_position.asc())
        .first()
    )
    if draft:
        return draft

    # 2. Otherwise return the earliest pending sentence in their sentence_position range
    pending = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(
            Sentence.sentence_position >= start_pos,
            Sentence.sentence_position <= end_pos,
            Sentence.status == "pending"
        )
        .order_by(Sentence.sentence_position.asc())
        .first()
    )
    if pending:
        return pending

    # 3. Check if any sentences exist in this range
    total_in_range = db.query(func.count(Sentence.id)).filter(
        Sentence.sentence_position >= start_pos,
        Sentence.sentence_position <= end_pos
    ).scalar() or 0

    if total_in_range == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sentences exist in {label} range (Sentences {start_pos:,}–{end_pos:,})."
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"All sentences assigned to {label} (Sentences {start_pos:,}–{end_pos:,}) have been verified!"
    )


@router.get("/sentences/{annotation_id}", response_model=SentenceDetailResponse)
def get_sentence_by_id(
    annotation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Fetch a specific sentence by its unique annotation_id with authorization check."""
    sentence = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(Sentence.annotation_id == annotation_id)
        .first()
    )
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sentence '{annotation_id}' not found."
        )

    # Server-side security check: expert cannot access sentences outside assigned sentence_position range
    if current_user.role != "admin":
        start_pos = current_user.assigned_range_start or 1
        end_pos = current_user.assigned_range_end or 1000
        pos = sentence.sentence_position or 0
        if pos < start_pos or pos > end_pos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Sentence '{annotation_id}' is at position #{pos}, which is outside your assigned sentence range ({start_pos:,}–{end_pos:,})."
            )

    return sentence


@router.post("/import")
def trigger_import(file_path: str = None, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin endpoint to trigger or re-trigger dataset import from the configured 70% CSV path."""
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
