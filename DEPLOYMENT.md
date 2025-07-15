# 🚀 WorkWale.ai - Live Deployment

## 🌐 **LIVE WEBSITE LINKS**

### ✅ **Frontend (User Interface)**
**🔗 https://workwale-frontend.onrender.com**

### ✅ **Backend API & Documentation** 
**🔗 https://workwale-backend.onrender.com/docs**

---

## 🚀 **ONE-CLICK DEPLOYMENT**

### Deploy to Render (Recommended - Free)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/som23ya/Workwale)

### Deploy Frontend to Netlify
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/som23ya/Workwale&base=frontend)

### Deploy to Vercel (Frontend)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/som23ya/Workwale&project-name=workwale&repository-name=workwale&root-directory=frontend)

---

## 📱 **How to Use the Live App**

1. **Visit**: https://workwale-frontend.onrender.com
2. **Upload Resume**: Click "Upload Resume" and select your PDF
3. **Set Preferences**: Define your job criteria and skills
4. **Get Matches**: AI will find and score relevant jobs
5. **Track Applications**: Monitor your job search progress

---

## 🔧 **API Endpoints (Backend)**

Base URL: `https://workwale-backend.onrender.com`

- **API Documentation**: `/docs`
- **Health Check**: `/health`
- **Authentication**: `/api/auth`
- **Resume Upload**: `/api/resume`
- **Job Matching**: `/api/jobs`
- **Dashboard**: `/api/dashboard`

---

## ⚠️ **Important Notes**

- **Free Tier**: Apps may sleep after 15 minutes of inactivity
- **Cold Start**: First load might take 30-60 seconds
- **Database**: PostgreSQL is included and configured
- **Features**: Core functionality works without API keys
- **Full Features**: Add OpenAI API key for AI resume parsing

---

## 🔑 **Optional API Keys Setup**

For full functionality, add these environment variables:

```
OPENAI_API_KEY=your_openai_key        # For AI resume parsing
TWILIO_ACCOUNT_SID=your_twilio_sid    # For WhatsApp alerts  
SMTP_USERNAME=your_email              # For email alerts
```

---

## 📞 **Support & Issues**

- **Repository**: https://github.com/som23ya/Workwale
- **Issues**: Report bugs on GitHub Issues
- **Documentation**: Check `/docs` endpoint for API reference

---

**🎉 Your WorkWale.ai platform is now LIVE and ready to use!**