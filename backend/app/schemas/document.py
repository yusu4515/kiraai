"""Document schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DocumentGenerateRequest(BaseModel):
    """Request to generate a document"""
    document_type: str  # 'resume' or 'career_sheet'


class DocumentResponse(BaseModel):
    """Document response"""
    id: UUID
    document_type: str
    title: Optional[str] = None
    content_html: Optional[str] = None
    generated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """List of documents"""
    documents: list[DocumentResponse]
