# TRENDY v1.0 - REQUIRED CREDENTIALS CHECKLIST

## Instructions
This document lists ALL credentials and API keys required for TRENDY full-stack production deployment. Each credential must be obtained and provided to enable complete verification of the application.

---

## CRITICAL PRIORITY - MUST HAVE (Production Blocking)

### 1. PostgreSQL Database Connection
**Environment Variable:** `DATABASE_URL`
**Format:** `postgresql://user:password@host:port/database`
**Example:** `postgresql://trendy_user:secure_password@trendy-db.render.com:5432/trendy_production`
**Status:** ✅ ALREADY PROVIDED
**Where to Get:** Render.com PostgreSQL instance
**Purpose:** Main application database for users, posts, comments, likes, followers, etc.
**Verification Method:** Backend startup, connection pool test

---

## HIGH PRIORITY - REQUIRED FOR FULL VERIFICATION

### 2. Firebase Admin SDK Credentials (JSON File)
**Environment Variable:** `FIREBASE_CREDENTIALS_JSON`
**Format:** Base64-encoded JSON with the following structure:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----...",
  "client_email": "firebase-adminsdk-xxx@your-project-id.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```
**Where to Get:** Firebase Console > Project Settings > Service Accounts > Generate New Private Key
**Purpose:** Firebase Admin SDK initialization for user authentication and Firestore operations
**Verification Method:** Backend startup, Firebase connection test

### 3. Firebase Project ID
**Environment Variable:** `FIREBASE_PROJECT_ID`
**Format:** String (e.g., `trendy-app-prod`)
**Where to Get:** Firebase Console > Project Settings
**Purpose:** Identifies Firebase project for backend initialization
**Verification Method:** Cross-check with credentials JSON

### 4. Firebase Web API Key
**Environment Variable:** `FIREBASE_API_KEY` (Frontend)
**Format:** String (e.g., `AIzaSyD...`)
**Where to Get:** Firebase Console > Project Settings > Web Apps > Copy API Key
**Purpose:** Frontend Firebase initialization for user signup/login
**Verification Method:** Frontend .env configuration, Firebase connection test

### 5. Stripe Secret Key (Production)
**Environment Variable:** `STRIPE_SECRET_KEY`
**Format:** String starting with `sk_live_` (production) or `sk_test_` (sandbox)
**Test Key:** `sk_test_4eC39HqLyjWDarhtT657tLz69` (contains test card functionality)
**Sandbox Test Card:** `4242 4242 4242 4242` (expiry: any future date, CVC: any 3 digits)
**Where to Get:** Stripe Dashboard > Developers > API Keys > Secret Key
**Purpose:** Payment processing for monetization features
**Verification Method:** Payment endpoint test with test card

### 6. Stripe Publishable Key (Production)
**Environment Variable:** `STRIPE_PUBLISHABLE_KEY`
**Format:** String starting with `pk_live_` (production) or `pk_test_` (sandbox)
**Where to Get:** Stripe Dashboard > Developers > API Keys > Publishable Key
**Purpose:** Frontend payment form initialization
**Verification Method:** Frontend integration test

### 7. Stripe Webhook Secret
**Environment Variable:** `STRIPE_WEBHOOK_SECRET`
**Format:** String starting with `whsec_`
**Where to Get:** Stripe Dashboard > Developers > Webhooks > Signing Secret (for your endpoint)
**Purpose:** Verify webhook authenticity for payment confirmations
**Verification Method:** Webhook endpoint signature verification

---

## CORE FEATURES - HIGH IMPORTANCE

### 8. TMDB (The Movie Database) API Key
**Environment Variable:** `TMDB_API_KEY`
**Format:** String (32 characters)
**Where to Get:** https://www.themoviedb.org/settings/api > Request API Key > Copy API Key
**Purpose:** Movie/TV show content integration for enhanced_content routes
**Verification Method:** `/api/content/tmdb/{id}` endpoint test

### 9. Spotify Client ID & Secret
**Environment Variables:**
- `SPOTIFY_CLIENT_ID` - Format: String (32 characters)
- `SPOTIFY_CLIENT_SECRET` - Format: String (32 characters)
**Where to Get:** https://developer.spotify.com/dashboard > Create App > Get Client ID & Secret
**Purpose:** Music/track content integration and audio recommendations
**Verification Method:** Spotify token generation and content fetch test

### 10. Agora App ID & Certificate
**Environment Variables:**
- `AGORA_APP_ID` - Format: String
- `AGORA_APP_CERTIFICATE` - Format: String
**Where to Get:** Agora Console > Projects > Your Project > App ID and Certificate
**Purpose:** Real-time voice/video calling capabilities (chat_ws routes)
**Verification Method:** Token generation and channel creation test

### 11. Google AdMob Credentials
**Environment Variables:**
- `ADMOB_APP_ID` - Format: `ca-app-pub-xxxxxxxxxxxxxxxx`
- `ADMOB_BANNER_AD_ID` - Format: `ca-app-pub-3940256099942544/6300978111` (test ID)
- `ADMOB_INTERSTITIAL_AD_ID` - Format: `ca-app-pub-3940256099942544/1033173712` (test ID)
- `ADMOB_REWARDED_AD_ID` - Format: `ca-app-pub-3940256099942544/5224354917` (test ID)
**Where to Get:** Google AdMob Console > Apps > Your App > Ad Units
**Test Ad IDs:** Google provides test IDs for development (see formats above)
**Purpose:** In-app advertising for revenue generation
**Verification Method:** AdMob test ads load/display verification

---

## OPTIONAL/ENHANCED FEATURES

### 12. Redis Connection String (Optional - Already Configured)
**Environment Variable:** `REDIS_URL`
**Status:** ✅ ALREADY CONFIGURED (async support verified)
**Purpose:** Caching, real-time features, session management
**Verification Method:** Redis async client connection test

### 13. OpenAI API Key (For AI Moderation Fallback)
**Environment Variable:** `OPENAI_API_KEY`
**Format:** String starting with `sk-`
**Where to Get:** OpenAI API Dashboard > API Keys
**Purpose:** Fallback AI moderation if primary system fails
**Verification Method:** Optional - `/api/ai` endpoint test

### 14. Apple Music Credentials (Optional)
**Environment Variables:**
- `APPLE_MUSIC_KEY`
- `APPLE_MUSIC_TEAM_ID`
**Purpose:** Apple Music integration for content
**Status:** Optional - not critical for MVP

### 15. Additional APIs (Optional)
- `LYRICS_API_KEY` - Lyrics/song metadata
- `APISPORTS_KEY` - Football/sports data
- `GOOGLE_TRANSLATE_API_KEY` - Content translation

---

## FRONTEND REQUIREMENTS (.env in trendy/ directory)

### Firebase Configuration (Already in .env.example)
```
FIREBASE_API_KEY=<from step 4>
FIREBASE_AUTH_DOMAIN=your_project_id.firebaseapp.com
FIREBASE_PROJECT_ID=<from step 3>
FIREBASE_STORAGE_BUCKET=your_project_id.appspot.com
FIREBASE_MESSAGING_SENDER_ID=<from Firebase Console>
FIREBASE_APP_ID=<from Firebase Console>
```

### Stripe Frontend Configuration
```
STRIPE_PUBLISHABLE_KEY=<from step 6>
```

### AdMob Configuration
```
ADMOB_APP_ID=<from step 11>
```

---

## BACKEND REQUIREMENTS (.env in trendy_backend/ directory)

All environment variables documented in `trendy_backend/.env.example` (113 lines):
- Database connection
- All service keys listed above
- Feature flags
- Server configuration

---

## CREDENTIAL INPUT CHECKLIST

- [ ] **DATABASE_URL** - PostgreSQL connection (READY)
- [ ] **FIREBASE_CREDENTIALS_JSON** - Service account JSON (Base64 encoded)
- [ ] **FIREBASE_PROJECT_ID** - Project ID string
- [ ] **FIREBASE_API_KEY** - Web API key
- [ ] **STRIPE_SECRET_KEY** - Production or test key
- [ ] **STRIPE_PUBLISHABLE_KEY** - Production or test key
- [ ] **STRIPE_WEBHOOK_SECRET** - Webhook signing secret
- [ ] **TMDB_API_KEY** - Movie database API key
- [ ] **SPOTIFY_CLIENT_ID** - Spotify app ID
- [ ] **SPOTIFY_CLIENT_SECRET** - Spotify app secret
- [ ] **AGORA_APP_ID** - Agora project ID
- [ ] **AGORA_APP_CERTIFICATE** - Agora certificate
- [ ] **ADMOB_APP_ID** - AdMob app ID
- [ ] **ADMOB_BANNER_AD_ID** - AdMob banner ad unit ID
- [ ] **ADMOB_INTERSTITIAL_AD_ID** - AdMob interstitial ad unit ID
- [ ] **ADMOB_REWARDED_AD_ID** - AdMob rewarded ad unit ID
- [ ] **REDIS_URL** - Redis connection (OPTIONAL - already configured)
- [ ] **OPENAI_API_KEY** - OpenAI API key (OPTIONAL)

---

## NEXT STEPS

1. **Collect all credentials** from the services listed above
2. **Provide them to Comet** via chat message
3. **Comet will input credentials** into the Render dashboard environment variables
4. **Comet will execute complete verification** of all 18 production readiness tasks
5. **Comet will generate final JSON report** with PASS/FAIL status for each component

---

## VERIFICATION AFTER CREDENTIALS RECEIVED

Once all credentials are provided, Comet will verify:
1. ✅ Backend starts cleanly (no duplicate index/schema errors)
2. ✅ Health endpoint (`/api/health`) returns {"status":"ok"}
3. ✅ PostgreSQL connection established and functional
4. ✅ Firebase initializes successfully
5. ✅ Redis async connection established
6. ✅ All 19+ registered routes visible at `/docs`
7. ✅ Flutter frontend `.env` correctly configured
8. ✅ User signup/login via Firebase authentication
9. ✅ Data synchronization (posts, comments, likes, notifications)
10. ✅ AdMob test ads load and Stripe sandbox payments work
11. ✅ Content APIs (TMDB, Spotify, Agora token generation)
12. ✅ AI assistant endpoint `/api/ai` responds
13. ✅ Async services handle connection retries gracefully
14. ✅ All Pydantic models v2-compatible
15. ✅ Backend logs contain zero critical errors
16. ✅ All environment variables correctly mapped in Render
17. ✅ Critical endpoints return 200 responses
18. ✅ Generate final readiness report with score and recommendations

---

## VERSION INFO
- **Document Version:** 1.0
- **Application:** TRENDY v1.0 Full-Stack
- **Backend:** FastAPI
- **Frontend:** Flutter
- **Created:** Phase 4 Production Readiness Verification
