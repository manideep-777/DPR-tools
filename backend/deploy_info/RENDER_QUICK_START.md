# Render Deployment Quick Start

10-step guide to deploy your FastAPI backend to Render.

## 🎯 Quick Steps

### 1. Create Account
- Go to https://render.com
- Sign up with GitHub
- Authorize repository access

### 2. Create Database
- Click "New +" → "PostgreSQL"
- Name: `dpr-database`
- Region: Oregon (US West)
- Plan: Free
- Copy **Internal Database URL**

### 3. Create Web Service
- Click "New +" → "Web Service"
- Select repository: `DPR-tools`
- Root directory: `backend`
- Runtime: Python 3

### 4. Configure Build
- Build Command: `bash render-build.sh`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 5. Set Environment Variables

Add these in the dashboard:

```bash
PYTHON_VERSION=3.11.0
DATABASE_URL=<Internal Database URL from step 2>
GOOGLE_API_KEY=<Your Gemini API key>
ENV=production
PYTHON_ENV=production
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-url.vercel.app
```

### 6. Deploy
- Plan: Free (or higher)
- Click "Create Web Service"
- Wait 5-10 minutes for build

### 7. Verify
```bash
curl https://dpr-backend.onrender.com/
```

### 8. Update CORS
After frontend deployment:
- Update `ALLOWED_ORIGINS` with real frontend URL
- Service auto-redeploys

### 9. Test Endpoints
```bash
# Health check
curl https://dpr-backend.onrender.com/

# Register user
curl -X POST https://dpr-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"pass123","name":"Test"}'
```

### 10. Enable Auto-Deploy
- Enable "Auto-Deploy" for `main` branch
- Now `git push` automatically deploys

## 📋 Files Needed

All files already created in your repository:

- ✅ `render.yaml` - Infrastructure config
- ✅ `render-build.sh` - Build script
- ✅ `requirements.txt` - Python dependencies
- ✅ `prisma/schema.prisma` - Database schema
- ✅ `.env.example` - Environment template

## 🆚 Render vs Railway

| Feature | Render | Railway |
|---------|--------|---------|
| Free Tier | 750 hrs/month | $5 credit/month |
| Database Free | 90 days | Unlimited |
| Setup Method | Blueprint or UI | UI only |
| Build Time | ~8 minutes | ~4 minutes |

## 🔧 Key Differences from Railway

1. **Database Free Tier**: 90-day expiration (upgrade to $7/mo for permanent)
2. **Blueprint File**: `render.yaml` instead of `railway.json`
3. **Build Command**: Specified in dashboard, not Procfile
4. **Environment Variables**: Set in dashboard under "Environment"
5. **Internal URLs**: Database uses internal URL for service-to-service

## 💰 Costs

### Recommended Setup
- **Free Tier**: $0 (limited time, database expires)
- **Production**: $14/month (Starter Web + Starter DB)

## 🐛 Common Issues

### Build fails
**Solution**: Check `render-build.sh` has execute permissions:
```bash
git add render-build.sh
git update-index --chmod=+x render-build.sh
git commit -m "Make render-build.sh executable"
git push
```

### Database connection fails
**Solution**: Use **Internal Database URL** from Render dashboard, not External URL

### Free database expired
**Solution**: Upgrade to Starter plan ($7/month) or create new free database

## ✅ Success Checklist

- [ ] Account created
- [ ] Database provisioned (Internal URL copied)
- [ ] Web service created
- [ ] Environment variables set
- [ ] Build completed successfully
- [ ] Health check returns 200
- [ ] Auto-deploy enabled

## 📌 Your URLs

After deployment, you'll have:

- **Backend API**: `https://dpr-backend.onrender.com`
- **Database**: Internal URL (for backend use only)
- **Dashboard**: `https://dashboard.render.com`

## 🚀 Deploy Now

Ready to deploy? Follow the 10 steps above!

Full guide: See `RENDER_DEPLOYMENT.md` for detailed instructions.

---

**Next**: Deploy frontend to Vercel and connect to this backend URL.
