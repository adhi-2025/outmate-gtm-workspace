from fastapi import APIRouter

router = APIRouter()


@router.get("/")
@router.get("/health")
@router.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "outmate-backend",
        "docs": "/docs",
        "health": "/health",
        "api_health": "/api/health",
    }