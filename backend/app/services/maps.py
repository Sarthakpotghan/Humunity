import httpx
import math
from typing import Tuple, List, Dict, Optional
from app.config import get_settings

settings = get_settings()


# Delivery mode thresholds (configurable)
DROPOFF_THRESHOLD_KM = settings.DROPOFF_THRESHOLD_KM  # <= 5km -> donor dropoff
VOLUNTEER_PICKUP_MAX_KM = settings.VOLUNTEER_PICKUP_MAX_KM  # 5-25km -> volunteer pickup
# > 25km -> donor dropoff with long_distance_flag


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def calculate_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate Haversine distance in kilometers between two points."""
    return haversine(lat1, lon1, lat2, lon2)


def suggest_delivery_mode(distance_km: float) -> tuple[str, bool]:
    """
    Suggest delivery mode based on distance.
    Returns (mode, long_distance_flag)
    - <= 5km: donor_dropoff, long_distance_flag=False
    - 5-25km: volunteer_pickup, long_distance_flag=False
    - > 25km: donor_dropoff, long_distance_flag=True
    """
    if distance_km <= settings.DROPOFF_THRESHOLD_KM:
        return "donor_dropoff", False
    elif distance_km <= settings.VOLUNTEER_PICKUP_MAX_KM:
        return "volunteer_pickup", False
    else:
        return "donor_dropoff", True


async def geocode(address: str) -> Optional[Tuple[float, float]]:
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }
    headers = {"User-Agent": settings.NOMINATIM_USER_AGENT}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if data:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception:
            pass
    return None


async def reverse_geocode(lat: float, lng: float) -> Optional[str]:
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        "lat": lat,
        "lon": lng,
        "format": "json",
    }
    headers = {"User-Agent": settings.NOMINATIM_USER_AGENT}
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data.get("display_name")
        except Exception:
            pass
    return None


async def get_route(waypoints: List[Tuple[float, float]]) -> Dict:
    if len(waypoints) < 2:
        return {"distance": 0, "duration": 0, "geometry": None, "estimated": False}
    
    coords = ";".join(f"{lon},{lat}" for lat, lon in waypoints)
    url = f"{settings.OSRM_BASE_URL}/route/v1/driving/{coords}"
    params = {
        "overview": "full",
        "geometries": "geojson",
        "steps": "true",
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == "Ok" and data.get("routes"):
                route = data["routes"][0]
                return {
                    "distance": route.get("distance", 0) / 1000,
                    "duration": route.get("duration", 0) / 60,
                    "geometry": route.get("geometry"),
                    "estimated": False,
                }
        except Exception:
            pass
    
    # Fallback: straight-line using Haversine
    total_distance = 0.0
    for i in range(len(waypoints) - 1):
        total_distance += haversine(waypoints[i][0], waypoints[i][1], waypoints[i+1][0], waypoints[i+1][1])
    
    # Assume ~50 km/h average speed for duration estimate
    estimated_duration = (total_distance / 50.0) * 60.0
    
    return {
        "distance": total_distance,
        "duration": estimated_duration,
        "geometry": None,
        "estimated": True,
    }


async def get_distance_matrix(origins: List[Tuple[float, float]], destinations: List[Tuple[float, float]]) -> List[List[float]]:
    if not origins or not destinations:
        return []
    
    coord_str = ";".join(f"{lon},{lat}" for lat, lon in origins + destinations)
    url = f"{settings.OSRM_BASE_URL}/table/v1/driving/{coord_str}"
    params = {
        "sources": ";".join(str(i) for i in range(len(origins))),
        "destinations": ";".join(str(len(origins) + i) for i in range(len(destinations))),
    }
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == "Ok":
                return data.get("distances", [])
        except Exception:
            pass
    return [[0.0] * len(destinations) for _ in origins]


async def geocode_user_address(address: str) -> Optional[Tuple[float, float]]:
    """Geocode user address string to (lat, lng). Returns None on failure."""
    if not address or not address.strip():
        return None
    try:
        return await geocode(address.strip())
    except Exception as e:
        import logging
        logging.warning(f"Geocoding failed for '{address}': {e}")
        return None