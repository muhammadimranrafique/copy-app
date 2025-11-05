#!/usr/bin/env python3
"""
Test script to verify Swagger UI authentication is working properly.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_authentication_flow():
    """Test the complete authentication flow."""
    print("🔍 Testing Swagger UI Authentication Flow")
    print("=" * 50)
    
    # Test 1: Check if API is running
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the server is running on localhost:8000")
        return False
    
    # Test 2: Check OpenAPI schema
    print("\n2. Testing OpenAPI Schema...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            
            # Check if security schemes are defined
            if "components" in openapi_data and "securitySchemes" in openapi_data["components"]:
                security_schemes = openapi_data["components"]["securitySchemes"]
                print("✅ Security schemes found:")
                for scheme_name, scheme_data in security_schemes.items():
                    print(f"   - {scheme_name}: {scheme_data.get('type', 'unknown')}")
            else:
                print("❌ No security schemes found in OpenAPI schema")
                return False
        else:
            print(f"❌ Failed to get OpenAPI schema: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking OpenAPI schema: {e}")
        return False
    
    # Test 3: Test login endpoint
    print("\n3. Testing Login Endpoint...")
    
    # First, let's create a test user (if not exists)
    test_user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "admin",
        "password": "testpass123"
    }
    
    # Try to register (might fail if user exists, that's OK)
    try:
        register_response = requests.post(f"{API_BASE}/auth/register", json=test_user_data)
        if register_response.status_code == 201:
            print("✅ Test user created successfully")
        elif register_response.status_code == 400:
            print("ℹ️  Test user already exists (that's OK)")
        else:
            print(f"⚠️  User registration response: {register_response.status_code}")
    except Exception as e:
        print(f"⚠️  Error during user registration: {e}")
    
    # Now test login
    login_data = {
        "username": test_user_data["email"],
        "password": test_user_data["password"]
    }
    
    try:
        # Use form data for OAuth2PasswordRequestForm
        response = requests.post(f"{API_BASE}/auth/login", data=login_data)
        
        if response.status_code == 200:
            login_result = response.json()
            access_token = login_result.get("access_token")
            token_type = login_result.get("token_type")
            
            if access_token and token_type == "bearer":
                print("✅ Login successful")
                print(f"   Token type: {token_type}")
                print(f"   Token preview: {access_token[:20]}...")
                
                # Test 4: Test protected endpoint
                print("\n4. Testing Protected Endpoint...")
                headers = {"Authorization": f"Bearer {access_token}"}
                
                try:
                    me_response = requests.get(f"{API_BASE}/auth/me", headers=headers)
                    if me_response.status_code == 200:
                        user_data = me_response.json()
                        print("✅ Protected endpoint access successful")
                        print(f"   User: {user_data.get('full_name')} ({user_data.get('email')})")
                        print(f"   Role: {user_data.get('role')}")
                        
                        # Test 5: Test another protected endpoint
                        print("\n5. Testing Orders Endpoint (Protected)...")
                        orders_response = requests.get(f"{API_BASE}/orders", headers=headers)
                        if orders_response.status_code == 200:
                            orders = orders_response.json()
                            print(f"✅ Orders endpoint accessible (found {len(orders)} orders)")
                        else:
                            print(f"❌ Orders endpoint failed: {orders_response.status_code}")
                            print(f"   Response: {orders_response.text}")
                        
                        return True
                    else:
                        print(f"❌ Protected endpoint failed: {me_response.status_code}")
                        print(f"   Response: {me_response.text}")
                        return False
                except Exception as e:
                    print(f"❌ Error testing protected endpoint: {e}")
                    return False
            else:
                print("❌ Login response missing token or wrong token type")
                print(f"   Response: {login_result}")
                return False
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return False

def print_swagger_instructions():
    """Print instructions for using Swagger UI."""
    print("\n" + "=" * 60)
    print("📋 SWAGGER UI AUTHENTICATION INSTRUCTIONS")
    print("=" * 60)
    print("\n1. Open Swagger UI in your browser:")
    print(f"   {BASE_URL}/docs")
    
    print("\n2. To authenticate:")
    print("   a) Click the 'Authorize' button (🔒) at the top right")
    print("   b) You'll see two authentication options:")
    print("      - OAuth2PasswordBearer (for login)")
    print("      - BearerAuth (for manual token entry)")
    
    print("\n3. Option A - Using OAuth2PasswordBearer:")
    print("   a) Click 'Authorize' next to OAuth2PasswordBearer")
    print("   b) Enter credentials:")
    print("      Username: test@example.com")
    print("      Password: testpass123")
    print("   c) Click 'Authorize'")
    
    print("\n4. Option B - Using BearerAuth (if you have a token):")
    print("   a) First get a token by calling /api/v1/auth/login")
    print("   b) Copy the access_token from the response")
    print("   c) Click 'Authorize' next to BearerAuth")
    print("   d) Paste the token (without 'Bearer ' prefix)")
    print("   e) Click 'Authorize'")
    
    print("\n5. Test protected endpoints:")
    print("   - Try /api/v1/auth/me")
    print("   - Try /api/v1/orders")
    print("   - Try /api/v1/products")
    
    print("\n6. If you see 🔒 icons next to endpoints, they require authentication")
    print("   After successful authentication, these should work without errors.")

if __name__ == "__main__":
    print("🚀 School Copy API - Swagger Authentication Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = test_authentication_flow()
    
    if success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Swagger UI authentication should now work properly.")
        print_swagger_instructions()
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the error messages above and ensure:")
        print("1. The FastAPI server is running (python main.py)")
        print("2. The database is properly initialized")
        print("3. All dependencies are installed")
    
    print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")