"""Job search API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.utils.auth import get_current_user
from app.schemas.job import JobSearchRequest, JobSearchResponse, JobResponse
from app.services.job_search_service import search_jobs, seed_sample_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/search", response_model=JobSearchResponse)
def search(
    request: JobSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search jobs by keyword, location, salary, etc."""
    jobs, total = search_jobs(
        db=db,
        keyword=request.keyword,
        location=request.location,
        salary_min=request.salary_min,
        job_type=request.job_type,
        page=request.page,
        per_page=request.per_page,
    )

    return JobSearchResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=total,
        page=request.page,
        per_page=request.per_page,
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get job details"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse.model_validate(job)


@router.post("/seed")
def seed_jobs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Seed sample jobs for testing"""
    count = seed_sample_jobs(db)
    return {"message": f"Seeded {count} jobs", "count": count}
