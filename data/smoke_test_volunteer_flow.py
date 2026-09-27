"""End-to-end smoke test of the volunteer assignment flow against a live
backend (uvicorn on :8000). Seeds a deterministic Delhi donation/request/match
via SQLAlchemy, then drives the API the way the admin + volunteer UIs do.

Run while the backend is up: python data/smoke_test_volunteer_flow.py
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

import requests  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Delivery,
    Donation,
    Feedback,
    ItemCategory,
    ItemCondition,
    Match,
    Request,
    RequestStatus,
    User,
    UserRole,
)

BASE = "http://127.0.0.1:8000"
LAT, LNG = 28.6139, 77.2090


def login(email: str, password: str) -> str:
    resp = requests.post(f"{BASE}/auth/login", json={"email": email, "password": password})
    resp.raise_for_status()
    return resp.json()["access_token"]


def headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def seed() -> tuple[int, int]:
    db = SessionLocal()
    try:
        donor = db.query(User).filter(User.email == "donor@test.com").first()
        ngo = db.query(User).filter(User.email == "ngo@test.com").first()
        if not donor or not ngo:
            raise SystemExit("demo users missing; run data/generate_synthetic_data.py first")
        donor.lat, donor.lng = LAT, LNG
        ngo.lat, ngo.lng = LAT, LNG
        ngo.verified = True

        # clean leftover smoke-test rows (keep the run idempotent)
        old_donations = db.query(Donation).filter(
            Donation.donor_id == donor.id,
            Donation.description == "40 warm jackets in good condition"
        ).all()
        old_ids = [d.id for d in old_donations]
        if old_ids:
            for did in old_ids:
                for m in db.query(Match).filter(Match.donation_id == did).all():
                    for d in db.query(Delivery).filter(Delivery.match_id == m.id).all():
                        db.query(Feedback).filter(Feedback.match_id == m.id).delete()
                        db.delete(d)
                db.flush()
                for m in db.query(Match).filter(Match.donation_id == did).all():
                    db.delete(m)
            for d in old_donations:
                db.delete(d)
        old_reqs = db.query(Request).filter(
            Request.ngo_id == ngo.id,
            Request.beneficiary_group == "homeless shelters",
            Request.item_type == "jacket",
        ).all()
        for r in old_reqs:
            db.delete(r)
        db.commit()

        donation = Donation(
            donor_id=donor.id,
            category=ItemCategory.CLOTHES,
            item_type="jacket",
            size="L",
            age_group="adult",
            gender="unisex",
            season="winter",
            condition=ItemCondition.GOOD,
            quantity=40,
            description="40 warm jackets in good condition",
            lat=LAT,
            lng=LNG,
            status="listed",
        )
        db.add(donation)
        db.flush()

        request_ = Request(
            ngo_id=ngo.id,
            category=ItemCategory.CLOTHES,
            item_type="jacket",
            size="L",
            age_group="adult",
            gender="unisex",
            season="winter",
            quantity_needed=100,
            urgency=4,
            beneficiary_group="homeless shelters",
            deadline=dt.datetime.utcnow() + dt.timedelta(days=5),
            status=RequestStatus.ACTIVE,
        )
        db.add(request_)
        db.flush()
        db.commit()
        return donation.id, request_.id
    finally:
        db.close()


def main() -> None:
    donation_id, request_id = seed()
    donor_tok = login("donor@test.com", "password123")
    ngo_tok2 = login("ngo@test.com", "password123")
    admin_tok = login("admin@test.com", "password123")

    # 1. run the production matcher for the seeded donation
    resp = requests.post(f"{BASE}/donations/{donation_id}/match", headers=headers(donor_tok), timeout=180)
    resp.raise_for_status()
    matches = resp.json()
    if not matches:
        print("FAIL: matching produced no candidates")
        sys.exit(1)
    match = next((m for m in matches if m["request_id"] == request_id), matches[0])
    print(f"[1] created match {match['id']} for request {match['request_id']}")

    accept = requests.patch(f"{BASE}/donations/matches/{match['id']}/accept", headers=headers(ngo_tok2))
    accept.raise_for_status()
    print(f"[2] accepted match {match['id']}")

    delivery = requests.post(f"{BASE}/deliveries", headers=headers(ngo_tok2),
                             json={"match_id": match["id"], "mode": "pickup"}).json()
    print(f"[3] created delivery {delivery['id']}")

    all_deliveries = requests.get(f"{BASE}/deliveries", headers=headers(admin_tok)).json()
    assert any(d["id"] == delivery["id"] for d in all_deliveries), "delivery missing from admin list"
    volunteers = requests.get(f"{BASE}/admin/users", headers=headers(admin_tok),
                              params={"role": "volunteer"}).json()
    volunteer = next(v for v in volunteers if v["email"] == "volunteer@test.com")
    assign = requests.patch(f"{BASE}/deliveries/{delivery['id']}/assign",
                            headers=headers(admin_tok),
                            json={"volunteer_id": volunteer["id"]})
    assign.raise_for_status()
    print(f"[4] assigned volunteer {volunteer['name']} ({volunteer['id']})")

    vol_tok = login("volunteer@test.com", "password123")
    mine = requests.get(f"{BASE}/deliveries", headers=headers(vol_tok)).json()
    mine_detail = next(d for d in mine if d["id"] == delivery["id"])
    assert mine_detail["donation_item"] == "jacket"
    print(f"[5] volunteer sees: {mine_detail['donation_item']} from "
          f"{mine_detail['donor_name']} to {mine_detail['ngo_name']} [{mine_detail['status']}]")

    start = requests.patch(f"{BASE}/deliveries/{delivery['id']}/status",
                           headers=headers(vol_tok), json={"status": "in_transit"})
    start.raise_for_status()
    delivered = requests.patch(f"{BASE}/deliveries/{delivery['id']}/status",
                               headers=headers(vol_tok), json={"status": "delivered"})
    delivered.raise_for_status()
    print(f"[6] volunteer status flow -> {delivered.json()['status']}")

    notifs = requests.get(f"{BASE}/notifications", headers=headers(vol_tok)).json()
    assert any("assigned" in (n.get("message") or "").lower() for n in notifs)
    print("[7] assignment notification present")

    print("ALL SMOKE CHECKS PASSED")


if __name__ == "__main__":
    main()