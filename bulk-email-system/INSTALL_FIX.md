# Installation Fix

If you encounter the nodemailer dependency conflict, there are two solutions:

## Solution 1: Use Updated Package (Recommended)
The package.json has been updated to use nodemailer@^7.0.7 to match next-auth's requirements.

```bash
npm install
```

## Solution 2: Use Legacy Peer Deps (Alternative)
If you prefer to stick with nodemailer 6.x, use:

```bash
npm install --legacy-peer-deps
```

Then update package.json to use nodemailer@^6.9.7 if needed.

The code should work with both nodemailer 6.x and 7.x as the API is backward compatible for our use case.

