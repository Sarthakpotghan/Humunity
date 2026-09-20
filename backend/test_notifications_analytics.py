from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Login donor
resp = client.post('/auth/login', json={
    'email': 'donor@test.com', 'password': 'password123'
})
print('Login donor:', resp.status_code)
donor_token = resp.json()['access_token']
donor_headers = {'Authorization': f'Bearer {donor_token}'}

# Login NGO
resp = client.post('/auth/login', json={
    'email': 'ngo@test.com', 'password': 'password123'
})
print('Login NGO:', resp.status_code)
ngo_token = resp.json()['access_token']
ngo_headers = {'Authorization': f'Bearer {ngo_token}'}

# Login Admin
resp = client.post('/auth/login', json={
    'email': 'admin@test.com', 'password': 'password123'
})
print('Login Admin:', resp.status_code)
admin_token = resp.json()['access_token']
admin_headers = {'Authorization': f'Bearer {admin_token}'}

# Test notifications for donor
resp = client.get('/notifications', headers=donor_headers)
print('Donor notifications:', resp.status_code, resp.json())

# Test notifications for NGO
resp = client.get('/notifications', headers=ngo_headers)
print('NGO notifications:', resp.status_code, resp.json())

# Test mark all read
resp = client.patch('/notifications/read-all', headers=donor_headers)
print('Mark all read:', resp.status_code)

# Test analytics (admin only)
resp = client.get('/analytics/summary', headers=admin_headers)
print('Analytics summary:', resp.status_code, resp.json())

resp = client.get('/analytics/heatmap', headers=admin_headers)
print('Analytics heatmap:', resp.status_code, resp.json())

resp = client.get('/analytics/trends', headers=admin_headers)
print('Analytics trends:', resp.status_code, resp.json())

# Test analytics with NGO (should fail)
resp = client.get('/analytics/summary', headers=ngo_headers)
print('Analytics with NGO:', resp.status_code, resp.json())