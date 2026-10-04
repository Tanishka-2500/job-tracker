from scrapers.adzuna import fetch_adzuna_jobs
from scrapers.jsearch import fetch_jsearch_jobs
from scrapers.serpapi import fetch_serpapi_jobs
from scrapers.company_careers import fetch_company_sitemap_jobs
from scrapers.internshala import fetch_internshala_jobs
from evaluator import evaluate_jobs_batch
from database import SessionLocal, Job, Role, ScrapeLog
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio


async def run_scrape_for_role(role: Role, db: Session) -> int:
    """Run all scrapers for a single role, upsert results into DB"""
    keywords = role.keywords
    category = role.category
    total_added = 0

    scrapers = [
        ("Adzuna", fetch_adzuna_jobs),
        ("JSearch", fetch_jsearch_jobs),
        ("SerpAPI", fetch_serpapi_jobs),
        ("Company Careers", fetch_company_sitemap_jobs),
        ("Internshala", fetch_internshala_jobs),
    ]

    for source_name, scraper_fn in scrapers:
        log = ScrapeLog(source=source_name, role=role.name, status="running")
        db.add(log)
        db.commit()

        try:
            jobs = await scraper_fn(keywords, category)
            
            # Pass jobs through LangChain Groq Qwen AI agent to filter and clean jobs
            if jobs:
                jobs = await evaluate_jobs_batch(jobs, category)
                
            added = 0
            for job_data in jobs:
                existing = db.query(Job).filter(Job.external_id == job_data["external_id"]).first()
                if not existing:
                    job = Job(**job_data)
                    db.add(job)
                    added += 1
                else:
                    # Update metadata but preserve user status/bookmarks
                    existing.title = job_data["title"]
                    existing.location = job_data["location"]
                    existing.url = job_data["url"]
                    existing.updated_at = datetime.utcnow()
            db.commit()
            total_added += added

            log.status = "success"
            log.jobs_found = len(jobs)
        except Exception as e:
            log.status = "error"
            log.error_msg = str(e)
            print(f"[Scraper] Error in {source_name} for {role.name}: {e}")
        finally:
            db.commit()

    return total_added


async def run_all_scrapes():
    """Run scrapes for all active roles"""
    db = SessionLocal()
    try:
        roles = db.query(Role).filter(Role.is_active == True).all()
        print(f"[Scheduler] Starting scrape for {len(roles)} roles...")
        total = 0
        for role in roles:
            count = await run_scrape_for_role(role, db)
            total += count
            await asyncio.sleep(2)  # Polite delay between roles
        print(f"[Scheduler] Scrape complete. {total} new jobs added.")
    finally:
        db.close()
