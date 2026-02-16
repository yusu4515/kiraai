"""Job schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class JobSearchRequest(BaseModel):
    keyword: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    job_type: Optional[str] = None
    page: int = 1
    per_page: int = 20


class JobResponse(BaseModel):
    id: UUID
    source: str
    external_id: Optional[str] = None
    title: str
    company_name: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    job_type: Optional[str] = None
    url: Optional[str] = None
    posted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobSearchResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    per_page: int
