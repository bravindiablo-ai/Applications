"""
Lightweight personalization placeholder.
- Uses a simple TF-IDF vectorization (or numeric proxies) in dev mode.
- Replace with real model/embedding service for production.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class PersonalizationOV:
    def __init__(self, db=None):
        self.db = db
        # In-memory sample corpus for dev; in prod use stored content features
        self.corpus = ["sample content one", "sample content two", "music upbeat", "travel vlog"]
        self.vectorizer = TfidfVectorizer()
        self.vectors = self.vectorizer.fit_transform(self.corpus)

    def recommend_for_user(self, user_id, limit=10):
        # mocked: return top-k pseudo content ids
        return [{"content_id": f"demo_{i}", "score": float(1/(i+1))} for i in range(limit)]
