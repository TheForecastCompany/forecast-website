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

- `GET /api/test` - Test endpoint to verify API is working
- `POST /api/login` - User authentication (hardcoded users)
- `POST /api/forgot-password` - Password reset email
- `POST /api/forecast` - Generate forecasts (mock data for now)

## Fixed Issues

- ✅ Removed Prisma dependency (causing crashes)
- ✅ Fixed mixed module systems (require/import)
- ✅ Replaced Python execution with mock data
- ✅ Simplified authentication to hardcoded users
- ✅ Added test endpoint for debugging

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

## Troubleshooting

### If you get 500 errors:
1. Check Vercel function logs in the dashboard
2. Test `/api/test` endpoint first to verify basic functionality
3. Ensure environment variables are set correctly
4. Check that all dependencies are in package.json

### Common Issues Fixed:
- **Mixed modules**: All API functions now use ES modules (`import/export`)
- **Prisma crashes**: Temporarily removed, using hardcoded authentication
- **Python execution**: Not supported on Vercel, replaced with mock data
- **Missing dependencies**: Simplified to only essential packages

## Notes

- The Express server (`server.js`) is no longer used
- All API functionality has been converted to Vercel serverless functions
- Frontend files have been updated to use relative API paths
- Python scripts in `/Server` directory are temporarily disabled (Vercel limitation)
- Authentication is currently hardcoded (can be upgraded to database later)
