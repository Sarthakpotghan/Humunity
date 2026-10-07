from fastapi.testclient import TestClient
from app.main import app

def test_notifications_and_analytics_flow():
    client = TestClient(app)

    # 1. Register all test users first
    client.post('/auth/register', json={'email': 'donor@test.com', 'password': 'password123', 'name': 'Test Donor', 'role': 'donor'})
    client.post('/auth/register', json={'email': 'ngo@test.com', 'password': 'password123', 'name': 'Test NGO', 'role': 'ngo'})
    client.post('/auth/register', json={'email': 'admin@test.com', 'password': 'password123', 'name': 'Test Admin', 'role': 'admin'})

    # 2. Login donor
    resp_donor = client.post('/auth/login', json={'email': 'donor@test.com', 'password': 'password123'})
    assert resp_donor.status_code == 200
    donor_headers = {'Authorization': f"Bearer {resp_donor.json()['access_token']}"}

    # 3. Login Admin (Moved up so the Admin can verify the NGO)
    resp_admin = client.post('/auth/login', json={'email': 'admin@test.com', 'password': 'password123'})
    assert resp_admin.status_code == 200
    admin_headers = {'Authorization': f"Bearer {resp_admin.json()['access_token']}"}

    # 4. Admin verifies the NGO
    # First, get the list of pending NGOs
    pending_resp = client.get('/admin/ngos/pending', headers=admin_headers)
    assert pending_resp.status_code == 200
    pending_ngos = pending_resp.json()
    
    if pending_ngos:
        ngo_id = pending_ngos[0]['id']
        # Admin approves the NGO
        verify_resp = client.patch(f'/admin/ngos/{ngo_id}/verify', json={"verified": True}, headers=admin_headers)
        assert verify_resp.status_code == 200

    # 5. NOW Login the NGO (will succeed since they are verified)
    resp_ngo = client.post('/auth/login', json={'email': 'ngo@test.com', 'password': 'password123'})
    assert resp_ngo.status_code == 200
    ngo_headers = {'Authorization': f"Bearer {resp_ngo.json()['access_token']}"}

    # 6. Test notifications for donor
    notif_donor = client.get('/notifications', headers=donor_headers)
    assert notif_donor.status_code in [200, 201]

    # 7. Test notifications for NGO
    notif_ngo = client.get('/notifications', headers=ngo_headers)
    assert notif_ngo.status_code in [200, 201]

    # 8. Test mark all read
    mark_read = client.patch('/notifications/read-all', headers=donor_headers)
    assert mark_read.status_code in [200, 201, 204]

    # 9. Test analytics (admin only)
    analytics_summary = client.get('/analytics/summary', headers=admin_headers)
    assert analytics_summary.status_code == 200

    analytics_heatmap = client.get('/analytics/heatmap', headers=admin_headers)
    assert analytics_heatmap.status_code == 200

    analytics_trends = client.get('/analytics/trends', headers=admin_headers)
    assert analytics_trends.status_code == 200

    # 10. Test analytics with NGO (should fail with 403 Forbidden)
    analytics_fail = client.get('/analytics/summary', headers=ngo_headers)
    assert analytics_fail.status_code in [401, 403], "Role guard failed: NGO accessed admin routes"