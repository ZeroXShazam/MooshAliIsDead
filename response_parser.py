"""Parse AI response: extract image URLs, send as normal Telegram photos."""

import re
from dataclasses import dataclass
from urllib.parse import urlparse

import requests


@dataclass
class ParsedBlock:
    """A block of content: either text or image."""

    kind: str  # "text" | "image"
    content: str  # text content or image URL
    caption: str | None = None  # for images: alt text


def _download_image(url: str, max_size_mb: int = 5) -> bytes | None:
    """Download image. Returns bytes if successful."""
    try:
        resp = requests.get(url, timeout=15, stream=True, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        data = resp.content
        if len(data) > max_size_mb * 1024 * 1024:
            return None
        # Accept if content-type is image, or if magic bytes look like image
        ct = resp.headers.get("content-type", "")
        if "image" in ct:
            return data
        # Check magic bytes
        if data[:2] == b"\xff\xd8" or data[:8] == b"\x89PNG\r\n\x1a\n":
            return data
        if data[:6] in (b"GIF87a", b"GIF89a") or (data[:4] == b"RIFF" and data[8:12] == b"WEBP"):
            return data
        return None
    except Exception:
        return None


def _clean_response(text: str) -> str:
    """Remove JSON blocks, action calls, DALL-E prompts."""
    for _ in range(20):
        start = text.find('"action"')
        if start < 0:
            break
        brace = text.rfind('{', 0, start)
        if brace < 0:
            break
        depth = 0
        end = -1
        for i in range(brace, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end < 0:
            break
        block = text[brace : end + 1]
        if 'dalle' in block or 'action_input' in block:
            text = (text[:brace].rstrip() + '\n' + text[end + 1 :].lstrip()).strip()
        else:
            break

    text = re.sub(r'\s*\{\s*"images"\s*:\s*\[[\s\S]*?\]\s*\}\s*', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def parse_response(text: str) -> list[ParsedBlock]:
    """
    Parse AI response. Extract ![alt](url) image refs.
    Returns list of blocks in order: text, image, text, ...
    """
    text = _clean_response(text)
    blocks: list[ParsedBlock] = []
    pattern = re.compile(r"!\[([^\]]*)\]\((https?://[^\)]+)\)")

    last_end = 0
    for m in pattern.finditer(text):
        before = text[last_end : m.start()].strip()
        if before:
            blocks.append(ParsedBlock(kind="text", content=before))

        alt, url = m.group(1), m.group(2)
        blocks.append(ParsedBlock(kind="image", content=url, caption=alt or None))
        last_end = m.end()

    after = text[last_end:].strip()
    if after:
        blocks.append(ParsedBlock(kind="text", content=after))

    if not blocks:
        blocks.append(ParsedBlock(kind="text", content=text))

    return blocks


def download_image(url: str) -> bytes | None:
    """Download image from URL. Returns bytes or None."""
    return _download_image(url)
