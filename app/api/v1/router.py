"""Aggregate versioned endpoint routers."""

from fastapi import APIRouter

from app.api.v1 import analytics, auth, locations, trips

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(locations.router)
api_router.include_router(trips.router)
api_router.include_router(analytics.router)
