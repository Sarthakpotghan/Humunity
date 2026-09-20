import httpx
from typing import Tuple, List, Dict, Optional
from app.config import get_settings

settings = get_settings()


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
        return {"distance": 0, "duration": 0, "geometry": None}
    
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
                }
        except Exception:
            pass
    return {"distance": 0, "duration": 0, "geometry": None}


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


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def suggest_delivery_mode(distance_km: float) -> str:
    if distance_km <= settings.DROPOFF_THRESHOLD_KM:
        return "dropoff"
    return "pickup"