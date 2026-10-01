import sys
sys.path.insert(0, r'D:\donation system\backend')

from app.main import app
from app.database import get_db, Base
from app.models import User, UserRole, NgoProfile, Request, Donation, Match, MatchStatus, DonationStatus, ItemCategory, ItemCondition, RequestStatus, Delivery, DeliveryEvent, DeliveryMode
from app.utils.security import get_password_hash, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

SQLITE_URL = 'sqlite:///:memory:'
engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

db = TestingSessionLocal()

# Create donor
donor = User(email='donor@test.com', name='Test Donor', role=UserRole.DONOR, password_hash='hash', verified=True, lat=28.6139, lng=77.2090)
db.add(donor)
db.flush()

# Create NGO close by (within 5km)
ngo_close = User(email='ngo_close@test.com', name='Test NGO Close', role=UserRole.NGO, password_hash='hash', verified=True, lat=28.6140, lng=77.2095)
db.add(ngo_close)
db.flush()

# Create NGO profile
ngo_profile = NgoProfile(user_id=ngo_close.id, reg_number='REG123')
db.add(ngo_profile)

# Create admin
admin = User(email='admin@test.com', name='Admin', role=UserRole.ADMIN, password_hash='hash', verified=True)
db.add(admin)
db.commit()
db.refresh(ngo)
db.refresh(donor)

# Create request
req = Request(ngo_id=ngo_close.id, category='clothes', item_type='Shirts', quantity_needed=10, urgency=3, status='active')
db.add(req)
db.commit()
db.refresh(req)

# Create donation
donation = Donation(donor_id=donor.id, category='clothes', item_type='Shirts', condition='good', quantity=50, lat=28.6139, lng=77.2090, status='listed')
db.add(donation)
db.commit()
db.refresh(donation)

# Create match
match = Match(donation_id=donation.id, request_id=req.id, score=0.85, score_breakdown={}, status='pending')
db.add(match)
db.commit()
db.refresh(match)

db.close()

# Test the flow
from app.utils.security import get_password_hash, create_access_token
from app.models import Delivery, DeliveryEvent, DeliveryStatus, DeliveryMode
from app.utils.security import create_access_token
from app.main import app
from app.database import get_db, Base
from app.models import User, UserRole, Donation, Request, Match, MatchStatus, DonationStatus, ItemCategory, ItemCondition, RequestStatus, Delivery, DeliveryEvent, DeliveryStatus, DeliveryMode
from app.utils.security import get_password_hash, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

SQLITE_URL = 'sqlite:///:memory:'
engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

db = TestingSessionLocal()
# Create donor
donor = User(email='donor@test.com', name='Test Donor', role=UserRole.DONOR, password_hash='hash', verified=True, lat=28.6139, lng=77.2090)
db.add(donor)
db.flush()

# Create NGO close by (within 5km)
ngo_close = User(email='ngo_close@test.com', name='Test NGO Close', role=UserRole.NGO, password_hash='hash', verified=True, lat=28.6140, lng=77.2095)
db.add(ngo_close)
db.flush()

# Create NGO profile
ngo_profile = NgoProfile(user_id=ngo_close.id, reg_number='REG123')
db.add(ngo_profile)
db.commit()

# Create admin
admin = User(email='admin@test.com', name='Admin', role=UserRole.ADMIN, password_hash='hash', verified=True)
db.add(admin)
db.commit()
db.refresh(ngo)
db.refresh(donor)

# Create request
req = Request(ngo_id=ngo_close.id, category='clothes', item_type='Shirts', quantity_needed=10, urgency=3, status='active')
db.add(req)
db.commit()
db.refresh(req)

# Create donation
donation = Donation(donor_id=donor.id, category='clothes', item_type='Shirts', condition='good', quantity=50, lat=28.6139, lng=77.2090, status='listed')
db.add(donation)
db.commit()
db.refresh(donation)

# Create match
match = Match(donation_id=donation.id, request_id=req.id, score=0.85, score_breakdown={}, status='pending')
db.add(match)
db.commit()
db.refresh(match)

db.close()

# Test the flow
from app.utils.security import get_password_hash, create_access_token
from app.models import Delivery, DeliveryEvent, DeliveryStatus, DeliveryMode
from app.utils.security import create_access_token
from app.main import app
from app.database import get_db, Base
from app.models import User, UserRole, Donation, Request, Match, MatchStatus, DonationStatus, ItemCategory, ItemCondition, RequestStatus, Delivery, DeliveryEvent, DeliveryStatus, DeliveryMode
from app.utils.security import get_password_hash, create_access_token
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

SQLITE_URL = 'sqlite:///:memory:'
engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

db = TestingSessionLocal()
# Create donor
donor = User(email='donor@test.com', name='Test Donor', role=UserRole.DONOR, password_hash='hash', verified=True, lat=28.6139, lng=77.2090)
db.add(donor)

# Create NGO close by (within 5km)
ngo = User(email='ngo@test.com', name='Test NGO', role=UserRole.NGO, password_hash='hash', verified=True, lat=28.6140, lng=77.2095)
db.add(ngo)
db.flush()

ngo_profile = NgoProfile(user_id=ngo.id, reg_number='REG123')
db.add(ngo_profile)
db.commit()

admin = User(email='admin@test.com', name='Admin', role=UserRole.ADMIN, password_hash='hash', verified=True)
db.add(admin)
db.commit()

# Create request
req = Request(ngo_id=ngo.id, category='clothes', item_type='Shirts', quantity_needed=10, urgency=3, status='active')
db.add(req)
db.commit()
db.refresh(req)

# Create donation
donation = Donation(donor_id=donor.id, category='clothes', item_type='Shirts', condition='good', quantity=50, lat=28.6139, lng=77.2090, status='listed')
db.add(donation)
db.commit()
db.refresh(donation)

# Create match
match = Match(donation_id=donation.id, request_id=req.id, score=0.85, score_breakdown={}, status='pending')
db.add(match)
db.commit()
db.refresh(match)

db.close()

# Test the flow
from app.utils.security import create_access_token
from app.models import Delivery, DeliveryEvent, DeliveryStatus, DeliveryMode
from app.utils.security import create_access_token

h = {'Authorization': 'Bearer ' + create_access_token({'sub': 'donor@test.com'})}
ngo_h = {'Authorization': 'Bearer ' + create_access_token({'sub': 'ngo@test.com'})}
admin_h = {'Authorization': 'Bearer ' + create_access_token({'sub': 'admin@test.com'})}

# Test accept match
resp = client.post('/donations/1/match', headers=h)
print('POST /donations/1/match:', resp.status_code)
if resp.status_code == 200:
    match_id = resp.json()[0]['id']
    print('Match ID:', match_id)
    
    # Accept match
    accept_resp = client.patch(f'/donations/matches/{match_id}/accept', headers={'Authorization': 'Bearer ' + create_access_token({'sub': 'ngo@test.com'})})
    print('Accept match:', accept_resp.status_code, accept_resp.json()['status'])
    
    # Check delivery was created
    admin_h = {'Authorization': 'Bearer ' + create_access_token({'sub': 'admin@test.com'})}
    resp = client.get('/deliveries', headers=admin_h)
    print('GET /deliveries:', resp.status_code)
    if resp.status_code == 200:
        deliveries = resp.json()
        if deliveries:
            d = deliveries[0]
            print('Delivery mode:', d.get('mode'))
            print('Delivery status:', d.get('status'))
        else:
            print('No deliveries found')
    else:
        print('Failed to get deliveries:', resp.status_code)
else:
    print('Create donation failed:', resp.status_code, resp.json())
" 2>&1