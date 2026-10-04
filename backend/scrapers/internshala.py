import httpx
from bs4 import BeautifulSoup
import hashlib
from typing import List, Dict
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

INTERNSHALA_BASE = "https://internshala.com"

CATEGORY_SLUGS = {
    "data_analyst": "data-analytics-jobs",
    "business_analyst": "business-development-jobs",
    "pmo": "project-management-jobs",
    "hr_it": "human-resource-jobs",
    "software_engineer": "computer-science-jobs",
    "internship": "internship",
}


def make_job_id(url: str) -> str:
    return hashlib.md5(f"internshala:{url}".encode()).hexdigest()


async def fetch_internshala_jobs(keywords: str, role_category: str) -> List[Dict]:
    """Scrape Internshala for fresher jobs/internships"""
    results = []
    slug = CATEGORY_SLUGS.get(role_category, "computer-science-jobs")

    if role_category == "internship":
        url = f"{INTERNSHALA_BASE}/internships/{slug}"
    else:
        url = f"{INTERNSHALA_BASE}/jobs/{slug}"

    try:
        async with httpx.AsyncClient(timeout=20, headers=HEADERS, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                print(f"[Internshala] Error {resp.status_code}")
                return []

            soup = BeautifulSoup(resp.text, "lxml")

            # Internshala job cards
            cards = soup.select(".individual_internship") or soup.select(".internship-card") or soup.select("[data-internship_id]")

            for card in cards[:20]:
                try:
                    title_el = card.select_one(".job-title-href") or card.select_one("h3.job-internship-name") or card.select_one(".heading_4_5")
                    company_el = card.select_one(".company_name") or card.select_one(".company_and_premium")
                    location_el = card.select_one(".location_link") or card.select_one(".locations")
                    link_el = title_el if title_el and title_el.name == "a" else card.select_one("a.job-title-href") or card.select_one("a[href]")

                    title = title_el.get_text(strip=True) if title_el else "Unknown"
                    if title == "Unknown":
                        continue  # skip invalid cards

                    company = company_el.get_text(strip=True) if company_el else "Unknown"
                    location = location_el.get_text(strip=True) if location_el else "India"
                    href = link_el["href"] if link_el else ""
                    job_url = f"{INTERNSHALA_BASE}{href}" if href.startswith("/") else href

                    # Get stipend/salary
                    stipend_el = card.select_one(".stipend") or card.select_one(".salary")
                    salary = stipend_el.get_text(strip=True) if stipend_el else None

                    results.append({
                        "external_id": make_job_id(job_url),
                        "title": title,
                        "company": company,
                        "location": f"{location}, India" if "india" not in location.lower() else location,
                        "description": f"Internshala listing. Click 'Apply' to view full details and apply.",
                        "url": job_url,
                        "source": "Internshala",
                        "role_category": role_category,
                        "salary": salary,
                        "posted_date": "",
                    })
                except Exception as e:
                    print(f"[Internshala] Card parse error: {e}")
                    continue

    except Exception as e:
        print(f"[Internshala] Exception: {e}")

    print(f"[Internshala] Found {len(results)} jobs for {role_category}")
    return results
