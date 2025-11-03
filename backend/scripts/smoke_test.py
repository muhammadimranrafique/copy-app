import requests
import os

BASE = "http://127.0.0.1:8000"
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"

s = requests.Session()
# Login (form data)
resp = s.post(f"{BASE}/api/v1/auth/login", data={"username": ADMIN_USER, "password": ADMIN_PASS})
print("login status", resp.status_code)
resp.raise_for_status()
access = resp.json().get("access_token")
print("token:", access[:20] + "..." if access else None)
headers = {"Authorization": f"Bearer {access}"}

# Get schools
resp = s.get(f"{BASE}/api/v1/schools", headers=headers)
resp.raise_for_status()
schools = resp.json()
print("schools:", schools)
if not schools:
    raise SystemExit("no schools available")
# pick Demo School
school = next((x for x in schools if x.get('name') == 'Demo School'), schools[0])
print('using school', school['id'], school['name'])

# Test GET orders endpoint first
resp = s.get(f"{BASE}/api/v1/orders/", headers=headers)
print('get orders status', resp.status_code)
if resp.status_code != 200:
    print('get orders error:', resp.text)
else:
    orders = resp.json()
    print('existing orders count:', len(orders))

# create order
order_payload = {
    "order_number": "ORD-1001",
    "client_id": school['id'],
    "total_amount": 250.50
}
resp = s.post(f"{BASE}/api/v1/orders", json=order_payload, headers=headers)
print('create order status', resp.status_code)
resp.raise_for_status()
order = resp.json()
print('created order', order)

# Test GET orders endpoint again after creating
resp = s.get(f"{BASE}/api/v1/orders/", headers=headers)
print('get orders after create status', resp.status_code)
if resp.status_code != 200:
    print('get orders after create error:', resp.text)
else:
    orders = resp.json()
    print('orders count after create:', len(orders))

# request invoice
out_dir = os.path.join(os.path.dirname(__file__), '..', 'invoices')
os.makedirs(out_dir, exist_ok=True)
outfile = os.path.join(out_dir, f"invoice_{order['order_number']}.pdf")
resp = s.post(f"{BASE}/api/v1/orders/{order['id']}/invoice", headers=headers, stream=True)
print('invoice status', resp.status_code)
resp.raise_for_status()
with open(outfile, 'wb') as f:
    for chunk in resp.iter_content(chunk_size=8192):
        if chunk:
            f.write(chunk)
print('saved invoice to', outfile)
