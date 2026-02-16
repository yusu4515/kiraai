"""Learning data model for AI training data collection"""

import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.database import Base


class LearningData(Base):
    __tablename__ = "learning_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    data_type = Column(String(50), nullable=False)  # 'hearing', 'document', 'feedback'
    input_data = Column(JSONB, default=dict)   # anonymized input
    output_data = Column(JSONB, default=dict)  # anonymized output
    metadata_ = Column("metadata", JSONB, default=dict)  # extra info (model, tokens, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
