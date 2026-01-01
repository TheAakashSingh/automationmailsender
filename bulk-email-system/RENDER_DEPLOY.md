# Deploy to Render - Step by Step Guide

## 🚀 Quick Deploy (5 Minutes)

### Step 1: Prepare Your Code

Make sure all files are committed:
```bash
cd bulk-email-system
git add .
git commit -m "Add Render deployment config"
git push
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Sign up or log in
3. Connect your GitHub account

### Step 3: Create New Blueprint

1. Click **"New +"** → **"Blueprint"**
2. Connect your GitHub repository: `TheAakashSingh/automationmailsender`
3. Select branch: **`main`**
4. Render will detect `render.yaml` automatically
5. Click **"Apply"**

### Step 4: Configure Environment Variables

After the blueprint is created, go to your service settings and add:

```
DATABASE_URL=mongodb+srv://automation_lead:automation_lead@cluster0.cvnkonw.mongodb.net/bulk-email-automation?retryWrites=true&w=majority
NEXTAUTH_URL=https://your-app-name.onrender.com
NEXTAUTH_SECRET=<generate-random-string>
CRON_SECRET=<generate-random-string>
NODE_ENV=production
```

**Generate secrets:**
```bash
# On Windows PowerShell:
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))

# Or use online tool: https://generate-secret.vercel.app/32
```

### Step 5: Deploy

1. Render will automatically start building
2. Wait for build to complete (5-10 minutes)
3. Your app will be live at: `https://your-app-name.onrender.com`

### Step 6: Setup Database

After deployment, run locally to push schema:
```bash
# Set DATABASE_URL in your local .env
npm run db:push
```

### Step 7: Create Admin User

```bash
node scripts/create-admin.js
# Enter email, password, name
```

### Step 8: Process Email Queue

**Option A: Manual Processing (Recommended)**
- Go to Dashboard
- Click **"Process Email Queue Now"** button
- Click every 1-2 minutes while campaigns are running

**Option B: External Cron Service (Free)**
- Use [cron-job.org](https://cron-job.org) or [EasyCron](https://www.easycron.com)
- URL: `https://your-app-name.onrender.com/api/cron/process-queue`
- Method: GET
- Headers: `Authorization: Bearer YOUR_CRON_SECRET`
- Schedule: Every 1-2 minutes

## ✅ Verification

1. Visit your Render URL
2. Login with admin credentials
3. Check dashboard loads
4. Test SMTP configuration
5. Verify queue processing works

## 🔧 Troubleshooting

### Build Errors

**Module Resolution Errors:**
- ✅ Already fixed in `next.config.js`
- ✅ `tsconfig.json` configured correctly
- ✅ Webpack alias set properly

**Prisma Errors:**
- Make sure `DATABASE_URL` is set correctly
- Run `npm run db:push` locally after deployment

### Runtime Errors

**Database Connection:**
- Verify `DATABASE_URL` includes database name
- Check MongoDB Atlas allows connections from anywhere (`0.0.0.0/0`)

**Authentication:**
- Verify `NEXTAUTH_URL` matches your Render URL
- Check `NEXTAUTH_SECRET` is set

### Performance

**Slow Cold Starts:**
- Render free tier has cold starts (30-60 seconds)
- Consider upgrading to Starter plan ($7/month) for faster starts

**Build Timeouts:**
- Free tier: 10 minutes max
- If build takes longer, optimize dependencies or upgrade plan

## 📝 Important Notes

- **MongoDB**: Must use MongoDB Atlas (cloud), not local
- **SMTP**: Configure in dashboard after deployment
- **Cron**: Use manual button or external cron service (Render doesn't support cron on free tier)
- **Secrets**: Never commit `.env` file to Git
- **Auto-Deploy**: Enabled by default - pushes to `main` branch trigger redeploy

## 💰 Pricing

- **Free Tier**: 
  - 750 hours/month
  - Sleeps after 15 minutes of inactivity
  - 10-minute build timeout
  
- **Starter Plan ($7/month)**:
  - Always on
  - Faster cold starts
  - Better performance

Your app should now be live on Render! 🎉

