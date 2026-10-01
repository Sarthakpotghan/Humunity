import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent / 'backend'))

from app.main import app
from app.database import get_db, Base
from app.models import User, UserRole, Donation, Request, Match, Delivery, Feedback, NgoProfile
from app.utils.security import get_password_hash, create_access_token


SQLITE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(create_tables):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def make_user(db_session, email, name, role, lat=28.6139, lng=77.2090):
    user = User(
        email=email,
        name=name,
        role=role,
        password_hash=get_password_hash("password123"),
        verified=True,
        lat=lat,
        lng=lng,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_user(db_session):
    return make_user(db_session, "admin@test.com", "Admin User", UserRole.ADMIN)


@pytest.fixture
def donor_user(db_session):
    return make_user(db_session, "donor@test.com", "Test Donor", UserRole.DONOR)


@pytest.fixture
def ngo_user(db_session):
    user = make_user(db_session, "ngo@test.com", "Test NGO", UserRole.NGO)
    ngo = NgoProfile(user_id=user.id, reg_number="REG123")
    db_session.add(ngo)
    db_session.commit()
    return user


@pytest.fixture
def volunteer_user(db_session):
    return make_user(db_session, "volunteer@test.com", "Test Volunteer", UserRole.VOLUNTEER)


def auth_header(user):
    token = create_access_token({"sub": user.email})
    return {"Authorization": f"Bearer {token}"}


# --- Auth Tests ---
def test_login_admin(client, admin_user):
    resp = client.post("/auth/login", json={"email": "admin@test.com", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid(client):
    resp = client.post("/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert resp.status_code == 401


# --- Donation Tests ---
def test_create_donation(client, donor_user):
    h = auth_header(donor_user)
    resp = client.post("/donations", json={
        "category": "clothes",
        "item_type": "jacket",
        "size": "L",
        "age_group": "adult",
        "gender": "unisex",
        "season": "winter",
        "condition": "good",
        "quantity": 10,
        "description": "Warm jackets",
        "lat": 28.6139,
        "lng": 77.2090,
    }, headers=h)
    assert resp.status_code == 201
    data = resp.json()
    assert data["item_type"] == "jacket"
    assert data["quantity"] == 10
    assert data["status"] == "listed"


def test_list_donations(client, donor_user):
    h = auth_header(donor_user)
    resp = client.get("/donations", headers=h)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


# --- Matching Tests ---
def test_match_donation(client, donor_user, ngo_user):
    h = auth_header(donor_user)
    nh = auth_header(ngo_user)
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "lat": 28.6139, "lng": 77.2090,
    }, headers=h)
    assert don_resp.status_code == 201
    don_id = don_resp.json()["id"]

    req_resp = client.post("/requests", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "quantity_needed": 5, "urgency": 3,
        "beneficiary_group": "homeless", "deadline": "2026-12-31",
    }, headers=nh)
    assert req_resp.status_code == 201

    match_resp = client.post(f"/donations/{don_id}/match", headers=h)
    assert match_resp.status_code == 200
    matches = match_resp.json()
    assert len(matches) >= 1
    assert matches[0]["donation_id"] == don_id


def test_accept_match(client, donor_user, ngo_user):
    h = auth_header(donor_user)
    nh = auth_header(ngo_user)
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "lat": 28.6139, "lng": 77.2090,
    }, headers=h)
    don_id = don_resp.json()["id"]
    req_resp = client.post("/requests", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "quantity_needed": 5, "urgency": 3,
        "beneficiary_group": "homeless", "deadline": "2026-12-31",
    }, headers=nh)
    match_resp = client.post(f"/donations/{don_id}/match", headers=h)
    match_id = match_resp.json()[0]["id"]

    accept_resp = client.patch(f"/donations/matches/{match_id}/accept", headers=nh)
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"


# --- Delivery Tests ---
def test_create_delivery(client, donor_user, ngo_user):
    h = auth_header(donor_user)
    nh = auth_header(ngo_user)
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "lat": 28.6139, "lng": 77.2090,
    }, headers=h)
    don_id = don_resp.json()["id"]
    req_resp = client.post("/requests", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "quantity_needed": 5, "urgency": 3,
        "beneficiary_group": "homeless", "deadline": "2026-12-31",
    }, headers=nh)
    match_resp = client.post(f"/donations/{don_id}/match", headers=h)
    match_id = match_resp.json()[0]["id"]
    client.patch(f"/donations/matches/{match_id}/accept", headers=nh)
    
    # Delivery is now auto-created on match acceptance
    del_resp = client.get(f"/deliveries", headers=h)
    assert del_resp.status_code == 200
    deliveries = del_resp.json()
    assert len(deliveries) >= 1
    # Find the delivery for our match
    delivery = next((d for d in deliveries if d["match_id"] == match_id), None)
    assert delivery is not None
    assert delivery["status"] == "scheduled"


def test_assign_volunteer(client, donor_user, ngo_user, volunteer_user):
    h = auth_header(donor_user)
    nh = auth_header(ngo_user)
    vh = auth_header(volunteer_user)
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "lat": 28.6139, "lng": 77.2090,
    }, headers=h)
    don_id = don_resp.json()["id"]
    req_resp = client.post("/requests", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "quantity_needed": 5, "urgency": 3,
        "beneficiary_group": "homeless", "deadline": "2026-12-31",
    }, headers=nh)
    match_resp = client.post(f"/donations/{don_id}/match", headers=h)
    match_id = match_resp.json()[0]["id"]
    client.patch(f"/donations/matches/{match_id}/accept", headers=nh)
    
    # Delivery is auto-created on match acceptance
    del_resp = client.get("/deliveries", headers=h)
    assert del_resp.status_code == 200
    deliveries = del_resp.json()
    delivery = next((d for d in deliveries if d["match_id"] == match_id), None)
    assert delivery is not None
    del_id = delivery["id"]
    
    assign_resp = client.patch(f"/deliveries/{del_id}/assign", json={"volunteer_id": volunteer_user.id}, headers=h)
    assert assign_resp.status_code == 200
    assert assign_resp.json()["volunteer_id"] == volunteer_user.id


def test_volunteer_status_flow(client, donor_user, ngo_user, volunteer_user):
    h = auth_header(donor_user)
    nh = auth_header(ngo_user)
    vh = auth_header(volunteer_user)
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "lat": 28.6139, "lng": 77.2090,
    }, headers=h)
    don_id = don_resp.json()["id"]
    req_resp = client.post("/requests", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "quantity_needed": 5, "urgency": 3,
        "beneficiary_group": "homeless", "deadline": "2026-12-31",
    }, headers=nh)
    match_resp = client.post(f"/donations/{don_id}/match", headers=h)
    match_id = match_resp.json()[0]["id"]
    client.patch(f"/donations/matches/{match_id}/accept", headers=nh)
    
    # Delivery is auto-created on match acceptance
    del_resp = client.get("/deliveries", headers=h)
    assert del_resp.status_code == 200
    deliveries = del_resp.json()
    delivery = next((d for d in deliveries if d["match_id"] == match_id), None)
    assert delivery is not None
    del_id = delivery["id"]
    client.patch(f"/deliveries/{del_id}/assign", json={"volunteer_id": volunteer_user.id}, headers=h)

    start_resp = client.patch(f"/deliveries/{del_id}/status", json={"status": "in_transit"}, headers=vh)
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "in_transit"

    delivered_resp = client.patch(f"/deliveries/{del_id}/status", json={"status": "delivered"}, headers=vh)
    assert delivered_resp.status_code == 200
    assert delivered_resp.json()["status"] == "delivered"


# --- Feedback Tests ---
def test_feedback_uniqueness_per_match(client, donor_user, ngo_user, volunteer_user):
    h = auth_header(donor_user)
    nh = auth_header(ngo_user)
    vh = auth_header(volunteer_user)
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "lat": 28.6139, "lng": 77.2090,
    }, headers=h)
    don_id = don_resp.json()["id"]
    req_resp = client.post("/requests", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "quantity_needed": 5, "urgency": 3,
        "beneficiary_group": "homeless", "deadline": "2026-12-31",
    }, headers=nh)
    match_resp = client.post(f"/donations/{don_id}/match", headers=h)
    match_id = match_resp.json()[0]["id"]
    client.patch(f"/donations/matches/{match_id}/accept", headers=nh)
    
    # Delivery is auto-created on match acceptance
    del_resp = client.get("/deliveries", headers=h)
    assert del_resp.status_code == 200
    deliveries = del_resp.json()
    delivery = next((d for d in deliveries if d["match_id"] == match_id), None)
    assert delivery is not None
    del_id = delivery["id"]
    client.patch(f"/deliveries/{del_id}/assign", json={"volunteer_id": volunteer_user.id}, headers=h)
    client.patch(f"/deliveries/{del_id}/status", json={"status": "in_transit"}, headers=vh)
    client.patch(f"/deliveries/{del_id}/status", json={"status": "delivered"}, headers=vh)

    fb1 = client.post("/feedback", json={"match_id": match_id, "rating": 5, "comments": "Great!"}, headers=h)
    assert fb1.status_code == 201

    fb2 = client.post("/feedback", json={"match_id": match_id, "rating": 4, "comments": "Good"}, headers=nh)
    assert fb2.status_code == 409


# --- Admin Tests ---
def test_admin_list_users(client, admin_user):
    h = auth_header(admin_user)
    resp = client.get("/admin/users", headers=h)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_admin_list_pending_ngos(client, admin_user):
    h = auth_header(admin_user)
    resp = client.get("/admin/ngos/pending", headers=h)
    assert resp.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])