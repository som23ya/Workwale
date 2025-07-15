from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    applications = relationship("JobApplication", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # Job preferences
    desired_job_title = Column(String(255))
    desired_location = Column(String(255))
    desired_salary_min = Column(Integer)
    desired_salary_max = Column(Integer)
    experience_level = Column(String(50))  # entry, mid, senior, executive
    work_type = Column(String(50))  # remote, hybrid, onsite
    
    # Skills and preferences
    skills = Column(JSON)  # List of skills
    industries = Column(JSON)  # Preferred industries
    company_sizes = Column(JSON)  # Preferred company sizes
    
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    whatsapp_notifications = Column(Boolean, default=False)
    notification_frequency = Column(String(20), default="daily")  # instant, daily, weekly
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="profile")

class Resume(Base):
    __tablename__ = "resumes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    
    # Parsed content
    parsed_text = Column(Text)
    parsed_data = Column(JSON)  # Structured resume data
    
    # AI analysis
    skills_extracted = Column(JSON)
    experience_years = Column(Float)
    education_level = Column(String(100))
    job_titles = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="resumes")

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Job details
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    description = Column(Text)
    requirements = Column(Text)
    
    # Job metadata
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    experience_level = Column(String(50))
    work_type = Column(String(50))
    job_type = Column(String(50))  # full-time, part-time, contract
    
    # Scraping info
    source = Column(String(50))  # linkedin, wellfound, naukri
    external_id = Column(String(255))
    external_url = Column(String(500))
    
    # Skills and requirements
    required_skills = Column(JSON)
    preferred_skills = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    posted_date = Column(DateTime)
    scraped_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    applications = relationship("JobApplication", back_populates="job")
    matches = relationship("JobMatch", back_populates="job")

class JobMatch(Base):
    __tablename__ = "job_matches"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    # Matching scores
    overall_score = Column(Float)  # 0-100
    skills_score = Column(Float)
    experience_score = Column(Float)
    location_score = Column(Float)
    salary_score = Column(Float)
    
    # Match reasons
    matching_skills = Column(JSON)
    missing_skills = Column(JSON)
    match_explanation = Column(Text)
    
    # Status
    is_recommended = Column(Boolean, default=False)
    is_viewed = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="matches")

class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(Integer, ForeignKey("jobs.id"))
    
    status = Column(String(50), default="applied")  # applied, reviewed, interview, rejected, offered
    applied_date = Column(DateTime, server_default=func.now())
    notes = Column(Text)
    
    # Application tracking
    resume_used = Column(String(255))
    cover_letter = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    type = Column(String(50))  # job_match, application_update, system
    title = Column(String(255))
    message = Column(Text)
    
    # Delivery
    email_sent = Column(Boolean, default=False)
    whatsapp_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    
    # Related data
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notifications")

class ScrapingJob(Base):
    __tablename__ = "scraping_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    source = Column(String(50))  # linkedin, wellfound, naukri
    search_query = Column(String(255))
    location = Column(String(255))
    
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    jobs_found = Column(Integer, default=0)
    jobs_saved = Column(Integer, default=0)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    
class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    value = Column(Text)
    description = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())