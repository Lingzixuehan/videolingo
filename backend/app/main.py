from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.root import router as root_router
from app.core.config import settings
from app.db.session import Base, engine

# 首次启动建表（SQLite 简化用）
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Videolingo Backend", version=settings.VERSION)
app.include_router(health_router, prefix="")
app.include_router(root_router, prefix="")
app.include_router(auth_router, prefix="")
