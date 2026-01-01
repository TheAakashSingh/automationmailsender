# Fix MongoDB Connection String

## The Problem
Your MongoDB connection string is missing the **database name**. Prisma requires the database name to be included in the connection string.

## Current (Wrong) Format:
```
mongodb+srv://user:pass@cluster0.cvnkonw.mongodb.net/?retryWrites=true&w=majority
```
❌ Missing database name before the `?`

## Correct Format:
```
mongodb+srv://user:pass@cluster0.cvnkonw.mongodb.net/bulk-email-automation?retryWrites=true&w=majority
```
✅ Database name (`bulk-email-automation`) included before the `?`

## How to Fix:

### Step 1: Open your `.env` file
Located at: `bulk-email-system/.env`

### Step 2: Update DATABASE_URL

**For MongoDB Atlas:**
```env
DATABASE_URL="mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.cvnkonw.mongodb.net/bulk-email-automation?retryWrites=true&w=majority"
```

**Key points:**
- Replace `YOUR_USERNAME` with your MongoDB username
- Replace `YOUR_PASSWORD` with your MongoDB password (URL-encode if it contains special characters)
- Keep `cluster0.cvnkonw.mongodb.net` as your cluster address
- **Add `/bulk-email-automation`** right after `.net` and before the `?`
- Keep the query parameters (`?retryWrites=true&w=majority`)

**For Local MongoDB:**
```env
DATABASE_URL="mongodb://localhost:27017/bulk-email-automation"
```

### Step 3: Save and retry
```bash
npm run db:push
```

## URL Encoding Special Characters

If your password contains special characters, you need to URL-encode them:
- `@` becomes `%40`
- `#` becomes `%23`
- `$` becomes `%24`
- `%` becomes `%25`
- `&` becomes `%26`
- `+` becomes `%2B`
- `=` becomes `%3D`

Example: If password is `p@ssw#rd`, use `p%40ssw%23rd`

## Getting MongoDB Atlas Connection String:

1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. **IMPORTANT**: Add the database name before the `?`
   - Original: `mongodb+srv://user:pass@cluster.net/?retryWrites=true`
   - Fixed: `mongodb+srv://user:pass@cluster.net/bulk-email-automation?retryWrites=true`

## Example Complete .env File:

```env
DATABASE_URL="mongodb+srv://myuser:mypassword@cluster0.cvnkonw.mongodb.net/bulk-email-automation?retryWrites=true&w=majority"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-random-secret-here"
CRON_SECRET="another-random-secret-here"
NODE_ENV="development"
```

After fixing, run:
```bash
npm run db:push
```

