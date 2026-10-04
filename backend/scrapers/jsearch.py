import httpx
import hashlib
from typing import List, Dict
import os

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY", "")


def make_job_id(source: str, title: str, company: str, url: str) -> str:
    raw = f"{source}:{title}:{company}:{url}"
    return hashlib.md5(raw.encode()).hexdigest()


async def fetch_jsearch_jobs(keywords: str, role_category: str) -> List[Dict]:
    """Fetch jobs from JSearch (RapidAPI) for India"""
    if not JSEARCH_API_KEY:
        print("[JSearch] No API key set — skipping")
        return []

    results = []
    try:
        query = f"{keywords.split(',')[0].strip()} in India"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://jsearch.p.rapidapi.com/search",
                params={
                    "query": query,
                    "page": "1",
                    "num_pages": "2",
                    "country": "in",
                    "date_posted": "week",
                },
                headers={
                    "X-RapidAPI-Key": JSEARCH_API_KEY,
                    "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
                },
            )
            if resp.status_code != 200:
                print(f"[JSearch] Error {resp.status_code}")
                return []
            data = resp.json()
            for j in data.get("data", []):
                results.append({
                    "external_id": make_job_id("jsearch", j.get("job_title",""), j.get("employer_name",""), j.get("job_apply_link","")),
                    "title": j.get("job_title", "Unknown"),
                    "company": j.get("employer_name", "Unknown"),
                    "location": f"{j.get('job_city','')}, {j.get('job_country','')}".strip(", "),
                    "description": j.get("job_description", "")[:800],
                    "url": j.get("job_apply_link", j.get("job_google_link", "")),
                    "source": "JSearch",
                    "role_category": role_category,
                    "salary": _fmt_salary(j.get("job_min_salary"), j.get("job_max_salary")),
                    "posted_date": j.get("job_posted_at_datetime_utc", "")[:10],
                })
    except Exception as e:
        print(f"[JSearch] Exception: {e}")
    return results


def _fmt_salary(mn, mx):
    if mn and mx:
        return f"₹{int(mn):,} - ₹{int(mx):,}"
    if mn:
        return f"₹{int(mn):,}+"
    return None
