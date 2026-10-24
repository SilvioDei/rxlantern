"""Safety rules that run in code, with no model and no API key needed.

- redact_phi: removes names, birthdates, member IDs, and similar details before anything is used or logged.
- emergency_reply: if a question sounds like an emergency or overdose (English or Spanish), the patient gets
  911 and Poison Control at once, before any AI call, and the rule is written to the audit trail.
"""

import re
import uuid

from backend.config import APP_NAME
from backend.models import FinalReply, TraceEvent, Usage

PHI_PATTERNS = [
    (re.compile(r"\b(my name is|i am called|me llamo|mi nombre es)\s+[A-ZÁÉÍÓÚÑa-záéíóúñ'\-]+(\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ'\-]+)?", re.I), r"\1 [removed]"),
    (re.compile(r"\b(born on|born|birthday is|dob|date of birth|fecha de nacimiento|nac[ií] el)\b[:\s]*[^,.;]*", re.I), "[birthdate removed]"),
    (re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"), "[date removed]"),
    (re.compile(r"\b(member|subscriber|policy|medicaid|masshealth|medicare)\s*(id|number|#|no\.?)\s*[:#]?\s*[A-Z0-9-]{4,}", re.I), "[member ID removed]"),
    (re.compile(r"\b[A-Z]{1,3}\d{7,}\b|\b\d{8,}\b"), "[ID removed]"),
    (re.compile(r"\b\d{3}[-.\s]\d{2}[-.\s]\d{4}\b"), "[ID removed]"),
]


def redact_phi(text: str) -> tuple[str, bool]:
    out = text
    for pat, repl in PHI_PATTERNS:
        out = pat.sub(repl, out)
    return out, out != text


# ----------------------------------------------------------------------------- emergencies
_PILLS = r"(pills?|tablets?|capsules?|meds|medicines?|medications?|doses?|gummies)"
_PASTILLAS = r"(pastillas?|p[ií]ldoras?|tabletas?|c[aá]psulas?|medicinas?|medicamentos?|dosis)"
EMERGENCY = re.compile(
    # English
    r"\bover\s*dos(e|ed|ing)\b|"
    r"\b(took|taken|take|swallowed|ate)\s+(too\s+many|too\s+much|a\s+(whole|full)\s+bottle|all\s+(of\s+)?(my|the))\b|"
    r"\btoo\s+many\s+" + _PILLS + r"\b|"
    r"\b(can'?t|cannot|can\s+not|could\s?n'?t|unable\s+to|trouble|hard\s+to|struggling\s+to)\s+breath(e|ing)?\b|"
    r"\bnot\s+breathing\b|\bstopped\s+breathing\b|\bchest\s+pain\b|\bheart\s+attack\b|\bstroke\b|"
    r"\bpoison(ed|ing)?\b(?!\s+(ivy|oak|sumac|control))|\bswallowed\s+(bleach|poison|cleaner|batter(y|ies))\b|"
    r"\b(unconscious|unresponsive|passed\s+out|won'?t\s+wake\s+up|seizures?|anaphyla\w*)\b|"
    r"\bthroat\s+(is\s+)?(closing|swelling)\b|\bsevere\s+allergic\s+reaction\b|"
    r"\b(suicid\w*|kill\s+myself|end\s+my\s+life|want\s+to\s+die|hurt\s+myself)\b|"
    # Spanish
    r"\bsobredosis\b|"
    r"\b(tom[eéó]|tomado|trag[uóo]e?|me\s+tom[eé])\s+(demasiad[ao]s?|muchas?|toda\s+la\s+caja|todo\s+el\s+frasco)\b|"
    r"\bdemasiad[ao]s\s+" + _PASTILLAS + r"\b|"
    r"\bno\s+(puedo|puede|pod[ií]a)\s+respirar\b|\bno\s+respira\b|\bdificultad\s+para\s+respirar\b|"
    r"\bdolor\s+(de|en\s+el)\s+pecho\b|\bataque\s+(al\s+coraz[oó]n|card[ií]aco)\b|"
    r"\benvenen\w*|\bintoxica\w*|\binconsciente\b|\bdesmay\w*|\bconvulsi\w*|\bno\s+despierta\b|"
    r"\bse\s+(me\s+)?cierra\s+la\s+garganta\b|\balergia\s+grave\b|"
    r"\b(suicid\w*|matarme|quitarme\s+la\s+vida|me\s+quiero\s+morir|quiero\s+morir|hacerme\s+da[ñn]o)\b",
    re.I)
SELF_HARM = re.compile(r"suicid|kill\s+myself|end\s+my\s+life|want\s+to\s+die|hurt\s+myself|matarme|"
                       r"quitarme\s+la\s+vida|quiero\s+morir|hacerme\s+da", re.I)

EMERGENCY_TEXT = {
    "en": "If this is an emergency, call 911. For a possible poisoning or overdose, call Poison Control at 1-800-222-1222.",
    "es": ("Si es una emergencia, llame al 911. Para un posible envenenamiento o sobredosis, llame a Poison Control "
           "(Control de Envenenamientos) al 1-800-222-1222."),
}
CRISIS_TEXT = {
    "en": "If you are thinking about hurting yourself, call or text 988 (Suicide & Crisis Lifeline), any time.",
    "es": "Si está pensando en hacerse daño, llame o envíe un texto al 988 (Línea de Prevención del Suicidio y Crisis), "
          "a cualquier hora. Hay ayuda en español.",
}
EMERGENCY_SOURCES = [
    ("Poison Control: 1-800-222-1222", "https://www.poison.org/contact-us", "2026-10-23"),
    ("988 Suicide & Crisis Lifeline", "https://988lifeline.org/", "2026-10-23"),
]


def is_emergency(text: str) -> bool:
    return bool(EMERGENCY.search(text or ""))


def emergency_reply(question: str, language: str = "en") -> FinalReply | None:
    """The emergency message, decided in code before any AI call. Logged to the audit trail. None if not an emergency."""
    if not is_emergency(question):
        return None
    from backend import usage_log
    from backend.models import Fact

    language = language if language in ("en", "es") else "en"
    clean, _ = redact_phi(question)
    text = EMERGENCY_TEXT[language]
    if SELF_HARM.search(question):
        text += " " + CRISIS_TEXT[language]
    rule = "emergency message shown (rule in code, no model call)"
    reply = FinalReply(app=APP_NAME, run_id=uuid.uuid4().hex[:12], language=language, reply_text=text,
                       stop_reason="emergency message shown", agents_run=["Front Desk (code safety rule)"],
                       trace=[TraceEvent(agent="Front Desk", note=rule)], usage=Usage(display=""),
                       sources=[Fact(text=t, source=s, checked_date=d) for t, s, d in EMERGENCY_SOURCES],
                       safety=[rule], emergency=True)
    ts = usage_log.boston_now().isoformat(timespec="seconds")
    zero = {"input_tokens": 0, "cached_input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "web_searches": 0,
            "model_requests": 0, "tool_calls": 0, "cost_usd": 0.0}
    usage_log.write_run(
        {"run_id": reply.run_id, "timestamp": ts, "language": language, "mode": "normal", "agents_run": reply.agents_run,
         "tools_run": [], "by_agent": [], "total": zero, "stop_reason": reply.stop_reason},
        {"run_id": reply.run_id, "timestamp": ts, "language": language, "mode": "normal", "question_redacted": clean,
         "stop_reason": reply.stop_reason, "agents_run": reply.agents_run,
         "steps": [{"type": "code_rule", "note": rule}], "tokens": {"total": zero, "by_agent": []},
         "safety_rules_fired": reply.safety, "reply_preview": text[:200]})
    return reply
