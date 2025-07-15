from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# Enums for various choices
class ExperienceLevel(str, Enum):
    entry = "entry"
    mid = "mid"
    senior = "senior"
    executive = "executive"

class WorkType(str, Enum):
    remote = "remote"
    hybrid = "hybrid"
    onsite = "onsite"

class JobType(str, Enum):
    full_time = "full-time"
    part_time = "part-time"
    contract = "contract"
    internship = "internship"

class NotificationFrequency(str, Enum):
    instant = "instant"
    daily = "daily"
    weekly = "weekly"

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# User Profile schemas
class UserProfileBase(BaseModel):
    desired_job_title: Optional[str] = None
    desired_location: Optional[str] = None
    desired_salary_min: Optional[int] = None
    desired_salary_max: Optional[int] = None
    experience_level: Optional[ExperienceLevel] = None
    work_type: Optional[WorkType] = None
    skills: Optional[List[str]] = []
    industries: Optional[List[str]] = []
    company_sizes: Optional[List[str]] = []
    email_notifications: bool = True
    whatsapp_notifications: bool = False
    notification_frequency: NotificationFrequency = NotificationFrequency.daily

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Resume schemas
class ResumeBase(BaseModel):
    filename: str

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    file_size: Optional[int]
    skills_extracted: Optional[List[str]]
    experience_years: Optional[float]
    education_level: Optional[str]
    job_titles: Optional[List[str]]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ResumeParsedData(BaseModel):
    name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    skills: List[str]
    experience: List[Dict[str, Any]]
    education: List[Dict[str, Any]]
    certifications: List[str]
    summary: Optional[str]

# Job schemas
class JobBase(BaseModel):
    title: str
    company: str
    location: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    experience_level: Optional[ExperienceLevel] = None
    work_type: Optional[WorkType] = None
    job_type: Optional[JobType] = None

class JobCreate(JobBase):
    source: str
    external_id: Optional[str] = None
    external_url: Optional[str] = None
    required_skills: Optional[List[str]] = []
    preferred_skills: Optional[List[str]] = []

class JobResponse(JobBase):
    id: int
    source: str
    external_url: Optional[str]
    required_skills: Optional[List[str]]
    preferred_skills: Optional[List[str]]
    is_active: bool
    posted_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobSearchRequest(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    experience_level: Optional[ExperienceLevel] = None
    work_type: Optional[WorkType] = None
    salary_min: Optional[int] = None
    skills: Optional[List[str]] = []
    page: int = 1
    limit: int = 20

# Job Match schemas
class JobMatchResponse(BaseModel):
    id: int
    job: JobResponse
    overall_score: float
    skills_score: float
    experience_score: float
    location_score: float
    salary_score: float
    matching_skills: List[str]
    missing_skills: List[str]
    match_explanation: str
    is_recommended: bool
    is_viewed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Job Application schemas
class JobApplicationBase(BaseModel):
    notes: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    job_id: int
    resume_used: Optional[str] = None
    cover_letter: Optional[str] = None

class JobApplicationUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None

class JobApplicationResponse(JobApplicationBase):
    id: int
    user_id: int
    job_id: int
    job: JobResponse
    status: str
    applied_date: datetime
    resume_used: Optional[str]
    cover_letter: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Notification schemas
class NotificationBase(BaseModel):
    type: str
    title: str
    message: str

class NotificationCreate(NotificationBase):
    user_id: int
    job_id: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    email_sent: bool
    whatsapp_sent: bool
    is_read: bool
    job_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Dashboard schemas
class DashboardStats(BaseModel):
    total_applications: int
    pending_applications: int
    interviews_scheduled: int
    offers_received: int
    total_matches: int
    new_matches_today: int
    profile_completion: float
    recent_activity: List[Dict[str, Any]]

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Job Scraping schemas
class ScrapingJobCreate(BaseModel):
    source: str
    search_query: str
    location: Optional[str] = None

class ScrapingJobResponse(BaseModel):
    id: int
    source: str
    search_query: str
    location: Optional[str]
    status: str
    jobs_found: int
    jobs_saved: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# File upload schemas
class FileUploadResponse(BaseModel):
    filename: str
    file_size: int
    upload_success: bool
    message: str

# API Response wrappers
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    limit: int
    pages: int