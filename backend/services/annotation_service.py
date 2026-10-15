from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models import Sentence, Token, AnnotationHistory, User
from schemas import TokenAnnotationInput
from config import settings

APPROVED_TAG_SET = set(settings.APPROVED_SANSKRIT_TAGS)

def save_sentence_draft(
    annotation_id: str,
    token_inputs: List[TokenAnnotationInput],
    note: Optional[str],
    user: User,
    db: Session,
    workspace: Optional[str] = None
) -> Sentence:
    """Saves expert's current progress as draft without marking sentence verified."""
    sentence = db.query(Sentence).filter(Sentence.annotation_id == annotation_id).first()
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sentence with annotation_id '{annotation_id}' not found."
        )

    # Server-side security check: expert cannot save drafts outside their assigned doc_id range
    if user.role != "admin":
        r_start = user.assigned_range_start or 1
        r_end = user.assigned_range_end or 1000
        try:
            doc_num = int(sentence.doc_id)
        except (ValueError, TypeError):
            doc_num = 0
        if doc_num < r_start or doc_num > r_end:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Sentence '{annotation_id}' belongs to doc_id {sentence.doc_id}, which is outside your assigned range ({r_start:,}–{r_end:,})."
            )

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
    sentence.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(sentence)
    return sentence


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
    sentence = db.query(Sentence).filter(Sentence.annotation_id == annotation_id).first()
    if not sentence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sentence with annotation_id '{annotation_id}' not found."
        )

    # Server-side security check: expert cannot verify sentences outside their assigned doc_id range
    if user.role != "admin":
        r_start = user.assigned_range_start or 1
        r_end = user.assigned_range_end or 1000
        try:
            doc_num = int(sentence.doc_id)
        except (ValueError, TypeError):
            doc_num = 0
        if doc_num < r_start or doc_num > r_end:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: Sentence '{annotation_id}' belongs to doc_id {sentence.doc_id}, which is outside your assigned range ({r_start:,}–{r_end:,})."
            )

    # Determine actor identity for verified_by
    verifier_name = user.display_name or user.username
    if workspace and workspace.strip().lower() != "all":
        clean_ws = workspace.strip().lower()
        if clean_ws.startswith("user"):
            num = clean_ws.replace("user", "").strip()
            verifier_name = f"User {num}"

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
                changed_at=datetime.utcnow()
            )
            db.add(history)

        token.gold_sanskrit_tag = new_tag
        if inp.annotation_note:
            token.annotation_note = inp.annotation_note.strip()

    sentence.status = "verified"
    sentence.annotation_note = note
    sentence.verified_by = verifier_name
    sentence.verified_at = datetime.utcnow()
    sentence.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(sentence)
    return sentence
