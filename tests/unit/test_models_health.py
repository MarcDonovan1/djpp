from app.models.health import HealthStatus


def test_health_status_valid() -> None:
    hs = HealthStatus(status="ok", uptime_seconds=12.5)
    assert hs.status == "ok"
    assert hs.uptime_seconds == 12.5


def test_health_status_serialization() -> None:
    hs = HealthStatus(status="ok", uptime_seconds=1.0)
    data = hs.model_dump()
    assert data == {"status": "ok", "uptime_seconds": 1.0}


def test_health_status_coerces_int_to_float() -> None:
    hs = HealthStatus(status="ok", uptime_seconds=5)
    assert isinstance(hs.uptime_seconds, float)
    assert hs.uptime_seconds == 5.0


def test_health_status_missing_field_raises() -> None:
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        HealthStatus(status="ok")  # type: ignore[call-arg]
