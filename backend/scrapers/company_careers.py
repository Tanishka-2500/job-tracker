import httpx
import xml.etree.ElementTree as ET
import hashlib
import re
from typing import List, Dict
import asyncio

INDIA_CITIES = {
    "mumbai", "pune", "bengaluru", "bangalore", "hyderabad", "chennai",
    "delhi", "gurgaon", "gurugram", "noida", "kolkata", "kochi", "cochin",
    "ahmedabad", "jaipur", "trivandrum", "thiruvananthapuram", "coimbatore",
    "navi-mumbai", "navi mumbai", "thane", "visakhapatnam", "bhubaneswar",
    "chandigarh", "indore", "nagpur", "lucknow", "mysuru", "mysore",
    "kancheepuram", "kota-kinabalu", "in", "india",
}

COMPANY_SITEMAPS = [
    {
        "name": "EY",
        "sitemap_url": "https://careers.ey.com/sitemap.xml",
        "base_url": "https://careers.ey.com",
    },
    {
        "name": "Deloitte",
        "sitemap_url": "https://apply.deloitte.com/careers/sitemap.xml",
        "base_url": "https://apply.deloitte.com",
    },
    {
        "name": "KPMG",
        "sitemap_url": "https://home.kpmg/sitemap.xml",
        "base_url": "https://home.kpmg",
    },
    {
        "name": "TCS",
        "sitemap_url": "https://www.tcs.com/sitemap.xml",
        "base_url": "https://www.tcs.com",
    },
    {
        "name": "Infosys",
        "sitemap_url": "https://www.infosys.com/sitemap.xml",
        "base_url": "https://www.infosys.com",
    },
    {
        "name": "Accenture",
        "sitemap_url": "https://www.accenture.com/sitemap.xml",
        "base_url": "https://www.accenture.com",
    },
    {
        "name": "Wipro",
        "sitemap_url": "https://careers.wipro.com/sitemap.xml",
        "base_url": "https://careers.wipro.com",
    },
    {
        "name": "HCL",
        "sitemap_url": "https://www.hcltech.com/sitemap.xml",
        "base_url": "https://www.hcltech.com",
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def make_job_id(source: str, url: str) -> str:
    return hashlib.md5(f"{source}:{url}".encode()).hexdigest()


def extract_title_from_url(url: str) -> str:
    """Extract job title embedded in career page URL"""
    # EY style: /job/Mumbai-Senior-Consultant-Tech-Consulting-...
    match = re.search(r"/job/([^/]+)/", url)
    if match:
        raw = match.group(1)
        # Remove city prefix and postal/ID suffixes
        parts = raw.replace("-", " ").split()
        # Remove short numeric/zip parts at the end
        cleaned = []
        for p in parts:
            if re.match(r"^\d{3,}$", p):
                break
            if re.match(r"^[A-Z]{2,3}$", p) and len(cleaned) > 3:
                break
            cleaned.append(p)
        return " ".join(cleaned).title()
    # Generic: last path segment
    slug = url.rstrip("/").split("/")[-1]
    return slug.replace("-", " ").replace("_", " ").title()


def extract_city_from_url(url: str) -> str:
    """Extract city from URL"""
    match = re.search(r"/job/([A-Za-z\-]+?)-[A-Z]", url)
    if match:
        return match.group(1).replace("-", " ").title()
    return "India"


def is_india_job(url: str) -> bool:
    url_lower = url.lower()
    return any(city in url_lower for city in INDIA_CITIES)


def matches_keywords(title: str, keywords: str) -> bool:
    title_lower = title.lower()
    keyword_list = [k.strip().lower() for k in keywords.split(",")]
    return any(kw in title_lower for kw in keyword_list)


async def fetch_company_sitemap_jobs(keywords: str, role_category: str) -> List[Dict]:
    """Parse company career sitemaps for India jobs matching keywords"""
    all_jobs = []
    keyword_list = [k.strip().lower() for k in keywords.split(",")]

    async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
        for company in COMPANY_SITEMAPS:
            try:
                resp = await client.get(company["sitemap_url"])
                if resp.status_code != 200:
                    print(f"[{company['name']}] Sitemap fetch failed: {resp.status_code}")
                    continue

                content = resp.text
                # Parse XML - handle both sitemap index and urlset
                try:
                    root = ET.fromstring(content)
                except ET.ParseError:
                    print(f"[{company['name']}] XML parse error")
                    continue

                ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
                urls = []

                # Check if it's a sitemap index (contains <sitemap> tags)
                sitemaps = root.findall(".//sm:sitemap/sm:loc", ns) or root.findall(".//sitemap/loc")
                if sitemaps:
                    # It's a sitemap index — fetch sub-sitemaps for jobs
                    for sm_loc in sitemaps[:5]:  # Limit to first 5 sub-sitemaps
                        sm_url = sm_loc.text
                        if sm_url and ("job" in sm_url.lower() or "career" in sm_url.lower()):
                            try:
                                sub_resp = await client.get(sm_url)
                                if sub_resp.status_code == 200:
                                    sub_root = ET.fromstring(sub_resp.text)
                                    sub_urls = sub_root.findall(".//sm:url/sm:loc", ns) or sub_root.findall(".//url/loc")
                                    urls.extend(sub_urls)
                            except Exception:
                                pass
                else:
                    # Direct urlset
                    urls = root.findall(".//sm:url/sm:loc", ns) or root.findall(".//url/loc")

                found = 0
                for loc_el in urls:
                    url = loc_el.text
                    if not url:
                        continue
                        
                    # Strict filter to exclude blogs, podcasts, articles, etc.
                    url_lower = url.lower()
                    if any(exclude in url_lower for exclude in ["/podcast", "/blog", "/article", "/news", "/press", "/about", "/investors", "/services"]):
                        continue
                        
                    if not any(job_term in url_lower for job_term in ["job", "career", "req", "role", "position", "opening", "opportunity"]):
                        continue

                    if not is_india_job(url):
                        continue

                    title = extract_title_from_url(url)
                    if not matches_keywords(title, keywords):
                        continue

                    city = extract_city_from_url(url)
                    job_id = make_job_id(company["name"], url)

                    all_jobs.append({
                        "external_id": job_id,
                        "title": title,
                        "company": company["name"],
                        "location": f"{city}, India",
                        "description": f"Job posting at {company['name']} career portal. Click 'Apply' to view full details.",
                        "url": url,
                        "source": f"{company['name']} Careers",
                        "role_category": role_category,
                        "salary": None,
                        "posted_date": "",
                    })
                    found += 1

                print(f"[{company['name']}] Found {found} matching India jobs")
                await asyncio.sleep(1)  # Be polite — 1 second delay between companies

            except Exception as e:
                print(f"[{company['name']}] Error: {e}")

    return all_jobs
