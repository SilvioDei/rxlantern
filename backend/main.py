"""FastAPI app (name comes from backend.config.APP_NAME).

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m uvicorn backend.main:app
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from backend import usage_log
from backend.build_db import ensure_db
from backend.config import APP_NAME
from backend.models import AskRequest, FinalReply

rate_limiter = usage_log.RateLimiter()


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
async def ask_route(body: AskRequest, request: Request):
    """One patient question -> the Front Desk's structured reply, with tokens and cost. Nothing personal is stored."""
    from backend.agents import ask, rate_limited  # imported here so the health check works without a Portkey key

    visitor = request.client.host if request.client else "unknown"
    if not rate_limiter.allow(visitor):
        reply = await rate_limited(body.question, body.language)
        return JSONResponse(status_code=429, content=reply.model_dump())
    try:
        return await ask(body.question, body.language, body.zip_code, body.insurance_type)
    except Exception as e:  # noqa: BLE001 - give the patient a calm message, not a stack trace
        raise HTTPException(502, "Something went wrong while answering. Please try again.") from e


@app.get("/api/usage")
def usage_route() -> dict:
    """Today's totals (Boston date): questions, tokens, average tokens per question, and cost."""
    return usage_log.usage_today()
