from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/humunity"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@humunity.org"
    NOMINATIM_USER_AGENT: str = "Humunity/1.0"
    OSRM_BASE_URL: str = "http://router.project-osrm.org"
    MAX_MATCH_DISTANCE_KM: float = 25.0
    DROPOFF_THRESHOLD_KM: float = 5.0
    VOLUNTEER_PICKUP_MAX_KM: float = 25.0
    # Default coordinates for Pune, India (used when NGO registers without address)
    DEFAULT_NGO_LAT: float = 18.5204
    DEFAULT_NGO_LNG: float = 73.8567

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()