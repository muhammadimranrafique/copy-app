from database import engine
from sqlalchemy import text
import requests

# Check database
print("=== Database Check ===")
with engine.connect() as conn:
    result = conn.execute(text('SELECT COUNT(*) FROM products'))
    count = result.scalar()
    print(f'Products count: {count}')
    
    if count > 0:
        result = conn.execute(text('SELECT id, name, is_active FROM products LIMIT 3'))
        rows = result.fetchall()
        print(f'Sample products:')
        for row in rows:
            print(f'  - {row}')

# Test API endpoint
print("\n=== API Test ===")
s = requests.Session()
resp = s.post('http://127.0.0.1:8000/api/v1/auth/login', 
              data={'username': 'admin', 'password': 'admin123'})
print(f'Login status: {resp.status_code}')

if resp.status_code == 200:
    token = resp.json().get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    resp = s.get('http://127.0.0.1:8000/api/v1/products/', headers=headers)
    print(f'Products endpoint status: {resp.status_code}')
    
    if resp.status_code == 200:
        products = resp.json()
        print(f'Products returned: {len(products)}')
        if products:
            print(f'First product: {products[0]}')
    else:
        print(f'Error: {resp.text}')
