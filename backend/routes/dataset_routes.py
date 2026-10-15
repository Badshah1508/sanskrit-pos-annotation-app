from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from database import get_db
from models import Sentence, Token, User
from schemas import DatasetStatsResponse, SentenceDetailResponse, WorkspaceInfo
from dependencies import get_current_user, get_current_admin
from services.csv_importer import import_sanskrit_csv
from config import settings

router = APIRouter(prefix="/dataset", tags=["Dataset"])

# Fixed configuration for the 7 expert workspaces
WORKSPACE_DEFS = [
    {"num": 1, "key": "user1", "label": "User 1", "username": "user1", "start": 1, "end": 1000},
    {"num": 2, "key": "user2", "label": "User 2", "username": "user2", "start": 1001, "end": 2000},
    {"num": 3, "key": "user3", "label": "User 3", "username": "user3", "start": 2001, "end": 3000},
    {"num": 4, "key": "user4", "label": "User 4", "username": "user4", "start": 3001, "end": 4000},
    {"num": 5, "key": "user5", "label": "User 5", "username": "user5", "start": 4001, "end": 5000},
    {"num": 6, "key": "user6", "label": "User 6", "username": "user6", "start": 5001, "end": 6000},
    {"num": 7, "key": "user7", "label": "User 7", "username": "user7", "start": 6001, "end": 7000},
]


def resolve_workspace_user(workspace: Optional[str], current_user: User, db: Session) -> Optional[User]:
    """
    Resolves the target expert user based on the requested workspace and enforces authorization:
    - If current_user is an expert: They are STRICTLY RESTRICTED to their own assigned workspace.
      Attempting to specify another expert's workspace raises 403 Forbidden.
    - If current_user is an admin: They can view any workspace (User 1 - User 7) or view global data.
    """
    if current_user.role != "admin":
        # Expert user: enforce self-assignment
        if workspace:
            clean_ws = workspace.strip().lower().replace(" ", "").replace("_", "")
            user_clean = current_user.username.lower().replace(" ", "").replace("_", "")
            disp_clean = (current_user.display_name or "").lower().replace(" ", "").replace("_", "")
            
            # Check if requested workspace matches this authenticated expert
            matches = (
                clean_ws == user_clean
                or (disp_clean != "" and clean_ws == disp_clean)
                or (clean_ws == f"user{current_user.id}")
                or (clean_ws == "user1" and user_clean in ["sanskrit_scholar", "scholar"])
            )
            if not matches:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: You are logged in as {current_user.display_name or current_user.username}. "
                           f"You cannot access sentences belonging to {workspace}. "
                           f"Please log in with the appropriate expert account."
                )
        return current_user

    # Admin user: can inspect any workspace
    if not workspace:
        return None

    clean_ws = workspace.strip().lower().replace(" ", "").replace("_", "")
    target_user = None

    for w_def in WORKSPACE_DEFS:
        if clean_ws in [w_def["key"], f"user{w_def['num']}", str(w_def["num"])]:
            target_user = db.query(User).filter(
                (User.username == w_def["username"]) | (User.username == f"user{w_def['num']}")
            ).first()
            if not target_user and w_def["num"] == 1:
                target_user = db.query(User).filter(User.username == "sanskrit_scholar").first()
            break

    if not target_user:
        # Try direct username lookup
        target_user = db.query(User).filter(
            (func.lower(User.username) == clean_ws) | (func.lower(User.display_name) == clean_ws)
        ).first()

    return target_user


@router.get("/workspaces", response_model=List[WorkspaceInfo])
def get_workspaces():
    """Returns the list of the 7 configured Sanskrit POS annotation expert workspaces."""
    return [
        WorkspaceInfo(
            id=w["num"],
            key=w["key"],
            label=w["label"],
            username=w["username"],
            range_label=f"{w['start']:,}–{w['end']:,}",
            range_start=w["start"],
            range_end=w["end"],
            total_sentences=1000
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
    Computes real-time annotation statistics.
    Optimized with single-query status aggregation for fast mobile & desktop performance.
    """
    target_user = resolve_workspace_user(workspace, current_user, db)

    if target_user:
        # Per-expert workspace stats (1,000 assigned sentences)
        counts = (
            db.query(Sentence.status, func.count(Sentence.id))
            .filter(Sentence.assigned_expert_id == target_user.id)
            .group_by(Sentence.status)
            .all()
        )
        counts_dict = dict(counts)
        pending = counts_dict.get("pending", 0)
        in_progress = counts_dict.get("in_progress", 0)
        verified = counts_dict.get("verified", 0)
        total_sentences = 1000

        completion_pct = (verified / total_sentences * 100.0) if total_sentences > 0 else 0.0

        r_start = target_user.assigned_range_start or 1
        r_end = target_user.assigned_range_end or 1000

        # Estimated token count for this 1,000 sentence segment (~9.9 tokens/sentence average)
        # Fast query for tokens belonging to this expert's sentences
        token_count = (
            db.query(func.count(Token.id))
            .join(Sentence, Token.sentence_id == Sentence.id)
            .filter(Sentence.assigned_expert_id == target_user.id)
            .scalar() or 0
        )

        return {
            "total_sentences": total_sentences,
            "pending_sentences": pending,
            "in_progress_sentences": in_progress,
            "verified_sentences": verified,
            "total_tokens": token_count,
            "completion_percentage": round(completion_pct, 2),
            "expert_verified": verified,
            "workspace_label": target_user.display_name or f"User {target_user.id}",
            "assigned_range": f"{r_start:,}–{r_end:,}"
        }

    # Global Admin Overview (when no specific workspace selected by admin)
    counts = (
        db.query(Sentence.status, func.count(Sentence.id))
        .group_by(Sentence.status)
        .all()
    )
    counts_dict = dict(counts)
    pending = counts_dict.get("pending", 0)
    in_progress = counts_dict.get("in_progress", 0)
    verified = counts_dict.get("verified", 0)
    total_sentences = 7000

    completion_pct = (verified / total_sentences * 100.0) if total_sentences > 0 else 0.0

    return {
        "total_sentences": total_sentences,
        "pending_sentences": pending,
        "in_progress_sentences": in_progress,
        "verified_sentences": verified,
        "total_tokens": 69364,
        "completion_percentage": round(completion_pct, 2),
        "expert_verified": verified,
        "workspace_label": "All Workspaces (Administrator Overview)",
        "assigned_range": "1–7,000"
    }


@router.get("/sentences/next", response_model=SentenceDetailResponse)
def get_next_sentence(
    workspace: Optional[str] = Query(None, description="Workspace key e.g. user1, user2"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the next pending or in-progress sentence strictly within the authenticated expert's assigned range.
    Uses selectinload for fast single-query token retrieval.
    """
    target_user = resolve_workspace_user(workspace, current_user, db)
    if not target_user:
        # Default to User 1 if admin did not specify a workspace
        target_user = db.query(User).filter(User.username == "user1").first() or current_user

    # 1. First check if user has an unfinished draft in their assigned range
    draft = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(Sentence.assigned_expert_id == target_user.id, Sentence.status == "in_progress")
        .order_by(Sentence.id.asc())
        .first()
    )
    if draft:
        return draft

    # 2. Otherwise return the earliest pending sentence in their assigned range
    pending = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(Sentence.assigned_expert_id == target_user.id, Sentence.status == "pending")
        .order_by(Sentence.id.asc())
        .first()
    )
    if pending:
        return pending

    r_start = target_user.assigned_range_start or 1
    r_end = target_user.assigned_range_end or 1000
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"All 1,000 sentences assigned to {target_user.display_name or target_user.username} (Range: {r_start:,}–{r_end:,}) have been verified!"
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

    # Security check: Expert can only access sentences in their assigned range
    if current_user.role != "admin" and sentence.assigned_expert_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: This sentence is assigned to another expert's workspace."
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
