def detect_offensive_content(text: str) -> bool:
    # Simple example (replace with real ML later)
    bad_words = ["hate", "violence", "kill"]
    for word in bad_words:
        if word in text.lower():
            return True
    return False
