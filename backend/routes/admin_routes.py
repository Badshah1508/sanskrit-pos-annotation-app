from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from dependencies import get_current_admin
from auth import get_password_hash

router = APIRouter(prefix="/admin", tags=["Administration"])

@router.post("/users", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Create a new expert or administrator account. Restricted to administrators."""
    existing_user = db.query(User).filter(
        (User.username == payload.username) | (User.email == payload.email)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username or email already exists."
        )

    new_user = User(
        username=payload.username.strip(),
        email=payload.email.strip(),
        password_hash=get_password_hash(payload.password),
        role=payload.role if payload.role in ["admin", "expert"] else "expert"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/users", response_model=List[UserResponse])
def list_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """List all expert and admin user accounts."""
    return db.query(User).order_by(User.id).all()
