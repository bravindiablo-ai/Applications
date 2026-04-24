import random
class AIModerationService:
    def analyze_text(self, text):
        bad = ["kill","nude","terror","bomb"]
        flags = [w for w in bad if w in (text or "").lower()]
        score = min(1.0, len(flags) * 0.5)
        return {"approved": score < 0.6, "flags": flags, "score": score}

    def analyze_file(self, filename):
        return {"approved": True, "score": 0.1, "flags": []}
