"""FastAPI app (name comes from backend.config.APP_NAME).

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m uvicorn backend.main:app
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from backend.build_db import ensure_db
from backend.config import APP_NAME
from backend.models import AskRequest, FinalReply


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Graders get the same pharmacy data with no extra steps.
    ensure_db()
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": APP_NAME}


@app.post("/api/ask", response_model=FinalReply)
async def ask_route(body: AskRequest) -> FinalReply:
    """One patient question -> the Front Desk's structured reply. Nothing personal is stored."""
    from backend.agents import ask  # imported here so the health check works without a Portkey key

    try:
        return await ask(body.question, body.language, body.zip_code, body.insurance_type)
    except Exception as e:  # noqa: BLE001 - give the patient a calm message, not a stack trace
        name = type(e).__name__
        if name == "UsageLimitExceeded":
            raise HTTPException(429, "This question needed too many steps. Please ask it in a shorter way.") from e
        raise HTTPException(502, "Something went wrong while answering. Please try again.") from e
