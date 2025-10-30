# Railway Deployment Guide for MSME DPR Backend

## Prerequisites
- GitHub repository with your backend code
- Railway account (sign up at https://railway.app)
- PostgreSQL database credentials

## Step-by-Step Deployment

### 1. Create a New Railway Project

1. Go to [Railway](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account if not already connected
5. Select your repository (DPR-tools)

### 2. Configure the Service

1. Railway will automatically detect your Python application
2. Set the root directory to `backend` if Railway doesn't auto-detect it
3. Railway will use the `railway.json` configuration file

### 3. Set Environment Variables

In the Railway dashboard, add the following environment variables:

**Required Variables:**

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database

# Google API Key
GOOGLE_API_KEY=your_google_api_key_here

# Environment
ENV=production
PYTHON_ENV=production

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=https://your-frontend-url.vercel.app,https://your-custom-domain.com

# Port (Railway sets this automatically)
PORT=8000
```

### 4. Add PostgreSQL Database

**Option 1: Use Railway's PostgreSQL (Recommended)**

1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL database
4. Copy the `DATABASE_URL` from the database service
5. Add it as an environment variable to your backend service

**Option 2: Use External PostgreSQL**

If you have an existing PostgreSQL database (e.g., from Render, Supabase, or AWS):
- Simply add the `DATABASE_URL` as an environment variable

### 5. Deploy

1. Railway will automatically deploy when you push to your GitHub repository
2. Monitor the build logs in the Railway dashboard
3. The build process will:
   - Install dependencies from `requirements.txt`
   - Generate Prisma client
   - Run database migrations
   - Seed the database
   - Start the FastAPI server

### 6. Verify Deployment

Once deployed, Railway will provide you with a public URL (e.g., `https://your-app.up.railway.app`)

Test the deployment:
```bash
# Health check
curl https://your-app.up.railway.app/health

# API root
curl https://your-app.up.railway.app/
```

### 7. Custom Domain (Optional)

1. In Railway dashboard, go to your service settings
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update your DNS records as instructed by Railway

### 8. Update Frontend Configuration

Update your frontend's API endpoint to use the Railway URL:

```typescript
// In your Next.js frontend
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://your-app.up.railway.app/api';
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `GOOGLE_API_KEY` | Google Gemini API key | `AIzaSy...` |
| `ENV` | Environment mode | `production` |
| `PYTHON_ENV` | Python environment | `production` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://app.vercel.app` |
| `PORT` | Server port (auto-set by Railway) | `8000` |

## Automatic Deployments

Railway automatically deploys when you push to your main branch:

```bash
git add .
git commit -m "Update backend"
git push origin main
```

## Monitoring and Logs

1. View logs in Railway dashboard → Your Service → Logs
2. Monitor metrics in the Railway dashboard
3. Set up alerts for errors or downtime

## Troubleshooting

### Build Failures

If the build fails:
1. Check the build logs in Railway dashboard
2. Verify `requirements.txt` is up to date
3. Ensure all dependencies are compatible

### Database Connection Issues

If database connection fails:
1. Verify `DATABASE_URL` is correct
2. Check database is accessible
3. Ensure Prisma migrations have run

### CORS Errors

If you get CORS errors:
1. Add your frontend URL to `ALLOWED_ORIGINS`
2. Ensure the URL includes the protocol (https://)
3. Restart the service after updating environment variables

## Cost Optimization

Railway offers:
- **Starter Plan**: $5/month with 500 hours
- **Developer Plan**: $20/month with unlimited hours

To optimize costs:
1. Use Railway's PostgreSQL (included in plans)
2. Monitor your usage in the dashboard
3. Scale down resources during low-traffic periods

## Security Best Practices

1. ✅ Never commit `.env` files
2. ✅ Use Railway's environment variables for secrets
3. ✅ Enable HTTPS (automatic with Railway)
4. ✅ Regularly update dependencies
5. ✅ Monitor logs for security issues

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Status: https://status.railway.app

---

## Quick Deployment Checklist

- [ ] Create Railway account
- [ ] Connect GitHub repository
- [ ] Add PostgreSQL database
- [ ] Set all environment variables
- [ ] Verify build succeeds
- [ ] Test API endpoints
- [ ] Update frontend API URL
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring

**Deployment Status**: ✅ Ready to Deploy!
