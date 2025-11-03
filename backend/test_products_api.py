import requests
import json

BASE = "http://127.0.0.1:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

def test_products_api():
    s = requests.Session()
    
    # Login
    resp = s.post(f"{BASE}/api/v1/auth/login", data={"username": ADMIN_USER, "password": ADMIN_PASS})
    print("Login status:", resp.status_code)
    if resp.status_code != 200:
        print("Login failed:", resp.text)
        return
    
    access = resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {access}"}
    
    # Test GET products
    print("\n=== Testing GET /api/v1/products/ ===")
    resp = s.get(f"{BASE}/api/v1/products/", headers=headers)
    print("GET products status:", resp.status_code)
    if resp.status_code == 200:
        products = resp.json()
        print("Products response:", json.dumps(products, indent=2, default=str))
        print("Number of products:", len(products))
    else:
        print("GET products failed:", resp.text)
    
    # Test POST product
    print("\n=== Testing POST /api/v1/products/ ===")
    test_product = {
        "productName": "Test Product API",
        "category": "Test Category",
        "costPrice": 10.50,
        "salePrice": 15.75,
        "stockQuantity": 100,
        "unit": "pcs"
    }
    
    resp = s.post(f"{BASE}/api/v1/products/", json=test_product, headers=headers)
    print("POST product status:", resp.status_code)
    if resp.status_code == 201:
        created_product = resp.json()
        print("Created product:", json.dumps(created_product, indent=2, default=str))
        
        # Test GET products again to see if it appears
        print("\n=== Testing GET /api/v1/products/ after creation ===")
        resp = s.get(f"{BASE}/api/v1/products/", headers=headers)
        print("GET products status:", resp.status_code)
        if resp.status_code == 200:
            products = resp.json()
            print("Number of products after creation:", len(products))
            # Find our test product
            test_found = any(p.get('productName') == 'Test Product API' for p in products)
            print("Test product found in list:", test_found)
        else:
            print("GET products failed:", resp.text)
    else:
        print("POST product failed:", resp.text)

if __name__ == "__main__":
    test_products_api()