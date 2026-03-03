"""In-memory conversation state per chat."""

from dataclasses import dataclass

from scraper import ScrapedContent


@dataclass
class ChatContext:
    """Stored context for a chat session."""

    url: str
    title: str
    content: ScrapedContent
    summary: str


# chat_id -> ChatContext
_sessions: dict[int, ChatContext] = {}


def set_context(chat_id: int, url: str, title: str, content: ScrapedContent, summary: str) -> None:
    _sessions[chat_id] = ChatContext(url=url, title=title, content=content, summary=summary)


def get_context(chat_id: int) -> ChatContext | None:
    return _sessions.get(chat_id)


def clear_context(chat_id: int) -> None:
    _sessions.pop(chat_id, None)
