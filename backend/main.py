"""FastAPI app (name comes from backend.config.APP_NAME).

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m uvicorn backend.main:app
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.build_db import ensure_db
from backend.config import APP_NAME


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Graders get the same pharmacy data with no extra steps.
    ensure_db()
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": APP_NAME}
