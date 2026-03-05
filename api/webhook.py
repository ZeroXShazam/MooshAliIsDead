"""Vercel serverless function: Telegram webhook handler."""

import asyncio
import json
import logging
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Bot

from bot import process_chat
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _read_body(h: BaseHTTPRequestHandler) -> bytes:
    content_length = int(h.headers.get("Content-Length", 0))
    return h.rfile.read(content_length) if content_length else b""


def _handle_update(update_dict: dict) -> None:
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    message = update_dict.get("message") or update_dict.get("edited_message")
    if not message:
        return

    text = (message.get("text") or "").strip()
    chat_id = message["chat"]["id"]

    if text and not text.startswith("/"):
        asyncio.run(process_chat(bot, chat_id, text))


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Telegram webhook is active.")
        return

    def do_POST(self):
        if not TELEGRAM_BOT_TOKEN:
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": False, "error": "TELEGRAM_BOT_TOKEN not set"}).encode())
            return

        try:
            body = _read_body(self)
            update = json.loads(body) if body else {}
            _handle_update(update)
        except Exception as exc:
            logger.exception("Webhook error: %s", exc)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True}).encode())
        return
