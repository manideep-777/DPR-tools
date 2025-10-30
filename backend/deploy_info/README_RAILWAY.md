# MSME DPR Generator Backend - Railway Deployment

This document provides step-by-step instructions for deploying the MSME DPR Generator backend to Railway.

## 📋 Prerequisites

- ✅ GitHub repository with your code
- ✅ Railway account ([Sign up here](https://railway.app))
- ✅ Google Gemini API key

## 🚀 Deployment Steps

### Step 1: Create Railway Project

1. Visit [Railway.app](https://railway.app) and sign in with GitHub
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your repository: `DPR-tools`

### Step 2: Add PostgreSQL Database

1. In your Railway project dashboard, click **"New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will provision a PostgreSQL database automatically
4. Note the connection details (automatically available as `DATABASE_URL`)

### Step 3: Configure Environment Variables

In the Railway dashboard, go to your backend service → **Variables** and add:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}  # Auto-filled if using Railway's Postgres
GOOGLE_API_KEY=your_actual_api_key_here
ENV=production
PYTHON_ENV=production
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

### Step 4: Configure Build Settings

Railway auto-detects Python apps, but you can customize:

1. Go to **Settings** → **Build**
2. Set **Root Directory**: `backend` (if needed)
3. **Build Command**: Automatically uses `railway-build.sh`
4. **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 5: Deploy

Railway automatically deploys on push to `main` branch:

```bash
git add .
git commit -m "Configure Railway deployment"
git push origin main
```

### Step 6: Verify Deployment

Once deployed, Railway provides a public URL. Test it:

```bash
# Replace with your Railway URL
curl https://your-app.up.railway.app/health
curl https://your-app.up.railway.app/
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "prisma": "initialized"
}
```

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `railway.json` | Railway build and deploy configuration |
| `Procfile` | Process type and start command |
| `railway-build.sh` | Build script for Prisma and migrations |
| `runtime.txt` | Python version specification |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment variables template |

## 🌍 Environment Variables Explained

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Auto-set by Railway Postgres |
| `GOOGLE_API_KEY` | Google Gemini API key for AI generation | `AIzaSy...` |
| `ENV` | Environment mode (affects logging) | `production` |
| `PYTHON_ENV` | Python environment identifier | `production` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `https://app.vercel.app` |
| `PORT` | Server port (auto-set by Railway) | `8000` |

## 📊 Monitoring

### View Logs

1. Go to your Railway project
2. Click on your backend service
3. Navigate to **"Deployments"** → **"Logs"**

### Monitor Usage

- **Metrics**: View CPU, Memory, and Network usage in Railway dashboard
- **Deployments**: Track deployment history and status
- **Database**: Monitor database metrics in the Postgres service

## 🔄 Automatic Deployments

Railway automatically deploys when you:
- Push to the `main` branch
- Merge a pull request
- Manually trigger a deployment in the dashboard

### Disable Auto-Deploy

If needed, you can disable auto-deploy:
1. Go to **Settings** → **Service**
2. Toggle **"Auto-Deploy"** off

## 🛠️ Troubleshooting

### Build Fails

**Symptom**: Deployment fails during build phase

**Solutions**:
1. Check build logs in Railway dashboard
2. Verify all dependencies in `requirements.txt`
3. Ensure Prisma schema is valid: `npx prisma validate`

### Database Connection Fails

**Symptom**: `DATABASE_URL` connection errors

**Solutions**:
1. Verify `DATABASE_URL` is correctly set
2. Check Railway Postgres is running
3. Run migrations manually: `npx prisma migrate deploy`

### CORS Errors

**Symptom**: Frontend can't connect to backend

**Solutions**:
1. Add frontend URL to `ALLOWED_ORIGINS`
2. Ensure URL includes protocol (https://)
3. Restart service after changing variables

### Port Binding Issues

**Symptom**: Server fails to start with port errors

**Solutions**:
1. Ensure using `$PORT` environment variable
2. Check `main.py` uses: `port = int(os.getenv("PORT", 8000))`
3. Verify start command in `Procfile`

## 💰 Pricing

Railway pricing (as of 2024):

- **Hobby Plan**: $5/month
  - 500 hours execution time
  - $0.01/hour after limit
  
- **Pro Plan**: $20/month
  - Unlimited execution time
  - Priority support

**Database Storage**: Included in plan

## 🔒 Security Best Practices

- ✅ Never commit `.env` files
- ✅ Use Railway's environment variables for all secrets
- ✅ Enable HTTPS (automatic with Railway)
- ✅ Regularly update dependencies
- ✅ Monitor logs for unusual activity
- ✅ Use strong database passwords
- ✅ Limit CORS origins to known domains

## 📝 Database Migrations

### Apply Migrations

Migrations run automatically during deployment via `railway-build.sh`.

### Manual Migration

If needed, run migrations manually:

```bash
# In Railway dashboard → Service → Shell
npx prisma migrate deploy
```

### Create New Migration (Locally)

```bash
cd backend
npx prisma migrate dev --name your_migration_name
git add prisma/migrations
git commit -m "Add migration: your_migration_name"
git push
```

## 🌐 Custom Domain

### Add Custom Domain

1. Go to Railway dashboard → Your service
2. Click **Settings** → **Domains**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `api.yourdomain.com`)
5. Update DNS records as instructed:
   - Add CNAME record pointing to Railway's URL

### Update CORS

After adding custom domain, update `ALLOWED_ORIGINS`:

```bash
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 📞 Support & Resources

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app
- **Prisma Docs**: https://www.prisma.io/docs

## ✅ Deployment Checklist

Before deploying, ensure:

- [ ] All environment variables are set
- [ ] PostgreSQL database is provisioned
- [ ] `requirements.txt` is up to date
- [ ] Prisma schema is valid
- [ ] Frontend URL is in `ALLOWED_ORIGINS`
- [ ] Google API key is valid
- [ ] `.env` is in `.gitignore`
- [ ] Test locally first
- [ ] Database migrations are ready
- [ ] Monitoring is configured

## 🎉 Post-Deployment

After successful deployment:

1. ✅ Test all API endpoints
2. ✅ Verify database connection
3. ✅ Check CORS configuration
4. ✅ Update frontend with production API URL
5. ✅ Set up monitoring alerts
6. ✅ Document your Railway URL
7. ✅ Configure custom domain (optional)

---

**Deployment Status**: ✅ Ready for Production!

For additional help, refer to the detailed [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md) guide.
