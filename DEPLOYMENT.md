# 🚀 Deployment Guide

This guide will help you deploy your Instagram Bot to **Render** (backend) and **Vercel** (frontend) for free!

## 📋 Prerequisites

- GitHub account
- Render account (free)
- Vercel account (free)
- Your Instagram Bot code

## 🎯 Deployment Overview

- **Backend (API)**: Deploy to Render
- **Frontend (Web UI)**: Deploy to Vercel
- **Total Cost**: $0 (completely free!)

---

## 🔧 Step 1: Deploy Backend to Render

### 1.1 Prepare Your Repository

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/instagram-bot.git
   git push -u origin main
   ```

### 1.2 Deploy to Render

1. **Go to [Render.com](https://render.com)**
2. **Sign up/Login** with your GitHub account
3. **Click "New +"** → **"Web Service"**
4. **Connect your GitHub repository**
5. **Configure the service:**
   - **Name**: `instagram-bot-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`

6. **Click "Create Web Service"**
7. **Wait for deployment** (5-10 minutes)
8. **Copy your service URL** (e.g., `https://instagram-bot-backend.onrender.com`)

### 1.3 Update Frontend Configuration

1. **Open `frontend/script.js`**
2. **Replace the API_BASE_URL:**
   ```javascript
   const API_BASE_URL = 'https://your-actual-render-url.onrender.com';
   ```
3. **Save the file**

---

## 🌐 Step 2: Deploy Frontend to Vercel

### 2.1 Prepare Frontend

1. **Navigate to the frontend folder:**
   ```bash
   cd frontend
   ```

2. **Initialize git (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Frontend deployment"
   ```

### 2.2 Deploy to Vercel

#### Option A: Using Vercel CLI (Recommended)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy from frontend folder:**
   ```bash
   cd frontend
   vercel
   ```

4. **Follow the prompts:**
   - **Set up and deploy?** → `Y`
   - **Which scope?** → Choose your account
   - **Link to existing project?** → `N`
   - **What's your project's name?** → `instagram-bot-frontend`
   - **In which directory is your code located?** → `./`

5. **Copy your deployment URL** (e.g., `https://instagram-bot-frontend.vercel.app`)

#### Option B: Using Vercel Dashboard

1. **Go to [Vercel.com](https://vercel.com)**
2. **Sign up/Login** with your GitHub account
3. **Click "New Project"**
4. **Import your GitHub repository**
5. **Configure the project:**
   - **Framework Preset**: `Other`
   - **Root Directory**: `frontend`
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty

6. **Click "Deploy"**
7. **Wait for deployment** (2-3 minutes)

---

## 🔗 Step 3: Connect Frontend to Backend

### 3.1 Update Frontend API URL

1. **Open your deployed frontend** (Vercel URL)
2. **Open browser developer tools** (F12)
3. **Check the console for errors**
4. **If you see CORS errors**, update the backend CORS settings

### 3.2 Update Backend CORS (if needed)

1. **Go to your Render dashboard**
2. **Open your service**
3. **Go to "Environment" tab**
4. **Add environment variable:**
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://your-vercel-url.vercel.app`

5. **Update `backend.py` CORS settings:**
   ```python
   allow_origins=[
       "https://your-vercel-url.vercel.app",
       "https://*.vercel.app",
       "https://*.onrender.com",
   ]
   ```

6. **Redeploy** by pushing changes to GitHub

---

## ✅ Step 4: Test Your Deployment

### 4.1 Test Backend

1. **Visit your Render URL + `/api/health`**
   - Example: `https://instagram-bot-backend.onrender.com/api/health`
   - Should return: `{"status": "healthy", "timestamp": "..."}`

### 4.2 Test Frontend

1. **Visit your Vercel URL**
2. **Try logging in** with your Instagram credentials
3. **Test sending messages** to a few usernames
4. **Check if everything works** as expected

---

## 🛠️ Troubleshooting

### Common Issues

#### Backend Issues

1. **"Service Unavailable" Error:**
   - Check if your service is running on Render
   - Look at the logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`

2. **CORS Errors:**
   - Update CORS settings in `backend.py`
   - Add your Vercel URL to allowed origins
   - Redeploy the backend

3. **Instagram Login Fails:**
   - Check if 2FA is disabled on your Instagram account
   - Try logging in manually on Instagram first
   - Check the logs for specific error messages

#### Frontend Issues

1. **"Cannot connect to backend":**
   - Verify the API_BASE_URL in `frontend/script.js`
   - Check if your backend is running
   - Test the backend URL directly

2. **Styling Issues:**
   - Ensure all CSS files are properly linked
   - Check if Font Awesome and Google Fonts are loading
   - Clear browser cache

### Debug Steps

1. **Check Render logs:**
   - Go to Render dashboard → Your service → Logs
   - Look for error messages

2. **Check Vercel logs:**
   - Go to Vercel dashboard → Your project → Functions
   - Check deployment logs

3. **Test API endpoints:**
   - Use Postman or curl to test backend endpoints
   - Check if CORS headers are present

---

## 🔒 Security Considerations

### Production Security

1. **Update CORS settings** to only allow your specific domains
2. **Add rate limiting** to prevent abuse
3. **Use environment variables** for sensitive data
4. **Monitor usage** and set up alerts

### Environment Variables

Add these to your Render service:

- `FRONTEND_URL`: Your Vercel frontend URL
- `LOG_LEVEL`: `INFO` or `DEBUG`
- `MAX_MESSAGES_PER_HOUR`: `50` (or your preferred limit)

---

## 📊 Monitoring

### Render Monitoring

1. **Go to Render dashboard**
2. **Click on your service**
3. **Check "Metrics" tab** for:
   - CPU usage
   - Memory usage
   - Response times
   - Error rates

### Vercel Monitoring

1. **Go to Vercel dashboard**
2. **Click on your project**
3. **Check "Analytics" tab** for:
   - Page views
   - Performance metrics
   - Error rates

---

## 🎉 Success!

Once deployed, you'll have:

- ✅ **Backend API** running on Render (free)
- ✅ **Frontend UI** running on Vercel (free)
- ✅ **Full functionality** accessible from anywhere
- ✅ **Mobile-friendly** interface
- ✅ **Real-time** status updates

### Your URLs:
- **Frontend**: `https://your-project.vercel.app`
- **Backend**: `https://your-service.onrender.com`
- **API Docs**: `https://your-service.onrender.com/docs`

---

## 🔄 Updates and Maintenance

### Updating the Application

1. **Make changes** to your code
2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update message"
   git push origin main
   ```
3. **Both services will auto-deploy** (if connected to GitHub)

### Monitoring Usage

- **Render Free Plan**: 750 hours/month
- **Vercel Free Plan**: Unlimited static hosting
- **Monitor usage** to avoid hitting limits

---

## 💡 Tips

1. **Test locally first** before deploying
2. **Use environment variables** for configuration
3. **Monitor logs** regularly
4. **Keep dependencies updated**
5. **Backup your code** regularly

---

## 🆘 Support

If you encounter issues:

1. **Check the logs** in both Render and Vercel
2. **Test API endpoints** directly
3. **Verify CORS settings**
4. **Check Instagram account status**
5. **Review this guide** for common solutions

---

**Happy Deploying! 🚀**
