# 🚀 Quick Railway Deployment Guide

## Task 25: Deploy Backend to Railway - Action Items

### ✅ COMPLETED
- Railway configuration files created
- Documentation written
- Code pushed to GitHub

### 📋 TO DO - Follow These Steps

#### 1. Create Railway Account (5 minutes)
```
1. Go to https://railway.app
2. Click "Login with GitHub"
3. Authorize Railway to access your repositories
```

#### 2. Create New Project (2 minutes)
```
1. Click "New Project" in Railway dashboard
2. Select "Deploy from GitHub repo"
3. Choose repository: "manideep-777/DPR-tools"
4. Select the repository
```

#### 3. Add PostgreSQL Database (1 minute)
```
1. In your Railway project, click "+ New"
2. Select "Database"
3. Choose "PostgreSQL"
4. Railway will provision it automatically
```

#### 4. Configure Backend Service (5 minutes)
```
1. Railway should auto-detect your Python app
2. If not, click "+ New" → "GitHub Repo" → Select your repo
3. Set Root Directory: backend
4. Railway will use railway.json configuration
```

#### 5. Set Environment Variables (3 minutes)
```
Go to your backend service → Variables → Add:

DATABASE_URL          → ${{Postgres.DATABASE_URL}}  (auto-reference)
GOOGLE_API_KEY        → AIzaSyDtfTgcyumyv9C7lxGspcr0czZnbFq8rpo  (your key)
ENV                   → production
PYTHON_ENV            → production
ALLOWED_ORIGINS       → http://localhost:3000  (add your Vercel URL later)
```

#### 6. Deploy! (Automatic)
```
Railway will automatically:
✅ Detect the push to main
✅ Build the application
✅ Run Prisma migrations
✅ Seed the database
✅ Start the FastAPI server
```

#### 7. Get Your URL (1 minute)
```
1. Go to your backend service in Railway
2. Click "Settings" → "Domains"
3. Railway provides: https://your-app.up.railway.app
4. Copy this URL - you'll need it for the frontend
```

#### 8. Test Deployment (2 minutes)
```bash
# Replace with your actual Railway URL
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/

# Expected response:
{
  "status": "healthy",
  "database": "connected"
}
```

#### 9. Update Frontend (if deployed)
```typescript
// In your frontend .env.local or Vercel environment variables
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app/api
```

#### 10. Update CORS (Important!)
```
Once you deploy frontend to Vercel:
1. Go to Railway → Backend Service → Variables
2. Update ALLOWED_ORIGINS:
   https://your-frontend.vercel.app,http://localhost:3000
3. Service will auto-redeploy
```

---

## 🎯 Success Checklist

- [ ] Railway account created
- [ ] GitHub connected to Railway
- [ ] PostgreSQL database added
- [ ] Backend service deployed
- [ ] Environment variables set
- [ ] Health check returns success
- [ ] Railway URL obtained
- [ ] API endpoints tested
- [ ] CORS configured
- [ ] Frontend updated with new API URL

---

## 📊 What Railway Gives You

✅ **Automatic Deployments**: Push to GitHub → Auto-deploy  
✅ **PostgreSQL Database**: Managed, backed up, secure  
✅ **HTTPS**: Automatic SSL certificates  
✅ **Logs**: Real-time application logs  
✅ **Metrics**: CPU, Memory, Network monitoring  
✅ **Scaling**: Easy horizontal scaling  
✅ **Custom Domains**: Add your own domain  

---

## 💰 Pricing

**Starter Plan**: $5/month
- 500 execution hours
- Enough for small to medium apps
- PostgreSQL included

**Pro Plan**: $20/month
- Unlimited execution hours
- Priority support
- Advanced features

---

## 🐛 Common Issues & Solutions

### Issue 1: Build Fails
**Solution**: Check Railway logs, ensure all dependencies in requirements.txt

### Issue 2: Database Connection Error
**Solution**: Verify DATABASE_URL is set to ${{Postgres.DATABASE_URL}}

### Issue 3: CORS Error from Frontend
**Solution**: Add frontend URL to ALLOWED_ORIGINS environment variable

### Issue 4: Port Binding Error
**Solution**: Already handled - main.py uses $PORT from Railway

---

## 📞 Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Your Backend Docs: See `README_RAILWAY.md` and `RAILWAY_DEPLOYMENT.md`

---

## 🎉 You're Ready!

All configuration is complete. Just follow steps 1-10 above and your backend will be live!

**Total Time**: ~20 minutes
**Difficulty**: Easy ⭐⭐☆☆☆

Good luck! 🚀
