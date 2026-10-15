from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, selectinload
from models import Sentence, Token, AnnotationHistory, User
from schemas import TokenAnnotationInput
from config import settings

APPROVED_TAG_SET = set(settings.APPROVED_SANSKRIT_TAGS)

def _get_utc_now():
    return datetime.now(timezone.utc)


def save_sentence_draft(
    annotation_id: str,
    token_inputs: List[TokenAnnotationInput],
    note: Optional[str],
    user: User,
    db: Session,
    workspace: Optional[str] = None
) -> Sentence:
    """Saves expert's current progress as draft without marking sentence verified."""
    sentence = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(Sentence.annotation_id == annotation_id)
        .first()
    )
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sentence with annotation_id '{annotation_id}' not found."
        )

    # Validate sentence position against target workspace range
    from routes.dataset_routes import WORKSPACE_DEFS
    target_start = None
    target_end = None
    target_label = None

    if workspace:
        clean_ws = workspace.strip().lower().replace(" ", "").replace("_", "")
        if clean_ws != "all":
            for w in WORKSPACE_DEFS:
                if clean_ws in [w["key"], f"user{w['num']}", str(w["num"])]:
                    target_start = w["start"]
                    target_end = w["end"]
                    target_label = w["label"]
                    break

    if target_start is None:
        if user.role != "admin" and user.assigned_range_start and user.assigned_range_end:
            target_start = user.assigned_range_start
            target_end = user.assigned_range_end
            target_label = user.display_name or user.username
        else:
            target_start = 1
            target_end = 7000 if user.role == "admin" else 1000
            target_label = "Workspace"

    pos = sentence.sentence_position or 0
    if pos < target_start or pos > target_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sentence '{annotation_id}' (position #{pos}) is outside {target_label} range ({target_start:,}–{target_end:,})."
        )

    try:
        # Map input by token_id
        tag_map = {t.token_id: t for t in token_inputs}

        for token in sentence.tokens:
            if token.token_id in tag_map:
                inp = tag_map[token.token_id]
                if inp.gold_sanskrit_tag is not None:
                    new_tag = inp.gold_sanskrit_tag.strip()
                    if new_tag and new_tag not in APPROVED_TAG_SET:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid Sanskrit Consortium tag '{new_tag}' for token '{token.token}'."
                        )
                    token.gold_sanskrit_tag = new_tag or None
                if inp.annotation_note is not None:
                    token.annotation_note = inp.annotation_note.strip()

        sentence.annotation_note = note
        if sentence.status != "verified":
            sentence.status = "in_progress"
        sentence.updated_at = _get_utc_now()

        db.commit()
        db.refresh(sentence)
        return sentence
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database transaction failed while saving draft: {str(exc)}"
        )


def verify_sentence_annotation(
    annotation_id: str,
    token_inputs: List[TokenAnnotationInput],
    note: Optional[str],
    user: User,
    db: Session,
    workspace: Optional[str] = None
) -> Sentence:
    """
    Validates completeness, saves all tags in an atomic transaction,
    and marks the sentence as verified.
    """
    sentence = (
        db.query(Sentence)
        .options(selectinload(Sentence.tokens))
        .filter(Sentence.annotation_id == annotation_id)
        .first()
    )
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sentence with annotation_id '{annotation_id}' not found."
        )

    # Validate sentence position against target workspace range
    from routes.dataset_routes import WORKSPACE_DEFS
    target_start = None
    target_end = None
    target_label = None

    if workspace:
        clean_ws = workspace.strip().lower().replace(" ", "").replace("_", "")
        if clean_ws != "all":
            for w in WORKSPACE_DEFS:
                if clean_ws in [w["key"], f"user{w['num']}", str(w["num"])]:
                    target_start = w["start"]
                    target_end = w["end"]
                    target_label = w["label"]
                    break

    if target_start is None:
        if user.role != "admin" and user.assigned_range_start and user.assigned_range_end:
            target_start = user.assigned_range_start
            target_end = user.assigned_range_end
            target_label = user.display_name or user.username
        else:
            target_start = 1
            target_end = 7000 if user.role == "admin" else 1000
            target_label = "Workspace"

    pos = sentence.sentence_position or 0
    if pos < target_start or pos > target_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sentence '{annotation_id}' (position #{pos}) is outside {target_label} range ({target_start:,}–{target_end:,})."
        )

    # Determine actor identity for verified_by
    if user.role == "admin":
        verifier_name = f"{target_label} (Admin)" if target_label else (user.display_name or user.username)
    else:
        verifier_name = target_label or user.display_name or user.username

    tag_map = {t.token_id: t for t in token_inputs}
    missing_tokens = []

    # Strict validation: every token MUST have an approved tag
    for token in sentence.tokens:
        inp = tag_map.get(token.token_id)
        tag = (inp.gold_sanskrit_tag.strip() if inp and inp.gold_sanskrit_tag else None)
        
        if not tag:
            missing_tokens.append(f"#{token.token_id} '{token.token}'")
        elif tag not in APPROVED_TAG_SET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tag '{tag}' for token '{token.token}'. Must be an approved Sanskrit Consortium tag."
            )

    if missing_tokens:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot verify: Missing approved POS tags for tokens: {', '.join(missing_tokens)}"
        )

    now = _get_utc_now()
    try:
        # Save within transaction and record history
        for token in sentence.tokens:
            inp = tag_map[token.token_id]
            new_tag = inp.gold_sanskrit_tag.strip()
            
            # History log if tag changed
            if token.gold_sanskrit_tag != new_tag:
                history = AnnotationHistory(
                    sentence_id=sentence.id,
                    token_id=token.token_id,
                    previous_tag=token.gold_sanskrit_tag,
                    new_tag=new_tag,
                    changed_by=user.username,
                    changed_at=now
                )
                db.add(history)

            token.gold_sanskrit_tag = new_tag
            if inp.annotation_note:
                token.annotation_note = inp.annotation_note.strip()

        sentence.status = "verified"
        sentence.annotation_note = note
        sentence.verified_by = verifier_name
        sentence.verified_at = now
        sentence.updated_at = now

        db.commit()
        db.refresh(sentence)
        return sentence
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database transaction failed while saving verification: {str(exc)}"
        )
