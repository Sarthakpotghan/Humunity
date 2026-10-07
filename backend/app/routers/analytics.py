from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.database import get_db
from app.models import Donation, Request, Match, Delivery, User, NgoProfile, DonationStatus, RequestStatus, UserRole, ItemCategory, MatchStatus
from app.schemas import AnalyticsSummary, HeatmapPoint
from app.utils.security import get_current_user, require_role

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def get_summary(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    total_items = db.query(func.sum(Donation.quantity)).filter(
        Donation.status.in_([DonationStatus.DELIVERED, DonationStatus.CONFIRMED])
    ).scalar() or 0
    
    by_category = {}
    for cat in ItemCategory:
        count = db.query(func.sum(Donation.quantity)).filter(
            Donation.category == cat,
            Donation.status.in_([DonationStatus.DELIVERED, DonationStatus.CONFIRMED])
        ).scalar() or 0
        by_category[cat.value] = count
    
    avg_time = db.query(
        func.avg(
            func.extract('epoch', Delivery.delivered_at - Match.created_at) / 3600
        )
    ).join(Match, Delivery.match_id == Match.id).filter(
        Delivery.delivered_at.isnot(None)
    ).scalar()
    
    unmet_requests = db.query(Request).filter(
        Request.status == RequestStatus.ACTIVE,
        Request.deadline < datetime.utcnow() - timedelta(days=30)
    ).count()
    
    top_ngos = db.query(
        NgoProfile.id,
        User.name,
        func.count(Match.id).label("matches_count"),
        func.avg(Match.score).label("avg_score"),
        NgoProfile.reliability_score
    ).join(User, NgoProfile.user_id == User.id).join(
        Request, Request.ngo_id == User.id
    ).join(Match, Match.request_id == Request.id).filter(
        Match.status == MatchStatus.ACCEPTED
    ).group_by(NgoProfile.id, User.name, NgoProfile.reliability_score).order_by(
        desc("matches_count")
    ).limit(10).all()
    
    top_ngos_list = [
        {
            "ngo_id": n.id,
            "name": n.name,
            "matches_count": n.matches_count,
            "avg_score": float(n.avg_score) if n.avg_score else 0,
            "reliability_score": n.reliability_score
        }
        for n in top_ngos
    ]
    
    is_sqlite = db.get_bind().dialect.name == "sqlite"
    month_col = (
        func.strftime('%Y-%m', Donation.created_at)
        if is_sqlite
        else func.date_trunc('month', Donation.created_at)
    ).label('month')

    monthly_trend = db.query(
        month_col,
        func.count(Donation.id).label('count'),
        func.sum(Donation.quantity).label('quantity')
    ).filter(
        Donation.status.in_([DonationStatus.DELIVERED, DonationStatus.CONFIRMED]),
        Donation.created_at >= datetime.utcnow() - timedelta(days=365)
    ).group_by('month').order_by('month').all()

    monthly_trend_list = [
        {
            "month": m.month if isinstance(m.month, str) else m.month.strftime("%Y-%m"),
            "donations": m.count,
            "quantity": m.quantity or 0
        }
        for m in monthly_trend
    ]
    
    return AnalyticsSummary(
        total_items_redistributed=total_items,
        by_category=by_category,
        avg_time_match_to_delivery_hours=float(avg_time) if avg_time else None,
        unmet_requests=unmet_requests,
        top_ngos=top_ngos_list,
        monthly_trend=monthly_trend_list
    )


@router.get("/heatmap", response_model=List[HeatmapPoint])
def get_heatmap(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    donations = db.query(Donation.lat, Donation.lng).filter(
        Donation.lat.isnot(None), Donation.lng.isnot(None)
    ).all()
    requests = db.query(Request).join(User, Request.ngo_id == User.id).filter(
        User.lat.isnot(None), User.lng.isnot(None)
    ).all()
    
    from collections import defaultdict
    grid = defaultdict(lambda: {"donations": 0, "requests": 0})
    
    for d in donations:
        key = (round(d.lat, 2), round(d.lng, 2))
        grid[key]["donations"] += 1
    
    for r in requests:
        if r.ngo is None or r.ngo.lat is None or r.ngo.lng is None:
            continue
        key = (round(r.ngo.lat, 2), round(r.ngo.lng, 2))
        grid[key]["requests"] += 1
    
    return [
        HeatmapPoint(lat=lat, lng=lng, donations=v["donations"], requests=v["requests"])
        for (lat, lng), v in grid.items()
    ]


@router.get("/trends")
def get_trends(
    days: int = 30,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    since = datetime.utcnow() - timedelta(days=days)
    
    donations_daily = db.query(
        func.date(Donation.created_at).label('date'),
        func.count(Donation.id).label('count')
    ).filter(Donation.created_at >= since).group_by('date').all()
    
    requests_daily = db.query(
        func.date(Request.created_at).label('date'),
        func.count(Request.id).label('count')
    ).filter(Request.created_at >= since).group_by('date').all()
    
    return {
        "donations": [{"date": str(d.date), "count": d.count} for d in donations_daily],
        "requests": [{"date": str(r.date), "count": r.count} for r in requests_daily]
    }