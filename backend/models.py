"""Structured types for the agent team and the /api/ask route."""

from typing import Literal

from pydantic import BaseModel, Field

Language = Literal["en", "es"]
InsuranceType = Literal["medicare", "masshealth", "commercial", "uninsured", "unknown"]


class Fact(BaseModel):
    """One fact, always tied to the tool result it came from."""

    text: str = Field(description="The fact in plain words.")
    source: str = Field(description="Source link exactly as the tool returned it.")
    checked_date: str = Field(description="Date checked exactly as the tool returned it (YYYY-MM-DD).")


class SpecialistResult(BaseModel):
    """What every specialist (Pharmacy Finder, Medication Access, Community) returns to the Front Desk."""

    answer: str = Field(description="Short plain-language answer for the Front Desk to use.")
    facts: list[Fact] = Field(default_factory=list, description="Only facts that came from tool results.")
    not_found: list[str] = Field(default_factory=list, description="Things the tools could not find.")
    warnings: list[str] = Field(default_factory=list, description="Safety notes, e.g. call to confirm stock.")
    pharmacy_ids: list[str] = Field(default_factory=list, description="IDs of pharmacies the answer is about, if any.")
    call_script: str | None = Field(default=None, description="Call script text from the call_script tool, if used.")


class FrontDeskOutput(BaseModel):
    """What the Front Desk model writes. Code then adds pharmacy cards and the run trace."""

    reply_text: str = Field(description="The full reply to the patient, in the patient's language.")
    pharmacy_ids: list[str] = Field(default_factory=list, description="Pharmacies to show as cards (IDs from specialists).")
    call_script: str | None = Field(default=None, description="Call script from a specialist, if any, in the patient's language.")
    sources: list[Fact] = Field(default_factory=list, description="Facts used in the reply, copied from specialist results.")
    follow_up_question: str | None = Field(default=None, description="One short question if a needed detail is missing.")


class PharmacyCard(BaseModel):
    id: str
    name: str
    address: str
    phone: str
    open_now: bool | None
    status: str
    closes_at: str | None = None
    opens_next: str | None = None
    distance_miles: float | None = None
    distance_label: str | None = None
    source: str
    checked_date: str


class TraceEvent(BaseModel):
    agent: str
    tool: str | None = None
    note: str | None = None


class AgentUsage(BaseModel):
    agent: str
    requests: int = 0
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    web_searches: int = 0
    cost_usd: float | None = None


class Usage(BaseModel):
    requests: int = 0
    tool_calls: int = 0
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    web_searches: int = 0
    cost_usd: float | None = Field(default=None, description="None if prices are not set in config.py.")
    by_agent: list[AgentUsage] = Field(default_factory=list)
    display: str = Field(default="", description='e.g. "This answer used 8,120 tokens (about $0.0012)."')


class FinalReply(BaseModel):
    """What POST /api/ask returns."""

    app: str
    run_id: str = ""
    language: Language
    reply_text: str
    stop_reason: str = "completed"
    pharmacy_cards: list[PharmacyCard] = Field(default_factory=list)
    call_script: str | None = None
    sources: list[Fact] = Field(default_factory=list)
    follow_up_question: str | None = None
    agents_run: list[str] = Field(default_factory=list)
    tools_run: list[str] = Field(default_factory=list)
    trace: list[TraceEvent] = Field(default_factory=list)
    usage: Usage = Field(default_factory=Usage)
    safety: list[str] = Field(default_factory=list, description="Code-level safety actions taken for this question.")


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    language: Language = "en"
    zip_code: str | None = Field(default=None, pattern=r"^\d{5}$")
    insurance_type: InsuranceType | None = None
