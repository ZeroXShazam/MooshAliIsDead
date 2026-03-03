"""Configuration management for the Telegram Link Analyzer bot."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent / ".env")


def get_env(key: str, default: str = "") -> str:
    """Get environment variable."""
    return os.getenv(key, default) or default


TELEGRAM_BOT_TOKEN = get_env("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = get_env("GEMINI_API_KEY")
POE_API_KEY = get_env("POE_API_KEY")
# Poe bot/model name (e.g. "shazambot", "gpt-4o", "claude-3-5-sonnet")
POE_MODEL = get_env("POE_MODEL", "gpt-4o")

# AI provider: "gemini" or "poe"
AI_PROVIDER = get_env("AI_PROVIDER", "gemini").lower()

# Scraper settings
MAX_CONTENT_LENGTH = 15000  # chars to send to Gemini
MAX_IMAGES = 5  # max images to include in analysis
IMAGE_MAX_SIZE_KB = 500  # skip images larger than this
