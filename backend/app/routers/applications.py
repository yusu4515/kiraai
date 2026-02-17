"""Application management API endpoints"""

from datetime import datetime
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.application import Application
from app.models.job import Job
from app.models.document import Document
from app.utils.auth import get_current_user
from app.schemas.application import ApplicationCreate, ApplicationApply, ApplicationUpdate, ApplicationResponse

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.get("", response_model=List[ApplicationResponse])
def list_applications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all applications for current user"""
    apps = (
        db.query(Application)
        .filter(Application.user_id == current_user.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return [ApplicationResponse.model_validate(a) for a in apps]


@router.post("", response_model=ApplicationResponse)
def create_application(
    request: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a job to applications"""
    # Check job exists
    job = db.query(Job).filter(Job.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check not already applied
    existing = (
        db.query(Application)
        .filter(
            Application.user_id == current_user.id,
            Application.job_id == request.job_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Already applied to this job")

    app = Application(
        user_id=current_user.id,
        job_id=request.job_id,
        status=request.status,
        notes=request.notes,
        applied_at=datetime.utcnow() if request.status == "applied" else None,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.post("/{application_id}/apply", response_model=ApplicationResponse)
def apply_to_job(
    application_id: uuid.UUID,
    request: ApplicationApply,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Apply to a job with attached documents - updates status to 'applied'"""
    app = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    # Validate documents belong to this user
    if request.document_ids:
        for doc_id in request.document_ids:
            doc = db.query(Document).filter(
                Document.id == doc_id,
                Document.user_id == current_user.id,
            ).first()
            if not doc:
                raise HTTPException(status_code=400, detail=f"Document {doc_id} not found")

    app.status = "applied"
    app.applied_at = datetime.utcnow()
    app.document_ids = request.document_ids
    app.cover_message = request.cover_message
    app.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    request: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update application status"""
    app = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if request.status is not None:
        app.status = request.status
        if request.status == "applied" and not app.applied_at:
            app.applied_at = datetime.utcnow()
    if request.notes is not None:
        app.notes = request.notes
    app.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(app)
    return ApplicationResponse.model_validate(app)


@router.delete("/{application_id}")
def delete_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete an application"""
    app = (
        db.query(Application)
        .filter(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
        .first()
    )
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    db.delete(app)
    db.commit()
    return {"message": "Application deleted"}
