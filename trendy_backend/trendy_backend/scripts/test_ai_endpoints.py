#!/usr/bin/env python3
"""
Test script for AI features endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_translate_text():
    """Test the text translation endpoint"""
    print("Testing text translation...")
    
    url = f"{BASE_URL}/api/ai/translate"
    payload = {
        "text": "Hello, how are you today?",
        "target_language": "es",
        "source_language": "en"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Translation successful: {result['translated_text']}")
            return True
        else:
            print(f"[FAIL] Translation failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Translation error: {e}")
        return False

def test_analyze_mood():
    """Test the mood analysis endpoint"""
    print("Testing mood analysis...")
    
    url = f"{BASE_URL}/api/ai/analyze-mood"
    payload = {
        "text": "I'm so excited about this new feature! It's going to be amazing!"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Mood analysis successful: {result['detected_mood']} (confidence: {result['confidence']})")
            return True
        else:
            print(f"[FAIL] Mood analysis failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Mood analysis error: {e}")
        return False

def test_smart_edit_suggest():
    """Test the smart editing suggestions endpoint"""
    print("Testing smart editing suggestions...")
    
    url = f"{BASE_URL}/api/ai/smart-edit/suggest"
    payload = {
        "text": "This is a sample text that could use some improvement."
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Smart edit suggestions successful: {len(result)} suggestions")
            for suggestion in result:
                print(f"  - {suggestion['suggestion']}")
            return True
        else:
            print(f"[FAIL] Smart edit suggestions failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Smart edit suggestions error: {e}")
        return False

def test_smart_edit_auto():
    """Test the auto-edit text endpoint"""
    print("Testing auto-edit text...")
    
    url = f"{BASE_URL}/api/ai/smart-edit/auto"
    payload = {
        "text": "This is a sample text that could use some improvement."
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Auto-edit successful: {result['edited_text']}")
            print(f"  Suggestions: {len(result['suggestions'])}")
            return True
        else:
            print(f"[FAIL] Auto-edit failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Auto-edit error: {e}")
        return False

def test_get_languages():
    """Test the get supported languages endpoint"""
    print("Testing get supported languages...")
    
    url = f"{BASE_URL}/api/ai/languages"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Languages retrieved successfully: {len(result['languages'])} languages")
            return True
        else:
            print(f"[FAIL] Languages retrieval failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Languages retrieval error: {e}")
        return False

def test_get_moods():
    """Test the get supported moods endpoint"""
    print("Testing get supported moods...")
    
    url = f"{BASE_URL}/api/ai/moods"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Moods retrieved successfully: {len(result['moods'])} moods")
            return True
        else:
            print(f"[FAIL] Moods retrieval failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Moods retrieval error: {e}")
        return False

def main():
    """Run all tests"""
    print("Running AI Features API Tests\n")
    
    tests = [
        test_get_languages,
        test_get_moods,
        test_translate_text,
        test_analyze_mood,
        test_smart_edit_suggest,
        test_smart_edit_auto,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()  # Add a blank line between tests
    
    print(f"Tests completed: {passed}/{total} passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed!")
    else:
        print(f"[FAILURE] {total - passed} tests failed. Please check the API implementation.")

if __name__ == "__main__":
    main()