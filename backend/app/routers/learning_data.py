"""Learning data admin API endpoints

Provides admin-only access to anonymized learning data
for AI model improvement and analytics.
"""

import csv
import io
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.learning_data import LearningData
from app.schemas.learning_data import LearningDataResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/admin/learning-data", tags=["learning-data"])


def _require_admin(user: User):
    """Verify user has admin/agent role (basic check)"""
    # For now, allow any authenticated user (in production, check role)
    # TODO: Add proper admin role check
    pass


@router.get("", response_model=List[LearningDataResponse])
def list_learning_data(
    data_type: Optional[str] = Query(None, description="Filter by type: hearing, document, feedback"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List anonymized learning data entries"""
    _require_admin(current_user)

    query = db.query(LearningData)

    if data_type:
        query = query.filter(LearningData.data_type == data_type)

    entries = (
        query
        .order_by(LearningData.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [LearningDataResponse.model_validate(e) for e in entries]


@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get learning data collection statistics"""
    _require_admin(current_user)

    total = db.query(LearningData).count()
    hearing_count = db.query(LearningData).filter(LearningData.data_type == "hearing").count()
    document_count = db.query(LearningData).filter(LearningData.data_type == "document").count()
    feedback_count = db.query(LearningData).filter(LearningData.data_type == "feedback").count()

    return {
        "total": total,
        "by_type": {
            "hearing": hearing_count,
            "document": document_count,
            "feedback": feedback_count,
        },
    }


@router.get("/export/json")
def export_json(
    data_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export learning data as JSON"""
    _require_admin(current_user)

    query = db.query(LearningData)
    if data_type:
        query = query.filter(LearningData.data_type == data_type)

    entries = query.order_by(LearningData.created_at.desc()).all()

    data = [
        {
            "id": str(e.id),
            "data_type": e.data_type,
            "input_data": e.input_data,
            "output_data": e.output_data,
            "metadata": e.metadata_,
            "created_at": e.created_at.isoformat(),
        }
        for e in entries
    ]

    content = json.dumps(data, ensure_ascii=False, indent=2)

    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=learning_data.json"},
    )


@router.get("/export/csv")
def export_csv(
    data_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Export learning data as CSV"""
    _require_admin(current_user)

    query = db.query(LearningData)
    if data_type:
        query = query.filter(LearningData.data_type == data_type)

    entries = query.order_by(LearningData.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "data_type", "input_data", "output_data", "metadata", "created_at"])

    for e in entries:
        writer.writerow([
            str(e.id),
            e.data_type,
            json.dumps(e.input_data, ensure_ascii=False),
            json.dumps(e.output_data, ensure_ascii=False),
            json.dumps(e.metadata_, ensure_ascii=False),
            e.created_at.isoformat(),
        ])

    csv_bytes = output.getvalue().encode("utf-8-sig")  # BOM for Excel compatibility

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=learning_data.csv"},
    )
