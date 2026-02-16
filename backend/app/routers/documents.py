"""Document generation API endpoints"""

from typing import List
from urllib.parse import quote
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.profile import Profile
from app.models.document import Document
from app.schemas.document import DocumentGenerateRequest, DocumentResponse
from app.services.document_service import generate_resume_html, generate_career_sheet_html
from app.services.pdf_service import html_to_pdf
from app.services.docx_service import html_to_docx
from app.utils.auth import get_current_user

router = APIRouter()


def _get_profile_data(user: User, db: Session) -> dict:
    """Get profile data as dict for document generation"""
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        return {
            "full_name": user.full_name or "",
            "work_history": [],
            "skills": [],
            "certifications": [],
            "languages": [],
            "preferences": {},
        }

    return {
        "full_name": profile.full_name or user.full_name or "",
        "birth_date": str(profile.birth_date) if profile.birth_date else "",
        "phone": profile.phone or "",
        "address": profile.address or "",
        "education": profile.education or [],
        "work_history": profile.work_history or [],
        "skills": profile.skills or [],
        "certifications": profile.certifications or [],
        "languages": profile.languages or [],
        "preferences": profile.preferences or {},
        "self_pr": profile.self_pr or "",
        "career_vision": profile.career_vision or "",
        "resignation_reason_positive": profile.resignation_reason_positive or "",
    }


@router.post("/generate", response_model=DocumentResponse)
def generate_document(
    request: DocumentGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a resume or career sheet HTML

    Args:
        request: Document type ('resume' or 'career_sheet')

    Returns:
        Generated document with HTML content
    """
    if request.document_type not in ("resume", "career_sheet"):
        raise HTTPException(
            status_code=400,
            detail="document_type must be 'resume' or 'career_sheet'",
        )

    profile_data = _get_profile_data(current_user, db)

    if request.document_type == "resume":
        html = generate_resume_html(profile_data)
        title = "履歴書"
    else:
        html = generate_career_sheet_html(profile_data)
        title = "職務経歴書"

    doc = Document(
        user_id=current_user.id,
        document_type=request.document_type,
        title=title,
        content_html=html,
        content_json=profile_data,
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


@router.get("", response_model=List[DocumentResponse])
def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all generated documents for the current user"""
    docs = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.generated_at.desc()).all()
    return docs


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific document"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return doc


@router.get("/{document_id}/pdf")
def download_pdf(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download document as PDF"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.content_html:
        raise HTTPException(status_code=400, detail="Document has no HTML content")

    pdf_bytes = html_to_pdf(doc.content_html)
    filename = f"{doc.title or 'document'}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )


@router.get("/{document_id}/docx")
def download_docx(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download document as Word (DOCX)"""
    doc = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if not doc.content_html:
        raise HTTPException(status_code=400, detail="Document has no HTML content")

    docx_bytes = html_to_docx(doc.content_html, title=doc.title or "Document")
    filename = f"{doc.title or 'document'}.docx"

    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}"},
    )
