# Vercel Deployment Fix

If you're getting module resolution errors like `Can't resolve '@/lib/auth'` on Vercel, try these solutions:

## Solution 1: Verify tsconfig.json

Make sure your `tsconfig.json` has:
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

## Solution 2: Clear Build Cache on Vercel

1. Go to your Vercel project settings
2. Go to "Build & Development Settings"
3. Clear the build cache
4. Redeploy

## Solution 3: Check File Structure

Make sure these files exist:
- `lib/auth.ts`
- `lib/prisma.ts`
- `lib/email.ts`
- `lib/campaign.ts`

## Solution 4: Force Clean Build

In Vercel settings, add build command:
```bash
rm -rf .next && npm run build
```

Or use:
```bash
npm run build
```

## Solution 5: Check Node.js Version

Make sure Vercel is using Node.js 18+:
1. Go to Vercel project settings
2. Go to "General" → "Node.js Version"
3. Set to 18.x or 20.x

## Solution 6: Verify Imports

All imports should use the `@/` prefix:
```typescript
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
```

NOT:
```typescript
import { authOptions } from '../../lib/auth'  // ❌ Wrong
```

The current `tsconfig.json` has been updated with `baseUrl: "."` which should fix the issue. Redeploy on Vercel.

