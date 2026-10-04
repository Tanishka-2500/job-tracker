import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./job_tracker.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, unique=True, index=True)
    title = Column(String, index=True)
    company = Column(String, index=True)
    location = Column(String)
    description = Column(Text, nullable=True)
    url = Column(String)
    source = Column(String)           # adzuna / jsearch / serpapi / ey / deloitte / kpmg / internshala etc
    role_category = Column(String)    # data_analyst / business_analyst / pmo / hr_it / software_engineer / internship
    salary = Column(String, nullable=True)
    posted_date = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User actions
    status = Column(String, default="new")   # new / saved / applied / interviewing / rejected / offer
    is_bookmarked = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    applied_date = Column(DateTime, nullable=True)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)           # Display name e.g. "Data Analyst"
    keywords = Column(Text)                       # Comma-separated keywords for searching
    is_active = Column(Boolean, default=True)
    category = Column(String)                     # Internal category key
    created_at = Column(DateTime, default=datetime.utcnow)


class ScrapeLog(Base):
    __tablename__ = "scrape_logs"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String)
    role = Column(String)
    status = Column(String)   # success / error
    jobs_found = Column(Integer, default=0)
    error_msg = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    # Seed default roles
    db = SessionLocal()
    existing = db.query(Role).count()
    if existing == 0:
        default_roles = [
            Role(name="Data Analyst", keywords="data analyst,data analytics,business intelligence,BI analyst,data science fresher", category="data_analyst"),
            Role(name="Business Analyst", keywords="business analyst,BA,business analysis,requirements analyst,product analyst", category="business_analyst"),
            Role(name="PMO", keywords="PMO,project management office,project coordinator,project analyst,program analyst", category="pmo"),
            Role(name="HR / IT", keywords="HR executive,human resources,IT recruiter,talent acquisition,people operations,IT support", category="hr_it"),
            Role(name="Associate Software Engineer", keywords="associate software engineer,junior software engineer,software developer fresher,graduate engineer trainee,GET,junior developer", category="software_engineer"),
            Role(name="Internships", keywords="internship,intern,trainee,summer intern,data analyst intern,business analyst intern", category="internship"),
        ]
        for role in default_roles:
            db.add(role)
        db.commit()
    db.close()
