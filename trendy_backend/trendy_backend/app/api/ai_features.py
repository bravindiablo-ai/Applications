from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.auth.middleware import get_current_user
from pydantic import BaseModel
import requests
import os
from datetime import datetime

router = APIRouter(prefix="/ai", tags=["AI Features"])

# Mock translation service (in production, use Google Translate, AWS Translate, etc.)
class TranslationService:
    def __init__(self):
        # Mock language codes
        self.languages = {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
    
    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> Dict[str, Any]:
        """
        Mock translation service - in production, integrate with real translation API
        """
        # This is a mock implementation - in production, use:
        # Google Cloud Translation: https://cloud.google.com/translate
        # AWS Translate: https://aws.amazon.com/translate/
        # Azure Translator: https://azure.microsoft.com/en-us/services/cognitive-services/translator/
        
        # For demo purposes, we'll just return the same text with a note
        return {
            "translated_text": f"[Translated to {self.languages.get(target_language, target_language)}]: {text}",
            "source_language": source_language,
            "target_language": target_language,
            "confidence": 0.95
        }

# Mock sentiment analysis service
class SentimentAnalyzer:
    def __init__(self):
        # Simple mood mapping
        self.mood_keywords = {
            "happy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "love", "celebrate"],
            "sad": ["sad", "depressed", "upset", "disappointed", "angry", "frustrated", "lonely"],
            "excited": ["excited", "thrilled", "amazing", "awesome", "fantastic", "incredible"],
            "chill": ["relaxed", "calm", "peaceful", "quiet", "serene", "mellow"],
            "hype": ["hype", "lit", "fire", "trending", "viral", "popular"]
        }
    
    def analyze_mood(self, text: str) -> str:
        """
        Simple mood analysis based on keywords
        In production, use NLP models like VADER, TextBlob, or cloud services
        """
        text_lower = text.lower()
        mood_scores = {}
        
        for mood, keywords in self.mood_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            mood_scores[mood] = score
        
        # Return the mood with highest score, default to "neutral"
        if any(mood_scores.values()):
            return max(mood_scores, key=mood_scores.get)
        return "neutral"

# Mock smart editing service
class SmartEditor:
    def __init__(self):
        self.editing_suggestions = [
            "Consider adding more details to make your point clearer.",
            "This sentence could be rephrased for better flow.",
            "Adding an example here would strengthen your message.",
            "Consider breaking this long paragraph into shorter ones.",
            "This transition could be smoother with a connecting word.",
            "Adding a call-to-action would engage your audience more.",
            "Consider using more descriptive language to paint a vivid picture.",
            "This section might benefit from a bullet point list for clarity."
        ]
    
    def suggest_edits(self, text: str) -> List[str]:
        """
        Provide editing suggestions
        In production, use grammar checking APIs like Grammarly, LanguageTool, or cloud services
        """
        # For demo, return random suggestions
        import random
        num_suggestions = min(random.randint(1, 3), len(self.editing_suggestions))
        return random.sample(self.editing_suggestions, num_suggestions)
    
    def auto_edit(self, text: str) -> str:
        """
        Apply automatic edits
        In production, use advanced NLP models for text improvement
        """
        # For demo, just return the text with a note
        return f"[Auto-edited]: {text}"

# Initialize services
translation_service = TranslationService()
sentiment_analyzer = SentimentAnalyzer()
smart_editor = SmartEditor()

# Pydantic models
class TranslationRequest(BaseModel):
    text: str
    target_language: str
    source_language: str = "auto"

class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float

class MoodAnalysisRequest(BaseModel):
    text: str

class MoodAnalysisResponse(BaseModel):
    text: str
    detected_mood: str
    confidence: float

class EditingSuggestion(BaseModel):
    suggestion: str

class SmartEditRequest(BaseModel):
    text: str

class SmartEditResponse(BaseModel):
    original_text: str
    edited_text: str
    suggestions: List[EditingSuggestion]

class MoodBasedFeedRequest(BaseModel):
    preferred_mood: str
    limit: int = 20

# API Endpoints

@router.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text to a specified language
    In production, integrate with Google Cloud Translation, AWS Translate, or similar services
    """
    try:
        result = translation_service.translate_text(
            request.text, 
            request.target_language, 
            request.source_language
        )
        
        return TranslationResponse(
            original_text=request.text,
            translated_text=result["translated_text"],
            source_language=result["source_language"],
            target_language=result["target_language"],
            confidence=result["confidence"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/posts/{post_id}/translate")
async def translate_post(
    post_id: int,
    target_language: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Translate a specific post to the user's preferred language
    """
    try:
        # Get the post
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Translate the content
        translation_result = translation_service.translate_text(
            post.content, 
            target_language
        )
        
        # In a real implementation, you might want to store the translation
        # in the database for future use
        
        return {
            "post_id": post_id,
            "original_content": post.content,
            "translated_content": translation_result["translated_text"],
            "target_language": target_language,
            "confidence": translation_result["confidence"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Post translation failed: {str(e)}")

@router.post("/analyze-mood", response_model=MoodAnalysisResponse)
async def analyze_text_mood(request: MoodAnalysisRequest):
    """
    Analyze the mood of a text
    In production, use sentiment analysis APIs like Google Cloud Natural Language,
    AWS Comprehend, or Azure Text Analytics
    """
    try:
        detected_mood = sentiment_analyzer.analyze_mood(request.text)
        
        # Confidence is mocked for demo
        confidence = 0.85 if detected_mood != "neutral" else 0.5
        
        return MoodAnalysisResponse(
            text=request.text,
            detected_mood=detected_mood,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mood analysis failed: {str(e)}")

@router.get("/feed/mood-based")
async def get_mood_based_feed(
    preferred_mood: str = Query("happy", description="Preferred mood for feed"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Get a mood-based feed of posts
    """
    try:
        # Get all posts (in production, you'd want to filter by user's network)
        posts = db.query(Post).order_by(Post.created_at.desc()).limit(100).all()
        
        # Filter posts by mood
        mood_filtered_posts = []
        for post in posts:
            mood = sentiment_analyzer.analyze_mood(post.content)
            if mood == preferred_mood or preferred_mood == "all":
                mood_filtered_posts.append(post)
                if len(mood_filtered_posts) >= limit:
                    break
        
        # Format the response
        result_posts = []
        for post in mood_filtered_posts:
            user = db.query(User).filter(User.id == post.user_id).first()
            result_posts.append({
                "id": post.id,
                "content": post.content,
                "mood": sentiment_analyzer.analyze_mood(post.content),
                "created_at": post.created_at,
                "user": {
                    "id": user.id if user else None,
                    "username": user.username if user else "Unknown"
                }
            })
        
        return {
            "posts": result_posts,
            "total": len(result_posts),
            "preferred_mood": preferred_mood
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get mood-based feed: {str(e)}")

@router.post("/smart-edit/suggest", response_model=List[EditingSuggestion])
async def suggest_edits(request: SmartEditRequest):
    """
    Get smart editing suggestions for text
    In production, use grammar checking APIs or NLP models
    """
    try:
        suggestions = smart_editor.suggest_edits(request.text)
        return [EditingSuggestion(suggestion=suggestion) for suggestion in suggestions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate editing suggestions: {str(e)}")

@router.post("/smart-edit/auto", response_model=SmartEditResponse)
async def auto_edit_text(request: SmartEditRequest):
    """
    Automatically edit text for better quality
    In production, use advanced NLP models for text improvement
    """
    try:
        edited_text = smart_editor.auto_edit(request.text)
        suggestions = smart_editor.suggest_edits(request.text)
        
        return SmartEditResponse(
            original_text=request.text,
            edited_text=edited_text,
            suggestions=[EditingSuggestion(suggestion=suggestion) for suggestion in suggestions]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auto-editing failed: {str(e)}")

@router.post("/posts/{post_id}/auto-edit")
async def auto_edit_post(
    post_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    """
    Automatically edit a post for better quality
    """
    try:
        # Get the post
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check if user is authorized to edit this post
        if post.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit this post")
        
        # Auto-edit the content
        edited_content = smart_editor.auto_edit(post.content)
        suggestions = smart_editor.suggest_edits(post.content)
        
        # Update the post with edited content (in a real implementation, you might want to keep the original)
        post.content = edited_content
        post.is_edited = True
        db.commit()
        
        return {
            "post_id": post_id,
            "original_content": post.content,
            "edited_content": edited_content,
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-edit post: {str(e)}")

@router.get("/languages")
async def get_supported_languages():
    """
    Get a list of supported languages for translation
    """
    return {
        "languages": [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "zh", "name": "Chinese"}
        ]
    }

@router.get("/moods")
async def get_supported_moods():
    """
    Get a list of supported moods for mood-based feed
    """
    return {
        "moods": [
            "happy",
            "sad",
            "excited",
            "chill",
            "hype",
            "neutral"
        ]
    }
