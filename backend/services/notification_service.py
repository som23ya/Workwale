import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
import logging
from sqlalchemy.orm import Session

from database.models import User, Notification, Job

load_dotenv()

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        # Twilio configuration for WhatsApp
        self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
        
        # SendGrid configuration for Email
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@workwale.ai")
        
        # Initialize clients
        if self.twilio_account_sid and self.twilio_auth_token:
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
            logger.warning("Twilio credentials not found. WhatsApp notifications disabled.")
        
        if self.sendgrid_api_key:
            self.sendgrid_client = SendGridAPIClient(api_key=self.sendgrid_api_key)
        else:
            self.sendgrid_client = None
            logger.warning("SendGrid API key not found. Email notifications disabled.")
    
    def send_email(self, to_email: str, subject: str, html_content: str, 
                   text_content: str = None) -> bool:
        """Send email using SendGrid."""
        if not self.sendgrid_client:
            logger.error("SendGrid client not initialized")
            return False
        
        try:
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
                plain_text_content=text_content
            )
            
            response = self.sendgrid_client.send(message)
            
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"Failed to send email to {to_email}. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def send_whatsapp(self, to_phone: str, message: str) -> bool:
        """Send WhatsApp message using Twilio."""
        if not self.twilio_client:
            logger.error("Twilio client not initialized")
            return False
        
        try:
            # Ensure phone number is in correct format
            if not to_phone.startswith('+'):
                to_phone = '+' + to_phone.replace('+', '').replace(' ', '').replace('-', '')
            
            message = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_whatsapp_number,
                to=f'whatsapp:{to_phone}'
            )
            
            logger.info(f"WhatsApp message sent successfully to {to_phone}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending WhatsApp to {to_phone}: {str(e)}")
            return False
    
    def create_job_match_email_template(self, user_name: str, matches: List[Dict]) -> str:
        """Create HTML email template for job matches."""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .logo {{ color: #4A90E2; font-size: 24px; font-weight: bold; }}
                .job-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin-bottom: 20px; }}
                .job-title {{ font-size: 18px; font-weight: bold; color: #333; margin-bottom: 5px; }}
                .company {{ color: #666; margin-bottom: 10px; }}
                .match-score {{ background: linear-gradient(90deg, #4A90E2, #50C878); color: white; padding: 5px 15px; border-radius: 20px; display: inline-block; font-weight: bold; }}
                .job-details {{ margin: 15px 0; }}
                .skills {{ background-color: #f0f8ff; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .btn {{ background-color: #4A90E2; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; display: inline-block; margin-top: 15px; }}
                .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">WorkWale.ai</div>
                    <h2>🎯 New Job Matches Found!</h2>
                    <p>Hi {user_name}, we found some exciting opportunities for you!</p>
                </div>
        """
        
        for match in matches:
            job = match['job']
            score = match['overall_score']
            
            score_class = ""
            if score >= 80:
                score_color = "#50C878"
                score_text = "Excellent Match"
            elif score >= 60:
                score_color = "#4A90E2"
                score_text = "Good Match"
            else:
                score_color = "#FFA500"
                score_text = "Moderate Match"
            
            html_content += f"""
                <div class="job-card">
                    <div class="job-title">{job.title}</div>
                    <div class="company">{job.company} • {job.location or 'Location not specified'}</div>
                    <div class="match-score" style="background-color: {score_color};">
                        {score}% {score_text}
                    </div>
                    <div class="job-details">
                        <p><strong>Experience Level:</strong> {job.experience_level or 'Not specified'}</p>
                        <p><strong>Work Type:</strong> {job.work_type or 'Not specified'}</p>
                        <p><strong>Salary:</strong> {f'${job.salary_min:,} - ${job.salary_max:,}' if job.salary_min and job.salary_max else 'Not disclosed'}</p>
                    </div>
                    <div class="skills">
                        <strong>Matching Skills:</strong> {', '.join(match.get('matching_skills', [])[:5])}
                        {f"and {len(match.get('matching_skills', [])) - 5} more..." if len(match.get('matching_skills', [])) > 5 else ""}
                    </div>
                    <a href="{job.external_url or '#'}" class="btn">View Job Details</a>
                </div>
            """
        
        html_content += """
                <div class="footer">
                    <p>🚀 Ready to apply? Visit your WorkWale.ai dashboard to manage your applications.</p>
                    <p style="font-size: 12px; color: #999;">
                        You're receiving this because you enabled job match notifications. 
                        <a href="#" style="color: #4A90E2;">Update preferences</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_content
    
    def create_job_match_whatsapp_message(self, user_name: str, matches: List[Dict]) -> str:
        """Create WhatsApp message for job matches."""
        
        message = f"🎯 *WorkWale.ai Job Alert*\n\n"
        message += f"Hi {user_name}! We found {len(matches)} new job matches for you:\n\n"
        
        for i, match in enumerate(matches[:3], 1):  # Limit to 3 jobs for WhatsApp
            job = match['job']
            score = match['overall_score']
            
            score_emoji = "🟢" if score >= 80 else "🔵" if score >= 60 else "🟡"
            
            message += f"{score_emoji} *{job.title}*\n"
            message += f"🏢 {job.company}\n"
            message += f"📍 {job.location or 'Remote'}\n"
            message += f"📊 {score}% Match\n"
            
            if match.get('matching_skills'):
                skills = ', '.join(match['matching_skills'][:3])
                message += f"💼 Skills: {skills}\n"
            
            message += f"🔗 {job.external_url or 'Link not available'}\n\n"
        
        if len(matches) > 3:
            message += f"... and {len(matches) - 3} more matches available on your dashboard!\n\n"
        
        message += "Visit WorkWale.ai to view all matches and apply! 🚀"
        
        return message
    
    def send_job_match_notification(self, db: Session, user: User, matches: List[Dict]) -> Dict[str, bool]:
        """Send job match notifications via email and/or WhatsApp."""
        
        results = {'email_sent': False, 'whatsapp_sent': False}
        
        # Get user preferences
        user_profile = user.profile
        if not user_profile:
            logger.warning(f"No profile found for user {user.id}")
            return results
        
        # Send email notification
        if user_profile.email_notifications and user.email:
            html_content = self.create_job_match_email_template(user.full_name, matches)
            text_content = f"Hi {user.full_name}, we found {len(matches)} new job matches for you! Visit WorkWale.ai to view them."
            
            subject = f"🎯 {len(matches)} New Job Matches Found - WorkWale.ai"
            
            if self.send_email(user.email, subject, html_content, text_content):
                results['email_sent'] = True
        
        # Send WhatsApp notification
        if user_profile.whatsapp_notifications and user.phone:
            whatsapp_message = self.create_job_match_whatsapp_message(user.full_name, matches)
            
            if self.send_whatsapp(user.phone, whatsapp_message):
                results['whatsapp_sent'] = True
        
        # Create notification record
        notification = Notification(
            user_id=user.id,
            type="job_match",
            title=f"{len(matches)} New Job Matches",
            message=f"We found {len(matches)} job opportunities that match your profile!",
            email_sent=results['email_sent'],
            whatsapp_sent=results['whatsapp_sent']
        )
        
        db.add(notification)
        db.commit()
        
        return results
    
    def send_application_update_notification(self, db: Session, user: User, 
                                          job_title: str, company: str, 
                                          new_status: str) -> Dict[str, bool]:
        """Send notification when application status changes."""
        
        results = {'email_sent': False, 'whatsapp_sent': False}
        
        # Get user preferences
        user_profile = user.profile
        if not user_profile:
            return results
        
        # Create message content
        status_emojis = {
            'applied': '📝',
            'reviewed': '👀',
            'interview': '🎯',
            'rejected': '❌',
            'offered': '🎉'
        }
        
        emoji = status_emojis.get(new_status.lower(), '📋')
        
        # Send email
        if user_profile.email_notifications and user.email:
            subject = f"{emoji} Application Update: {job_title} at {company}"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #4A90E2;">{emoji} Application Status Update</h2>
                <p>Hi {user.full_name},</p>
                <p>Your application for <strong>{job_title}</strong> at <strong>{company}</strong> has been updated:</p>
                <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="font-size: 18px; margin: 0;"><strong>New Status: {new_status.title()}</strong></p>
                </div>
                <p>Visit your WorkWale.ai dashboard to view more details and manage your applications.</p>
                <p>Best regards,<br>The WorkWale.ai Team</p>
            </div>
            """
            
            if self.send_email(user.email, subject, html_content):
                results['email_sent'] = True
        
        # Send WhatsApp
        if user_profile.whatsapp_notifications and user.phone:
            whatsapp_message = f"{emoji} *Application Update*\n\n"
            whatsapp_message += f"Hi {user.full_name}!\n\n"
            whatsapp_message += f"Your application for *{job_title}* at *{company}* has been updated:\n\n"
            whatsapp_message += f"📋 *Status:* {new_status.title()}\n\n"
            whatsapp_message += "Visit WorkWale.ai to view details! 🚀"
            
            if self.send_whatsapp(user.phone, whatsapp_message):
                results['whatsapp_sent'] = True
        
        # Create notification record
        notification = Notification(
            user_id=user.id,
            type="application_update",
            title=f"Application Update: {job_title}",
            message=f"Status changed to: {new_status.title()}",
            email_sent=results['email_sent'],
            whatsapp_sent=results['whatsapp_sent']
        )
        
        db.add(notification)
        db.commit()
        
        return results
    
    def send_welcome_notification(self, db: Session, user: User) -> Dict[str, bool]:
        """Send welcome notification to new users."""
        
        results = {'email_sent': False, 'whatsapp_sent': False}
        
        # Send welcome email
        if user.email:
            subject = "🎉 Welcome to WorkWale.ai - Your AI Job Search Begins!"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #4A90E2;">Welcome to WorkWale.ai! 🎉</h1>
                </div>
                
                <p>Hi {user.full_name},</p>
                
                <p>Welcome to WorkWale.ai! We're excited to help you discover your dream job with the power of AI.</p>
                
                <h3>🚀 Get Started in 3 Easy Steps:</h3>
                <ol style="line-height: 1.8;">
                    <li><strong>Upload Your Resume:</strong> Let our AI parse and understand your skills</li>
                    <li><strong>Complete Your Profile:</strong> Tell us about your job preferences</li>
                    <li><strong>Get Matched:</strong> Receive personalized job recommendations</li>
                </ol>
                
                <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin: 30px 0;">
                    <h3 style="margin-top: 0; color: #4A90E2;">✨ What makes WorkWale.ai special?</h3>
                    <ul style="line-height: 1.6;">
                        <li>🤖 GPT-powered resume parsing</li>
                        <li>🎯 Smart job matching algorithm</li>
                        <li>📱 Real-time alerts via email and WhatsApp</li>
                        <li>📊 Comprehensive application tracking</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://workwale.ai/dashboard" style="background-color: #4A90E2; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Start Your Job Search 🚀</a>
                </div>
                
                <p>If you have any questions, our team is here to help!</p>
                
                <p>Best regards,<br>The WorkWale.ai Team</p>
            </div>
            """
            
            if self.send_email(user.email, subject, html_content):
                results['email_sent'] = True
        
        # Create notification record
        notification = Notification(
            user_id=user.id,
            type="system",
            title="Welcome to WorkWale.ai!",
            message="Your AI-powered job search journey begins now!",
            email_sent=results['email_sent'],
            whatsapp_sent=results['whatsapp_sent']
        )
        
        db.add(notification)
        db.commit()
        
        return results