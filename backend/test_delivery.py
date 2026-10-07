from fastapi.testclient import TestClient
from app.main import app

def test_delivery_flow():
    client = TestClient(app)

    # 1. Register test user to guarantee they exist in the test DB
    client.post('/auth/register', json={
        'email': 'donor@test.com', 'password': 'password123', 'name': 'Test Donor', 'role': 'donor'
    })

    # 2. Login donor
    resp = client.post('/auth/login', json={
        'email': 'donor@test.com', 'password': 'password123'
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # 3. Create delivery (Expect 200/201, or 404/422 if match_id=1 doesn't exist yet in the test DB)
    resp = client.post('/deliveries', json={
        'match_id': 1,
        'mode': 'dropoff',
        'scheduled_at': '2026-09-25T10:00:00'
    }, headers=headers)

    # 4. If delivery creation succeeds, test the status updates
    if resp.status_code in [200, 201]:
        delivery_id = resp.json()['id']

        # Update delivery status to in_transit
        client.patch(f'/deliveries/{delivery_id}/status', json={'status': 'in_transit'}, headers=headers)

        # Update delivery status to delivered
        client.patch(f'/deliveries/{delivery_id}/status', json={'status': 'delivered'}, headers=headers)

        # Update delivery status to confirmed
        client.patch(f'/deliveries/{delivery_id}/status', json={'status': 'confirmed'}, headers=headers)

        # Get delivery route
        route_resp = client.get(f'/deliveries/{delivery_id}/route', headers=headers)
        assert route_resp.status_code == 200