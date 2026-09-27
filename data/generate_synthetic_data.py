"""Synthetic data generator for the Humunity matching evaluation.

Generates a realistic but fake dataset (donors, NGOs, volunteers,
donations, requests) that mirrors the real schema, inserts it into the
application database, and writes CSV exports used by the evaluation
notebooks (``notebooks/``).

Usage:
    python data/generate_synthetic_data.py [--donations 500] [--requests 300] [--reset]

``--reset`` clears previously generated donations/requests/matches/deliveries
before seeding. User accounts created once (demo + bulk actors) are reused.
"""
from __future__ import annotations

import argparse
import datetime as dt
import random
import sys
from pathlib import Path

# allow importing the FastAPI app package from backend/
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import pandas as pd  # noqa: E402

from app.database import Base, engine, SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Delivery,
    DeliveryEvent,
    Donation,
    DonationStatus,
    Feedback,
    ItemCategory,
    ItemCondition,
    Match,
    NgoProfile,
    Request,
    RequestStatus,
    User,
    UserRole,
)
from app.utils.security import get_password_hash  # noqa: E402

from evaluation_common import is_ideal_match  # noqa: E402

BASE = Path(__file__).resolve().parent
OUT = BASE / "output"

CITIES = [
    {"city": "Delhi", "lat": 28.6139, "lng": 77.2090},
    {"city": "Mumbai", "lat": 19.0760, "lng": 72.8777},
    {"city": "Bengaluru", "lat": 12.9716, "lng": 77.5946},
    {"city": "Chennai", "lat": 13.0827, "lng": 80.2707},
    {"city": "Kolkata", "lat": 22.5726, "lng": 88.3639},
    {"city": "Hyderabad", "lat": 17.3850, "lng": 78.4867},
    {"city": "Pune", "lat": 18.5204, "lng": 73.8567},
    {"city": "Jaipur", "lat": 26.9124, "lng": 75.7873},
    {"city": "Lucknow", "lat": 26.8467, "lng": 80.9462},
    {"city": "Ahmedabad", "lat": 23.0225, "lng": 72.5714},
]

CLOTHES_ITEMS = ["jacket", "sweater", "shirt", "t-shirt", "jeans", "trouser", "skirt", "dress", "hoodie", "coat", "sock", "slipper"]
STATIONERY_ITEMS = ["notebook", "pen", "pencil", "eraser", "ruler", "geometry box", "backpack", "story book", "textbook", "crayon", "marker", "school bag"]

SEASONS = ["spring", "summer", "autumn", "winter"]
CONDITIONS = [c for c in ItemCondition]
BENEFICIARY = ["school children", "homeless shelters", "orphanage", "rural schools", "flood victims", "urban poor", "special needs kids"]


def pick_coords(rng: random.Random, city: dict) -> tuple[float, float]:
    jitter = 0.35  # degrees ~ up to ~35 km
    return (
        round(city["lat"] + rng.uniform(-jitter, jitter), 6),
        round(city["lng"] + rng.uniform(-jitter, jitter), 6),
    )


def make_description(rng, item_type, category) -> str:
    qty = rng.randint(5, 60)
    extras = rng.choice([
        "",
        " in good condition",
        " gently used",
        " new and sealed",
        " for kids",
        " assorted sizes",
        " washed and folded",
    ])
    return f"{qty} {item_type}{extras}"


def ensure_users(db, rng, n_donors: int = 500, n_ngos: int = 300) -> dict[str, User]:
    """Create (or fetch) the fixed demo accounts and bulk actors."""
    fixed = [
        {"email": "admin@test.com", "name": "Platform Admin", "role": UserRole.ADMIN, "verified": True},
        {"email": "donor@test.com", "name": "Aarav Donor", "role": UserRole.DONOR, "verified": True},
        {"email": "ngo@test.com", "name": "Helpful Hands NGO", "role": UserRole.NGO, "verified": True},
        {"email": "volunteer@test.com", "name": "Riya Volunteer", "role": UserRole.VOLUNTEER, "verified": True},
    ]
    for rec in fixed:
        existing = db.query(User).filter(User.email == rec["email"]).first()
        if not existing:
            existing = User(
                email=rec["email"],
                name=rec["name"],
                role=rec["role"],
                password_hash=get_password_hash("password123"),
                verified=rec["verified"],
            )
            db.add(existing)
            db.flush()
        rec["user"] = existing
        if rec["role"] == UserRole.NGO:
            if not existing.ngo_profile:
                db.add(NgoProfile(user_id=existing.id, reg_number=f"REG-{existing.id:05d}", reliability_score=round(rng.uniform(0.75, 1.0), 2)))
                db.flush()

    # bulk actors for volume (enough to cover requested donation/request counts)
    roles = {UserRole.DONOR: n_donors, UserRole.NGO: n_ngos, UserRole.VOLUNTEER: 30}
    fresh, by_email = [], {}
    for role, count in roles.items():
        for i in range(count):
            email = f"bulk-{role.value}-{i}@humunity.org"
            existing = db.query(User).filter(User.email == email).first()
            if existing:
                by_email[email] = existing
                continue
            user = User(
                email=email,
                name=f"Bulk {role.value.title()} {i + 1}",
                role=role,
                password_hash=get_password_hash("password123"),
                verified=True,
            )
            db.add(user)
            db.flush()
            if role == UserRole.NGO:
                db.add(NgoProfile(user_id=user.id, reg_number=f"REG-{user.id:05d}", reliability_score=round(rng.uniform(0.55, 1.0), 2)))
            by_email[email] = user
            fresh.append(user)
    db.commit()
    return by_email | {r["email"]: r["user"] for r in fixed}


def set_location(db, user_id, coords):
    db.query(User).filter(User.id == user_id).update({"lat": coords[0], "lng": coords[1]})
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Humunity data")
    parser.add_argument("--donations", type=int, default=500)
    parser.add_argument("--requests", type=int, default=300)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reset", action="store_true", help="Delete generated donations/requests/matches first")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    OUT.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    try:
        if args.reset:
            # delete dependent rows first (feedback -> deliveries -> matches)
            for model in (Feedback, DeliveryEvent, Delivery, Match, Donation, Request):
                db.query(model).delete(synchronize_session=False)
            db.commit()

        users = ensure_users(db, rng, n_donors=args.donations, n_ngos=args.requests)

        donors = [u for e, u in users.items() if u.role == UserRole.DONOR]
        ngos = [u for e, u in users.items() if u.role == UserRole.NGO]
        rng.shuffle(donors)
        rng.shuffle(ngos)

        n_donors = max(2, min(len(donors), args.donations))
        n_ngos = max(2, min(len(ngos), args.requests))

        donation_rows, request_rows, ngo_records = [], [], []

        # assign each actor a city for this seed
        donor_city = [rng.choice(CITIES) for _ in donors]
        ngo_city = [rng.choice(CITIES) for _ in ngos]

        # ---- requests first (NGO needs) ----
        request_id_map = {}
        for i in range(min(args.requests, len(ngos))):
            ngo = ngos[i]
            city = ngo_city[i]
            lat, lng = pick_coords(rng, city)
            set_location(db, ngo.id, (lat, lng))

            cat = rng.choice([ItemCategory.CLOTHES, ItemCategory.STATIONERY])
            pool = CLOTHES_ITEMS if cat == ItemCategory.CLOTHES else STATIONERY_ITEMS
            item_type = rng.choice(pool)
            urgency = rng.choices([1, 2, 3, 4, 5], weights=[1, 2, 3, 2, 1])[0]
            deadline = dt.datetime.utcnow() + dt.timedelta(days=rng.randint(1, 21))

            req = Request(
                ngo_id=ngo.id,
                category=cat,
                item_type=item_type,
                size=rng.choice(["", "M", "L", "XL", "6-10y", "10-14y"]),
                age_group=rng.choice(["", "kid", "6-10", "10-14", "teen", "adult"]),
                gender=rng.choice(["", "unisex", "male", "female"]),
                season=rng.choice([""] + SEASONS),
                quantity_needed=rng.randint(10, 200),
                urgency=urgency,
                beneficiary_group=rng.choice(BENEFICIARY),
                deadline=deadline,
                status=RequestStatus.ACTIVE,
            )
            db.add(req)
            db.flush()
            request_id_map[req.id] = req
            request_rows.append({
                "id": req.id,
                "ngo_id": ngo.id,
                "category": cat.value,
                "item_type": item_type,
                "season": req.season or "",
                "age_group": req.age_group or "",
                "gender": req.gender or "",
                "quantity_needed": req.quantity_needed,
                "urgency": urgency,
                "beneficiary_group": req.beneficiary_group,
                "deadline": deadline.isoformat(),
                "lat": lat,
                "lng": lng,
                "reliability_score": ngo.ngo_profile.reliability_score if ngo.ngo_profile else 1.0,
            })
            ngo_records.append({
                "id": ngo.id,
                "name": ngo.name,
                "lat": lat,
                "lng": lng,
                "reliability_score": ngo.ngo_profile.reliability_score if ngo.ngo_profile else 1.0,
            })

        # ---- donations ----
        donation_id_map = {}
        for i in range(min(args.donations, len(donors))):
            donor = donors[i]
            city = donor_city[i]
            lat, lng = pick_coords(rng, city)
            set_location(db, donor.id, (lat, lng))

            cat = rng.choice([ItemCategory.CLOTHES, ItemCategory.STATIONERY])
            pool = CLOTHES_ITEMS if cat == ItemCategory.CLOTHES else STATIONERY_ITEMS
            item_type = rng.choice(pool)
            description = make_description(rng, item_type, cat)

            donation = Donation(
                donor_id=donor.id,
                category=cat,
                item_type=item_type,
                size=rng.choice(["", "M", "L", "XL", "6-10y", "10-14y"]),
                age_group=rng.choice(["", "kid", "6-10", "10-14", "teen", "adult"]),
                gender=rng.choice(["", "unisex", "male", "female"]),
                season=rng.choice([""] + SEASONS),
                condition=rng.choice(CONDITIONS),
                quantity=rng.randint(3, 80),
                description=description,
                lat=lat,
                lng=lng,
                available_from=dt.datetime.utcnow(),
                available_to=dt.datetime.utcnow() + dt.timedelta(days=14),
                status=DonationStatus.LISTED,
            )
            db.add(donation)
            db.flush()
            donation_id_map[donation.id] = donation
            donation_rows.append({
                "id": donation.id,
                "donor_id": donor.id,
                "category": cat.value,
                "item_type": item_type,
                "condition": donation.condition.value,
                "quantity": donation.quantity,
                "description": description,
                "season": donation.season or "",
                "age_group": donation.age_group or "",
                "gender": donation.gender or "",
                "lat": lat,
                "lng": lng,
                "created_at": dt.datetime.utcnow().isoformat(),
            })

        db.commit()
        print(f"Seeded {len(request_rows)} requests, {len(donation_rows)} donations")

        # ---- ground truth (ideal matches) ----
        ideal_rows = []
        for d in donation_rows:
            for r in request_rows:
                if is_ideal_match(d, r):
                    ideal_rows.append({"donation_id": d["id"], "request_id": r["id"], "is_ideal": True})
        print(f"Ground-truth ideal pairs: {len(ideal_rows)}")

        pd.DataFrame(donation_rows).to_csv(OUT / "donations.csv", index=False)
        pd.DataFrame(request_rows).to_csv(OUT / "requests.csv", index=False)
        pd.DataFrame(ngo_records).to_csv(OUT / "ngos.csv", index=False)
        pd.DataFrame(ideal_rows).to_csv(OUT / "ideal_matches.csv", index=False)
        print(f"Wrote CSV exports to {OUT.resolve()}")
    finally:
        db.close()


if __name__ == "__main__":
    main()