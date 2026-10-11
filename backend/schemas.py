from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

# ----------------- User Schemas -----------------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str = "expert"

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ----------------- Token Schemas -----------------
class TokenSchema(BaseModel):
    id: int
    token_id: int
    token: str
    lemma: Optional[str] = None
    upos: Optional[str] = None
    stanza_upos: Optional[str] = None
    xpos: Optional[str] = None
    feats: Optional[str] = None
    gold_sanskrit_tag: Optional[str] = None
    annotation_note: Optional[str] = None

    class Config:
        from_attributes = True

class TokenAnnotationInput(BaseModel):
    token_id: int
    gold_sanskrit_tag: Optional[str] = None
    annotation_note: Optional[str] = None


# ----------------- Sentence Schemas -----------------
class SentenceBase(BaseModel):
    doc_id: str
    sentence_id: int
    annotation_id: str
    sentence_text: str
    status: str
    annotation_note: Optional[str] = None
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None

class SentenceDetailResponse(SentenceBase):
    id: int
    tokens: List[TokenSchema] = []

    class Config:
        from_attributes = True

class SentenceDraftRequest(BaseModel):
    tokens: List[TokenAnnotationInput]
    note: Optional[str] = None

class SentenceVerifyRequest(BaseModel):
    tokens: List[TokenAnnotationInput]
    note: Optional[str] = None


# ----------------- Dataset Stats Schema -----------------
class DatasetStatsResponse(BaseModel):
    total_sentences: int
    pending_sentences: int
    in_progress_sentences: int
    verified_sentences: int
    total_tokens: int
    completion_percentage: float
    expert_verified: int


# ----------------- Tag Schema -----------------
class TagItem(BaseModel):
    tag: str
    name: str
    description: Optional[str] = None
