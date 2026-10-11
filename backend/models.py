from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="expert", nullable=False)  # 'admin' or 'expert'
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Sentence(Base):
    __tablename__ = "sentences"

    id = Column(Integer, primary_key=True, index=True)
    annotation_id = Column(String(100), unique=True, index=True, nullable=False)
    doc_id = Column(String(50), index=True, nullable=False)
    sentence_id = Column(Integer, nullable=False)
    sentence_text = Column(Text, nullable=False)
    status = Column(String(20), default="pending", index=True, nullable=False)  # pending, in_progress, verified
    annotation_note = Column(Text, nullable=True)
    
    assigned_expert_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_by = Column(String(50), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    tokens = relationship("Token", back_populates="sentence", cascade="all, delete-orphan", order_by="Token.token_id")
    assigned_expert = relationship("User", foreign_keys=[assigned_expert_id])


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id", ondelete="CASCADE"), index=True, nullable=False)
    token_id = Column(Integer, nullable=False)
    token = Column(String(255), nullable=False)
    lemma = Column(String(255), nullable=True)
    upos = Column(String(50), nullable=True)
    stanza_upos = Column(String(50), nullable=True)
    xpos = Column(String(50), nullable=True)
    feats = Column(Text, nullable=True)
    
    # Expert Gold Sanskrit Tag (Consortium Tag: N, KP, etc.)
    gold_sanskrit_tag = Column(String(50), nullable=True)
    annotation_note = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    sentence = relationship("Sentence", back_populates="tokens")

    __table_args__ = (
        UniqueConstraint('sentence_id', 'token_id', name='uq_sentence_token_order'),
        Index('idx_sentence_token', 'sentence_id', 'token_id'),
    )


class AnnotationHistory(Base):
    __tablename__ = "annotation_history"

    id = Column(Integer, primary_key=True, index=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id", ondelete="CASCADE"), nullable=False)
    token_id = Column(Integer, nullable=False)
    previous_tag = Column(String(50), nullable=True)
    new_tag = Column(String(50), nullable=False)
    changed_by = Column(String(50), nullable=False)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class TagInventory(Base):
    __tablename__ = "tag_inventory"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
