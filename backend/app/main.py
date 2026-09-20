from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import get_settings
from app.database import Base, engine
from app.routers import auth, donations, requests, matches, deliveries, notifications, analytics, admin

settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Humunity API",
    description="Donation matching platform for clothes and educational stationery",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/donations", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.include_router(auth.router)
app.include_router(donations.router)
app.include_router(requests.router)
app.include_router(matches.router)
app.include_router(deliveries.router)
app.include_router(notifications.router)
app.include_router(analytics.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {"message": "Humunity API", "docs": "/docs"}