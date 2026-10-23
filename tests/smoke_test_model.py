"""Tiny setup check: .env loading, Portkey key, and a tool call on the model.

Run from rxcompass/:  ..\\.venv\\Scripts\\python.exe -m tests.smoke_test_model
"""

from pydantic_ai import Agent

from backend.config import ENV_FILE, MODEL_NAME, MODEL_SETTINGS, get_model

agent = Agent(get_model(), model_settings=MODEL_SETTINGS)


@agent.tool_plain
def get_greeting_word() -> str:
    """Return the word the assistant should use to greet the user."""
    return "hello"


def main() -> None:
    print(f".env loaded from: {ENV_FILE or 'no .env file found; using environment variable'}")
    print(f"Model: {MODEL_NAME}")
    result = agent.run_sync("Call get_greeting_word, then say that word to me in one short sentence.")
    tool_called = any(
        getattr(part, "part_kind", "") == "tool-call"
        for msg in result.all_messages()
        for part in msg.parts
    )
    usage = result.usage
    print(f"Reply: {result.output}")
    print(f"Tool called: {tool_called}")
    print(f"Tokens: input={usage.input_tokens} cached={usage.cache_read_tokens} output={usage.output_tokens}")


if __name__ == "__main__":
    main()
