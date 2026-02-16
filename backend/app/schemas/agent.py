"""Agent schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AgentProfileUpdate(BaseModel):
    company_name: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None


class AgentProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_name: str
    plan: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    website_url: Optional[str] = None
    is_approved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AgentDashboardResponse(BaseModel):
    profile: AgentProfileResponse
    stats: dict
