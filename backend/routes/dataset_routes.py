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

# Fixed configuration for the 7 expert workspaces by doc_id
WORKSPACE_DEFS = [
    {"num": 1, "key": "user1", "label": "User 1", "username": "user1", "start": 1, "end": 1000, "docs": 1000, "sentences": 2658},
    {"num": 2, "key": "user2", "label": "User 2", "username": "user2", "start": 1001, "end": 2000, "docs": 1000, "sentences": 2029},
    {"num": 3, "key": "user3", "label": "User 3", "username": "user3", "start": 2001, "end": 3000, "docs": 1000, "sentences": 1611},
    {"num": 4, "key": "user4", "label": "User 4", "username": "user4", "start": 3001, "end": 4000, "docs": 597, "sentences": 702},
    {"num": 5, "key": "user5", "label": "User 5", "username": "user5", "start": 4001, "end": 5000, "docs": 0, "sentences": 0},
    {"num": 6, "key": "user6", "label": "User 6", "username": "user6", "start": 5001, "end": 6000, "docs": 0, "sentences": 0},
    {"num": 7, "key": "user7", "label": "User 7", "username": "user7", "start": 6001, "end": 7000, "docs": 0, "sentences": 0},
]


def resolve_doc_id_range(workspace: Optional[str], current_user: User) -> tuple:
    """
    Resolves (start_doc, end_doc, label) enforcing server-side access control.
    Returns:
        start_doc (int): Minimum doc_id (inclusive)
        end_doc (int): Maximum doc_id (inclusive)
        label (str): Workspace human-readable label
    Raises:
        HTTPException(403) if a non-admin expert attempts to access outside their assigned range.
    """
    # 1. Non-admin expert must always be restricted to their server-side assigned range
    if current_user.role != "admin":
        start_doc = current_user.assigned_range_start or 1
        end_doc = current_user.assigned_range_end or 1000
        user_label = current_user.display_name or current_user.username
        
        # If client passed a workspace, ensure it matches user's assigned range
        if workspace:
            clean_ws = workspace.strip().lower().replace(" ", "").replace("_", "")
            for w in WORKSPACE_DEFS:
                if clean_ws in [w["key"], f"user{w['num']}", str(w["num"])]:
                    if w["start"] != start_doc or w["end"] != end_doc:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Access forbidden: You are authenticated as {current_user.username} (assigned doc_id range {start_doc:,}–{end_doc:,}). You cannot access workspace '{w['label']}'."
                        )
                    break
        return start_doc, end_doc, user_label

    # 2. Admin user can view any workspace or global dataset
    if workspace:
        clean_ws = workspace.strip().lower().replace(" ", "").replace("_", "")
        if clean_ws == "all":
            return 1, 7000, "All Workspaces (Administrator Overview)"
        for w in WORKSPACE_DEFS:
            if clean_ws in [w["key"], f"user{w['num']}", str(w["num"])]:
                return w["start"], w["end"], w["label"]

    # Default for admin without workspace parameter is User 1 (doc_id 1–1,000)
    return 1, 1000, "User 1"


def resolve_workspace_user(workspace: Optional[str], current_user: User, db: Session) -> Optional[User]:
    """Compatibility helper to find the target User model instance."""
    start_doc, _, _ = resolve_doc_id_range(workspace, current_user)
    target = db.query(User).filter(User.assigned_range_start == start_doc).first()
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
            range_label=f"doc_id {w['start']:,}–{w['end']:,}",
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
    Computes real-time annotation statistics for the requested doc_id range.
    Calculates document counts and sentence counts separately.
    """
    start_doc, end_doc, label = resolve_doc_id_range(workspace, current_user)
    doc_num = cast(Sentence.doc_id, Integer)
    base_filter = (doc_num >= start_doc) & (doc_num <= end_doc)

    # Status counts for sentences in this doc_id range
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

    # Count distinct unique documents in this doc_id range
    total_documents = (
        db.query(func.count(func.distinct(Sentence.doc_id)))
        .filter(base_filter)
        .scalar() or 0
    )

    # Count distinct verified documents in this doc_id range
    verified_documents = (
        db.query(func.count(func.distinct(Sentence.doc_id)))
        .filter(base_filter, Sentence.status == "verified")
        .scalar() or 0
    )

    completion_pct = (verified / total_sentences * 100.0) if total_sentences > 0 else 0.0

    # Token count for sentences in this doc_id range
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
        "assigned_range": f"doc_id {start_doc:,}–{end_doc:,}"
    }


@router.get("/sentences/next", response_model=SentenceDetailResponse)
def get_next_sentence(
    workspace: Optional[str] = Query(None, description="Workspace key e.g. user1, user2"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the next pending or in-progress sentence strictly within the doc_id range
    assigned to the requested expert workspace.
    Uses cast(Sentence.doc_id, Integer) for safe numeric filtering.
    """
    start_doc, end_doc, label = resolve_doc_id_range(workspace, current_user)
    doc_num = cast(Sentence.doc_id, Integer)

    # 1. First check if user has an unfinished draft in their doc_id range
    draft = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(
            doc_num >= start_doc,
            doc_num <= end_doc,
            Sentence.status == "in_progress"
        )
        .order_by(doc_num.asc(), Sentence.sentence_id.asc(), Sentence.id.asc())
        .first()
    )
    if draft:
        return draft

    # 2. Otherwise return the earliest pending sentence in their doc_id range
    pending = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(
            doc_num >= start_doc,
            doc_num <= end_doc,
            Sentence.status == "pending"
        )
        .order_by(doc_num.asc(), Sentence.sentence_id.asc(), Sentence.id.asc())
        .first()
    )
    if pending:
        return pending

    # 3. Check if any sentences exist in this range
    total_in_range = db.query(func.count(Sentence.id)).filter(
        doc_num >= start_doc,
        doc_num <= end_doc
    ).scalar() or 0

    if total_in_range == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No sentences exist in {label} range (doc_id {start_doc:,}–{end_doc:,}). The 70% annotation queue spans doc_id 1 to 3,597."
        )

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"All sentences assigned to {label} (doc_id range {start_doc:,}–{end_doc:,}) have been verified!"
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

    # Server-side security check: expert cannot access sentences outside assigned doc_id range
    if current_user.role != "admin":
        start_doc = current_user.assigned_range_start or 1
        end_doc = current_user.assigned_range_end or 1000
        try:
            doc_num = int(sentence.doc_id)
        except (ValueError, TypeError):
            doc_num = 0
        if doc_num < start_doc or doc_num > end_doc:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Sentence '{annotation_id}' belongs to doc_id {sentence.doc_id}, which is outside your assigned range ({start_doc:,}–{end_doc:,})."
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
