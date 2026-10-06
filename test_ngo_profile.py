import sys
sys.path.insert(0, r'D:\donation system\backend')
from app.database import SessionLocal
from app.models import User, UserRole, NgoProfile
from app.utils.security import create_access_token
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Create a test NGO user without a profile
db = SessionLocal()
test_ngo = User(
    email='test-ngo-no-profile@test.com',
    name='Test NGO No Profile',
    role=UserRole.NGO,
    password_hash='$2b$12$dummyhash',
    verified=True
)
db.add(test_ngo)
db.commit()
db.refresh(test_ngo)
print(f'Created test NGO user: {test_ngo.id}')

# Create token for this NGO
token = create_access_token(data={"sub": test_ngo.email})
headers = {"Authorization": f"Bearer {token}"}

# Test GET /auth/ngo/profile for NGO without profile
resp = client.get('/auth/ngo/profile', headers=headers)
print(f'Status: {resp.status_code}')
print(f'Response: {resp.json()}')

# Clean up
db.delete(test_ngo)
db.commit()
db.close()
print('Test completed successfully!')