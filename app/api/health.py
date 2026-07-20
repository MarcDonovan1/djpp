import time

from fastapi import APIRouter

from app.models.health import HealthStatus

router = APIRouter()

_start_time = time.time()


@router.get("/health", response_model=HealthStatus, tags=["ops"])
def health_check() -> HealthStatus:
    return HealthStatus(
        status="ok",
        uptime_seconds=round(time.time() - _start_time, 2),
    )
