"""Chat history per user."""

# chat_id -> list of {"role": "user"|"model"|"assistant", "content": str}
_sessions: dict[int, list[dict]] = {}


def get_history(chat_id: int) -> list[dict]:
    return _sessions.get(chat_id, [])


def set_history(chat_id: int, history: list[dict]) -> None:
    _sessions[chat_id] = history


def clear_history(chat_id: int) -> None:
    _sessions.pop(chat_id, None)
