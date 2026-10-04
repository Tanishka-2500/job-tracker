import httpx
import hashlib
from typing import List, Dict, Optional
import os

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")


def make_job_id(source: str, title: str, company: str, url: str) -> str:
    raw = f"{source}:{title}:{company}:{url}"
    return hashlib.md5(raw.encode()).hexdigest()


async def fetch_adzuna_jobs(keywords: str, role_category: str) -> List[Dict]:
    """Fetch jobs from Adzuna API for India"""
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[Adzuna] No API keys set — skipping")
        return []

    results = []
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            for page in range(1, 3):  # Fetch 2 pages = up to 40 results
                url = f"https://api.adzuna.com/v1/api/jobs/in/search/{page}"
                params = {
                    "app_id": ADZUNA_APP_ID,
                    "app_key": ADZUNA_APP_KEY,
                    "results_per_page": 20,
                    "what": keywords.split(",")[0].strip(),
                    "where": "India",
                    "content-type": "application/json",
                    "sort_by": "date",
                }
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    print(f"[Adzuna] Error {resp.status_code}")
                    break
                data = resp.json()
                jobs_raw = data.get("results", [])
                for j in jobs_raw:
                    results.append({
                        "external_id": make_job_id("adzuna", j.get("title",""), j.get("company",{}).get("display_name",""), j.get("redirect_url","")),
                        "title": j.get("title", "Unknown"),
                        "company": j.get("company", {}).get("display_name", "Unknown"),
                        "location": j.get("location", {}).get("display_name", "India"),
                        "description": j.get("description", ""),
                        "url": j.get("redirect_url", ""),
                        "source": "Adzuna",
                        "role_category": role_category,
                        "salary": _fmt_salary(j.get("salary_min"), j.get("salary_max")),
                        "posted_date": j.get("created", "")[:10] if j.get("created") else "",
                    })
    except Exception as e:
        print(f"[Adzuna] Exception: {e}")
    return results


def _fmt_salary(mn, mx) -> Optional[str]:
    if mn and mx:
        return f"₹{int(mn):,} - ₹{int(mx):,}"
    if mn:
        return f"₹{int(mn):,}+"
    return None
