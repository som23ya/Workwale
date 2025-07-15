from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv

# Try to import database modules with fallback
try:
    from database.database import get_db, engine, Base
    from database import models
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Warning: Database modules not available. Running in minimal mode.")

# Try to import routers with fallback
try:
    from routers import auth, users, jobs, resume, dashboard, notifications
    ROUTERS_AVAILABLE = True
except ImportError:
    ROUTERS_AVAILABLE = False
    print("Warning: Router modules not available. Running with basic endpoints only.")

# Try to import services with fallback
try:
    from services.resume_parser import ResumeParser
    from services.job_matcher import JobMatcher
    from services.notification_service import NotificationService
    SERVICES_AVAILABLE = True
except ImportError:
    SERVICES_AVAILABLE = False
    print("Warning: Service modules not available. Basic functionality only.")

load_dotenv()

# Create all database tables if available
if DATABASE_AVAILABLE:
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Warning: Could not create database tables: {e}")

app = FastAPI(
    title="WorkWale.ai API",
    description="AI-Powered Job Discovery Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://workwale-frontend.onrender.com").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers if available
if ROUTERS_AVAILABLE:
    try:
        app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
        app.include_router(users.router, prefix="/api/users", tags=["Users"])
        app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
        app.include_router(resume.router, prefix="/api/resume", tags=["Resume"])
        app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
        app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
    except Exception as e:
        print(f"Warning: Could not include some routers: {e}")

@app.get("/")
async def root():
    return {
        "message": "Welcome to WorkWale.ai API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "features": {
            "database": DATABASE_AVAILABLE,
            "routers": ROUTERS_AVAILABLE,
            "services": SERVICES_AVAILABLE
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "WorkWale.ai API"}

# Basic demo endpoints for when full routers aren't available
@app.get("/api/demo")
async def demo_endpoint():
    return {
        "message": "WorkWale.ai Demo API",
        "features": [
            "AI-powered resume parsing",
            "Smart job matching",
            "Real-time notifications",
            "Application tracking"
        ],
        "status": "demo_mode"
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True if os.getenv("ENVIRONMENT") == "development" else False
    )