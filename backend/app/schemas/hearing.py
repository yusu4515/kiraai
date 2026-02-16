"""Hearing session schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class HearingMessage(BaseModel):
    """Single message in hearing conversation"""
    role: str  # 'user' or 'assistant'
    content: str


class HearingStreamRequest(BaseModel):
    """Request to stream hearing response"""
    session_id: Optional[UUID] = None
    message: str
    step: int = 1


class HearingSessionResponse(BaseModel):
    """Hearing session response"""
    id: UUID
    current_step: int
    conversation_log: list
    extracted_data: dict
    is_completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class HearingStartResponse(BaseModel):
    """Response when starting a new hearing session"""
    session_id: UUID
    current_step: int
    step_title: str
    greeting: str
