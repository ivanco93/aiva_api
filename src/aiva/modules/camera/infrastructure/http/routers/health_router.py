from fastapi import APIRouter

router = APIRouter(prefix="/cameras", tags=["camera"])


@router.get("/health")
async def camera_health_check():
    return {
        "status": "ok",
        "module": "camera",
    }
