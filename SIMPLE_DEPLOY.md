# 🚀 Simple WorkWale.ai Deployment Guide

## Option 1: Manual Deployment (Recommended - Most Reliable)

### Step 1: Deploy Backend First

1. **Go to [render.com](https://render.com)** and sign in with GitHub
2. **Click "New +" → "Web Service"**
3. **Connect your repository**: `som23ya/Workwale`
4. **Configure the backend service**:
   ```
   Name: workwale-backend
   Root Directory: backend
   Environment: Python
   Region: Ohio (US East)
   Branch: main
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   Instance Type: Free
   ```

5. **Add Environment Variables**:
   ```
   DATABASE_URL: (will add after creating database)
   SECRET_KEY: (click "Generate" for random value)
   ENVIRONMENT: production
   DEBUG: false
   CORS_ORIGINS: https://workwale-frontend.onrender.com
   ```

6. **Click "Create Web Service"** (don't deploy yet)

### Step 2: Create PostgreSQL Database

1. **Click "New +" → "PostgreSQL"**
2. **Configure database**:
   ```
   Name: workwale-db
   Database: workwale
   User: workwale_user
   Region: Ohio (US East) 
   Instance Type: Free
   ```
3. **Click "Create Database"**
4. **Wait 2-3 minutes** for database to be ready

### Step 3: Connect Database to Backend

1. **Go to your database** → Click "Connect" → Copy the "Internal Connection String"
2. **Go to your backend service** → "Environment" tab
3. **Update DATABASE_URL** with the connection string you copied
4. **Click "Save Changes"**

### Step 4: Deploy Backend

1. **In your backend service** → Click "Manual Deploy" → "Deploy Latest Commit"
2. **Wait 10-15 minutes** for build to complete
3. **Check logs** to ensure deployment succeeds
4. **Test**: Visit `https://workwale-backend.onrender.com/health`

### Step 5: Deploy Frontend

1. **Click "New +" → "Web Service"**
2. **Connect same repository**: `som23ya/Workwale`
3. **Configure frontend service**:
   ```
   Name: workwale-frontend
   Root Directory: frontend
   Environment: Node.js
   Region: Ohio (US East)
   Branch: main
   Build Command: npm install && npm run build
   Start Command: npm start
   Instance Type: Free
   ```

4. **Add Environment Variables**:
   ```
   NEXT_PUBLIC_API_URL: https://workwale-backend.onrender.com
   NODE_ENV: production
   ```

5. **Click "Create Web Service"**
6. **Wait 10-15 minutes** for build to complete

## Option 2: One-Click Deploy (If render.yaml works)

Click this button after fixing the render.yaml:
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/som23ya/Workwale)

## 🎯 Final URLs

After deployment:
- **Frontend**: https://workwale-frontend.onrender.com
- **Backend**: https://workwale-backend.onrender.com
- **API Docs**: https://workwale-backend.onrender.com/docs

## ⚠️ Important Notes

1. **Free tier limitations**: 
   - Apps sleep after 15 minutes of inactivity
   - Cold start takes 30-60 seconds
   - Database expires after 90 days

2. **Build times**: 
   - Backend: ~10-15 minutes
   - Frontend: ~10-15 minutes
   - Total: ~20-30 minutes

3. **Troubleshooting**:
   - Check build logs if deployment fails
   - Ensure all environment variables are set
   - Database must be ready before backend deployment

## 🔧 Optional Enhancements

Add these environment variables to enable full AI features:

```bash
# Backend service environment variables
OPENAI_API_KEY=your_openai_key
TWILIO_ACCOUNT_SID=your_twilio_sid  
TWILIO_AUTH_TOKEN=your_twilio_token
SMTP_USERNAME=your_email@domain.com
SMTP_PASSWORD=your_email_password
```

## ✅ Success Indicators

Your deployment is successful when:
- ✅ Backend health check returns: `{"status": "healthy"}`
- ✅ Frontend loads the WorkWale.ai homepage
- ✅ API docs are accessible at `/docs` endpoint
- ✅ No error messages in service logs