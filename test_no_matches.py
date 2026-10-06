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

# Create donation with stationery category (no matching requests)
donation_data = {
    'category': 'stationery',
    'item_type': 'Test Pens',
    'condition': 'good',
    'quantity': 10,
    'description': 'Test donation with no matching requests'
}
resp = client.post('/donations', json=donation_data, headers=headers)
donation = resp.json()
donation_id = donation['id']
print(f'Created donation {donation_id}, status={donation["status"]}')

# Match donation (should find no matches)
resp = client.post(f'/donations/{donation_id}/match', headers=headers)
matches = resp.json()
print(f'Match response: {matches}')

# Check donation status - should remain LISTED since no matches
resp = client.get(f'/donations/{donation_id}', headers=headers)
donation = resp.json()
print(f'Donation status after match (no matches): {donation["status"]}')

# Get matches
resp = client.get(f'/donations/{donation_id}/matches', headers=headers)
matches = resp.json()
print(f'Matches from GET: {len(matches)}')

# Clean up
db = SessionLocal()
db.query(Match).filter(Match.donation_id == donation_id).delete()
db.query(Donation).filter(Donation.id == donation_id).delete()
db.commit()
print('Test completed successfully!')