import math
from typing import Tuple, List


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def bbox_from_point(lat: float, lng: float, radius_km: float) -> Tuple[float, float, float, float]:
    lat_delta = radius_km / 111.0
    lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))
    return (
        lat - lat_delta,
        lat + lat_delta,
        lng - lng_delta,
        lng + lng_delta,
    )


def points_within_radius(
    center_lat: float, center_lng: float,
    points: List[Tuple[float, float]],
    radius_km: float
) -> List[Tuple[float, float]]:
    return [
        (lat, lng) for lat, lng in points
        if haversine(center_lat, center_lng, lat, lng) <= radius_km
    ]