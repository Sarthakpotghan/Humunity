import sys
sys.path.insert(0, r'D:\donation system\backend')
from app.database import SessionLocal
from app.models import User, UserRole, Donation, Request, DonationStatus, RequestStatus, ItemCategory, ItemCondition, Match
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Login as donor
login_resp = client.post('/auth/login', json={'email': 'donor@test.com', 'password': 'password123'})
token = login_resp.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Create donation without coordinates
donation_data = {
    'category': 'clothes',
    'item_type': 'Test Papers',
    'condition': 'good',
    'quantity': 10,
    'description': 'Test donation without coordinates'
}
resp = client.post('/donations', json=donation_data, headers=headers)
donation = resp.json()
donation_id = donation['id']
print(f'Created donation {donation_id}, status={donation["status"]}')

# Login as NGO to create request
login_resp = client.post('/auth/login', json={'email': 'ngo@test.com', 'password': 'password123'})
ngo_token = login_resp.json()['access_token']
ngo_headers = {'Authorization': f'Bearer {ngo_token}'}

# Create request
request_data = {
    'category': 'clothes',
    'item_type': 'Papers',
    'quantity_needed': 5,
    'urgency': 3
}
resp = client.post('/requests', json=request_data, headers=ngo_headers)
request = resp.json()
request_id = request['id']
print(f'Created request {request_id}')

# Match donation
resp = client.post(f'/donations/{donation_id}/match', headers=headers)
matches = resp.json()
print(f'Match response: {matches}')

# Check donation status
resp = client.get(f'/donations/{donation_id}', headers=headers)
donation = resp.json()
print(f'Donation status after match: {donation["status"]}')

# Get matches
resp = client.get(f'/donations/{donation_id}/matches', headers=headers)
matches = resp.json()
print(f'Matches from GET: {len(matches)}')
for m in matches:
    print(f'  Match {m["id"]}: score={m["score"]}, status={m["status"]}')

# Clean up
db = SessionLocal()
db.query(Match).filter(Match.donation_id == donation_id).delete()
db.query(Donation).filter(Donation.id == donation_id).delete()
db.query(Request).filter(Request.id == request_id).delete()
db.commit()
print('Test completed successfully!')