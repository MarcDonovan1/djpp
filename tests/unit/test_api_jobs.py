from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from app.api.jobs import _jobs
from app.models.job import JobStatus

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_job_returns_201_and_job(client: TestClient) -> None:
    resp = client.post("/jobs", json={"name": "job-a", "payload": {"x": 1}})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "job-a"
    assert body["payload"] == {"x": 1}
    assert body["status"] == "pending"
    assert body["attempts"] == 0
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_job_defaults_payload(client: TestClient) -> None:
    resp = client.post("/jobs", json={"name": "job-b"})
    assert resp.status_code == 201
    assert resp.json()["payload"] == {}


def test_create_job_missing_name_returns_422(client: TestClient) -> None:
    resp = client.post("/jobs", json={})
    assert resp.status_code == 422


def test_list_jobs_empty(client: TestClient) -> None:
    resp = client.get("/jobs")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_jobs_returns_created_jobs(client: TestClient) -> None:
    client.post("/jobs", json={"name": "job-a"})
    client.post("/jobs", json={"name": "job-b"})

    resp = client.get("/jobs")
    assert resp.status_code == 200
    names = {job["name"] for job in resp.json()}
    assert names == {"job-a", "job-b"}


def test_list_jobs_filter_by_status(client: TestClient) -> None:
    _ = client.post("/jobs", json={"name": "job-a"}).json()
    client.post("/jobs", json={"name": "job-b"})

    # Manually move job-a's status by going through retry after failing it
    # (simpler: just filter on PENDING, since both start pending)
    resp = client.get("/jobs", params={"status_filter": "pending"})
    assert resp.status_code == 200
    assert len(resp.json()) == 2

    resp = client.get("/jobs", params={"status_filter": "failed"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_job_success(client: TestClient) -> None:
    created = client.post("/jobs", json={"name": "job-a"}).json()
    resp = client.get(f"/jobs/{created['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


def test_get_job_not_found(client: TestClient) -> None:
    resp = client.get(f"/jobs/{uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Job not found"


def test_get_job_invalid_uuid_returns_422(client: TestClient) -> None:
    resp = client.get("/jobs/not-a-uuid")
    assert resp.status_code == 422


def test_retry_job_not_found(client: TestClient) -> None:
    resp = client.post(f"/jobs/{uuid4()}/retry")
    assert resp.status_code == 404


def test_retry_job_from_pending_returns_409(client: TestClient) -> None:
    created = client.post("/jobs", json={"name": "job-a"}).json()
    resp = client.post(f"/jobs/{created['id']}/retry")
    assert resp.status_code == 409
    assert "pending" in resp.json()["detail"]


def test_retry_job_from_failed_succeeds(client: TestClient) -> None:
    created = client.post("/jobs", json={"name": "job-a"}).json()
    job_id = UUID(created["id"])
    _jobs[job_id].status = JobStatus.FAILED  # simulate a failed job directly

    resp = client.post(f"/jobs/{job_id}/retry")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "pending"
    assert body["attempts"] == 1


def test_retry_job_from_succeeded_succeeds(client: TestClient) -> None:
    created = client.post("/jobs", json={"name": "job-a"}).json()
    job_id = UUID(created["id"])
    _jobs[job_id].status = JobStatus.SUCCEEDED

    resp = client.post(f"/jobs/{job_id}/retry")
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"


def test_retry_job_increments_attempts_each_time(client: TestClient) -> None:
    created = client.post("/jobs", json={"name": "job-a"}).json()
    job_id = UUID(created["id"])

    _jobs[job_id].status = JobStatus.FAILED
    resp1 = client.post(f"/jobs/{job_id}/retry")
    assert resp1.json()["attempts"] == 1

    _jobs[job_id].status = JobStatus.FAILED
    resp2 = client.post(f"/jobs/{job_id}/retry")
    assert resp2.json()["attempts"] == 2


def test_delete_job_success(client: TestClient) -> None:
    created = client.post("/jobs", json={"name": "job-a"}).json()
    resp = client.delete(f"/jobs/{created['id']}")
    assert resp.status_code == 204

    resp = client.get(f"/jobs/{created['id']}")
    assert resp.status_code == 404


def test_delete_job_not_found(client: TestClient) -> None:
    resp = client.delete(f"/jobs/{uuid4()}")
    assert resp.status_code == 404
