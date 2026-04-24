# Social Authentication & Email Verification Setup Guide

## Overview

This guide covers the setup and configuration of social authentication (Google, Facebook, Apple) and email verification features for the TRENDY app backend.

## Prerequisites

- Python 3.8+
- FastAPI application
- SQLite/PostgreSQL database
- Firebase Admin SDK configured
- Environment variables set up

## Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id

# Facebook OAuth
FACEBOOK_CLIENT_ID=your_facebook_app_id
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret

# Apple Sign-In
APPLE_CLIENT_ID=your_apple_service_id
APPLE_TEAM_ID=your_apple_team_id
APPLE_KEY_ID=your_apple_key_id
APPLE_PRIVATE_KEY=your_apple_private_key

# Email Service
MAIL_USERNAME=your_email_username
MAIL_PASSWORD=your_email_password
MAIL_FROM=your_email@domain.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=TRENDY App
```

## Installation

Install required dependencies:

```bash
pip install google-auth httpx fastapi-mail python-multipart
```

## Google OAuth Setup

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google+ API

2. **Configure OAuth Consent Screen**
   - Go to APIs & Services > OAuth consent screen
   - Configure external user type
   - Add required scopes: `email`, `profile`, `openid`

3. **Create Credentials**
   - Go to APIs & Services > Credentials
   - Create OAuth 2.0 Client ID
   - Set application type to "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/auth/google/callback` (development)
     - `https://yourdomain.com/auth/google/callback` (production)

4. **Get Client ID**
   - Copy the Client ID and add to environment variables

## Facebook OAuth Setup

1. **Create Facebook App**
   - Go to [Facebook Developers](https://developers.facebook.com/)
   - Create a new app
   - Select "Consumer" as app type

2. **Configure Facebook Login**
   - Add Facebook Login product
   - Configure Valid OAuth Redirect URIs:
     - `http://localhost:8000/auth/facebook/callback`
     - `https://yourdomain.com/auth/facebook/callback`

3. **Get App Credentials**
   - Copy App ID and App Secret to environment variables

4. **Configure App Settings**
   - Add your domain to App Domains
   - Configure privacy policy URL
   - Set app to live mode when ready

## Apple Sign-In Setup

1. **Create Apple Developer Account**
   - Requires paid Apple Developer account ($99/year)

2. **Create App ID**
   - Go to Certificates, Identifiers & Profiles
   - Create new App ID with Sign In with Apple capability

3. **Create Service ID**
   - Create a new Services ID for authentication
   - Configure Return URLs

4. **Generate Private Key**
   - Create a new private key for your Service ID
   - Download the .p8 file and convert to string for environment variable

## Email Service Setup

1. **Gmail Setup (Recommended)**
   - Use Gmail SMTP server
   - Enable 2-factor authentication
   - Generate app-specific password

2. **Other Email Providers**
   - Update SMTP server settings accordingly
   - Ensure proper authentication method

## Database Migration

The User model has been updated with email verification fields:

```python
# New fields added
verification_token = Column(String(255), nullable=True, index=True)
verification_token_expires = Column(DateTime, nullable=True)
```

Run database migrations to apply changes:

```bash
# If using Alembic
alembic revision --autogenerate -m "add_email_verification_fields"
alembic upgrade head

# If using direct SQL
# The script will automatically create the necessary columns
```

## API Endpoints

### Social Authentication

- `POST /auth/social/google` - Google OAuth authentication
- `POST /auth/social/facebook` - Facebook OAuth authentication  
- `POST /auth/social/apple` - Apple Sign-In authentication
- `GET /auth/social/providers` - Get available providers
- `GET /auth/social/user/{user_id}/providers` - Get user's linked providers

### Email Verification

- `POST /auth/email/send-verification` - Send verification email
- `POST /auth/email/verify` - Verify email with token
- `POST /auth/email/resend-verification` - Resend verification email

### User Relationships

- `POST /users/follow` - Follow another user
- `DELETE /users/unfollow/{user_id}` - Unfollow user
- `POST /users/block` - Block another user
- `POST /users/mute` - Mute another user
- `GET /users/{user_id}/followers` - Get user's followers
- `GET /users/{user_id}/following` - Get users followed by user

## Testing

Run the comprehensive test script:

```bash
cd trendy_backend
python scripts/test_social_auth.py
```

## Frontend Integration

### Google Sign-In

```javascript
// Example frontend implementation
import { GoogleSignin } from '@react-native-google-signin/google-signin';

GoogleSignin.configure({
  webClientId: 'YOUR_GOOGLE_CLIENT_ID',
  offlineAccess: true,
});

const signIn = async () => {
  try {
    await GoogleSignin.hasPlayServices();
    const userInfo = await GoogleSignin.signIn();
    const token = userInfo.idToken;
    
    // Send token to backend
    const response = await fetch('/auth/social/google', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    });
  } catch (error) {
    console.error(error);
  }
};
```

### Facebook Login

```javascript
// React Native example
import { LoginManager, AccessToken } from 'react-native-fbsdk-next';

const loginWithFacebook = async () => {
  try {
    const result = await LoginManager.logInWithPermissions(['public_profile', 'email']);
    
    if (result.isCancelled) {
      throw new Error('User cancelled login');
    }

    const data = await AccessToken.getCurrentAccessToken();
    
    if (data) {
      const response = await fetch('/auth/social/facebook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code: data.accessToken,
          redirect_uri: 'your_redirect_uri'
        })
      });
    }
  } catch (error) {
    console.error(error);
  }
};
```

## Security Considerations

1. **Token Validation**
   - All social tokens are validated on the backend
   - Never trust client-side validation

2. **Rate Limiting**
   - Implement rate limiting on authentication endpoints
   - Prevent brute force attacks

3. **Email Verification**
   - Tokens expire after 24 hours
   - Use secure random token generation

4. **Data Privacy**
   - Only store necessary user data from social providers
   - Comply with GDPR and other privacy regulations

## Troubleshooting

### Common Issues

1. **Google Auth Fails**
   - Check Client ID matches environment variable
   - Verify redirect URIs are configured correctly

2. **Facebook Auth Fails**  
   - Ensure App ID and Secret are correct
   - Check app is in development/live mode appropriately

3. **Email Not Sending**
   - Verify SMTP credentials
   - Check firewall/port restrictions

4. **Database Errors**
   - Ensure migrations have run successfully
   - Verify database schema matches models

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export AUTH_DEBUG=true
```

This will provide detailed error messages for authentication issues.

## Production Deployment

1. **Update Redirect URIs**
   - Replace localhost with production domain
   - Update all social provider configurations

2. **SSL Certificate**
   - Ensure HTTPS is enabled in production
   - Social providers require secure connections

3. **Environment Variables**
   - Use secure secret management
   - Never commit secrets to version control

4. **Monitoring**
   - Set up logging and monitoring
   - Track authentication success/failure rates

## Support

For issues with this implementation, check:

1. API documentation at `/docs` endpoint
2. Test scripts in `scripts/test_social_auth.py`
3. Error logs in application output
4. Social provider developer documentation
