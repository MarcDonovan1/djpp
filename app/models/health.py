from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    uptime_seconds: float
