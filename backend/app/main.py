from fastapi import FastAPI
from app.core.config import settings
from app.api.health import router as health_router
from app.api.root import router as root_router

app = FastAPI(title="Videolingo Backend", version=settings.VERSION)
app.include_router(health_router, prefix="")  
app.include_router(root_router,   prefix="")
