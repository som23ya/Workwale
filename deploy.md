# WorkWale.ai Deployment Guide

## Automated Deployment Links

### Frontend (Vercel)
[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fsom23ya%2FWorkwale&project-name=workwale-frontend&repository-name=workwale-frontend&root-directory=frontend&env=NEXT_PUBLIC_API_URL&envDescription=Backend%20API%20URL&envLink=https%3A%2F%2Fgithub.com%2Fsom23ya%2FWorkwale%23environment-variables)

### Backend (Railway)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/JTmPKP?referralCode=workwale)

## Manual Deployment Steps

### 1. Deploy Backend to Railway

1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub account
3. Select the `som23ya/Workwale` repository
4. Choose "Deploy from GitHub repo"
5. Set the following environment variables:
   - `DATABASE_URL`: Railway will provide PostgreSQL
   - `SECRET_KEY`: Generate a random string
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ENVIRONMENT`: production
   - `CORS_ORIGINS`: Will be updated after frontend deployment

### 2. Deploy Frontend to Vercel

1. Go to [Vercel.com](https://vercel.com)
2. Connect your GitHub account
3. Import the `som23ya/Workwale` repository
4. Set root directory to `frontend`
5. Set environment variable:
   - `NEXT_PUBLIC_API_URL`: Your Railway backend URL

### 3. Update CORS Origins

After frontend deployment, update the Railway backend environment:
- `CORS_ORIGINS`: Add your Vercel frontend URL

## Live URLs (Will be available after deployment)

- **Frontend**: https://workwale-frontend.vercel.app
- **Backend**: https://workwale-backend.railway.app
- **API Docs**: https://workwale-backend.railway.app/docs

## Required API Keys

To fully deploy the application, you'll need:

1. **OpenAI API Key** - For resume parsing and job matching
2. **Twilio Account** - For WhatsApp notifications (optional)
3. **SMTP Credentials** - For email notifications (optional)

You can deploy without the optional services for basic functionality.