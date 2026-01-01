# Vercel Deployment Guide

## Quick Deploy to Vercel

### Option 1: Deploy via Vercel Dashboard

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will auto-detect Next.js

3. **Configure Environment Variables**
   In Vercel project settings → Environment Variables, add:
   
   ```
   DATABASE_URL=mongodb+srv://user:pass@cluster.net/database?retryWrites=true&w=majority
   NEXTAUTH_URL=https://your-app.vercel.app
   NEXTAUTH_SECRET=your-random-secret-here
   CRON_SECRET=another-random-secret
   NODE_ENV=production
   ```

4. **Build Settings**
   - Framework Preset: Next.js
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `.next` (auto-detected)
   - Install Command: `npm install` (auto-detected)

5. **Deploy**
   - Click "Deploy"
   - Wait for build to complete

### Option 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd bulk-email-system
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? bulk-email-automation
# - Directory? ./
# - Override settings? No

# Add environment variables
vercel env add DATABASE_URL
vercel env add NEXTAUTH_URL
vercel env add NEXTAUTH_SECRET
vercel env add CRON_SECRET

# Redeploy with env vars
vercel --prod
```

## Required Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

### Production Environment

```
DATABASE_URL=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/bulk-email-automation?retryWrites=true&w=majority
NEXTAUTH_URL=https://your-app.vercel.app
NEXTAUTH_SECRET=<generate-random-32-char-string>
CRON_SECRET=<generate-random-32-char-string>
NODE_ENV=production
```

### Generate Secrets

```bash
# Generate NEXTAUTH_SECRET
openssl rand -base64 32

# Generate CRON_SECRET
openssl rand -base64 32
```

## Post-Deployment Setup

### 1. Push Database Schema

After deployment, run:
```bash
# From your local machine
cd bulk-email-system
npm run db:push
```

Or use Vercel CLI:
```bash
vercel env pull .env.local
npm run db:push
```

### 2. Create Admin User

Run locally (connects to your production DB):
```bash
node scripts/create-admin.js
```

### 3. Setup Cron Job

The system needs a cron job to process emails. Options:

**Option A: Vercel Cron (Recommended)**
Create `vercel.json` with cron configuration (already included):
```json
{
  "crons": [{
    "path": "/api/cron/process-queue",
    "schedule": "*/2 * * * *"
  }]
}
```

**Option B: External Cron Service**
- Use [cron-job.org](https://cron-job.org) or similar
- URL: `https://your-app.vercel.app/api/cron/process-queue`
- Method: GET
- Headers: `Authorization: Bearer YOUR_CRON_SECRET`
- Frequency: Every 1-2 minutes

**Option C: GitHub Actions**
Create `.github/workflows/cron.yml`:
```yaml
name: Process Email Queue
on:
  schedule:
    - cron: '*/2 * * * *'  # Every 2 minutes
jobs:
  cron:
    runs-on: ubuntu-latest
    steps:
      - name: Call API
        run: |
          curl -X GET \
            -H "Authorization: Bearer ${{ secrets.CRON_SECRET }}" \
            https://your-app.vercel.app/api/cron/process-queue
```

## Troubleshooting

### Build Fails with Module Resolution Errors

✅ **Fixed**: Added webpack alias in `next.config.js` and `baseUrl` in `tsconfig.json`

### Database Connection Fails

- Verify `DATABASE_URL` includes database name
- Check MongoDB Atlas IP whitelist (add `0.0.0.0/0` for Vercel)
- Verify credentials are correct

### Cron Job Not Working

- Check `CRON_SECRET` matches in Vercel env vars
- Verify cron endpoint is accessible
- Check Vercel function logs

### Prisma Client Not Generated

✅ **Fixed**: Added `postinstall` script to auto-generate Prisma client

## Vercel-Specific Notes

1. **Serverless Functions**: All API routes run as serverless functions
2. **Cold Starts**: First request may be slow (~1-2 seconds)
3. **Function Timeout**: Default 10 seconds (upgrade for longer)
4. **Environment Variables**: Must be set in Vercel dashboard
5. **Database**: Use MongoDB Atlas (cloud) - local MongoDB won't work

## Next Steps After Deployment

1. ✅ Visit your Vercel URL
2. ✅ Login with admin credentials
3. ✅ Configure SMTP account
4. ✅ Upload leads CSV
5. ✅ Create email templates
6. ✅ Start your first campaign
7. ✅ Setup cron job for email processing

Your app is now live! 🚀

