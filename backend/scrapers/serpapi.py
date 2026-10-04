import httpx
import hashlib
from typing import List, Dict
import os

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")


def make_job_id(source: str, title: str, company: str, url: str) -> str:
    raw = f"{source}:{title}:{company}:{url}"
    return hashlib.md5(raw.encode()).hexdigest()


async def fetch_serpapi_jobs(keywords: str, role_category: str) -> List[Dict]:
    """Fetch jobs from SerpAPI Google Jobs for India"""
    if not SERPAPI_KEY:
        print("[SerpAPI] No API key set — skipping")
        return []

    results = []
    try:
        query = f"{keywords.split(',')[0].strip()} fresher India"
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={
                    "engine": "google_jobs",
                    "q": query,
                    "location": "India",
                    "gl": "in",
                    "hl": "en",
                    "api_key": SERPAPI_KEY,
                },
            )
            if resp.status_code != 200:
                print(f"[SerpAPI] Error {resp.status_code}")
                return []
            data = resp.json()
            for j in data.get("jobs_results", []):
                apply_link = ""
                if j.get("apply_options"):
                    apply_link = j["apply_options"][0].get("link", "")
                results.append({
                    "external_id": make_job_id("serpapi", j.get("title",""), j.get("company_name",""), apply_link),
                    "title": j.get("title", "Unknown"),
                    "company": j.get("company_name", "Unknown"),
                    "location": j.get("location", "India"),
                    "description": j.get("description", "")[:800],
                    "url": apply_link,
                    "source": "Google Jobs",
                    "role_category": role_category,
                    "salary": j.get("detected_extensions", {}).get("salary", None),
                    "posted_date": j.get("detected_extensions", {}).get("posted_at", ""),
                })
    except Exception as e:
        print(f"[SerpAPI] Exception: {e}")
    return results
