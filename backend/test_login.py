#!/usr/bin/env python3

import requests
import json

def test_login():
    """Test the login endpoint"""
    url = "http://127.0.0.1:8000/api/v1/auth/login"
    
    # Test data
    login_data = {
        "username": "arsal@gmail.com",  # OAuth2PasswordRequestForm uses 'username' field
        "password": "password123"
    }
    
    print("Testing login endpoint...")
    print(f"URL: {url}")
    print(f"Data: {login_data}")
    
    try:
        response = requests.post(url, data=login_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Login successful!")
            data = response.json()
            print(f"Access Token: {data.get('access_token', 'N/A')[:50]}...")
            print(f"User: {data.get('user', {})}")
        else:
            print("❌ Login failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_register():
    """Test the register endpoint"""
    url = "http://127.0.0.1:8000/api/v1/auth/register"
    
    register_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "staff",
        "password": "testpass123"
    }
    
    print("\nTesting register endpoint...")
    print(f"URL: {url}")
    print(f"Data: {register_data}")
    
    try:
        response = requests.post(url, json=register_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ Registration successful!")
        else:
            print("❌ Registration failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("School Copy Login Test")
    print("=" * 30)
    
    # Test login with the user we created
    test_login()
    
    # Test registration
    test_register()