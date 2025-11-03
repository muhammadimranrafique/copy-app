import requests
import json

def test_cors():
    """Test CORS headers and API functionality"""
    base_url = "http://127.0.0.1:8000/api/v1"
    origin = "http://localhost:5173"
    
    # Login to get token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    # Test preflight request
    preflight = requests.options(
        f"{base_url}/payments/",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type,authorization"
        }
    )
    print("\nPreflight Response Headers:")
    for key, value in preflight.headers.items():
        if key.lower().startswith('access-control'):
            print(f"{key}: {value}")
    
    # Login
    s = requests.Session()
    login_response = s.post(
        f"{base_url}/auth/login",
        data=login_data,
        headers={"Origin": origin}
    )
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    token = login_response.json().get("access_token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Origin": origin,
        "Content-Type": "application/json"
    }
    
    # Test GET payments
    payments_response = s.get(
        f"{base_url}/payments/",
        headers=headers
    )
    
    print("\nPayments Response:")
    print(f"Status Code: {payments_response.status_code}")
    print("Headers:")
    for key, value in payments_response.headers.items():
        if key.lower().startswith('access-control'):
            print(f"{key}: {value}")
    print("\nResponse Body:")
    print(json.dumps(payments_response.json(), indent=2) if payments_response.ok else payments_response.text)

if __name__ == "__main__":
    test_cors()