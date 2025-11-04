from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    return {"status": "ok", "service": "videolingo-backend", "version": settings.VERSION}
