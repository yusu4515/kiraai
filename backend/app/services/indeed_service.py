"""Indeed/Job search API integration via RapidAPI JSearch

JSearch API aggregates jobs from Indeed, LinkedIn, Glassdoor, etc.
Docs: https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

Fallback: If no API key is configured, returns empty results
and the system falls back to local DB search.
"""

import hashlib
import json
import logging
from datetime import datetime

import httpx

from app.config import settings
from app.database import redis_client

logger = logging.getLogger(__name__)

JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com"
CACHE_TTL = 3600  # 1 hour


def _cache_key(query: str, location: str | None, page: int) -> str:
    raw = f"jsearch:{query}:{location or ''}:{page}"
    return f"jobs:api:{hashlib.md5(raw.encode()).hexdigest()}"


def _parse_jsearch_job(item: dict) -> dict:
    """Parse JSearch API response item to our Job format"""
    salary_min = None
    salary_max = None
    if item.get("job_min_salary"):
        salary_min = int(item["job_min_salary"])
    if item.get("job_max_salary"):
        salary_max = int(item["job_max_salary"])

    posted_at = None
    if item.get("job_posted_at_datetime_utc"):
        try:
            posted_at = datetime.fromisoformat(
                item["job_posted_at_datetime_utc"].replace("Z", "+00:00")
            ).isoformat()
        except (ValueError, AttributeError):
            pass

    # Map employment type
    job_type = None
    emp_type = item.get("job_employment_type", "")
    if emp_type:
        type_map = {
            "FULLTIME": "full_time",
            "PARTTIME": "part_time",
            "CONTRACTOR": "contract",
            "INTERN": "intern",
        }
        job_type = type_map.get(emp_type.upper(), emp_type.lower())

    return {
        "source": "jsearch",
        "external_id": item.get("job_id", ""),
        "title": item.get("job_title", "Unknown"),
        "company_name": item.get("employer_name", ""),
        "location": f"{item.get('job_city', '')} {item.get('job_state', '')} {item.get('job_country', '')}".strip(),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "description": item.get("job_description", ""),
        "requirements": "\n".join(item.get("job_required_skills") or []),
        "job_type": job_type,
        "url": item.get("job_apply_link") or item.get("job_google_link", ""),
        "posted_at": posted_at,
    }


async def search_indeed_jobs(
    keyword: str,
    location: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict:
    """Search jobs via JSearch API (Indeed aggregator)

    Returns:
        {"jobs": [...], "total": int} or None if API unavailable
    """
    api_key = settings.indeed_publisher_id
    if not api_key:
        logger.info("No JSearch API key configured, skipping external search")
        return None

    # Check cache first
    cache_k = _cache_key(keyword, location, page)
    try:
        cached = redis_client.get(cache_k)
        if cached:
            logger.info(f"Cache hit for search: {keyword}")
            return json.loads(cached)
    except Exception:
        pass

    # Build query
    query = keyword
    if location:
        query += f" in {location}"

    params = {
        "query": query,
        "page": str(page),
        "num_pages": "1",
        "date_posted": "month",
        "country": "jp",
        "language": "ja",
    }

    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{JSEARCH_BASE_URL}/search",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()

        raw_jobs = data.get("data", [])
        total = data.get("parameters", {}).get("num_pages", 1) * len(raw_jobs)

        jobs = [_parse_jsearch_job(item) for item in raw_jobs[:per_page]]

        result = {"jobs": jobs, "total": total}

        # Cache result
        try:
            redis_client.setex(cache_k, CACHE_TTL, json.dumps(result, default=str))
        except Exception:
            pass

        logger.info(f"JSearch returned {len(jobs)} jobs for '{keyword}'")
        return result

    except httpx.HTTPStatusError as e:
        logger.error(f"JSearch API error: {e.response.status_code} - {e.response.text[:200]}")
        return None
    except Exception as e:
        logger.error(f"JSearch API request failed: {type(e).__name__}: {e}", exc_info=True)
        return None


async def search_indeed_jobs_direct(
    keyword: str,
    location: str | None = None,
    page: int = 1,
    per_page: int = 10,
) -> dict:
    """Search using Indeed Publisher API (legacy, deprecated)

    Kept for reference. Indeed's Publisher API was shut down in 2024.
    Use search_indeed_jobs() with RapidAPI JSearch instead.
    """
    logger.warning("Indeed Publisher API is deprecated. Use JSearch API instead.")
    return None
