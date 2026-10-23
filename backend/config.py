"""Central settings for RxCompass.

The model name lives here and nowhere else. Every agent builds its model with
get_model() so there is exactly one place to change it.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai.models.openai import OpenAIResponsesModel, OpenAIResponsesModelSettings
from pydantic_ai.providers.openai import OpenAIProvider

MODEL_NAME = "gpt-6-luna"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
OUTPUT_DIR = REPO_DIR / "output"


def load_env() -> Path | None:
    """Load .env from rxcompass/ first, then from the folder one level above.

    Returns the path that was loaded, or None if no .env file was found
    (in that case an already-set PORTKEY_API_KEY environment variable is used).
    """
    for candidate in (REPO_DIR / ".env", REPO_DIR.parent / ".env"):
        if candidate.is_file():
            load_dotenv(candidate, override=False)
            return candidate
    return None


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
