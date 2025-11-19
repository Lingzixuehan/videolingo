from fastapi import APIRouter

router = APIRouter(tags=["root"])


@router.get("/")
def root():
    return {"message": "Videolingo backend is up", "docs": "/docs"}
