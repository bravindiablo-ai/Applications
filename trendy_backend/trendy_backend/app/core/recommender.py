from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, timedelta
import json

class TrendyRecommender:
    """AI-based recommendation engine for music, movies, and shopping"""
    
    def __init__(self):
        self.user_profiles = {}
        self.content_vectors = {}
        self.interaction_weights = {
            'like': 1.0,
            'play': 0.8,
            'skip': -0.5,
            'complete': 1.5,
            'share': 2.0,
            'save': 1.2
        }
    
    def update_user_profile(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user profile based on interactions"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preferences': {},
                'interaction_history': [],
                'last_updated': datetime.now()
            }
        
        # Update interaction history
        self.user_profiles[user_id]['interaction_history'].append({
            'content_id': interaction_data.get('content_id'),
            'content_type': interaction_data.get('content_type'),
            'action': interaction_data.get('action'),
            'timestamp': datetime.now(),
            'metadata': interaction_data.get('metadata', {})
        })
        
        # Update preferences based on interaction
        self._update_preferences(user_id, interaction_data)
    
    def _update_preferences(self, user_id: str, interaction_data: Dict[str, Any]):
        """Update user preferences based on interaction"""
        content_type = interaction_data.get('content_type')
        action = interaction_data.get('action')
        metadata = interaction_data.get('metadata', {})
        
        if content_type not in self.user_profiles[user_id]['preferences']:
            self.user_profiles[user_id]['preferences'][content_type] = {}
        
        # Update genre preferences
        if 'genre' in metadata:
            genre = metadata['genre']
            weight = self.interaction_weights.get(action, 0.5)
            if genre not in self.user_profiles[user_id]['preferences'][content_type]:
                self.user_profiles[user_id]['preferences'][content_type][genre] = 0
            self.user_profiles[user_id]['preferences'][content_type][genre] += weight
        
        # Update artist/brand preferences
        if 'artist' in metadata or 'brand' in metadata:
            key = metadata.get('artist') or metadata.get('brand')
            weight = self.interaction_weights.get(action, 0.5)
            if key not in self.user_profiles[user_id]['preferences'][content_type]:
                self.user_profiles[user_id]['preferences'][content_type][key] = 0
            self.user_profiles[user_id]['preferences'][content_type][key] += weight
    
    def get_recommendations(self, user_id: str, content_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        if user_id not in self.user_profiles:
            return self._get_trending_recommendations(content_type, limit)
        
        user_prefs = self.user_profiles[user_id]['preferences'].get(content_type, {})
        if not user_prefs:
            return self._get_trending_recommendations(content_type, limit)
        
        # Calculate similarity scores
        recommendations = []
        # This is a simplified version - in production, use collaborative filtering or neural networks
        
        return recommendations
    
    def _get_trending_recommendations(self, content_type: str, limit: int) -> List[Dict[str, Any]]:
        """Get trending recommendations when no user profile exists"""
        # Mock trending recommendations
        return [
            {"id": f"{content_type}_{i}", "score": 0.8 - (i * 0.1)}
            for i in range(min(limit, 10))
        ]
    
    def get_daily_feed(self, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Generate daily personalized feed"""
        feed = {
            'music': self.get_recommendations(user_id, 'music', 5),
            'movies': self.get_recommendations(user_id, 'movies', 3),
            'products': self.get_recommendations(user_id, 'shop', 4)
        }
        return feed
    
    def calculate_similarity(self, user_vector: Dict[str, float], content_vector: Dict[str, float]) -> float:
        """Calculate similarity between user preferences and content"""
        # Simple cosine similarity implementation
        common_keys = set(user_vector.keys()) & set(content_vector.keys())
        if not common_keys:
            return 0.0
        
        dot_product = sum(user_vector[k] * content_vector[k] for k in common_keys)
        user_magnitude = np.sqrt(sum(v**2 for v in user_vector.values()))
        content_magnitude = np.sqrt(sum(v**2 for v in content_vector.values()))
        
        if user_magnitude == 0 or content_magnitude == 0:
            return 0.0
        
        return dot_product / (user_magnitude * content_magnitude)

# Global recommender instance
recommender = TrendyRecommender()
