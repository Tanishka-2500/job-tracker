from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import asyncio

from database import get_db, init_db, Job, Role, ScrapeLog
from scraper_runner import run_all_scrapes, run_scrape_for_role
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import os

app = FastAPI(title="Job Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def startup_event():
    init_db()
    # Daily auto-refresh at 8:00 AM IST
    scheduler.add_job(
        run_all_scrapes,
        CronTrigger(hour=8, minute=0, timezone="Asia/Kolkata"),
        id="daily_scrape",
        replace_existing=True,
    )
    scheduler.start()
    print("[Server] Job Tracker API started. Daily refresh scheduled at 8 AM IST.")


@app.on_event("shutdown")
async def shutdown_event():
    scheduler.shutdown()


# ─── JOBS ───────────────────────────────────────────────────────────────────

@app.get("/api/jobs")
def get_jobs(
    db: Session = Depends(get_db),
    role_category: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    search: Optional[str] = None,
    location: Optional[str] = None,
    sort_by: Optional[str] = "newest",
    bookmarked: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    query = db.query(Job)

    if role_category:
        query = query.filter(Job.role_category == role_category)
    if status:
        query = query.filter(Job.status == status)
    if source:
        query = query.filter(Job.source == source)
    if bookmarked is not None:
        query = query.filter(Job.is_bookmarked == bookmarked)
    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%"),
            )
        )

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    total = query.count()
    
    if sort_by == "oldest":
        query = query.order_by(Job.created_at.asc())
    else:
        query = query.order_by(desc(Job.created_at))
        
    jobs = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "jobs": [job_to_dict(j) for j in jobs],
    }


@app.get("/api/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_dict(job)


class JobUpdateRequest(BaseModel):
    status: Optional[str] = None
    is_bookmarked: Optional[bool] = None
    notes: Optional[str] = None


@app.patch("/api/jobs/{job_id}")
def update_job(job_id: int, update: JobUpdateRequest, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if update.status is not None:
        job.status = update.status
        if update.status == "applied":
            job.applied_date = datetime.utcnow()
    if update.is_bookmarked is not None:
        job.is_bookmarked = update.is_bookmarked
    if update.notes is not None:
        job.notes = update.notes

    job.updated_at = datetime.utcnow()
    db.commit()
    return job_to_dict(job)


@app.delete("/api/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return {"message": "Job deleted"}


# ─── ROLES ──────────────────────────────────────────────────────────────────

@app.get("/api/roles")
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    return [role_to_dict(r) for r in roles]


class RoleCreate(BaseModel):
    name: str
    keywords: str
    category: str


@app.post("/api/roles")
def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.name == role_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")
    role = Role(
        name=role_data.name,
        keywords=role_data.keywords,
        category=role_data.category.lower().replace(" ", "_"),
    )
    db.add(role)
    db.commit()
    return role_to_dict(role)


@app.patch("/api/roles/{role_id}")
def toggle_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    role.is_active = not role.is_active
    db.commit()
    return role_to_dict(role)


@app.delete("/api/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(role)
    db.commit()
    return {"message": "Role deleted"}


# ─── SCRAPE TRIGGER ──────────────────────────────────────────────────────────

scrape_status = {"is_running": False, "last_run": None, "last_count": 0}


@app.post("/api/scrape")
async def trigger_scrape(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    if scrape_status["is_running"]:
        return {"message": "Scrape already running", "status": scrape_status}

    async def run():
        scrape_status["is_running"] = True
        try:
            await run_all_scrapes()
            scrape_status["last_run"] = datetime.utcnow().isoformat()
        finally:
            scrape_status["is_running"] = False

    background_tasks.add_task(run)
    return {"message": "Scrape started", "status": scrape_status}


@app.get("/api/scrape/status")
def get_scrape_status(db: Session = Depends(get_db)):
    last_log = db.query(ScrapeLog).order_by(desc(ScrapeLog.created_at)).first()
    return {
        **scrape_status,
        "last_log": {
            "source": last_log.source,
            "role": last_log.role,
            "status": last_log.status,
            "jobs_found": last_log.jobs_found,
            "time": last_log.created_at.isoformat(),
        } if last_log else None
    }


# ─── STATS ──────────────────────────────────────────────────────────────────

@app.get("/api/stats")
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Job).count()
    bookmarked = db.query(Job).filter(Job.is_bookmarked == True).count()
    applied = db.query(Job).filter(Job.status == "applied").count()
    new_jobs = db.query(Job).filter(Job.status == "new").count()
    interviewing = db.query(Job).filter(Job.status == "interviewing").count()

    by_role = {}
    roles = db.query(Role).all()
    for role in roles:
        count = db.query(Job).filter(Job.role_category == role.category).count()
        by_role[role.name] = count

    by_source = {}
    from sqlalchemy import func
    source_counts = db.query(Job.source, func.count(Job.id)).group_by(Job.source).all()
    for source, count in source_counts:
        by_source[source] = count

    return {
        "total": total,
        "bookmarked": bookmarked,
        "applied": applied,
        "new": new_jobs,
        "interviewing": interviewing,
        "by_role": by_role,
        "by_source": by_source,
    }


# ─── HELPERS ────────────────────────────────────────────────────────────────

def job_to_dict(j: Job) -> dict:
    return {
        "id": j.id,
        "external_id": j.external_id,
        "title": j.title,
        "company": j.company,
        "location": j.location,
        "description": j.description,
        "url": j.url,
        "source": j.source,
        "role_category": j.role_category,
        "salary": j.salary,
        "posted_date": j.posted_date,
        "status": j.status,
        "is_bookmarked": j.is_bookmarked,
        "notes": j.notes,
        "applied_date": j.applied_date.isoformat() if j.applied_date else None,
        "created_at": j.created_at.isoformat() if j.created_at else None,
    }


def role_to_dict(r: Role) -> dict:
    return {
        "id": r.id,
        "name": r.name,
        "keywords": r.keywords,
        "category": r.category,
        "is_active": r.is_active,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
