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


def test_admin_verify_ngo_persists_verified_status(client, admin_user, db_session):
    """
    Test that when an admin verifies an NGO:
    1. The NGO's verified status is set to True in the database
    2. The NGO can log in and /auth/me returns verified=True
    3. The NGO no longer appears in the pending NGOs list
    """
    from app.utils.security import get_password_hash, create_access_token
    from app.models import NgoProfile
    
    h = auth_header(admin_user)
    
    # Create an unverified NGO user with a profile
    unverified_ngo = User(
        email="unverified_ngo@test.com",
        name="Unverified NGO",
        role=UserRole.NGO,
        password_hash=get_password_hash("password123"),
        verified=False,
    )
    db_session.add(unverified_ngo)
    db_session.commit()
    db_session.refresh(unverified_ngo)
    
    ngo_profile = NgoProfile(user_id=unverified_ngo.id, reg_number="REG999")
    db_session.add(ngo_profile)
    db_session.commit()
    db_session.refresh(ngo_profile)
    
    # Verify NGO appears in pending list
    pending_resp = client.get("/admin/ngos/pending", headers=h)
    assert pending_resp.status_code == 200
    pending_ngos = pending_resp.json()
    assert any(ngo["user_id"] == unverified_ngo.id for ngo in pending_ngos)
    
    # Admin verifies the NGO
    verify_resp = client.patch(f"/admin/ngos/{ngo_profile.id}/verify", json={"approve": True}, headers=h)
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verified"] is True
    
    # NGO should no longer be in pending list
    pending_resp = client.get("/admin/ngos/pending", headers=h)
    assert pending_resp.status_code == 200
    pending_ngos = pending_resp.json()
    assert not any(ngo["user_id"] == unverified_ngo.id for ngo in pending_ngos)
    
    # NGO logs in
    login_resp = client.post("/auth/login", json={"email": "unverified_ngo@test.com", "password": "password123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    ngo_auth_header = {"Authorization": f"Bearer {token}"}
    
    # /auth/me should return verified=True
    me_resp = client.get("/auth/me", headers=ngo_auth_header)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["verified"] is True, f"Expected verified=True, got {me_data}"


def test_admin_verify_ngo_without_profile(client, admin_user, db_session):
    """
    Test that when an admin verifies an NGO without a profile:
    1. The NGO's verified status is set to True in the database
    2. The NGO can log in and /auth/me returns verified=True
    3. The NGO no longer appears in the pending NGOs list
    """
    from app.utils.security import get_password_hash, create_access_token
    
    h = auth_header(admin_user)
    
    # Create an unverified NGO user WITHOUT a profile
    unverified_ngo = User(
        email="unverified_ngo_no_profile@test.com",
        name="Unverified NGO No Profile",
        role=UserRole.NGO,
        password_hash=get_password_hash("password123"),
        verified=False,
    )
    db_session.add(unverified_ngo)
    db_session.commit()
    db_session.refresh(unverified_ngo)
    
    # Verify NGO appears in pending list (has_profile=False)
    pending_resp = client.get("/admin/ngos/pending", headers=h)
    assert pending_resp.status_code == 200
    pending_ngos = pending_resp.json()
    assert any(ngo["user_id"] == unverified_ngo.id and not ngo["has_profile"] for ngo in pending_ngos)
    
    # Admin verifies the NGO using User.id as identifier
    verify_resp = client.patch(f"/admin/ngos/{unverified_ngo.id}/verify", json={"approve": True}, headers=h)
    assert verify_resp.status_code == 200
    assert verify_resp.json()["verified"] is True
    
    # NGO should no longer be in pending list
    pending_resp = client.get("/admin/ngos/pending", headers=h)
    assert pending_resp.status_code == 200
    pending_ngos = pending_resp.json()
    assert not any(ngo["user_id"] == unverified_ngo.id for ngo in pending_ngos)
    
    # NGO logs in
    login_resp = client.post("/auth/login", json={"email": "unverified_ngo_no_profile@test.com", "password": "password123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    ngo_auth_header = {"Authorization": f"Bearer {token}"}
    
    # /auth/me should return verified=True
    me_resp = client.get("/auth/me", headers=ngo_auth_header)
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["verified"] is True, f"Expected verified=True, got {me_data}"


# --- Matching Tests ---
def test_matching_no_duplicates_on_rerun(client, donor_user, ngo_user, db_session):
    """
    Test that running matching multiple times for the same donation
    does not create duplicate match records (Bug 1 fix).
    """
    from app.models import Request, NgoProfile, RequestStatus, Match, MatchStatus, DonationStatus
    
    h = auth_header(donor_user)
    
    # Update ngo_user to have Pune coordinates (matching donation location)
    ngo_user.lat = 18.5204
    ngo_user.lng = 73.8567
    db_session.commit()
    db_session.refresh(ngo_user)
    
    # Create a second NGO user for multiple matches
    ngo_user2 = User(
        email="ngo2@test.com",
        name="Test NGO 2",
        role=UserRole.NGO,
        password_hash=get_password_hash("password123"),
        verified=True,
        lat=18.5204,
        lng=73.8567,
    )
    db_session.add(ngo_user2)
    db_session.commit()
    db_session.refresh(ngo_user2)
    
    ngo_profile2 = NgoProfile(user_id=ngo_user2.id, reg_number="REG456")
    db_session.add(ngo_profile2)
    db_session.commit()
    
    # Create requests for both NGOs
    req1 = Request(
        ngo_id=ngo_user.id,
        category="clothes",
        item_type="jacket",
        quantity_needed=5,
        urgency=3,
        status=RequestStatus.ACTIVE,
    )
    req2 = Request(
        ngo_id=ngo_user2.id,
        category="clothes",
        item_type="jacket",
        quantity_needed=5,
        urgency=2,
        status=RequestStatus.ACTIVE,
    )
    db_session.add_all([req1, req2])
    db_session.commit()
    db_session.refresh(req1)
    db_session.refresh(req2)
    
    # Create a donation
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "pickup_address": "Pune, Maharashtra",
    }, headers=h)
    assert don_resp.status_code == 201
    don_id = don_resp.json()["id"]
    
    # Run matching first time
    match_resp1 = client.post(f"/donations/{don_id}/match", headers=h)
    assert match_resp1.status_code == 200
    matches1 = match_resp1.json()
    assert len(matches1) == 2
    
    # Reset donation status to LISTED to allow re-running matching
    donation = db_session.query(Donation).filter(Donation.id == don_id).first()
    donation.status = DonationStatus.LISTED
    db_session.commit()
    
    # Run matching second time (should not create duplicates)
    match_resp2 = client.post(f"/donations/{don_id}/match", headers=h)
    assert match_resp2.status_code == 200
    matches2 = match_resp2.json()
    assert len(matches2) == 2, f"Expected 2 matches, got {len(matches2)}: {matches2}"
    
    # Verify database has only 2 pending matches for this donation
    matches_in_db = db_session.query(Match).filter(
        Match.donation_id == don_id,
        Match.status == MatchStatus.PENDING
    ).count()
    assert matches_in_db == 2, f"Expected 2 pending matches in DB, got {matches_in_db}"


def test_only_top_ranked_match_can_accept(client, donor_user, ngo_user, db_session):
    """
    Test that only the highest-scoring (rank #1) match can be accepted (Bug 2 fix).
    """
    from app.models import Request, NgoProfile, RequestStatus
    
    h = auth_header(donor_user)
    nh = auth_header(ngo_user)
    
    # Update ngo_user to have Pune coordinates (matching donation location)
    ngo_user.lat = 18.5204
    ngo_user.lng = 73.8567
    db_session.commit()
    db_session.refresh(ngo_user)
    
    # Create a second NGO user with different urgency (lower score)
    ngo_user2 = User(
        email="ngo3@test.com",
        name="Test NGO 3",
        role=UserRole.NGO,
        password_hash=get_password_hash("password123"),
        verified=True,
        lat=18.5204,
        lng=73.8567,
    )
    db_session.add(ngo_user2)
    db_session.commit()
    db_session.refresh(ngo_user2)
    
    ngo_profile2 = NgoProfile(user_id=ngo_user2.id, reg_number="REG789")
    db_session.add(ngo_profile2)
    db_session.commit()
    
    # Create requests - ngo_user has higher urgency (higher score)
    req1 = Request(
        ngo_id=ngo_user.id,
        category="clothes",
        item_type="jacket",
        quantity_needed=5,
        urgency=5,  # High urgency = higher score
        status=RequestStatus.ACTIVE,
    )
    req2 = Request(
        ngo_id=ngo_user2.id,
        category="clothes",
        item_type="jacket",
        quantity_needed=5,
        urgency=1,  # Low urgency = lower score
        status=RequestStatus.ACTIVE,
    )
    db_session.add_all([req1, req2])
    db_session.commit()
    db_session.refresh(req1)
    db_session.refresh(req2)
    
    # Create a donation
    don_resp = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets", "pickup_address": "Pune, Maharashtra",
    }, headers=h)
    assert don_resp.status_code == 201
    don_id = don_resp.json()["id"]
    
    # Run matching
    match_resp = client.post(f"/donations/{don_id}/match", headers=h)
    assert match_resp.status_code == 200
    matches = match_resp.json()
    assert len(matches) == 2
    
    # Verify matches are sorted by score descending and have rank
    assert matches[0]["score"] >= matches[1]["score"]
    assert matches[0]["score_breakdown"]["rank"] == 1
    assert matches[1]["score_breakdown"]["rank"] == 2
    
    # The top match (rank 1) should be for ngo_user (higher urgency)
    top_match_id = matches[0]["id"]
    second_match_id = matches[1]["id"]
    
    # NGO for top match should be able to accept
    top_ngo_token = auth_header(ngo_user)["Authorization"].replace("Bearer ", "")
    # Actually let's login as the NGO
    login_resp = client.post("/auth/login", json={"email": "ngo@test.com", "password": "password123"})
    assert login_resp.status_code == 200
    top_ngo_header = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}
    
    # Top match NGO accepts - should succeed
    accept_resp = client.patch(f"/donations/matches/{top_match_id}/accept", headers=top_ngo_header)
    assert accept_resp.status_code == 200, f"Top match accept failed: {accept_resp.json()}"
    
    # Second match NGO tries to accept - should fail with 403
    login_resp2 = client.post("/auth/login", json={"email": "ngo3@test.com", "password": "password123"})
    assert login_resp2.status_code == 200
    second_ngo_header = {"Authorization": f"Bearer {login_resp2.json()['access_token']}"}
    
    # First, we need to create a new donation for the second test since the first one is now accepted
    don_resp2 = client.post("/donations", json={
        "category": "clothes", "item_type": "jacket", "size": "L", "age_group": "adult",
        "gender": "unisex", "season": "winter", "condition": "good", "quantity": 10,
        "description": "Warm jackets 2", "pickup_address": "Pune, Maharashtra",
    }, headers=h)
    assert don_resp2.status_code == 201
    don_id2 = don_resp2.json()["id"]
    
    match_resp2 = client.post(f"/donations/{don_id2}/match", headers=h)
    assert match_resp2.status_code == 200
    matches2 = match_resp2.json()
    assert len(matches2) == 2
    
    # The second match (rank 2) should not be acceptable
    second_match_id = matches2[1]["id"]
    accept_resp2 = client.patch(f"/donations/matches/{second_match_id}/accept", headers=second_ngo_header)
    assert accept_resp2.status_code == 403, f"Expected 403 for rank 2 match, got {accept_resp2.status_code}: {accept_resp2.json()}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])