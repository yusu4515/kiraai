"""Careerjet API integration for Japanese job search

Careerjet is a job search engine aggregating listings from thousands of sites.
The ja_JP locale provides access to Japanese job listings via careerjet.jp.

Docs: https://www.careerjet.com/partners/api
GitHub: https://github.com/careerjet/careerjet-api-client-python

Requires a free affiliate ID (affid) from Careerjet partner registration.
"""

import hashlib
import json
import logging

import httpx

from app.config import settings
from app.database import redis_client

logger = logging.getLogger(__name__)

CAREERJET_API_URL = "http://public.api.careerjet.net/search"
LOCALE = "ja_JP"
CACHE_TTL = 3600  # 1 hour


def _cache_key(query: str, location: str | None, page: int) -> str:
    raw = f"careerjet:{query}:{location or ''}:{page}"
    return f"jobs:cj:{hashlib.md5(raw.encode()).hexdigest()}"


def _parse_careerjet_job(item: dict) -> dict:
    """Parse Careerjet API response item to our Job format"""
    salary_min = None
    salary_max = None
    salary_str = item.get("salary", "")
    if salary_str:
        # Try to extract numeric salary values from string like "300万円～500万円"
        import re
        nums = re.findall(r'(\d+)万', salary_str)
        if len(nums) >= 2:
            salary_min = int(nums[0]) * 10000
            salary_max = int(nums[1]) * 10000
        elif len(nums) == 1:
            salary_min = int(nums[0]) * 10000

    return {
        "source": "careerjet",
        "external_id": item.get("url", ""),
        "title": item.get("title", "Unknown"),
        "company_name": item.get("company", ""),
        "location": item.get("locations", ""),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "description": item.get("description", ""),
        "requirements": "",
        "job_type": None,
        "url": item.get("url", ""),
        "posted_at": item.get("date", None),
    }


async def search_careerjet_jobs(
    keyword: str,
    location: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> dict | None:
    """Search jobs via Careerjet API (Japanese job aggregator)

    Returns:
        {"jobs": [...], "total": int} or None if API unavailable
    """
    affid = settings.careerjet_affid
    if not affid:
        logger.info("No Careerjet affiliate ID configured, skipping")
        return None

    # Check cache
    cache_k = _cache_key(keyword, location, page)
    try:
        cached = redis_client.get(cache_k)
        if cached:
            logger.info(f"Careerjet cache hit for: {keyword}")
            return json.loads(cached)
    except Exception:
        pass

    params = {
        "locale_code": LOCALE,
        "keywords": keyword,
        "affid": affid,
        "user_ip": "127.0.0.1",
        "user_agent": "Mozilla/5.0 (KiraAI Job Search)",
        "url": "https://kira-ai.jp/jobs",
        "page": str(page),
        "pagesize": str(per_page),
        "sort": "relevance",
    }
    if location:
        params["location"] = location

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(CAREERJET_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        if data.get("type") == "ERROR":
            logger.error(f"Careerjet API error: {data.get('error', 'unknown')}")
            return None

        raw_jobs = data.get("jobs", [])
        total = data.get("hits", len(raw_jobs))

        jobs = [_parse_careerjet_job(item) for item in raw_jobs]

        result = {"jobs": jobs, "total": total}

        # Cache result
        try:
            redis_client.setex(cache_k, CACHE_TTL, json.dumps(result, default=str))
        except Exception:
            pass

        logger.info(f"Careerjet returned {len(jobs)} jobs for '{keyword}'")
        return result

    except httpx.HTTPStatusError as e:
        logger.error(f"Careerjet API error: {e.response.status_code} - {e.response.text[:200]}")
        return None
    except Exception as e:
        logger.error(f"Careerjet API request failed: {type(e).__name__}: {e}", exc_info=True)
        return None
