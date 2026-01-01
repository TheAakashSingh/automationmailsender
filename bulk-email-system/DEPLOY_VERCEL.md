# 🚀 Deploy to Vercel - Complete Guide

## Quick Deploy (5 Steps)

### Step 1: Push to GitHub

```bash
cd bulk-email-system
git init
git add .
git commit -m "Ready for Vercel deployment"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bulk-email-automation.git
git push -u origin main
```

### Step 2: Import to Vercel

1. Go to [vercel.com](https://vercel.com) → Sign in
2. Click **"Add New..."** → **"Project"**
3. Click **"Import Git Repository"**
4. Select your repository
5. Vercel auto-detects Next.js ✅

### Step 3: Add Environment Variables

In Vercel project → **Settings** → **Environment Variables**, add:

**Production Environment:**
```
DATABASE_URL=mongodb+srv://automation_lead:automation_lead@cluster0.cvnkonw.mongodb.net/bulk-email-automation?retryWrites=true&w=majority
NEXTAUTH_URL=https://your-app-name.vercel.app
NEXTAUTH_SECRET=<generate-random-32-chars>
CRON_SECRET=<generate-random-32-chars>
NODE_ENV=production
```

**Generate Secrets:**
```bash
# Run these commands:
openssl rand -base64 32  # Copy for NEXTAUTH_SECRET
openssl rand -base64 32  # Copy for CRON_SECRET
```

### Step 4: Deploy

Click **"Deploy"** button. Wait 2-3 minutes for build.

### Step 5: Post-Deployment Setup

After deployment succeeds:

1. **Push Database Schema:**
   ```bash
   # From your local machine
   cd bulk-email-system
   npm run db:push
   ```

2. **Create Admin User:**
   ```bash
   node scripts/create-admin.js
   ```

3. **Verify Cron is Running:**
   - Vercel cron is auto-configured in `vercel.json`
   - Runs every 2 minutes automatically
   - Check Vercel logs to verify

## ✅ What's Already Configured

- ✅ **Webpack aliases** - Fixed module resolution (`@/lib/*`)
- ✅ **Prisma auto-generation** - Runs on `postinstall`
- ✅ **Vercel cron** - Auto-configured in `vercel.json`
- ✅ **TypeScript paths** - `baseUrl` and paths configured
- ✅ **Build script** - Includes Prisma generation

## 🔧 Configuration Files

### `next.config.js`
- Webpack alias for `@/` paths
- Works on Vercel build

### `vercel.json`
- Cron job configured (runs every 2 minutes)
- Framework preset: Next.js

### `package.json`
- `postinstall`: Auto-generates Prisma client
- `build`: Includes Prisma generation

## 📋 Environment Variables Checklist

Before deploying, make sure you have:

- [ ] `DATABASE_URL` - MongoDB connection string (with database name!)
- [ ] `NEXTAUTH_URL` - Your Vercel app URL
- [ ] `NEXTAUTH_SECRET` - Random 32+ character string
- [ ] `CRON_SECRET` - Random 32+ character string
- [ ] `NODE_ENV=production`

## 🎯 After Deployment

1. Visit: `https://your-app.vercel.app`
2. Login with admin credentials
3. Go to **SMTP** → Add your SMTP account
4. Go to **Leads** → Upload CSV
5. Go to **Templates** → Create or use pre-built templates
6. Go to **Campaigns** → Create and start campaign
7. Monitor in **Dashboard** and **Logs**

## 🐛 Troubleshooting

### Build Fails: "Can't resolve '@/lib/auth'"
✅ **FIXED** - Webpack alias configured in `next.config.js`

### Prisma Client Not Found
✅ **FIXED** - `postinstall` script auto-generates Prisma client

### Cron Not Running
- Check `vercel.json` has cron configuration
- Verify `CRON_SECRET` in environment variables
- Check Vercel function logs

### Database Connection Error
- Verify `DATABASE_URL` includes database name
- Check MongoDB Atlas allows `0.0.0.0/0` (all IPs)
- Verify credentials are correct

## 🎉 Success!

Once deployed, your bulk email automation system will be live on Vercel with:
- ✅ Automatic cron jobs (every 2 minutes)
- ✅ Serverless functions
- ✅ Auto-scaling
- ✅ Global CDN

**Your app URL:** `https://your-app-name.vercel.app`

Happy emailing! 📧

