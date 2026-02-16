"""Document model"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    document_type = Column(String(50), nullable=False)  # 'resume' or 'career_sheet'
    title = Column(String(255), nullable=True)
    content_html = Column(Text, nullable=True)
    content_json = Column(JSONB, default=dict)
    generated_at = Column(DateTime, default=datetime.utcnow)
