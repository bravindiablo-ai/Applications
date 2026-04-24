# Trendy

Trendy is a comprehensive social media platform built with Flutter, featuring real-time feeds, content hubs for music, movies, and sports, video calling, chat, and monetization systems. It integrates with a FastAPI backend for robust API services and uses Firebase for authentication and storage.

## Project Overview

Trendy is a modern social media application that combines traditional social networking with specialized content hubs. Users can share posts, engage with content, participate in real-time chat and video calls, and explore curated content in music, movies, and sports categories. The app includes monetization features like ads and subscriptions, powered by a scalable FastAPI backend.

## Features

- **Authentication**: Email/password, Google, Facebook, and Apple sign-in via Firebase
- **Social Feed**: Posts with text, images, videos, likes, comments, and shares
- **Content Hubs**: Dedicated sections for music, movies, and sports with trending content
- **Real-time Chat**: One-on-one and group messaging with Agora RTM
- **Video Calling**: High-quality video calls using Agora RTC
- **Monetization**: AdMob integration for ads, subscription tiers
- **Notifications**: Push notifications for interactions and updates
- **Rewards System**: Points, leaderboards, and referral programs
- **Analytics**: User engagement tracking and insights

## Prerequisites

- Flutter SDK (version 3.0 or higher)
- Dart SDK (version 2.19 or higher)
- Firebase account and project setup
- Agora account for video calling and messaging
- Running Trendy backend (see main README at `c:/Users/BRVINX.LV/final/vibes4/README.md`)

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd trendy
   ```

2. **Install dependencies**:
   ```bash
   flutter pub get
   ```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env`
   - Fill in required values (API_BASE_URL, Firebase credentials, Agora keys, AdMob IDs)
   - For Android emulator, set `API_BASE_URL=http://10.0.2.2:8000`
   - For iOS simulator or physical devices, use `http://localhost:8000`

4. **Set up Firebase**:
   - Download `google-services.json` from Firebase console
   - Place it in `android/app/google-services.json`
   - Configure iOS if deploying to iOS

5. **Run the backend**:
   - Follow setup instructions in `c:/Users/BRVINX.LV/final/vibes4/README.md`
   - Ensure the backend is running on the configured port

6. **Run the app**:
   ```bash
   flutter run
   ```

## Project Structure

The `lib/` directory is organized as follows:

- `main.dart`: Application entry point with Firebase initialization and provider setup
- `config/`: App configuration, themes, and routes
- `models/`: Data models matching backend schemas (UserProfile, Post, Song, etc.)
- `services/`: API services, authentication, storage, and third-party integrations
- `providers/`: State management using Provider pattern for auth, posts, users, etc.
- `screens/`: Main UI screens (auth, home, profile, content hubs, etc.)
- `views/`: Specialized views for chat, discover, post creation, and profile components
- `widgets/`: Reusable UI components (post widgets, headers, etc.)
- `data/`: Dummy data for development and testing

## Configuration Guide

### Firebase Setup
1. Create a Firebase project at https://console.firebase.google.com/
2. Enable Authentication with email/password, Google, Facebook providers
3. Enable Firestore, Storage, and Cloud Messaging
4. Download `google-services.json` and place in `android/app/`
5. Update `.env` with Firebase credentials from the console

### Agora Setup
1. Create an Agora account at https://console.agora.io/
2. Create a project and note the App ID and App Certificate
3. Update `.env` with `AGORA_APP_ID` and `AGORA_APP_CERTIFICATE`
4. Enable RTC and RTM services

### AdMob Setup
1. Create an AdMob account and app
2. Get App IDs and Ad Unit IDs
3. Update `.env` with AdMob configuration
4. Add test device IDs for development

## Backend Integration

The app integrates with the FastAPI backend running on the configured `API_BASE_URL`. Key endpoints include:

- **Authentication**: `/api/v1/auth/login`, `/api/v1/auth/register` for user auth
- **Posts**: `/api/v1/posts` for CRUD operations on posts
- **Social**: `/api/v1/followers/*` for follow/unfollow, `/api/v1/notifications` for notifications
- **Content**: `/api/v1/content/music/*`, `/api/v1/content/movies/*`, `/api/v1/content/football/*` for content hubs
- **Agora**: `/api/v1/agora/token` for generating video call tokens
- **Monetization**: `/api/v1/monetization/*` for subscriptions and ads

The app uses `BackendApiService` to handle HTTP requests with JWT authentication. All API responses are parsed into model objects for type safety.

## Troubleshooting

### Common Issues

- **Backend connection failed**: Ensure backend is running and `API_BASE_URL` is correct. For emulator, use `10.0.2.2:8000`
- **Firebase initialization error**: Verify `google-services.json` is in the correct location and credentials are valid
- **Video calling not working**: Check Agora credentials and ensure microphone/camera permissions are granted
- **Ads not showing**: Verify AdMob configuration and use test IDs in development
- **Build failures**: Run `flutter clean` and `flutter pub get`, ensure Flutter version is compatible

### Debug Tips
- Enable logging in `ApiService` to see request/response details
- Use Flutter DevTools for performance profiling
- Check device logs for native platform errors

## Contributing Guidelines

1. Follow Flutter best practices and the existing code style
2. Use Provider for state management and keep business logic in services/providers
3. Write comprehensive tests for new features
4. Update models when backend schemas change
5. Reference backend API documentation for new endpoints
6. Test on multiple devices and screen sizes

For backend contributions, see the main project README at `c:/Users/BRVINX.LV/final/vibes4/README.md`.