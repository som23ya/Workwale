# WorkWale.ai - AI-Powered Job Discovery Platform

WorkWale.ai is a no-code, AI-powered job discovery platform that automates resume parsing, smart job matching, and real-time alerts. Designed for high-intent job seekers, it reduces manual effort by 90%, increases job relevance, and delivers matches directly to users across preferred channels.

## 🚀 Core Features

✅ **GPT-based Resume Parser** - Upload PDF resumes for intelligent parsing  
✅ **Job Matching Score Engine** - Smart matching based on skills and preferences  
✅ **Job Scraping** - Automated scraping from LinkedIn, Wellfound, Naukri  
✅ **Smart Alerts** - Real-time notifications via WhatsApp/Email  
✅ **User Dashboard** - Track applications and manage job searches  

## 🏗️ Tech Stack

- **Backend**: Python FastAPI
- **Frontend**: Next.js with React
- **Database**: PostgreSQL with SQLAlchemy
- **AI**: OpenAI GPT for resume parsing and job matching
- **Scraping**: Selenium + BeautifulSoup
- **Notifications**: Twilio (WhatsApp), SMTP (Email)
- **Authentication**: JWT tokens

## 📁 Project Structure

```
workwale-ai/
├── backend/           # FastAPI backend
├── frontend/          # Next.js frontend
├── scrapers/          # Job scraping modules
├── database/          # Database schemas and migrations
├── notifications/     # Email and WhatsApp services
└── docker-compose.yml # Container orchestration
```

## 🛠️ Setup Instructions

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run database migrations
5. Start the application: `docker-compose up`

## 🌟 Getting Started

1. **Upload Resume**: Upload your PDF resume for AI parsing
2. **Set Preferences**: Define your ideal job criteria and skills
3. **Auto-Match**: Let AI find and score relevant opportunities
4. **Get Alerts**: Receive notifications for new matches
5. **Track Progress**: Monitor applications in your dashboard

---

Built with ❤️ for job seekers everywhere