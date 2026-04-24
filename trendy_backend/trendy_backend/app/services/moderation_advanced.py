from textblob import TextBlob
from app.services.moderation_engine import AIModerationService

class ModerationAdvanced:
    def __init__(self):
        self.base = AIModerationService()

    def analyze_comment(self, text: str):
        # sentiment analysis via TextBlob (dev-only)
        blob = TextBlob(text or "")
        polarity = blob.sentiment.polarity
        result = self.base.analyze_text(text)
        result.update({"sentiment": polarity})
        # if strongly negative or contains flags mark for review
        flagged = (polarity < -0.6) or (len(result.get("flags", []))>0)
        result["needs_review"] = flagged
        return result
