#!/usr/bin/env python3
"""
Test script for messaging endpoints
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def get_auth_token():
    """Get authentication token"""
    print("Getting auth token...")
    
    url = f"{BASE_URL}/login"
    payload = {
        "identifier": "testuser",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Auth token obtained successfully")
            return result['access_token']
        else:
            print(f"[FAIL] Auth failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Auth error: {e}")
        return None

def test_create_message(token):
    """Test creating a new message"""
    print("Testing create message...")
    
    url = f"{BASE_URL}/api/messages"
    payload = {
        "receiver_id": 2,
        "content": "Hello, this is a test message!",
        "message_type": "text"
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Message created successfully with ID: {result['id']}")
            return result['id']
        else:
            print(f"[FAIL] Message creation failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Message creation error: {e}")
        return None

def test_get_messages(token):
    """Test getting messages"""
    print("Testing get messages...")
    
    url = f"{BASE_URL}/api/messages"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Retrieved {len(result)} messages")
            return True
        else:
            print(f"[FAIL] Get messages failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Get messages error: {e}")
        return False

def test_create_group(token):
    """Test creating a new group"""
    print("Testing create group...")
    
    url = f"{BASE_URL}/api/groups"
    payload = {
        "name": "Test Group",
        "description": "A test group for messaging",
        "is_public": True
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Group created successfully with ID: {result['id']}")
            return result['id']
        else:
            print(f"[FAIL] Group creation failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Group creation error: {e}")
        return None

def test_create_voice_channel(group_id, token):
    """Test creating a voice channel"""
    print("Testing create voice channel...")
    
    url = f"{BASE_URL}/api/messages/voice-channels"
    payload = {
        "group_id": group_id,
        "name": "Test Voice Channel",
        "description": "A test voice channel"
    }
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Voice channel created successfully with ID: {result['id']}")
            return result['id']
        else:
            print(f"[FAIL] Voice channel creation failed with status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Voice channel creation error: {e}")
        return None

def test_join_voice_channel(channel_id, token):
    """Test joining a voice channel"""
    print("Testing join voice channel...")
    
    url = f"{BASE_URL}/api/messages/voice-channels/{channel_id}/join"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Joined voice channel successfully: {result['message']}")
            return True
        else:
            print(f"[FAIL] Join voice channel failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Join voice channel error: {e}")
        return False

def test_leave_voice_channel(channel_id, token):
    """Test leaving a voice channel"""
    print("Testing leave voice channel...")
    
    url = f"{BASE_URL}/api/messages/voice-channels/{channel_id}/leave"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"[PASS] Left voice channel successfully: {result['message']}")
            return True
        else:
            print(f"[FAIL] Leave voice channel failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Leave voice channel error: {e}")
        return False

def main():
    """Run all tests"""
    print("Running Messaging API Tests\n")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("Failed to get auth token, exiting...")
        return
    
    # Test message creation
    message_id = test_create_message(token)
    
    # Test getting messages
    test_get_messages(token)
    
    # Test group creation
    group_id = test_create_group(token)
    
    if group_id:
        # Test voice channel creation
        channel_id = test_create_voice_channel(group_id, token)
        
        if channel_id:
            # Test joining voice channel
            test_join_voice_channel(channel_id, token)
            
            # Test leaving voice channel
            test_leave_voice_channel(channel_id, token)
    
    print("\nMessaging API tests completed!")

if __name__ == "__main__":
    main()