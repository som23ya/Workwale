import os
import json
from typing import Dict, List, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import math
from datetime import datetime
from sqlalchemy.orm import Session

from database.models import User, UserProfile, Resume, Job, JobMatch
from schemas.schemas import JobSearchRequest

load_dotenv()

class JobMatcher:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Weights for different matching criteria
        self.weights = {
            'skills': 0.35,
            'experience': 0.25,
            'location': 0.15,
            'salary': 0.15,
            'education': 0.10
        }
    
    def calculate_skills_match(self, user_skills: List[str], job_required_skills: List[str], 
                              job_preferred_skills: List[str] = None) -> Tuple[float, List[str], List[str]]:
        """Calculate skills matching score."""
        if not user_skills:
            return 0.0, [], job_required_skills or []
        
        if not job_required_skills:
            job_required_skills = []
        
        if not job_preferred_skills:
            job_preferred_skills = []
        
        # Normalize skills for comparison (lowercase, strip spaces)
        user_skills_norm = [skill.lower().strip() for skill in user_skills]
        required_skills_norm = [skill.lower().strip() for skill in job_required_skills]
        preferred_skills_norm = [skill.lower().strip() for skill in job_preferred_skills or []]
        
        # Find matching skills
        matching_required = []
        matching_preferred = []
        
        for skill in user_skills_norm:
            if skill in required_skills_norm:
                matching_required.append(skill)
            elif skill in preferred_skills_norm:
                matching_preferred.append(skill)
        
        # Calculate score
        total_required = len(job_required_skills)
        total_preferred = len(job_preferred_skills or [])
        
        # Base score from required skills
        if total_required > 0:
            required_score = len(matching_required) / total_required
        else:
            required_score = 1.0  # No requirements means full score
        
        # Bonus from preferred skills
        preferred_bonus = 0.0
        if total_preferred > 0:
            preferred_bonus = len(matching_preferred) / total_preferred * 0.3
        
        # Final score (0-100)
        final_score = min(100.0, (required_score + preferred_bonus) * 100)
        
        # Get original skill names for matching skills
        matching_skills = []
        for skill in user_skills:
            if skill.lower().strip() in matching_required or skill.lower().strip() in matching_preferred:
                matching_skills.append(skill)
        
        # Get missing required skills
        missing_skills = []
        for skill in job_required_skills:
            if skill.lower().strip() not in user_skills_norm:
                missing_skills.append(skill)
        
        return final_score, matching_skills, missing_skills
    
    def calculate_experience_match(self, user_experience_years: float, 
                                 job_experience_level: str) -> float:
        """Calculate experience level matching score."""
        if not user_experience_years:
            user_experience_years = 0
        
        # Define experience level ranges
        experience_ranges = {
            'entry': (0, 2),
            'mid': (2, 5),
            'senior': (5, 10),
            'executive': (10, 20)
        }
        
        if not job_experience_level or job_experience_level.lower() not in experience_ranges:
            return 75.0  # Neutral score if no requirement specified
        
        min_exp, max_exp = experience_ranges[job_experience_level.lower()]
        
        # Perfect match if within range
        if min_exp <= user_experience_years <= max_exp:
            return 100.0
        
        # Calculate penalty for being outside range
        if user_experience_years < min_exp:
            # Under-qualified
            gap = min_exp - user_experience_years
            penalty = min(gap * 20, 80)  # Max 80% penalty
            return max(20.0, 100 - penalty)
        else:
            # Over-qualified (less penalty)
            gap = user_experience_years - max_exp
            penalty = min(gap * 10, 40)  # Max 40% penalty
            return max(60.0, 100 - penalty)
    
    def calculate_location_match(self, user_location: str, job_location: str, 
                               user_work_type: str, job_work_type: str) -> float:
        """Calculate location matching score."""
        # Remote work gets perfect score regardless of location
        if job_work_type and job_work_type.lower() == 'remote':
            return 100.0
        
        if user_work_type and user_work_type.lower() == 'remote':
            return 90.0 if job_work_type and job_work_type.lower() in ['remote', 'hybrid'] else 70.0
        
        if not user_location or not job_location:
            return 50.0  # Neutral score if location not specified
        
        # Normalize locations
        user_loc = user_location.lower().strip()
        job_loc = job_location.lower().strip()
        
        # Exact match
        if user_loc == job_loc:
            return 100.0
        
        # City match (if one contains the other)
        if user_loc in job_loc or job_loc in user_loc:
            return 85.0
        
        # Extract city/state for partial matching
        user_parts = user_loc.split(',')
        job_parts = job_loc.split(',')
        
        # Check if same city
        if len(user_parts) > 0 and len(job_parts) > 0:
            if user_parts[0].strip() == job_parts[0].strip():
                return 90.0
        
        # Check if same state/region
        if len(user_parts) > 1 and len(job_parts) > 1:
            if user_parts[-1].strip() == job_parts[-1].strip():
                return 60.0
        
        return 30.0  # Different locations
    
    def calculate_salary_match(self, user_salary_min: int, user_salary_max: int,
                             job_salary_min: int, job_salary_max: int) -> float:
        """Calculate salary matching score."""
        # If no salary requirements from user, assume salary is acceptable
        if not user_salary_min and not user_salary_max:
            return 75.0
        
        # If no salary information from job, neutral score
        if not job_salary_min and not job_salary_max:
            return 50.0
        
        # Use defaults if one bound is missing
        if not user_salary_min:
            user_salary_min = 0
        if not user_salary_max:
            user_salary_max = user_salary_min * 1.5 if user_salary_min else 200000
        
        if not job_salary_min:
            job_salary_min = job_salary_max * 0.8 if job_salary_max else 0
        if not job_salary_max:
            job_salary_max = job_salary_min * 1.3 if job_salary_min else 200000
        
        # Check for overlap
        overlap_start = max(user_salary_min, job_salary_min)
        overlap_end = min(user_salary_max, job_salary_max)
        
        if overlap_start <= overlap_end:
            # There's overlap - calculate how much
            overlap_amount = overlap_end - overlap_start
            user_range = user_salary_max - user_salary_min
            job_range = job_salary_max - job_salary_min
            
            # Score based on overlap percentage
            if user_range > 0:
                overlap_pct = overlap_amount / user_range
                return min(100.0, 60 + overlap_pct * 40)
            else:
                return 100.0  # Perfect match if user has exact salary requirement
        
        # No overlap - check if job salary is above user minimum
        if job_salary_max >= user_salary_min:
            return 40.0  # Acceptable but not ideal
        
        return 20.0  # Job salary below expectations
    
    def generate_match_explanation(self, overall_score: float, skills_score: float,
                                 experience_score: float, location_score: float,
                                 salary_score: float, matching_skills: List[str],
                                 missing_skills: List[str]) -> str:
        """Generate human-readable explanation for the match."""
        explanation_parts = []
        
        # Overall assessment
        if overall_score >= 80:
            explanation_parts.append("🎯 Excellent match!")
        elif overall_score >= 60:
            explanation_parts.append("✅ Good match")
        elif overall_score >= 40:
            explanation_parts.append("⚠️ Moderate match")
        else:
            explanation_parts.append("❌ Poor match")
        
        # Skills analysis
        if skills_score >= 80:
            explanation_parts.append(f"Strong skills alignment with {len(matching_skills)} matching skills.")
        elif skills_score >= 60:
            explanation_parts.append(f"Good skills match with {len(matching_skills)} relevant skills.")
        elif missing_skills:
            explanation_parts.append(f"Missing {len(missing_skills)} key skills: {', '.join(missing_skills[:3])}{'...' if len(missing_skills) > 3 else ''}")
        
        # Experience analysis
        if experience_score >= 80:
            explanation_parts.append("Experience level aligns well with requirements.")
        elif experience_score >= 60:
            explanation_parts.append("Experience level is acceptable for this role.")
        else:
            explanation_parts.append("Experience level may not fully meet requirements.")
        
        # Location analysis
        if location_score >= 90:
            explanation_parts.append("Perfect location match.")
        elif location_score >= 70:
            explanation_parts.append("Good location compatibility.")
        elif location_score >= 50:
            explanation_parts.append("Location may require consideration.")
        
        # Salary analysis
        if salary_score >= 80:
            explanation_parts.append("Salary range aligns well with expectations.")
        elif salary_score >= 60:
            explanation_parts.append("Salary is within acceptable range.")
        elif salary_score >= 40:
            explanation_parts.append("Salary may be lower than ideal.")
        
        return " ".join(explanation_parts)
    
    def calculate_job_match(self, user: User, user_profile: UserProfile, 
                          user_resume: Resume, job: Job) -> Dict[str, Any]:
        """Calculate comprehensive job match score."""
        
        # Get user skills from resume and profile
        user_skills = []
        if user_resume and user_resume.skills_extracted:
            user_skills.extend(user_resume.skills_extracted)
        if user_profile and user_profile.skills:
            user_skills.extend(user_profile.skills)
        
        # Remove duplicates
        user_skills = list(set(user_skills))
        
        # Calculate individual scores
        skills_score, matching_skills, missing_skills = self.calculate_skills_match(
            user_skills,
            job.required_skills or [],
            job.preferred_skills or []
        )
        
        experience_score = self.calculate_experience_match(
            user_resume.experience_years if user_resume else 0,
            job.experience_level
        )
        
        location_score = self.calculate_location_match(
            user_profile.desired_location if user_profile else None,
            job.location,
            user_profile.work_type if user_profile else None,
            job.work_type
        )
        
        salary_score = self.calculate_salary_match(
            user_profile.desired_salary_min if user_profile else None,
            user_profile.desired_salary_max if user_profile else None,
            job.salary_min,
            job.salary_max
        )
        
        # Calculate weighted overall score
        overall_score = (
            skills_score * self.weights['skills'] +
            experience_score * self.weights['experience'] +
            location_score * self.weights['location'] +
            salary_score * self.weights['salary']
        )
        
        # Generate explanation
        explanation = self.generate_match_explanation(
            overall_score, skills_score, experience_score,
            location_score, salary_score, matching_skills, missing_skills
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'skills_score': round(skills_score, 1),
            'experience_score': round(experience_score, 1),
            'location_score': round(location_score, 1),
            'salary_score': round(salary_score, 1),
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'match_explanation': explanation
        }
    
    def find_job_matches(self, db: Session, user: User, limit: int = 20) -> List[JobMatch]:
        """Find and score job matches for a user."""
        
        # Get user profile and latest resume
        user_profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        user_resume = db.query(Resume).filter(
            Resume.user_id == user.id, 
            Resume.is_active == True
        ).order_by(Resume.created_at.desc()).first()
        
        # Get active jobs
        jobs_query = db.query(Job).filter(Job.is_active == True)
        
        # Filter by user preferences if available
        if user_profile:
            if user_profile.desired_location:
                # Include remote jobs and jobs in desired location
                jobs_query = jobs_query.filter(
                    (Job.work_type == 'remote') | 
                    (Job.location.ilike(f"%{user_profile.desired_location}%"))
                )
            
            if user_profile.desired_salary_min:
                jobs_query = jobs_query.filter(
                    (Job.salary_max.is_(None)) | 
                    (Job.salary_max >= user_profile.desired_salary_min)
                )
        
        jobs = jobs_query.limit(100).all()  # Limit to avoid processing too many jobs
        
        # Calculate matches
        matches = []
        for job in jobs:
            # Check if match already exists
            existing_match = db.query(JobMatch).filter(
                JobMatch.user_id == user.id,
                JobMatch.job_id == job.id
            ).first()
            
            if existing_match:
                continue
            
            # Calculate match score
            match_data = self.calculate_job_match(user, user_profile, user_resume, job)
            
            # Only create matches above threshold
            if match_data['overall_score'] >= 30:
                job_match = JobMatch(
                    user_id=user.id,
                    job_id=job.id,
                    overall_score=match_data['overall_score'],
                    skills_score=match_data['skills_score'],
                    experience_score=match_data['experience_score'],
                    location_score=match_data['location_score'],
                    salary_score=match_data['salary_score'],
                    matching_skills=match_data['matching_skills'],
                    missing_skills=match_data['missing_skills'],
                    match_explanation=match_data['match_explanation'],
                    is_recommended=match_data['overall_score'] >= 70
                )
                
                db.add(job_match)
                matches.append(job_match)
        
        # Commit new matches
        db.commit()
        
        # Return top matches
        return sorted(matches, key=lambda x: x.overall_score, reverse=True)[:limit]
    
    def update_match_recommendations(self, db: Session, user: User):
        """Update match recommendations for a user (called after profile/resume updates)."""
        
        # Remove old matches that are no longer relevant
        old_matches = db.query(JobMatch).filter(
            JobMatch.user_id == user.id,
            JobMatch.is_viewed == False,
            JobMatch.overall_score < 40
        ).all()
        
        for match in old_matches:
            db.delete(match)
        
        # Find new matches
        self.find_job_matches(db, user, limit=50)
        
        db.commit()