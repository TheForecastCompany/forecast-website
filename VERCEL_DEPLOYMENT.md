# Vercel Deployment Guide

## Environment Variables

Set these environment variables in your Vercel dashboard:

### Required Variables:
- `EMAIL_USER`: Your Gmail address for sending emails
- `EMAIL_PASS`: Your Gmail app password (not your regular password)

### Optional Variables:
- `DATABASE_URL`: If using Prisma database
- `VERCEL_URL`: Your Vercel domain (automatically set by Vercel)

## Deployment Steps

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy:
   ```bash
   vercel
   ```

4. Set environment variables in Vercel dashboard:
   - Go to your project settings
   - Add the required environment variables

## API Endpoints

- `POST /api/login` - User authentication
- `POST /api/forgot-password` - Password reset email
- `POST /api/forecast` - Generate forecasts

## File Structure

```
/
├── api/                    # Vercel serverless functions
│   ├── login.js
│   ├── forgot-password.js
│   └── forecast.js
├── Server/                 # Legacy server files (not used in production)
├── prisma/                 # Database schema and migrations
├── vercel.json            # Vercel configuration
└── package.json           # Updated for Vercel
```

## Notes

- The Express server (`server.js`) is no longer used
- All API functionality has been converted to Vercel serverless functions
- Frontend files have been updated to use relative API paths
- Python scripts in `/Server` directory are still used by the forecast API
