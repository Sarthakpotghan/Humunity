from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Login donor
resp = client.post('/auth/login', json={
    'email': 'donor@test.com', 'password': 'password123'
})
print('Login:', resp.status_code)
token = resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Create delivery
resp = client.post('/deliveries', json={
    'match_id': 1,
    'mode': 'dropoff',
    'scheduled_at': '2026-09-25T10:00:00'
}, headers=headers)
print('Create delivery:', resp.status_code, resp.json())

delivery_id = resp.json()['id']

# Update delivery status to in_transit
resp = client.patch(f'/deliveries/{delivery_id}/status', json={
    'status': 'in_transit'
}, headers=headers)
print('Update to in_transit:', resp.status_code, resp.json())

# Update delivery status to delivered
resp = client.patch(f'/deliveries/{delivery_id}/status', json={
    'status': 'delivered'
}, headers=headers)
print('Update to delivered:', resp.status_code, resp.json())

# Update delivery status to confirmed
resp = client.patch(f'/deliveries/{delivery_id}/status', json={
    'status': 'confirmed'
}, headers=headers)
print('Update to confirmed:', resp.status_code, resp.json())

# Get delivery route
resp = client.get(f'/deliveries/{delivery_id}/route', headers=headers)
print('Get route:', resp.status_code, resp.json())