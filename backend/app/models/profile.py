"""Profile model"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    full_name = Column(String(100), nullable=True)
    birth_date = Column(Date, nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    education = Column(JSONB, default=list)
    work_history = Column(JSONB, default=list)
    skills = Column(JSONB, default=list)
    certifications = Column(JSONB, default=list)
    languages = Column(JSONB, default=list)
    preferences = Column(JSONB, default=dict)
    self_pr = Column(Text, nullable=True)
    career_vision = Column(Text, nullable=True)
    resignation_reason_original = Column(Text, nullable=True)
    resignation_reason_positive = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
