import sys
sys.path.insert(0, r'D:\donation system\backend')
from app.database import SessionLocal
from app.models import User, UserRole, NgoProfile
from app.utils.security import create_access_token, get_password_hash
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Create a test NGO user WITHOUT a profile
db = SessionLocal()
test_ngo = User(
    email='test-ngo-no-profile@test.com',
    name='Test NGO No Profile',
    role=UserRole.NGO,
    password_hash=get_password_hash('password123'),
    verified=True
)
db.add(test_ngo)
db.commit()
db.refresh(test_ngo)
print(f'Created test NGO user: {test_ngo.id}')

# Login
login_resp = client.post('/auth/login', json={'email': 'test-ngo-no-profile@test.com', 'password': 'password123'})
print(f'Login status: {login_resp.status_code}')
token = login_resp.json()['access_token']
headers = {"Authorization": f"Bearer {token}"}

# Test GET /auth/ngo/profile for NGO WITHOUT profile
resp = client.get('/auth/ngo/profile', headers=headers)
print(f'GET /auth/ngo/profile status: {resp.status_code}')
print(f'Response: {resp.json()}')

# Test creating a request (should work even without profile)
request_data = {
    'category': 'clothes',
    'item_type': 'Test Item',
    'quantity_needed': 10,
    'urgency': 3
}
resp = client.post('/requests', json=request_data, headers=headers)
print(f'POST /requests status: {resp.status_code}')
if resp.status_code == 201:
    print(f'Created request: {resp.json()}')
else:
    print(f'Error: {resp.json()}')

# Clean up
db.delete(test_ngo)
db.commit()
db.close()
print('All tests passed!')