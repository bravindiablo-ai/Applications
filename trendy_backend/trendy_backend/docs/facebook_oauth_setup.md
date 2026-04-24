# Facebook OAuth Setup Guide for TRENDY App

This guide will help you set up Facebook OAuth authentication for the TRENDY App backend.

## Prerequisites

1. A Facebook Developer account
2. A Facebook App created in the Developer Portal
3. Valid domain for OAuth redirects

## Step 1: Create Facebook App

1. Go to [Facebook Developer Portal](https://developers.facebook.com/)
2. Click "Create App" and select "Consumer" as the app type
3. Choose a display name for your app (e.g., "TRENDY App")
4. Complete the app setup process

## Step 2: Configure Facebook App Settings

### Basic Settings
1. Go to your app's dashboard
2. Navigate to Settings → Basic
3. Add your contact email
4. Add your app domain and privacy policy URL (if available)

### OAuth Settings
1. Navigate to Facebook Login → Settings
2. Add valid OAuth redirect URIs:
   - Development: `http://localhost:3000/auth/facebook/callback`
   - Production: `https://yourdomain.com/auth/facebook/callback`
3. Enable "Client OAuth Login"
4. Enable "Web OAuth Login"

### App Review (Optional for Development)
For development/testing, you can add yourself as a tester:
1. Go to Roles → Testers
2. Add your Facebook account as a tester
3. This allows you to test the login flow without app review

## Step 3: Get App Credentials

1. From your app dashboard, note down:
   - **App ID** (Client ID)
   - **App Secret** (Client Secret)

2. These will be used as environment variables:
   - `FACEBOOK_CLIENT_ID` = Your App ID
   - `FACEBOOK_CLIENT_SECRET` = Your App Secret

## Step 4: Configure Environment Variables

Add the following environment variables to your `.env` file:

```bash
# Facebook OAuth Configuration
FACEBOOK_CLIENT_ID=your_facebook_app_id_here
FACEBOOK_CLIENT_SECRET=your_facebook_app_secret_here
FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/facebook/callback
```

## Step 5: Test Facebook OAuth

### Test Configuration
1. Start your backend server
2. Make a GET request to `/api/v1/auth/facebook/test`
3. You should see a response indicating if Facebook OAuth is configured

### Test Login Flow
1. Use the Facebook SDK on your frontend to get an access token
2. Send a POST request to `/api/v1/auth/facebook/login` with the token:
   ```json
   {
     "token": "facebook_access_token_here"
   }
   ```
3. The backend will verify the token and return user information + JWT

## API Endpoints

### POST `/api/v1/auth/facebook/login`
Authenticate with Facebook OAuth token

**Request:**
```json
{
  "token": "facebook_access_token"
}
```

**Response:**
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user_id": 123,
  "email": "user@example.com",
  "username": "username",
  "display_name": "User Name",
  "avatar_url": "https://example.com/avatar.jpg",
  "is_verified": true
}
```

### GET `/api/v1/auth/facebook/config`
Get Facebook OAuth configuration for frontend

**Response:**
```json
{
  "success": true,
  "data": {
    "client_id": "facebook_app_id",
    "auth_uri": "https://www.facebook.com/v12.0/dialog/oauth",
    "token_uri": "https://graph.facebook.com/v12.0/oauth/access_token",
    "scope": "email,public_profile",
    "redirect_uri": "http://localhost:3000/auth/facebook/callback"
  }
}
```

### GET `/api/v1/auth/facebook/test`
Test Facebook API connection

**Response:**
```json
{
  "success": true,
  "message": "Facebook OAuth configuration is valid",
  "configured": true,
  "client_id": "facebook_app_id",
  "redirect_uri": "http://localhost:3000/auth/facebook/callback"
}
```

## Frontend Integration

### Flutter Integration
Use the `flutter_facebook_auth` package:

```yaml
dependencies:
  flutter_facebook_auth: ^4.0.0
```

Example usage:
```dart
import 'package:flutter_facebook_auth/flutter_facebook_auth.dart';

// Login with Facebook
final LoginResult result = await FacebookAuth.i.login(
  permissions: ['email', 'public_profile'],
);

if (result.status == LoginStatus.success) {
  final AccessToken accessToken = result.accessToken!;
  // Send accessToken.token to backend
  final response = await http.post(
    Uri.parse('$apiUrl/auth/facebook/login'),
    body: json.encode({'token': accessToken.token}),
    headers: {'Content-Type': 'application/json'},
  );
}
```

## Troubleshooting

### Common Issues

1. **Invalid OAuth redirect URI**
   - Ensure redirect URIs are exactly matched in Facebook Developer Portal
   - Include both HTTP and HTTPS versions if needed

2. **App not available to general public**
   - For development, add testers in the Roles section
   - For production, submit your app for review

3. **Email permission not granted**
   - Ensure you request 'email' scope
   - User must grant email permission during login

4. **Token validation errors**
   - Check that your App Secret is correct
   - Verify token hasn't expired

### Debug Endpoints

Use the test endpoint to verify configuration:
```bash
curl http://localhost:8000/api/v1/auth/facebook/test
```

## Security Considerations

1. **Never expose App Secret** - Keep it in environment variables only
2. **Validate redirect URIs** - Prevent open redirect vulnerabilities
3. **Use HTTPS in production** - Protect tokens during transmission
4. **Implement proper error handling** - Don't expose sensitive error details

## Production Deployment

1. Update redirect URIs to your production domain
2. Submit your app for Facebook review
3. Set proper app permissions and data access
4. Monitor API usage and errors

## Support

If you encounter issues:
1. Check Facebook Developer Documentation
2. Verify all environment variables are set
3. Test with the `/test` endpoint first
4. Check server logs for detailed error messages
