# Deploy to Vercel - Step by Step

## 🚀 Quick Deploy (5 Minutes)

### Step 1: Prepare Your Code

Make sure all files are committed:
```bash
cd bulk-email-system
git add .
git commit -m "Ready for Vercel deployment"
```

### Step 2: Push to GitHub

```bash
# If you haven't created a repo yet:
git init
git remote add origin https://github.com/yourusername/bulk-email-automation.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Vercel will auto-detect Next.js settings

### Step 4: Configure Environment Variables

In Vercel project settings → **Environment Variables**, add:

```
DATABASE_URL=mongodb+srv://automation_lead:automation_lead@cluster0.cvnkonw.mongodb.net/bulk-email-automation?retryWrites=true&w=majority
NEXTAUTH_URL=https://your-app-name.vercel.app
NEXTAUTH_SECRET=<generate-with-openssl-rand-base64-32>
CRON_SECRET=<generate-with-openssl-rand-base64-32>
NODE_ENV=production
```

**Generate secrets:**
```bash
openssl rand -base64 32  # Copy for NEXTAUTH_SECRET
openssl rand -base64 32  # Copy for CRON_SECRET
```

### Step 5: Deploy

Click **"Deploy"** and wait for build to complete.

### Step 6: Setup Database

After deployment, run locally to push schema:
```bash
# Pull env vars from Vercel (optional)
vercel env pull .env.local

# Push Prisma schema
npm run db:push
```

### Step 7: Create Admin User

```bash
node scripts/create-admin.js
# Enter email, password, name
```

### Step 8: Setup Cron Job

**Option A: Vercel Cron (Easiest)**
The `vercel.json` file already includes cron configuration. Vercel will automatically run it every 2 minutes.

**Option B: External Service**
- Go to [cron-job.org](https://cron-job.org)
- Create new cron job
- URL: `https://your-app.vercel.app/api/cron/process-queue`
- Method: GET
- Headers: `Authorization: Bearer YOUR_CRON_SECRET`
- Schedule: Every 1-2 minutes

## ✅ Verification

1. Visit your Vercel URL
2. Login with admin credentials
3. Check dashboard loads
4. Test SMTP configuration
5. Verify cron is running (check logs)

## 🔧 Troubleshooting

### Build Errors
- ✅ Path aliases fixed in `next.config.js`
- ✅ Prisma auto-generates in `postinstall` script
- ✅ TypeScript config updated

### Module Resolution Errors
- ✅ Webpack alias configured
- ✅ `baseUrl` set in `tsconfig.json`
- ✅ All imports use `@/` prefix

### Database Issues
- Make sure `DATABASE_URL` includes database name
- Check MongoDB Atlas allows connections from anywhere (`0.0.0.0/0`)

### Cron Not Working
- Verify `CRON_SECRET` in environment variables
- Check Vercel function logs
- Test endpoint manually: `curl -H "Authorization: Bearer YOUR_SECRET" https://your-app.vercel.app/api/cron/process-queue`

## 📝 Important Notes

- **MongoDB**: Must use MongoDB Atlas (cloud), not local
- **SMTP**: Configure in dashboard after deployment
- **Cron**: Vercel cron runs automatically (configured in `vercel.json`)
- **Secrets**: Never commit `.env` file to Git

Your app should now be live on Vercel! 🎉

