# Bulk Email Automation System

A complete self-hosted bulk email automation system built with Next.js 14, MongoDB, and your own SMTP server. No third-party email services required.

## Features

- ✅ **Admin Authentication** - Secure login system
- ✅ **Lead Management** - CSV upload with validation and deduplication
- ✅ **Email Templates** - Create and manage plain-text email templates
- ✅ **SMTP Management** - Configure multiple SMTP accounts with rotation
- ✅ **Campaign System** - Create, start, pause, and manage email campaigns
- ✅ **Smart Sending** - Rate-limited, human-like email sending (30-120s delays)
- ✅ **Follow-up Automation** - Automatic follow-up emails after 3-7 days
- ✅ **Reply Detection** - Detect replies and unsubscribe requests
- ✅ **Bounce Handling** - Auto-pause campaigns if bounce rate > 5%
- ✅ **Dashboard** - Real-time statistics and activity monitoring
- ✅ **Export** - Export leads by status (sent, replied, bounced)

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Database:** MongoDB with Prisma ORM
- **Email:** Nodemailer (SMTP)
- **Auth:** NextAuth.js
- **UI:** React + Tailwind CSS
- **Charts:** Recharts

## Prerequisites

- Node.js 18+ 
- MongoDB (local or remote)
- SMTP server (Gmail, SendGrid SMTP, or your own)

## Installation

### 1. Clone and Install

```bash
cd bulk-email-system
npm install
```

### 2. Setup Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL="mongodb://localhost:27017/bulk-email-automation"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="generate-a-random-secret-here"
CRON_SECRET="another-random-secret-for-cron"
```

Generate secrets:
```bash
openssl rand -base64 32  # For NEXTAUTH_SECRET
openssl rand -base64 32  # For CRON_SECRET
```

### 3. Setup Database

```bash
# Generate Prisma Client
npm run db:generate

# Push schema to database
npm run db:push
```

### 4. Create Admin User

Run this script to create your first admin user:

```bash
node scripts/create-admin.js
```

Or create manually using Prisma Studio:
```bash
npm run db:studio
```

### 5. Run Development Server

```bash
npm run dev
```

Visit http://localhost:3000 and login with your admin credentials.

## Setup Cron Job (Email Processing)

The system needs a cron job to process the email queue. You have two options:

### Option 1: External Cron (Recommended)

Use a service like [cron-job.org](https://cron-job.org) or set up a system cron:

```bash
# Run every minute
* * * * * curl -H "Authorization: Bearer YOUR_CRON_SECRET" http://localhost:3000/api/cron/process-queue
```

### Option 2: Worker Script (Local)

Create a worker script that runs continuously:

```javascript
// scripts/worker.js
const fetch = require('node-fetch');

setInterval(async () => {
  try {
    await fetch('http://localhost:3000/api/cron/process-queue', {
      headers: {
        'Authorization': `Bearer ${process.env.CRON_SECRET}`
      }
    });
  } catch (error) {
    console.error('Error processing queue:', error);
  }
}, 60000); // Run every minute
```

Run it:
```bash
CRON_SECRET=your-secret node scripts/worker.js
```

## Usage Guide

### 1. Setup SMTP

1. Go to **SMTP** in the sidebar
2. Click **Add SMTP Account**
3. Enter your SMTP details:
   - **Host:** smtp.gmail.com (for Gmail)
   - **Port:** 587 (TLS) or 465 (SSL)
   - **Username:** your-email@gmail.com
   - **Password:** App Password (for Gmail)
   - **From Email:** your-email@gmail.com
   - **From Name:** Your Company Name
4. Click **Test SMTP** to verify
5. Mark as **Active**

### 2. Upload Leads

1. Go to **Leads** → Click **Upload CSV**
2. CSV format:
   ```csv
   company,email,phone,website,city,country,industry
   Acme Corp,contact@acme.com,555-1234,https://acme.com,New York,USA,Technology
   ```
3. System will:
   - Validate emails
   - Remove duplicates
   - Auto-tag by industry/country

### 3. Create Email Template

1. Go to **Templates** → **Create Template**
2. Use variables:
   - `{{company}}` - Company name
   - `{{email}}` - Email address
   - `{{city}}` - City
   - `{{country}}` - Country
   - `{{industry}}` - Industry
   - `{{website}}` - Website
3. Example:
   ```
   Subject: Partnership opportunity with {{company}}
   
   Hi,
   
   I noticed {{company}} is in {{industry}} based in {{city}}.
   We offer services that might interest you.
   
   Best regards
   ```

### 4. Create Campaign

1. Go to **Campaigns** → **Create Campaign**
2. Select:
   - Template
   - Lead filters (industry, country, status)
   - Daily sending limit (default: 50)
   - Follow-up settings (optional)
3. Click **Start Campaign**

### 5. Monitor Progress

- View stats on **Dashboard**
- Check **Logs** for detailed email history
- Export leads from **Leads** page

## Security Best Practices

1. **Never commit `.env` file**
2. **Use strong secrets** for NEXTAUTH_SECRET and CRON_SECRET
3. **Use App Passwords** for Gmail (not your main password)
4. **Rate limit** - System sends 30-120s between emails automatically
5. **Bounce protection** - Campaigns auto-pause if bounce rate > 5%
6. **Unsubscribe handling** - Replies with "stop" auto-unsubscribe

## Production Deployment

### Environment Variables

Set these in your hosting platform:
- `DATABASE_URL` - MongoDB connection string
- `NEXTAUTH_URL` - Your domain URL
- `NEXTAUTH_SECRET` - Strong random secret
- `CRON_SECRET` - Secret for cron endpoint
- `NODE_ENV=production`

### Build

```bash
npm run build
npm start
```

### Email Queue Processing

**Option 1: Manual Processing (Dashboard)**
- Go to Dashboard
- Click **"Process Email Queue Now"** button
- Click every 1-2 minutes while campaigns are running

**Option 2: External Cron Service (Free)**
Set up a cron job (cron-job.org, EasyCron, etc.) to hit:
```
https://yourdomain.com/api/cron/process-queue
Authorization: Bearer YOUR_CRON_SECRET
```
Schedule: Every 1-2 minutes

**Note:** Vercel Hobby plan only allows daily cron jobs, so use manual processing or external cron service.

## Troubleshooting

### Emails not sending

1. Check SMTP configuration (Test SMTP button)
2. Verify SMTP account is marked "Active"
3. Check email logs for error messages
4. Verify cron job is running

### High bounce rate

- Verify email addresses are valid
- Don't send to purchased lists
- Follow email best practices
- System auto-pauses at 5% bounce rate

### Database connection error

- Verify MongoDB is running
- Check DATABASE_URL in .env
- Run `npm run db:push` to sync schema

## License

MIT License - Use at your own risk for internal business purposes only.

## Support

This is a self-hosted solution. No external dependencies or paid services required.

