# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for the TRENDY App backend.

## Prerequisites

1. A Google Cloud Platform account
2. A Google Cloud project
3. OAuth consent screen configured

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API

## Step 2: Configure OAuth Consent Screen

1. In the Google Cloud Console, go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" (for development) or "Internal" (for production)
3. Fill in the required information:
   - App name: "TRENDY App"
   - User support email: your email
   - Developer contact information: your email
4. Add scopes: `email`, `profile`, `openid`
5. Add test users (for external apps during development)

## Step 3: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Choose "Web application" as the application type
4. Configure authorized JavaScript origins:
   - `http://localhost:3000` (for development)
   - `https://yourdomain.com` (for production)
5. Configure authorized redirect URIs:
   - `http://localhost:3000/auth/google/callback` (for development)
   - `https://yourdomain.com/auth/google/callback` (for production)
6. Copy the Client ID and Client Secret

## Step 4: Configure Environment Variables

Copy the `.env.example` file to `.env` and update the Google OAuth values:

```bash
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
```

## Step 5: Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

## Step 6: Test the Setup

1. Start the backend server:
```bash
cd trendy_backend
uvicorn app.main:app --reload
```

2. Test the Google OAuth configuration endpoint:
```bash
curl http://localhost:8000/api/v1/auth/google/config
```

This should return your Google Client ID and configuration.

## Step 7: Frontend Integration

For the Flutter frontend, you'll need to:

1. Use the `google_sign_in` package
2. Configure the Google Sign-In with your Client ID
3. Handle the authentication flow:
   - Get ID token from Google Sign-In
   - Send token to `/api/v1/auth/google/login` endpoint
   - Store the JWT token returned

## API Endpoints

### POST `/api/v1/auth/google/login`
Authenticate with Google OAuth token

**Request:**
```json
{
  "token": "google-id-token-here"
}
```

**Response:**
```json
{
  "access_token": "jwt-token-here",
  "token_type": "bearer",
  "user_id": 123,
  "email": "user@example.com",
  "username": "user",
  "display_name": "User Name",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

### GET `/api/v1/auth/google/config`
Get Google OAuth configuration for frontend

**Response:**
```json
{
  "client_id": "your-google-client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "scope": "openid email profile",
  "redirect_uri": "http://localhost:3000/auth/google/callback"
}
```

## Troubleshooting

### Common Issues

1. **Invalid audience error**: Make sure the Client ID matches between Google Cloud and your environment variables
2. **Token verification failed**: Ensure the token is a valid Google ID token
3. **CORS issues**: Verify your frontend URL is in the authorized JavaScript origins

### Testing

You can test the OAuth flow using:

1. Google's OAuth Playground
2. Postman with a valid Google ID token
3. The Flutter app with Google Sign-In configured

## Security Considerations

1. Always use HTTPS in production
2. Validate the token audience on the server
3. Implement proper error handling
4. Use secure storage for JWT tokens on the client
5. Regularly rotate your OAuth credentials
