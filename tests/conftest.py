from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.health import router as health_router
from app.api.jobs import router as jobs_router


@pytest.fixture
def app() -> FastAPI:
    test_app = FastAPI()
    test_app.include_router(jobs_router, prefix="/jobs")
    test_app.include_router(health_router)
    return test_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_jobs_store() -> Any:
    """Reset the in-memory job store between tests so they don't leak state."""
    from app.api.jobs import _jobs

    _jobs.clear()
    yield
    _jobs.clear()
