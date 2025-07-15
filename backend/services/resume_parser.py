import os
import json
import PyPDF2
import pdfplumber
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
import re
from datetime import datetime

load_dotenv()

class ResumeParser:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using multiple methods."""
        text = ""
        
        # Try pdfplumber first (better for formatted text)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"pdfplumber failed: {e}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except Exception as e:
                print(f"PyPDF2 also failed: {e}")
                raise Exception("Could not extract text from PDF")
        
        return text.strip()
    
    def parse_resume_with_gpt(self, resume_text: str) -> Dict[str, Any]:
        """Use GPT to parse resume and extract structured information."""
        
        prompt = f"""
        Please analyze the following resume text and extract the information in a structured JSON format.
        
        Resume Text:
        {resume_text}
        
        Please extract and return a JSON object with the following structure:
        {{
            "personal_info": {{
                "name": "Full name",
                "email": "Email address",
                "phone": "Phone number",
                "location": "Current location/address"
            }},
            "summary": "Professional summary or objective",
            "skills": [
                "List of technical and professional skills"
            ],
            "experience": [
                {{
                    "company": "Company name",
                    "position": "Job title",
                    "start_date": "Start date",
                    "end_date": "End date or 'Present'",
                    "duration_months": "Duration in months (estimate)",
                    "description": "Job description and achievements",
                    "technologies": ["Technologies used"]
                }}
            ],
            "education": [
                {{
                    "institution": "School/University name",
                    "degree": "Degree type and major",
                    "graduation_date": "Graduation date",
                    "gpa": "GPA if mentioned"
                }}
            ],
            "certifications": [
                "List of certifications"
            ],
            "projects": [
                {{
                    "name": "Project name",
                    "description": "Project description",
                    "technologies": ["Technologies used"]
                }}
            ],
            "languages": [
                "List of languages"
            ],
            "total_experience_years": "Total years of experience (estimate as a number)"
        }}
        
        Important notes:
        - If any field is not found, set it to null or empty array as appropriate
        - For experience duration, estimate months based on dates
        - For total experience, calculate the sum of all work experience
        - Extract ALL skills mentioned, including technical, soft skills, tools, etc.
        - Be thorough in extracting information
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume parser. Extract information accurately and comprehensively."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse the JSON response
            parsed_data = json.loads(response.choices[0].message.content)
            return parsed_data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from GPT response: {e}")
            return self._fallback_parsing(resume_text)
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return self._fallback_parsing(resume_text)
    
    def _fallback_parsing(self, resume_text: str) -> Dict[str, Any]:
        """Fallback parsing using regex patterns if GPT fails."""
        
        # Basic regex patterns for common resume elements
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        # Extract basic information
        emails = re.findall(email_pattern, resume_text)
        phones = re.findall(phone_pattern, resume_text)
        
        # Extract skills (common technical skills)
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Angular', 'Vue.js',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'Git', 'Linux', 'HTML', 'CSS', 'TypeScript',
            'FastAPI', 'Django', 'Flask', 'Spring', 'Express.js', 'TensorFlow',
            'PyTorch', 'Machine Learning', 'Data Science', 'Pandas', 'NumPy'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill.lower() in resume_text.lower():
                found_skills.append(skill)
        
        return {
            "personal_info": {
                "name": None,
                "email": emails[0] if emails else None,
                "phone": phones[0] if phones else None,
                "location": None
            },
            "summary": None,
            "skills": found_skills,
            "experience": [],
            "education": [],
            "certifications": [],
            "projects": [],
            "languages": [],
            "total_experience_years": 0
        }
    
    def calculate_experience_years(self, experience_data: List[Dict]) -> float:
        """Calculate total years of experience from experience data."""
        total_months = 0
        
        for exp in experience_data:
            duration_months = exp.get('duration_months', 0)
            if isinstance(duration_months, (int, float)):
                total_months += duration_months
            elif isinstance(duration_months, str):
                # Try to extract number from string
                try:
                    total_months += float(re.findall(r'\d+', duration_months)[0])
                except:
                    pass
        
        return round(total_months / 12, 1)
    
    def extract_skills_list(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Extract and normalize skills list."""
        skills = []
        
        # Get skills from skills section
        if parsed_data.get('skills'):
            skills.extend(parsed_data['skills'])
        
        # Get technologies from experience
        for exp in parsed_data.get('experience', []):
            if exp.get('technologies'):
                skills.extend(exp['technologies'])
        
        # Get technologies from projects
        for project in parsed_data.get('projects', []):
            if project.get('technologies'):
                skills.extend(project['technologies'])
        
        # Remove duplicates and normalize
        skills = list(set([skill.strip() for skill in skills if skill]))
        
        return skills
    
    def get_education_level(self, education_data: List[Dict]) -> str:
        """Determine highest education level."""
        if not education_data:
            return "Not specified"
        
        levels = {
            'phd': 4, 'doctorate': 4, 'ph.d': 4,
            'master': 3, 'mba': 3, 'ms': 3, 'ma': 3,
            'bachelor': 2, 'bs': 2, 'ba': 2, 'be': 2,
            'associate': 1, 'diploma': 1
        }
        
        highest_level = 0
        highest_degree = "Not specified"
        
        for edu in education_data:
            degree = edu.get('degree', '').lower()
            for level_name, level_value in levels.items():
                if level_name in degree:
                    if level_value > highest_level:
                        highest_level = level_value
                        highest_degree = edu.get('degree', 'Not specified')
        
        return highest_degree if highest_level > 0 else "Not specified"
    
    def parse_resume(self, file_path: str) -> Dict[str, Any]:
        """Main method to parse resume from PDF file."""
        
        # Extract text from PDF
        resume_text = self.extract_text_from_pdf(file_path)
        
        if not resume_text:
            raise Exception("No text could be extracted from the PDF")
        
        # Parse with GPT
        parsed_data = self.parse_resume_with_gpt(resume_text)
        
        # Calculate derived fields
        experience_years = self.calculate_experience_years(parsed_data.get('experience', []))
        skills_list = self.extract_skills_list(parsed_data)
        education_level = self.get_education_level(parsed_data.get('education', []))
        
        # Extract job titles from experience
        job_titles = [exp.get('position') for exp in parsed_data.get('experience', []) if exp.get('position')]
        
        return {
            'raw_text': resume_text,
            'parsed_data': parsed_data,
            'skills_extracted': skills_list,
            'experience_years': experience_years,
            'education_level': education_level,
            'job_titles': job_titles
        }