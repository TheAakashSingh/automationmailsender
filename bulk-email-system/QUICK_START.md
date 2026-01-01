# Quick Start Guide

## Complete Setup in 5 Minutes

### 1. Install Dependencies
```bash
cd bulk-email-system
npm install
```

### 2. Setup Environment
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env and add:
DATABASE_URL="mongodb://localhost:27017/bulk-email-automation"
NEXTAUTH_SECRET="your-random-secret-here"  # Generate with: openssl rand -base64 32
CRON_SECRET="another-random-secret"        # Generate with: openssl rand -base64 32
NEXTAUTH_URL="http://localhost:3000"
```

### 3. Setup Database
```bash
# Generate Prisma Client
npm run db:generate

# Push schema to MongoDB
npm run db:push
```

### 4. Create Admin User
```bash
node scripts/create-admin.js
# Enter email, password, name when prompted
```

### 5. Start Development Server
```bash
npm run dev
```

Visit: http://localhost:3000/login

### 6. Setup SMTP (Required for Sending)
1. Login to dashboard
2. Go to **SMTP** → Click **Add SMTP Account**
3. Enter your SMTP details (Gmail example below)
4. Click **Test SMTP** to verify
5. Click **Activate**

**Gmail SMTP Settings:**
- Host: `smtp.gmail.com`
- Port: `587`
- Secure: ✓ (checked)
- Username: `your-email@gmail.com`
- Password: App Password (generate from Google Account → Security → 2-Step Verification → App Passwords)
- From Email: `your-email@gmail.com`
- From Name: `Your Company Name`

### 7. Upload Leads
1. Go to **Leads** → Click **Upload CSV**
2. CSV format:
   ```csv
   company,email,phone,website,city,country,industry
   Acme Insurance,contact@acme.com,555-1234,https://acme.com,New York,USA,Insurance
   ```
3. System auto-validates emails and removes duplicates

### 8. Create Email Template
1. Go to **Templates** → Click **Create Template**
2. Or click any pre-built template button to load it
3. Pre-built templates available for:
   - Insurance companies
   - Logistics & Shipping
   - Healthcare
   - Financial Services
   - Manufacturing
   - Real Estate
   - General tech solutions
   - Follow-up emails
4. Edit as needed and save

### 9. Create Campaign
1. Go to **Campaigns** → Click **Create Campaign**
2. Select:
   - Campaign name
   - Email template
   - Daily limit (50-100 recommended)
   - Lead filters (industry, country, status)
   - Follow-up settings (optional)
3. Click **Create Campaign**

### 10. Start Campaign
1. Click **Start** on your campaign
2. System creates jobs in queue
3. Campaign status becomes "running"

### 11. Setup Cron Job (Critical!)
The system needs a cron job to process the email queue:

**Option A: External Cron Service**
- Use cron-job.org or similar
- URL: `https://yourdomain.com/api/cron/process-queue`
- Headers: `Authorization: Bearer YOUR_CRON_SECRET`
- Frequency: Every 1-2 minutes

**Option B: Local Worker Script**
Create `worker.js`:
```javascript
const fetch = require('node-fetch');
setInterval(async () => {
  await fetch('http://localhost:3000/api/cron/process-queue', {
    headers: { 'Authorization': `Bearer ${process.env.CRON_SECRET}` }
  });
}, 60000);
```
Run: `CRON_SECRET=your-secret node worker.js`

### 12. Monitor Progress
- **Dashboard**: View real-time stats
- **Campaigns**: See campaign progress
- **Logs**: View detailed email history
- **Leads**: Filter by status (sent, replied, bounced)

## Pre-built Templates Included

The system comes with 8 pre-built templates specifically for software companies reaching out to:

1. **Insurance Companies** - Partnership opportunity
2. **Logistics & Shipping** - Technology solutions
3. **Healthcare** - Medical practice software
4. **Financial Services** - Banking/finance tech
5. **Manufacturing** - Production optimization
6. **Real Estate** - Property management
7. **General** - Custom software solutions
8. **Follow-up** - No response follow-up

All templates use variables: `{{company}}`, `{{city}}`, `{{country}}`, `{{industry}}`, `{{website}}`

## Features Summary

✅ **Complete Lead Management** - CSV upload, validation, deduplication
✅ **SMTP Management** - Multiple accounts, test connection, activate/deactivate
✅ **Email Templates** - Create/edit with variables, 8 pre-built templates
✅ **Campaign System** - Filter leads, set daily limits, track progress
✅ **Smart Sending** - One-by-one, 30-120s delays, daily limits
✅ **Follow-up Automation** - Auto follow-up after 3-7 days (configurable)
✅ **Reply Detection** - Process replies, auto-unsubscribe on "STOP"
✅ **Bounce Protection** - Auto-pause if bounce rate > 5%
✅ **Dashboard** - Real-time stats, recent activity
✅ **Logs & Export** - Full email history, CSV export

## Next Steps

1. ✅ Setup complete
2. ✅ SMTP configured
3. ✅ Upload your leads CSV
4. ✅ Create/select template
5. ✅ Create campaign
6. ✅ Start campaign
7. ✅ Setup cron job
8. ✅ Monitor and optimize!

## Tips

- Start with small daily limits (50 emails/day)
- Use industry-specific templates for better response rates
- Monitor bounce rates and adjust targeting
- Test SMTP before starting campaigns
- Use follow-up emails for better engagement
- Export replied leads for follow-up

Your system is ready to start sending emails to your leads! 🚀

