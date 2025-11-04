from fastapi import FastAPI
from .core.config import settings

app = FastAPI(title="Videolingo Backend", version=settings.VERSION)


@app.get("/health")
def health():
    return {"status": "ok", "service": "videolingo-backend", "version": settings.VERSION}


@app.get("/")
def root():
    return {"message": "Videolingo backend is up", "docs": "/docs"}
