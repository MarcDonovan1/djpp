from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.api import health, jobs


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    # startup logic (e.g. connect to a queue/DB) goes here
    yield
    # shutdown logic goes here

def create_app() -> FastAPI:
    app = FastAPI(title="Jobs API", version="1.0.0", lifespan=lifespan)

    return app

app = create_app()
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
app.include_router(health.router)  # /health and /metrics live at root, no prefix
