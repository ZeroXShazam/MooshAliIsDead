"""Web scraper to extract content and images from URLs."""

import re
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


@dataclass
class ScrapedContent:
    """Content extracted from a webpage."""

    url: str
    title: str
    text: str
    images: list[tuple[str, bytes]]  # (url, raw_bytes)
    success: bool
    error: str | None = None


def _is_valid_url(url: str) -> bool:
    """Check if URL is valid and safe to fetch."""
    try:
        parsed = urlparse(url)
        return parsed.scheme in ("http", "https") and bool(parsed.netloc)
    except Exception:
        return False


def _extract_text(soup: BeautifulSoup) -> str:
    """Extract readable text from soup, removing scripts and styles."""
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    # Collapse multiple spaces/newlines
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _get_image_bytes(img_url: str, base_url: str, max_size_kb: int = 500) -> bytes | None:
    """Fetch image bytes, return None if too large or fetch fails."""
    try:
        full_url = urljoin(base_url, img_url)
        resp = requests.get(full_url, timeout=10, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "image" not in content_type:
            return None
        data = resp.content
        if len(data) > max_size_kb * 1024:
            return None
        return data
    except Exception:
        return None


def scrape_url(
    url: str,
    max_content_length: int = 15000,
    max_images: int = 5,
    image_max_size_kb: int = 500,
) -> ScrapedContent:
    """
    Scrape a URL and return title, text, and important images.

    Images are filtered by size and limited in count.
    """
    if not _is_valid_url(url):
        return ScrapedContent(
            url=url,
            title="",
            text="",
            images=[],
            success=False,
            error="Invalid URL. Please send a valid http(s) link.",
        )

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; LinkAnalyzerBot/1.0; +https://github.com/telegram-link-analyzer)",
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding or "utf-8"
        html = resp.text
    except requests.RequestException as e:
        return ScrapedContent(
            url=url,
            title="",
            text="",
            images=[],
            success=False,
            error=f"Could not fetch URL: {e}",
        )

    soup = BeautifulSoup(html, "lxml")
    title = (soup.title and soup.title.string) or url
    if title:
        title = title.strip()[:200]

    text = _extract_text(soup)
    if len(text) > max_content_length:
        text = text[:max_content_length] + "..."

    # Collect images: prefer og:image, then large img tags
    images: list[tuple[str, bytes]] = []
    seen_urls: set[str] = set()

    # Open Graph image
    og_img = soup.find("meta", property="og:image")
    if og_img and og_img.get("content"):
        img_url = og_img["content"]
        if img_url not in seen_urls:
            data = _get_image_bytes(img_url, url, image_max_size_kb)
            if data:
                images.append((img_url, data))
                seen_urls.add(img_url)

    # Other img tags, prefer larger ones
    imgs = soup.find_all("img", src=True)
    for img in imgs:
        if len(images) >= max_images:
            break
        src = img.get("src")
        if not src or src in seen_urls:
            continue
        # Prefer images that look like content (not icons/trackers)
        if any(skip in src.lower() for skip in ("pixel", "tracker", "1x1", "spacer", "icon")):
            continue
        data = _get_image_bytes(src, url, image_max_size_kb)
        if data:
            images.append((src, data))
            seen_urls.add(src)

    return ScrapedContent(
        url=url,
        title=title or "Untitled",
        text=text,
        images=images[:max_images],
        success=True,
    )
