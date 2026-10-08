"""Shared geocoding utilities."""
from typing import Optional, Tuple
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from app.config import get_settings

settings = get_settings()


def geocode_address(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Geocode an address string to (latitude, longitude) using Nominatim.
    Returns (None, None) if geocoding fails.
    """
    if not address or not address.strip():
        return None, None
    
    try:
        geolocator = Nominatim(user_agent=settings.NOMINATIM_USER_AGENT)
        location = geolocator.geocode(address.strip(), timeout=10)
        if location:
            return location.latitude, location.longitude
    except (GeocoderTimedOut, GeocoderServiceError):
        pass
    return None, None