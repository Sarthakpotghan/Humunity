import sys
sys.path.insert(0, r'D:\donation system\backend')
from app.database import SessionLocal
from app.models import User, UserRole, NgoProfile
from app.utils.security import create_access_token, get_password_hash
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test with existing NGO user (ngo@test.com)
login_resp = client.post('/auth/login', json={'email': 'ngo@test.com', 'password': 'password123'})
print(f'Login status: {login_resp.status_code}')
token = login_resp.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

# Test GET /auth/ngo/profile
resp = client.get('/auth/ngo/profile', headers=headers)
print(f'GET /auth/ngo/profile status: {resp.status_code}')
print(f'Response: {resp.json()}')

# Test GET /requests
resp = client.get('/requests', headers=headers)
print(f'GET /requests status: {resp.status_code}')
print(f'Requests count: {len(resp.json())}')

# Test GET /requests/matches/all
resp = client.get('/requests/matches/all', headers=headers)
print(f'GET /requests/matches/all status: {resp.status_code}')
print(f'Matches count: {len(resp.json())}')

# Test creating a request
request_data = {
    'category': 'clothes',
    'item_type': 'Winter Jackets',
    'quantity_needed': 50,
    'urgency': 4,
    'beneficiary_group': 'Homeless families'
}
resp = client.post('/requests', json=request_data, headers=headers)
print(f'POST /requests status: {resp.status_code}')
if resp.status_code == 201:
    print(f'Created request: {resp.json()}')
else:
    print(f'Error: {resp.json()}')

print('All tests passed!')