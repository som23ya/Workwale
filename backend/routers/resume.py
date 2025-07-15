from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
import uuid

from database.database import get_db
from database.models import User, Resume
from schemas.schemas import ResumeResponse, APIResponse, FileUploadResponse
from services.auth import get_current_active_user
from services.resume_parser import ResumeParser
from services.job_matcher import JobMatcher

router = APIRouter()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=APIResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume PDF file."""
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum 10MB allowed."
        )
    
    try:
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Parse resume using AI
        resume_parser = ResumeParser()
        parsed_data = resume_parser.parse_resume(str(file_path))
        
        # Deactivate previous resumes
        db.query(Resume).filter(
            Resume.user_id == current_user.id,
            Resume.is_active == True
        ).update({"is_active": False})
        
        # Create resume record
        new_resume = Resume(
            user_id=current_user.id,
            filename=file.filename,
            file_path=str(file_path),
            file_size=file.size,
            parsed_text=parsed_data['raw_text'],
            parsed_data=parsed_data['parsed_data'],
            skills_extracted=parsed_data['skills_extracted'],
            experience_years=parsed_data['experience_years'],
            education_level=parsed_data['education_level'],
            job_titles=parsed_data['job_titles'],
            is_active=True
        )
        
        db.add(new_resume)
        db.commit()
        db.refresh(new_resume)
        
        # Update job matches after resume upload
        job_matcher = JobMatcher()
        job_matcher.update_match_recommendations(db, current_user)
        
        return APIResponse(
            success=True,
            message="Resume uploaded and parsed successfully",
            data={
                "resume_id": new_resume.id,
                "skills_found": len(parsed_data['skills_extracted']),
                "experience_years": parsed_data['experience_years'],
                "education_level": parsed_data['education_level']
            }
        )
        
    except Exception as e:
        # Clean up file if processing failed
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process resume: {str(e)}"
        )

@router.get("/list", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """List all user's resumes."""
    
    resumes = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.created_at.desc()).all()
    
    return resumes

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific resume details."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return resume

@router.get("/{resume_id}/parsed-data")
async def get_resume_parsed_data(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get parsed resume data in detail."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    return {
        "parsed_data": resume.parsed_data,
        "skills_extracted": resume.skills_extracted,
        "experience_years": resume.experience_years,
        "education_level": resume.education_level,
        "job_titles": resume.job_titles,
        "raw_text": resume.parsed_text
    }

@router.post("/{resume_id}/activate", response_model=APIResponse)
async def activate_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Set a resume as the active one."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Deactivate all other resumes
    db.query(Resume).filter(
        Resume.user_id == current_user.id,
        Resume.is_active == True
    ).update({"is_active": False})
    
    # Activate the selected resume
    resume.is_active = True
    db.commit()
    
    # Update job matches
    job_matcher = JobMatcher()
    job_matcher.update_match_recommendations(db, current_user)
    
    return APIResponse(
        success=True,
        message="Resume activated successfully"
    )

@router.delete("/{resume_id}", response_model=APIResponse)
async def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a resume."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    # Delete file from filesystem
    try:
        file_path = Path(resume.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Warning: Could not delete file {resume.file_path}: {e}")
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return APIResponse(
        success=True,
        message="Resume deleted successfully"
    )

@router.post("/{resume_id}/reparse", response_model=APIResponse)
async def reparse_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Re-parse an existing resume with updated AI."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    try:
        # Re-parse the resume
        resume_parser = ResumeParser()
        parsed_data = resume_parser.parse_resume(resume.file_path)
        
        # Update resume record
        resume.parsed_text = parsed_data['raw_text']
        resume.parsed_data = parsed_data['parsed_data']
        resume.skills_extracted = parsed_data['skills_extracted']
        resume.experience_years = parsed_data['experience_years']
        resume.education_level = parsed_data['education_level']
        resume.job_titles = parsed_data['job_titles']
        
        db.commit()
        
        # Update job matches
        job_matcher = JobMatcher()
        job_matcher.update_match_recommendations(db, current_user)
        
        return APIResponse(
            success=True,
            message="Resume re-parsed successfully",
            data={
                "skills_found": len(parsed_data['skills_extracted']),
                "experience_years": parsed_data['experience_years'],
                "education_level": parsed_data['education_level']
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to re-parse resume: {str(e)}"
        )

@router.get("/{resume_id}/download")
async def download_resume(
    resume_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download original resume file."""
    
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    file_path = Path(resume.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume file not found on server"
        )
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=file_path,
        filename=resume.filename,
        media_type='application/pdf'
    )