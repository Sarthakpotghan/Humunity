#!/usr/bin/env python3
"""
Diagnostic script for matching engine debugging.
Connects to SQLite database, fetches latest Donation and Request,
and runs diagnostics to understand why matching returns empty.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Donation, Request, User, RequestStatus, DonationStatus, UserRole, NgoProfile
from app.services.matching import haversine, run_matching_for_donation
from app.config import get_settings

settings = get_settings()

# Use SQLite database
SQLITE_URL = "sqlite:///./humunity.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

try:
    print("=" * 60)
    print("MATCHING ENGINE DIAGNOSTIC")
    print("=" * 60)

    # Fetch most recent donation
    donation = db.query(Donation).order_by(Donation.created_at.desc()).first()
    if not donation:
        print("ERROR: No donations found in database")
        sys.exit(1)

    # Fetch most recent request
    request = db.query(Request).order_by(Request.created_at.desc()).first()
    if not request:
        print("ERROR: No requests found in database")
        sys.exit(1)

    # Fetch donor user
    donor = db.query(User).filter(User.id == donation.donor_id).first()
    if not donor:
        print(f"ERROR: Donor user {donation.donor_id} not found")
        sys.exit(1)

    # Fetch NGO user
    ngo = db.query(User).filter(User.id == request.ngo_id).first()
    if not ngo:
        print(f"ERROR: NGO user {request.ngo_id} not found")
        sys.exit(1)

    # Fetch NGO profile
    ngo_profile = db.query(NgoProfile).filter(NgoProfile.user_id == ngo.id).first()

    print("\n--- DIAGNOSTICS PART 1: THE STRINGS ---")
    print(f"Donation category: \"{donation.category}\"")
    print(f"Request category:  \"{request.category}\"")
    print(f"Category match: {donation.category == request.category}")
    print(f"Donation item_type: \"{donation.item_type}\"")
    print(f"Request item_type:  \"{request.item_type}\"")

    print("\n--- DIAGNOSTICS PART 2: THE STATUS ---")
    print(f"Request status: {request.status} (expected: {RequestStatus.ACTIVE})")
    print(f"Request status is ACTIVE: {request.status == RequestStatus.ACTIVE}")
    print(f"NGO user verified: {ngo.verified}")
    print(f"NGO user role: {ngo.role} (expected: {UserRole.NGO})")
    print(f"NGO role is NGO: {ngo.role == UserRole.NGO}")

    print("\n--- DIAGNOSTICS PART 3: THE DISTANCE ---")
    print(f"Donor coordinates: lat={donor.lat}, lng={donor.lng}")
    print(f"NGO coordinates:   lat={ngo.lat}, lng={ngo.lng}")
    print(f"Donation coordinates: lat={donation.lat}, lng={donation.lng}")
    print(f"Request NGO coordinates: lat={request.ngo.lat if request.ngo else 'N/A'}, lng={request.ngo.lng if request.ngo else 'N/A'}")

    distance = None
    if all([donation.lat, donation.lng, ngo.lat, ngo.lng]):
        distance = haversine(donation.lat, donation.lng, ngo.lat, ngo.lng)
        max_dist = settings.MAX_MATCH_DISTANCE_KM
        print(f"\nHaversine distance: {distance:.2f} km")
        print(f"Max allowed distance: {max_dist} km")
        print(f"Within radius: {distance <= max_dist}")
        if distance > max_dist:
            print(f"  >>> FLAGGED: Distance ({distance:.2f} km) exceeds max ({max_dist} km)")
    else:
        print("\nCannot calculate distance: missing coordinates")
        print(f"  donation.lat={donation.lat}, donation.lng={donation.lng}")
        print(f"  ngo.lat={ngo.lat}, ngo.lng={ngo.lng}")

    print("\n--- DIAGNOSTICS PART 4: EXECUTION ---")
    print(f"Running run_matching_for_donation(donation_id={donation.id})...")
    
    try:
        matches = run_matching_for_donation(donation.id, db)
        print(f"Matches returned: {len(matches)}")
        if matches:
            for m in matches:
                print(f"  Match ID: {m.id}, Request ID: {m.request_id}, Score: {m.score:.4f}")
                print(f"    Breakdown: {m.score_breakdown}")
        else:
            print("  >>> NO MATCHES FOUND")
            print("\n--- ADDITIONAL DEBUG: Checking candidate requests ---")
            
            # Debug: see what requests pass the initial filter
            candidate_requests = db.query(Request).join(User, Request.ngo_id == User.id).filter(
                Request.category == donation.category,
                Request.status == RequestStatus.ACTIVE,
                User.verified == True
            ).all()
            
            print(f"Candidate requests after hard filter: {len(candidate_requests)}")
            for req in candidate_requests:
                req_ngo = req.ngo
                print(f"  Request {req.id}: category={req.category}, status={req.status}, NGO verified={req_ngo.verified}, NGO coords=({req_ngo.lat}, {req_ngo.lng})")
                if req_ngo.lat and req_ngo.lng and donation.lat and donation.lng:
                    d = haversine(donation.lat, donation.lng, req_ngo.lat, req_ngo.lng)
                    print(f"    Distance: {d:.2f} km (max: {settings.MAX_MATCH_DISTANCE_KM})")
                    if d > settings.MAX_MATCH_DISTANCE_KM:
                        print(f"    >>> EXCLUDED: distance > max")
                else:
                    print(f"    Missing coordinates")
                    
    except Exception as e:
        print(f"ERROR during matching: {e}")
        import traceback
        traceback.print_exc()

finally:
    db.close()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)