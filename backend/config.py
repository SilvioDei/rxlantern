"""Central settings for RxLantern.

The app name and the model name live here and nowhere else. The website, agents, and page
title read APP_NAME from here; every agent builds its model with get_model().
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

APP_NAME = "RxLantern"
MODEL_NAME = "gpt-6-luna"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"

# gpt-6-luna prices in US dollars per 1 million tokens, from Portkey's pricing config
# (https://api.portkey.ai/model-configs/pricing/openai/gpt-6-luna, checked 2026-10-23, standard tier <= 272k context).
# Portkey lists prices in cents per token (0.00001 cents/token = $0.10 per 1M), the same unit as its other OpenAI
# entries (for example gpt-4o-mini 0.000015 = $0.15 per 1M). Web search is a flat price per search call.
PRICES_USD_PER_MILLION = {"input": 0.10, "cached_input": 0.01, "output": 0.50}
WEB_SEARCH_USD_PER_CALL = 0.01
PRICE_SOURCE = "https://api.portkey.ai/model-configs/pricing/openai/gpt-6-luna"

# Spending limits.
MAX_MODEL_REQUESTS_PER_QUESTION = 14
MAX_TOOL_CALLS_PER_QUESTION = 24
MAX_TOKENS_PER_QUESTION = 60_000          # input + output, all agents together
DAILY_TOKEN_BUDGET = 3_000_000            # whole app, per Boston calendar day
MAX_QUESTIONS_PER_VISITOR_PER_HOUR = 30

# Sample stock reports and reviews for demonstration (graders start with an empty database). They are never saved
# to the database, never counted with real posts, and always shown with a "Sample" badge. Turn off with False
# (or set RXLANTERN_SHOW_SAMPLE_DATA=0 in the environment).
SHOW_SAMPLE_DATA = os.getenv("RXLANTERN_SHOW_SAMPLE_DATA", "1").strip().lower() not in ("0", "false", "no", "off")

# Who can approve or reject comments in the moderation queue. Kept out of the public repo:
# set RXLANTERN_ADMIN_EMAILS in your .env (comma-separated), e.g. RXLANTERN_ADMIN_EMAILS=you@example.com
ADMIN_EMAILS_ENV = "RXLANTERN_ADMIN_EMAILS"


def admin_emails() -> set[str]:
    """Admin emails from RXLANTERN_ADMIN_EMAILS. Missing or empty = no admins (the queue still works, nobody can
    approve), never an error."""
    return {e.strip().lower() for e in (os.getenv(ADMIN_EMAILS_ENV) or "").split(",") if e.strip()}

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
OUTPUT_DIR = REPO_DIR / "output"


def load_env() -> Path | None:
    """Load .env from rxcompass/ first, then from the folder one level above (where graders put theirs).

    Both files are read, so one never hides the other. A value set earlier wins: an already-set environment
    variable beats rxcompass/.env, which beats ../.env. Returns the first file found, or None if neither exists
    (then an already-set PORTKEY_API_KEY environment variable is used).
    """
    found = None
    for candidate in (REPO_DIR / ".env", REPO_DIR.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            found = found or candidate
    return found


ENV_FILE = load_env()


def get_portkey_key() -> str:
    key = os.getenv("PORTKEY_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "PORTKEY_API_KEY not found. Put it in a .env file in rxcompass/ "
            "or in the folder one level above it."
        )
    return key


def get_model() -> OpenAIResponsesModel:
    """gpt-6-luna through Portkey, using the Responses API so function tools work."""
    key = get_portkey_key()
    client = AsyncOpenAI(
        base_url=PORTKEY_BASE_URL,
        api_key=key,
        default_headers={"x-portkey-api-key": key},
    )
    return OpenAIResponsesModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))


# Shared model settings for every agent. Tools are allowed with the Responses API.
MODEL_SETTINGS = OpenAIResponsesModelSettings()
