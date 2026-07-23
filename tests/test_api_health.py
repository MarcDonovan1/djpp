from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200


def test_health_check_body_shape(client: TestClient) -> None:
    resp = client.get("/health")
    body = resp.json()
    assert body["status"] == "ok"
    assert isinstance(body["uptime_seconds"], (int, float))
    assert body["uptime_seconds"] >= 0


def test_health_check_uptime_increases(client: TestClient) -> None:
    import time

    first = client.get("/health").json()["uptime_seconds"]
    time.sleep(0.05)
    second = client.get("/health").json()["uptime_seconds"]
    assert second >= first
