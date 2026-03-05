"""AI chat agent. Supports Gemini and Poe with conversation history."""

from dataclasses import dataclass

from config import AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, POE_API_KEY, POE_MODEL


@dataclass
class ChatResult:
    """Result of AI chat."""

    text: str
    success: bool
    error: str | None = None


SYSTEM_PROMPT = """You are a friendly, helpful AI assistant in a Telegram bot. Chat naturally.

FORMATTING (STRICT - output goes to Telegram):
- Use ONLY Telegram HTML: <b>bold</b>, <i>italic</i>, <code>code</code>, <a href="url">link</a>
- NEVER use Markdown: no **, no *, no `, no [text](url) for links — use <a href="url">text</a>
- Escape & < > in plain text as &amp; &lt; &gt;
- Use <b>Header</b> for headers, • or - for bullets
- Emojis like 📄 ✅ ⚠️ 💡 are fine

IMAGES:
- When including figures, use: ![caption](direct_image_url)
- URL must point directly to an image file (.jpg, .png, .gif, etc.)
- Example: ![Figure 1](https://example.com/figure.jpg)
- NEVER output JSON, "action", or "dalle" — we only display images from URLs

Keep responses concise but thorough. Structure with headers and bullets."""


def chat(chat_id: int, message: str, history: list[dict]) -> tuple[ChatResult, list[dict]]:
    """
    Send message to AI, get response. Returns (result, updated_history).
    history: list of {"role": "user"|"model", "content": str}
    """
    if AI_PROVIDER == "poe":
        return _chat_poe(chat_id, message, history)
    return _chat_gemini(chat_id, message, history)


def _chat_gemini(chat_id: int, message: str, history: list[dict]) -> tuple[ChatResult, list[dict]]:
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        return ChatResult("", False, "GEMINI_API_KEY not configured."), history

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)

        # Build history for start_chat: list of Content with role and parts
        gemini_history = []
        for h in history:
            role = "user" if h["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [h["content"]]})

        chat_session = model.start_chat(history=gemini_history)
        response = chat_session.send_message(message)

        if not response.text:
            return ChatResult("", False, "Empty response."), history

        text = response.text.strip()
        new_history = history + [
            {"role": "user", "content": message},
            {"role": "model", "content": text},
        ]
        # Keep last 20 exchanges to avoid token limits
        if len(new_history) > 40:
            new_history = new_history[-40:]
        return ChatResult(text, True), new_history
    except Exception as e:
        return ChatResult("", False, f"Gemini failed: {str(e)}"), history


def _chat_poe(chat_id: int, message: str, history: list[dict]) -> tuple[ChatResult, list[dict]]:
    from openai import OpenAI

    if not POE_API_KEY:
        return ChatResult("", False, "POE_API_KEY not configured."), history

    try:
        client = OpenAI(api_key=POE_API_KEY, base_url="https://api.poe.com/v1")

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": message})

        resp = client.chat.completions.create(
            model=POE_MODEL,
            messages=messages,
        )
        text = resp.choices[0].message.content
        if not text:
            return ChatResult("", False, "Empty response."), history

        text = text.strip()
        new_history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": text},
        ]
        if len(new_history) > 40:
            new_history = new_history[-40:]
        return ChatResult(text, True), new_history
    except Exception as e:
        return ChatResult("", False, f"Poe failed: {str(e)}"), history
