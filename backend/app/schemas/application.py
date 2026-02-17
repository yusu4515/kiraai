"""Application schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ApplicationCreate(BaseModel):
    job_id: UUID
    status: str = "interested"
    notes: Optional[str] = None


class ApplicationApply(BaseModel):
    """Apply to a job with documents"""
    document_ids: list[str] = []
    cover_message: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    job_id: Optional[UUID] = None
    status: str
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None
    document_ids: Optional[list[str]] = None
    cover_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
