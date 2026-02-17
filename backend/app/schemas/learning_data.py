"""Learning data schemas"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class LearningDataResponse(BaseModel):
    id: UUID
    data_type: str
    input_data: dict = {}
    output_data: dict = {}
    metadata_: dict = {}
    created_at: datetime

    class Config:
        from_attributes = True
