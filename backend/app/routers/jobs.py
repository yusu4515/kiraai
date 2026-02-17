"""Job search API endpoints - combines external APIs and local DB search"""

import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.job import Job
from app.utils.auth import get_current_user
from app.schemas.job import JobSearchRequest, JobSearchResponse, JobResponse
from app.services.job_search_service import search_jobs, seed_sample_jobs
from app.services.indeed_service import search_indeed_jobs
from app.services.careerjet_service import search_careerjet_jobs

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _save_api_jobs_to_db(db: Session, api_jobs: list[dict]) -> list[Job]:
    """Save API results to DB as cache and return Job objects"""
    saved = []
    for j in api_jobs:
        # Check if already exists
        existing = None
        if j.get("external_id"):
            existing = db.query(Job).filter(
                Job.source == j["source"],
                Job.external_id == j["external_id"],
            ).first()

        if existing:
            saved.append(existing)
            continue

        job = Job(
            source=j.get("source", "api"),
            external_id=j.get("external_id"),
            title=j["title"],
            company_name=j.get("company_name"),
            location=j.get("location"),
            salary_min=j.get("salary_min"),
            salary_max=j.get("salary_max"),
            description=j.get("description"),
            requirements=j.get("requirements"),
            job_type=j.get("job_type"),
            url=j.get("url"),
            posted_at=datetime.fromisoformat(j["posted_at"]) if j.get("posted_at") else None,
            fetched_at=datetime.utcnow(),
        )
        db.add(job)
        saved.append(job)

    if saved:
        db.commit()
        for job in saved:
            db.refresh(job)

    return saved


@router.post("/search", response_model=JobSearchResponse)
async def search(
    request: JobSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search jobs - queries multiple external APIs in parallel, falls back to local DB"""

    # Query JSearch and Careerjet in parallel
    jsearch_task = search_indeed_jobs(
        keyword=request.keyword,
        location=request.location,
        page=request.page,
        per_page=request.per_page,
    )
    careerjet_task = search_careerjet_jobs(
        keyword=request.keyword,
        location=request.location,
        page=request.page,
        per_page=request.per_page,
    )

    jsearch_result, careerjet_result = await asyncio.gather(
        jsearch_task, careerjet_task, return_exceptions=True
    )

    # Handle exceptions from gather
    if isinstance(jsearch_result, Exception):
        jsearch_result = None
    if isinstance(careerjet_result, Exception):
        careerjet_result = None

    # Combine results from all sources
    all_api_jobs = []
    total = 0

    if jsearch_result and jsearch_result.get("jobs"):
        all_api_jobs.extend(jsearch_result["jobs"])
        total += jsearch_result.get("total", len(jsearch_result["jobs"]))

    if careerjet_result and careerjet_result.get("jobs"):
        all_api_jobs.extend(careerjet_result["jobs"])
        total += careerjet_result.get("total", len(careerjet_result["jobs"]))

    if all_api_jobs:
        # Save API results to DB for persistence
        db_jobs = _save_api_jobs_to_db(db, all_api_jobs)

        return JobSearchResponse(
            jobs=[JobResponse.model_validate(j) for j in db_jobs],
            total=total,
            page=request.page,
            per_page=request.per_page,
        )

    # Fallback: search local DB
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
