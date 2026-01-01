# Installation Troubleshooting

## Network Error (ECONNRESET)

If you see `network read ECONNRESET`, try these solutions:

### Solution 1: Close File Handles and Retry
1. Close your IDE/editor (VS Code, etc.)
2. Close any processes using the `node_modules` folder
3. Try again:
   ```bash
   npm install --legacy-peer-deps
   ```

### Solution 2: Clear npm Cache
```bash
npm cache clean --force
npm install --legacy-peer-deps
```

### Solution 3: Delete node_modules and Retry
```bash
# Close your IDE first!
rmdir /s /q node_modules
del package-lock.json
npm install --legacy-peer-deps
```

### Solution 4: Use Slower Network Settings
```bash
npm install --legacy-peer-deps --prefer-offline --no-audit
```

### Solution 5: Install with Increased Timeout
```bash
npm install --legacy-peer-deps --timeout=60000
```

## File Lock Errors (EPERM)

The cleanup warnings about EPERM are usually harmless. They happen when:
- Your IDE has files open
- Antivirus is scanning files
- Node processes are still running

**Solution:** Close your IDE and any Node.js processes, then retry.

## Quick Fix Sequence

```bash
# 1. Close IDE/Editor
# 2. Kill any node processes (Task Manager)
# 3. Run these commands:
cd C:\Users\dell\Documents\automation_leads\bulk-email-system
rmdir /s /q node_modules 2>nul
del package-lock.json 2>nul
npm cache clean --force
npm install --legacy-peer-deps
```

## If All Else Fails

Try installing dependencies one by one:
```bash
npm install next@14.0.4 react@^18.2.0 react-dom@^18.2.0 --legacy-peer-deps
npm install next-auth@^4.24.5 @prisma/client@^5.7.1 prisma@^5.7.1 --legacy-peer-deps
npm install bcryptjs@^2.4.3 nodemailer@^7.0.7 csv-parse@^5.5.3 --legacy-peer-deps
npm install recharts@^2.10.3 zod@^3.22.4 date-fns@^3.0.6 --legacy-peer-deps
npm install --save-dev @types/node@^20.10.6 @types/react@^18.2.46 @types/react-dom@^18.2.18 --legacy-peer-deps
npm install --save-dev @types/nodemailer@^6.4.15 @types/bcryptjs@^2.4.6 --legacy-peer-deps
npm install --save-dev typescript@^5.3.3 tailwindcss@^3.4.0 postcss@^8.4.32 autoprefixer@^10.4.16 --legacy-peer-deps
npm install --save-dev eslint@^8.56.0 eslint-config-next@14.0.4 --legacy-peer-deps
```

