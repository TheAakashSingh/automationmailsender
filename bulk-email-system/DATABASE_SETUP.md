# MongoDB Database Setup

## Connection String Format

Your MongoDB connection string **must include the database name**.

### Format for MongoDB Atlas (Cloud):
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/bulk-email-automation?retryWrites=true&w=majority
```

### Format for Local MongoDB:
```
mongodb://localhost:27017/bulk-email-automation
```

## Important Notes:

1. **Database name is required** - It should be included in the connection string after the host
2. For MongoDB Atlas, use `mongodb+srv://` (not just `mongodb://`)
3. Replace `username` and `password` with your MongoDB credentials
4. Replace `cluster0.xxxxx.mongodb.net` with your actual cluster address
5. The database name (`bulk-email-automation`) can be any name you prefer

## Example .env file:

```env
DATABASE_URL="mongodb+srv://myuser:mypassword@cluster0.cvnkonw.mongodb.net/bulk-email-automation?retryWrites=true&w=majority"
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="your-secret-key-change-this-in-production"
CRON_SECRET="another-random-secret"
```

## Getting MongoDB Atlas Connection String:

1. Go to MongoDB Atlas dashboard
2. Click "Connect" on your cluster
3. Choose "Connect your application"
4. Copy the connection string
5. **IMPORTANT**: Add the database name before the `?` symbol
   - Change: `mongodb+srv://user:pass@cluster.net/?retryWrites=true`
   - To: `mongodb+srv://user:pass@cluster.net/bulk-email-automation?retryWrites=true`

## After Fixing .env:

```bash
npm run db:push
```

This will create the database and all tables (collections) in MongoDB.

