# Render Deployment Guide for DPR Backend

Complete guide to deploy the FastAPI backend to Render with PostgreSQL database.

## 📋 Prerequisites

- GitHub account with this repository
- Render account (free tier available)
- Google Gemini API key

## 🚀 Quick Start (10 Steps)

### Step 1: Create Render Account

1. Go to https://render.com
2. Sign up using your GitHub account
3. Authorize Render to access your repositories

### Step 2: Create PostgreSQL Database

1. From Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure database:
   - **Name**: `dpr-database`
   - **Database**: `dpr_db`
   - **User**: `dpr_user`
   - **Region**: `Oregon (US West)` (or nearest to you)
   - **Plan**: `Free` (or `Starter` for production)
3. Click **"Create Database"**
4. Wait 2-3 minutes for database to provision
5. **IMPORTANT**: Copy the **Internal Database URL** (starts with `postgresql://`)

### Step 3: Create Web Service

1. From Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `manideep-777/DPR-tools`
3. Configure web service:
   - **Name**: `dpr-backend`
   - **Region**: `Oregon (US West)` (same as database)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `bash render-build.sh`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Click **"Advanced"** to expand advanced settings

### Step 4: Set Environment Variables

In the "Environment Variables" section, add:

| Key | Value | Notes |
|-----|-------|-------|
| `PYTHON_VERSION` | `3.11.0` | Python version |
| `DATABASE_URL` | *Internal Database URL from Step 2* | PostgreSQL connection |
| `GOOGLE_API_KEY` | *Your Google Gemini API key* | AI generation |
| `ENV` | `production` | Environment flag |
| `PYTHON_ENV` | `production` | Python environment |
| `ALLOWED_ORIGINS` | `http://localhost:3000,https://your-frontend-url.vercel.app` | CORS origins |

**How to add variables:**
1. Click **"Add Environment Variable"**
2. Enter Key and Value
3. Repeat for all variables

### Step 5: Configure Auto-Deploy

1. In **"Auto-Deploy"** section:
   - Enable **"Auto-Deploy"** toggle
   - Set to **"Yes"** for `main` branch
2. This enables automatic deployment on git push

### Step 6: Create Web Service

1. Select **"Free"** plan (or higher for production)
2. Click **"Create Web Service"**
3. Render will start building your application
4. Build process takes 5-10 minutes

### Step 7: Monitor Deployment

1. Watch the **"Logs"** tab for build progress
2. Look for these success messages:
   ```
   ✓ Installing Python dependencies...
   ✓ Generating Prisma Client...
   ✓ Running database migrations...
   ✓ Seeding database...
   ✓ Build process completed!
   ```
3. Once build completes, service will automatically start

### Step 8: Verify Deployment

1. Copy your Render URL: `https://dpr-backend.onrender.com`
2. Test endpoints:
   ```bash
   # Health check
   curl https://dpr-backend.onrender.com/

   # API root
   curl https://dpr-backend.onrender.com/api/
   ```
3. Expected response: `{"message": "DPR Preparation Tool API"}`

### Step 9: Update CORS Origins

1. Once frontend is deployed, update `ALLOWED_ORIGINS`:
   ```
   https://your-actual-frontend.vercel.app,http://localhost:3000
   ```
2. Go to Render Dashboard → Your service → "Environment"
3. Edit `ALLOWED_ORIGINS` variable
4. Service will automatically redeploy

### Step 10: Test API Endpoints

Test key endpoints:

```bash
# 1. Health check
curl https://dpr-backend.onrender.com/

# 2. Get schemes (requires authentication)
curl https://dpr-backend.onrender.com/api/schemes/all

# 3. User registration
curl -X POST https://dpr-backend.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}'
```

## 📁 Files Created for Render Deployment

### 1. `render.yaml` (Blueprint File)
Infrastructure-as-code configuration for Render. Defines:
- Web service configuration
- Database configuration
- Environment variables
- Auto-deploy settings

### 2. `render-build.sh` (Build Script)
Automated build script that:
- Installs Python dependencies
- Generates Prisma client
- Runs database migrations
- Seeds database with schemes

### 3. `requirements.txt` (Already exists)
Python dependencies to install

### 4. `.env.example` (Environment template)
Template showing all required environment variables

## 🔧 Environment Variables Reference

| Variable | Purpose | Example | Required |
|----------|---------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` | ✅ Yes |
| `GOOGLE_API_KEY` | Google Gemini API | `AIza...` | ✅ Yes |
| `ENV` | Environment mode | `production` | ✅ Yes |
| `PYTHON_ENV` | Python environment | `production` | ✅ Yes |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://frontend.vercel.app` | ✅ Yes |
| `PORT` | Server port | Auto-set by Render | 🔄 Auto |
| `PYTHON_VERSION` | Python version | `3.11.0` | ⚙️ Optional |

## 🆚 Render vs Railway Comparison

| Feature | Render | Railway |
|---------|--------|---------|
| **Free Tier** | ✅ 750 hours/month | ✅ $5 credit/month |
| **Database Free Tier** | ⚠️ 90-day limit | ✅ Included |
| **Build Time** | ~5-10 min | ~3-5 min |
| **Auto-Deploy** | ✅ Yes | ✅ Yes |
| **Custom Domains** | ✅ Free SSL | ✅ Free SSL |
| **Deployment Method** | Blueprint/Dashboard | Dashboard only |
| **Log Retention** | 7 days (free) | 2 days (free) |

## 🔄 Automatic Deployments

Once configured, deployments are automatic:

```bash
# Make changes to code
git add .
git commit -m "Update feature"
git push origin main

# Render automatically:
# 1. Detects push to main branch
# 2. Pulls latest code
# 3. Runs render-build.sh
# 4. Deploys new version
# 5. Zero-downtime deployment
```

## 🐛 Troubleshooting

### Build Fails: "Prisma not found"

**Problem**: Prisma CLI not installed
**Solution**: Check `requirements.txt` includes `prisma`:
```txt
prisma==0.15.0
```

### Database Connection Fails

**Problem**: Wrong DATABASE_URL format
**Solution**: 
1. Use **Internal Database URL** from Render dashboard
2. Format: `postgresql://user:password@hostname:5432/database`
3. Copy from: Database → "Info" → "Internal Database URL"

### Migration Fails: "No schema found"

**Problem**: Prisma schema not found
**Solution**: 
1. Verify `prisma/schema.prisma` exists in `backend/` directory
2. Check build logs for schema path errors

### Service Returns 503 Error

**Problem**: Application not starting
**Solution**:
1. Check logs: Dashboard → Service → "Logs"
2. Verify all environment variables are set
3. Ensure `PORT` is used in start command: `--port $PORT`

### CORS Errors in Frontend

**Problem**: Frontend can't access API
**Solution**: Update `ALLOWED_ORIGINS`:
```bash
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
```

### Free Tier Database Expires

**Problem**: Free PostgreSQL expires after 90 days
**Solution**: 
- Upgrade to Starter plan ($7/month)
- Or export data before expiry and create new database

## 💰 Pricing & Plans

### Web Service Plans

| Plan | Price | RAM | CPU | Features |
|------|-------|-----|-----|----------|
| Free | $0 | 512 MB | Shared | 750 hrs/mo, sleeps after 15 min |
| Starter | $7/mo | 512 MB | Shared | Always on, auto-scaling |
| Standard | $25/mo | 2 GB | 1 CPU | Faster builds, more resources |
| Pro | $85/mo | 4 GB | 2 CPU | High performance |

### Database Plans

| Plan | Price | Storage | Connections | Notes |
|------|-------|---------|-------------|-------|
| Free | $0 | 1 GB | 97 | **Expires in 90 days** |
| Starter | $7/mo | 1 GB | 97 | No expiration |
| Standard | $20/mo | 10 GB | 197 | Production-ready |

**Recommended for Production**: Starter Web Service + Starter Database = $14/month

## 🔒 Security Best Practices

1. **Never commit `.env` files** to git
2. **Use strong passwords** for database
3. **Rotate API keys** regularly
4. **Enable IP allowlist** for database (in production)
5. **Use HTTPS only** in production (automatic on Render)
6. **Keep dependencies updated**: `pip list --outdated`

## 📊 Monitoring & Logs

### View Logs
1. Dashboard → Your service → "Logs"
2. Live logs show real-time activity
3. Filter by severity: Info, Warning, Error

### Monitor Metrics
1. Dashboard → Your service → "Metrics"
2. View:
   - CPU usage
   - Memory usage
   - Request rate
   - Response times

### Set Up Alerts
1. Dashboard → Your service → "Settings" → "Notifications"
2. Configure:
   - Email notifications
   - Slack integration
   - Deploy notifications

## 🌐 Custom Domain Setup

1. Go to service → "Settings" → "Custom Domain"
2. Click "Add Custom Domain"
3. Enter your domain: `api.yourdomain.com`
4. Add CNAME record to your DNS:
   ```
   Type: CNAME
   Name: api
   Value: dpr-backend.onrender.com
   ```
5. Wait for DNS propagation (5-60 minutes)
6. Render automatically provisions SSL certificate

## 🔄 Rollback Deployment

If deployment fails or has issues:

1. Dashboard → Service → "Events"
2. Find previous successful deployment
3. Click "Redeploy" on that event
4. Service rolls back to previous version

## 📝 Next Steps

1. ✅ **Deploy Backend** (this guide)
2. ⏭️ **Deploy Frontend** to Vercel
3. 🔗 **Update Frontend** API URL to Render URL
4. 🧪 **Test End-to-End** integration
5. 🚀 **Launch to Production**

## 🆘 Support Resources

- **Render Docs**: https://render.com/docs
- **Render Community**: https://community.render.com
- **Status Page**: https://status.render.com
- **Support Email**: support@render.com

## 📌 Success Checklist

Before marking deployment complete:

- [ ] Render account created and verified
- [ ] GitHub repository connected
- [ ] PostgreSQL database created and running
- [ ] All environment variables set correctly
- [ ] Web service created and deployed successfully
- [ ] Build logs show no errors
- [ ] Health check endpoint returns 200 OK
- [ ] Database migrations completed
- [ ] Test user registration works
- [ ] CORS configured for frontend URL
- [ ] Auto-deploy enabled for main branch
- [ ] Render URL documented for frontend team

## 🎯 Production Checklist

Additional steps for production launch:

- [ ] Upgrade to paid plans (Starter minimum)
- [ ] Set up custom domain
- [ ] Configure environment-specific secrets
- [ ] Enable database backups
- [ ] Set up monitoring alerts
- [ ] Configure log retention
- [ ] Review security settings
- [ ] Load test API endpoints
- [ ] Document API URL for frontend
- [ ] Create deployment runbook

---

**Deployment URL**: `https://dpr-backend.onrender.com` (replace with your actual URL)

**Database URL**: Available in Render dashboard (Internal URL for backend)

**Need Help?** Check logs first, then refer to troubleshooting section above.
