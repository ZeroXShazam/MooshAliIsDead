"""One-time setup: set Telegram webhook to your Vercel URL. Call after deploy."""

import json
import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import requests


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        vercel_url = os.getenv("VERCEL_URL")  # e.g. your-app.vercel.app

        if not token or not vercel_url:
            self.send_response(400)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": False,
                "error": "Set TELEGRAM_BOT_TOKEN and VERCEL_URL (or use ?url=...)",
            }).encode())
            return

        base = f"https://{vercel_url}" if not vercel_url.startswith("http") else vercel_url
        webhook_url = (params.get("url") or [f"{base}/api/webhook"])[0]
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/setWebhook",
            json={"url": webhook_url},
            timeout=10,
        )
        data = resp.json()

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
        return
