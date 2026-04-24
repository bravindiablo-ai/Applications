from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Dict, Any, List
import json

class AnalyticsEngine:
    "Analytics and activity tracking engine"
    
    def __init__(self):
        self.analytics_db = {}
        
    def track_event(self, user_id: str, event_type: str, event_data: Dict[str, Any]):
        "Track user events"
        if user_id not in self.analytics_db:
            self.analytics_db[user_id] = []
        
        self.analytics_db[user_id].append({
            'event_type': event_type,
            'event_data': event_data,
            'timestamp': datetime.now()
        })
    
    def get_user_analytics(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        "Get user analytics for specified days"
        if user_id not in self.analytics_db:
            return {}
        
        events = [e for e in self.analytics_db[user_id] if e['timestamp'] > datetime.now() - timedelta(days=days)]
        
        return {
            'total_events': len(events),
            'event_types': {},
            'timeline': events
        }
    
    def get_site_analytics(self, days: int = 30) -> Dict[str, Any]:
        "Get site-wide analytics"
        total_events = 0
        event_types = {}
        
        for user_id, events in self.analytics_db.items():
            for event in events:
                if event['timestamp'] > datetime.now() - timedelta(days=days):
                    total_events += 1
                    event_type = event['event_type']
                    event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            'total_events': total_events,
            'event_types': event_types
        }
