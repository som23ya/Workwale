import time
import json
import os
from typing import List, Dict, Any, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
import re

load_dotenv()

logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self):
        self.email = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
        self.driver = None
        self.base_url = "https://www.linkedin.com"
        
    def setup_driver(self, headless: bool = True) -> webdriver.Chrome:
        """Setup Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.managed_default_content_settings.stylesheets": 2,
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            raise
    
    def login(self) -> bool:
        """Login to LinkedIn."""
        if not self.email or not self.password:
            logger.error("LinkedIn credentials not provided")
            return False
        
        try:
            self.driver.get(f"{self.base_url}/login")
            
            # Wait for login form
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            
            # Enter credentials
            email_field.clear()
            email_field.send_keys(self.email)
            password_field.clear()
            password_field.send_keys(self.password)
            
            # Click login
            login_button.click()
            
            # Wait for dashboard or check if login was successful
            WebDriverWait(self.driver, 15).until(
                lambda driver: "/feed" in driver.current_url or "/checkpoint" in driver.current_url
            )
            
            # Handle potential security check
            if "/checkpoint" in self.driver.current_url:
                logger.warning("LinkedIn security checkpoint detected. Manual intervention may be required.")
                time.sleep(30)  # Wait for manual intervention or automatic resolution
            
            logger.info("Successfully logged into LinkedIn")
            return True
            
        except TimeoutException:
            logger.error("Login timeout - LinkedIn may have detected automation")
            return False
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def search_jobs(self, query: str, location: str = "", experience_level: str = "",
                   work_type: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """Search for jobs on LinkedIn."""
        
        if not self.driver:
            self.driver = self.setup_driver()
            if not self.login():
                logger.error("Failed to login to LinkedIn")
                return []
        
        jobs = []
        
        try:
            # Build search URL
            search_params = {
                "keywords": query,
                "location": location,
                "f_TPR": "r604800",  # Past week
                "f_E": self._get_experience_filter(experience_level),
                "f_WT": self._get_work_type_filter(work_type),
                "sortBy": "DD"  # Sort by date
            }
            
            # Remove empty parameters
            search_params = {k: v for k, v in search_params.items() if v}
            
            # Build URL
            job_search_url = f"{self.base_url}/jobs/search?" + "&".join([f"{k}={v}" for k, v in search_params.items()])
            
            logger.info(f"Searching LinkedIn jobs: {job_search_url}")
            self.driver.get(job_search_url)
            
            # Wait for job results
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "jobs-search-results-list"))
            )
            
            processed_jobs = 0
            page = 0
            
            while processed_jobs < limit:
                # Get job cards on current page
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
                
                if not job_cards:
                    logger.info("No more job cards found")
                    break
                
                for card in job_cards:
                    if processed_jobs >= limit:
                        break
                    
                    try:
                        job_data = self._extract_job_from_card(card)
                        if job_data:
                            jobs.append(job_data)
                            processed_jobs += 1
                            
                        # Random delay to avoid detection
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.warning(f"Error extracting job card: {e}")
                        continue
                
                # Try to load more jobs or go to next page
                if processed_jobs < limit:
                    if not self._load_more_jobs():
                        break
                
                page += 1
                if page > 10:  # Safety limit
                    break
            
            logger.info(f"Successfully scraped {len(jobs)} jobs from LinkedIn")
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn jobs: {e}")
        
        return jobs
    
    def _extract_job_from_card(self, card) -> Optional[Dict[str, Any]]:
        """Extract job information from a job card element."""
        try:
            # Get job link and ID
            job_link_element = card.find_element(By.CSS_SELECTOR, "a[data-control-name='job_search_job_result_clicked']")
            job_url = job_link_element.get_attribute("href")
            
            # Extract job ID from URL
            job_id_match = re.search(r'/jobs/view/(\d+)', job_url)
            job_id = job_id_match.group(1) if job_id_match else None
            
            # Get basic info
            title_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__title a span[title]")
            title = title_element.get_attribute("title")
            
            company_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__subtitle a span[title]")
            company = company_element.get_attribute("title")
            
            # Location
            try:
                location_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                location = location_element.text.strip()
            except NoSuchElementException:
                location = ""
            
            # Posted date
            try:
                posted_element = card.find_element(By.CSS_SELECTOR, ".job-search-card__listdate")
                posted_text = posted_element.text.strip()
                posted_date = self._parse_posted_date(posted_text)
            except NoSuchElementException:
                posted_date = datetime.now()
            
            # Get detailed job information by clicking the card
            try:
                card.click()
                time.sleep(2)  # Wait for details to load
                
                # Extract job description
                description = self._extract_job_description()
                
                # Extract additional details
                job_details = self._extract_job_details()
                
            except Exception as e:
                logger.warning(f"Could not get detailed job info: {e}")
                description = ""
                job_details = {}
            
            job_data = {
                "title": title,
                "company": company,
                "location": location,
                "description": description,
                "requirements": job_details.get("requirements", ""),
                "experience_level": job_details.get("experience_level"),
                "work_type": job_details.get("work_type"),
                "job_type": job_details.get("job_type"),
                "salary_min": job_details.get("salary_min"),
                "salary_max": job_details.get("salary_max"),
                "required_skills": job_details.get("required_skills", []),
                "preferred_skills": job_details.get("preferred_skills", []),
                "source": "linkedin",
                "external_id": job_id,
                "external_url": job_url,
                "posted_date": posted_date
            }
            
            return job_data
            
        except Exception as e:
            logger.warning(f"Error extracting job from card: {e}")
            return None
    
    def _extract_job_description(self) -> str:
        """Extract job description from the detailed view."""
        try:
            description_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".jobs-description-content__text"))
            )
            return description_element.text.strip()
        except:
            return ""
    
    def _extract_job_details(self) -> Dict[str, Any]:
        """Extract additional job details from the detailed view."""
        details = {}
        
        try:
            # Look for job criteria section
            criteria_section = self.driver.find_element(By.CSS_SELECTOR, ".jobs-unified-top-card__job-insight")
            criteria_text = criteria_section.text.lower()
            
            # Extract experience level
            if "entry" in criteria_text or "junior" in criteria_text:
                details["experience_level"] = "entry"
            elif "senior" in criteria_text:
                details["experience_level"] = "senior"
            elif "mid" in criteria_text or "intermediate" in criteria_text:
                details["experience_level"] = "mid"
            elif "executive" in criteria_text or "director" in criteria_text:
                details["experience_level"] = "executive"
            
            # Extract work type
            if "remote" in criteria_text:
                details["work_type"] = "remote"
            elif "hybrid" in criteria_text:
                details["work_type"] = "hybrid"
            else:
                details["work_type"] = "onsite"
            
            # Extract job type
            if "full-time" in criteria_text or "full time" in criteria_text:
                details["job_type"] = "full-time"
            elif "part-time" in criteria_text or "part time" in criteria_text:
                details["job_type"] = "part-time"
            elif "contract" in criteria_text:
                details["job_type"] = "contract"
            elif "internship" in criteria_text:
                details["job_type"] = "internship"
            
        except:
            pass
        
        # Extract skills from description
        description = self._extract_job_description()
        details["required_skills"] = self._extract_skills_from_text(description)
        
        return details
    
    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description text."""
        # Common technical skills to look for
        skills_keywords = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Angular', 'Vue.js',
            'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'Git', 'Linux', 'HTML', 'CSS', 'TypeScript',
            'FastAPI', 'Django', 'Flask', 'Spring', 'Express.js', 'TensorFlow',
            'PyTorch', 'Machine Learning', 'Data Science', 'Pandas', 'NumPy',
            'C++', 'C#', '.NET', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go', 'Rust'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in skills_keywords:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def _get_experience_filter(self, experience_level: str) -> str:
        """Get LinkedIn experience filter parameter."""
        filters = {
            "entry": "1",
            "mid": "2", 
            "senior": "3",
            "executive": "4"
        }
        return filters.get(experience_level.lower(), "")
    
    def _get_work_type_filter(self, work_type: str) -> str:
        """Get LinkedIn work type filter parameter."""
        filters = {
            "remote": "2",
            "hybrid": "3",
            "onsite": "1"
        }
        return filters.get(work_type.lower(), "")
    
    def _parse_posted_date(self, posted_text: str) -> datetime:
        """Parse LinkedIn posted date text to datetime."""
        try:
            posted_text = posted_text.lower()
            now = datetime.now()
            
            if "hour" in posted_text:
                hours = int(re.search(r'(\d+)', posted_text).group(1))
                return now - timedelta(hours=hours)
            elif "day" in posted_text:
                days = int(re.search(r'(\d+)', posted_text).group(1))
                return now - timedelta(days=days)
            elif "week" in posted_text:
                weeks = int(re.search(r'(\d+)', posted_text).group(1))
                return now - timedelta(weeks=weeks)
            elif "month" in posted_text:
                months = int(re.search(r'(\d+)', posted_text).group(1))
                return now - timedelta(days=months * 30)
            else:
                return now
        except:
            return datetime.now()
    
    def _load_more_jobs(self) -> bool:
        """Try to load more jobs by scrolling or clicking pagination."""
        try:
            # First try scrolling to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Look for "See more jobs" button
            try:
                see_more_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label*='See more jobs']")
                if see_more_button.is_enabled():
                    see_more_button.click()
                    time.sleep(3)
                    return True
            except NoSuchElementException:
                pass
            
            # Try pagination
            try:
                next_button = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
                if next_button.is_enabled():
                    next_button.click()
                    time.sleep(3)
                    return True
            except NoSuchElementException:
                pass
            
            return False
            
        except Exception as e:
            logger.warning(f"Error loading more jobs: {e}")
            return False
    
    def close(self):
        """Close the browser driver."""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()