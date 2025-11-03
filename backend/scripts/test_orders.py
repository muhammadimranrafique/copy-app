import requests

BASE = "http://127.0.0.1:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

s = requests.Session()

# Login
print("Logging in...")
resp = s.post(f"{BASE}/api/v1/auth/login", data={"username": ADMIN_USER, "password": ADMIN_PASS})
print(f"Login status: {resp.status_code}")
if resp.status_code != 200:
    print(f"Login failed: {resp.text}")
    exit(1)

access = resp.json().get("access_token")
headers = {"Authorization": f"Bearer {access}"}

# Test GET orders endpoint
print("\nTesting GET /api/v1/orders/")
resp = s.get(f"{BASE}/api/v1/orders/", headers=headers)
print(f"GET orders status: {resp.status_code}")
print(f"Response headers: {dict(resp.headers)}")
if resp.status_code != 200:
    print(f"GET orders error: {resp.text}")
else:
    orders = resp.json()
    print(f"Orders response: {orders}")
    print(f"Orders count: {len(orders) if isinstance(orders, list) else 'Not a list'}")

# Test GET orders endpoint without trailing slash
print("\nTesting GET /api/v1/orders (no trailing slash)")
resp = s.get(f"{BASE}/api/v1/orders", headers=headers)
print(f"GET orders (no slash) status: {resp.status_code}")
print(f"Response headers: {dict(resp.headers)}")
if resp.status_code != 200:
    print(f"GET orders (no slash) error: {resp.text}")
else:
    orders = resp.json()
    print(f"Orders response: {orders}")