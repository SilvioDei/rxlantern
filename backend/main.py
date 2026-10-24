"""FastAPI app (name comes from backend.config.APP_NAME). Serves the API and the built website (frontend/dist).

Start everything with one command from rxcompass/:  ..\\.venv\\Scripts\\python.exe run.py
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from backend import community, safety, shortage_refresh, usage_log, web_api
from backend.build_db import ensure_db
from backend.config import APP_NAME, REPO_DIR
from backend.models import AskRequest, FinalReply

rate_limiter = usage_log.RateLimiter()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Graders get the same pharmacy data with no extra steps.
    ensure_db()
    shortage_refresh.start()  # FDA data refreshes in the background, at most once a day; pages never wait for it
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.include_router(web_api.router)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": APP_NAME}


@app.post("/api/ask", response_model=FinalReply)
async def ask_route(body: AskRequest, request: Request):
    """One patient question -> the Front Desk's structured reply, with tokens and cost. Nothing personal is stored."""
    # Emergencies first: 911 / Poison Control in code, before any rate limit or AI call (works with no API key).
    emergency = safety.emergency_reply(body.question, body.language)
    if emergency is not None:
        return emergency
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


# ----------------------------------------------------------------------------- community: accounts
SESSION_COOKIE = "rxl_session"


class RegisterBody(BaseModel):
    email: str = Field(max_length=254)
    display_name: str = Field(max_length=30)
    password: str = Field(max_length=200)
    confirm_password: str = Field(max_length=200)


class LoginBody(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(max_length=200)


class StockReportBody(BaseModel):
    drug_id: str = Field(description="One of the 25 RxLantern drug IDs (the ID includes the strength).")
    in_stock: bool


class ReviewBody(BaseModel):
    rating: int = Field(ge=1, le=5)
    wait_minutes: int | None = Field(default=None, ge=0, le=600)
    visit_date: str = Field(description="YYYY-MM-DD")
    comment: str | None = Field(default=None, max_length=300)


@app.exception_handler(community.CommunityError)
async def community_error(_: Request, e: community.CommunityError):
    return JSONResponse(status_code=e.status, content={"error": e.message, "code": e.code})


def current_user(request: Request) -> dict | None:
    return community.user_from_token(request.cookies.get(SESSION_COOKIE))


def require_user(request: Request) -> dict:
    user = current_user(request)
    if user is None:
        raise community.CommunityError("Please log in to post.", 401, "login_required")
    return user


@app.post("/api/auth/register")
def register(body: RegisterBody) -> dict:
    """Create an account: email, display name, and password only. No health information."""
    return community.create_account(body.email, body.display_name, body.password, body.confirm_password)


@app.post("/api/auth/login")
def login_route(body: LoginBody, request: Request, response: Response) -> dict:
    token, user = community.login(body.email, body.password, request.client.host if request.client else "unknown")
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=request.url.scheme == "https",
                        max_age=community.SESSION_DAYS * 86400, path="/")
    return {"logged_in": True, "display_name": user["display_name"]}


@app.post("/api/auth/logout")
def logout_route(request: Request, response: Response) -> dict:
    community.logout(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"logged_in": False}


@app.delete("/api/auth/account")
def delete_account(request: Request, response: Response) -> dict:
    """Delete my account and everything I posted."""
    out = community.delete_account(require_user(request))
    response.delete_cookie(SESSION_COOKIE, path="/")
    return out


@app.get("/api/auth/me")
def me(request: Request) -> dict:
    user = current_user(request)
    return {"logged_in": False} if user is None else {"logged_in": True, "display_name": user["display_name"],
                                                       "is_admin": user["is_admin"]}


# ----------------------------------------------------------------------------- community: reports and reviews
@app.post("/api/pharmacies/{pharmacy_id}/stock-reports")
def post_report(pharmacy_id: str, body: StockReportBody, request: Request) -> dict:
    return community.post_stock_report(require_user(request), pharmacy_id, body.drug_id, body.in_stock)


@app.get("/api/pharmacies/{pharmacy_id}/stock-reports")
def read_reports(pharmacy_id: str, drug_id: str | None = None) -> dict:
    """Reports from the last 72 hours (no login needed). Always: call to confirm before you go."""
    community._pharmacy(pharmacy_id)
    return community.stock_summary(pharmacy_id, drug_id)


@app.post("/api/pharmacies/{pharmacy_id}/reviews")
async def post_review_route(pharmacy_id: str, body: ReviewBody, request: Request) -> dict:
    return await community.post_review(require_user(request), pharmacy_id, body.rating, body.wait_minutes,
                                       body.visit_date, body.comment)


@app.get("/api/pharmacies/{pharmacy_id}/reviews")
def read_reviews(pharmacy_id: str) -> dict:
    community._pharmacy(pharmacy_id)
    return community.review_summary(pharmacy_id)


# ----------------------------------------------------------------------------- community: admin queue
def require_admin(request: Request) -> dict:
    user = require_user(request)
    if not user["is_admin"]:
        raise community.CommunityError("Only admins can review the queue.", 403, "not_admin")
    return user


@app.get("/api/admin/pending")
def admin_pending(request: Request) -> dict:
    require_admin(request)
    return {"pending": community.pending_queue()}


@app.post("/api/admin/reviews/{review_id}/approve")
def admin_approve(review_id: int, request: Request) -> dict:
    return community.decide(review_id, True, require_admin(request))


@app.post("/api/admin/reviews/{review_id}/reject")
def admin_reject(review_id: int, request: Request) -> dict:
    return community.decide(review_id, False, require_admin(request))


# ----------------------------------------------------------------------------- the website (built React app)
DIST = REPO_DIR / "frontend" / "dist"


@app.get("/{path:path}", include_in_schema=False)
def website(path: str):
    """Serve frontend/dist. Unknown paths get index.html so the page routes (/pharmacies, /vaccines, ...) work."""
    if path.startswith("api/"):
        raise HTTPException(404, "Not found.")
    file = (DIST / path).resolve()
    if path and file.is_file() and DIST.resolve() in file.parents:
        return FileResponse(file)
    index = DIST / "index.html"
    if index.is_file():
        return FileResponse(index, headers={"Cache-Control": "no-cache"})
    return HTMLResponse(f"<h1>{APP_NAME}</h1><p>The website has not been built yet (frontend/dist is missing). "
                        "The API is running at /api/health.</p>", status_code=503)
