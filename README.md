# Telegram Link Analyzer Bot

Send a link to this bot and get an AI-powered full explanation with important pictures.

**Supports:** Gemini API and Poe API

## One-Click Deploy

### Deploy on Railway (recommended)

Railway runs the bot 24/7 with no timeout limits. Best for reliability.

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?repository=https://github.com/YOUR_USERNAME/TelegramBrowser)

1. Click the button and connect your GitHub repo
2. Add environment variables in Railway dashboard
3. Deploy — the bot starts automatically

### Deploy on Vercel

Vercel uses webhooks (serverless). After deploy, set the webhook once.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/TelegramBrowser)

1. Click the button and import your repo
2. Add environment variables
3. Deploy
4. **Set webhook:** Visit `https://your-app.vercel.app/api/setup_webhook` (or add `?url=https://your-app.vercel.app/api/webhook` if needed)

> **Note:** Replace `YOUR_USERNAME` with your GitHub username in the deploy URLs above.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | From [@BotFather](https://t.me/BotFather) |
| `GEMINI_API_KEY` | Yes* | From [Google AI Studio](https://aistudio.google.com/apikey) |
| `POE_API_KEY` | Yes* | From [Poe](https://poe.com/api_key) |
| `AI_PROVIDER` | No | `gemini` (default) or `poe` |
| `POE_MODEL` | No | Poe bot name, e.g. `shazambot` or `gpt-4o` |

\* One of `GEMINI_API_KEY` or `POE_API_KEY` is required depending on `AI_PROVIDER`.

## Local Development

```bash
# Clone and install
git clone https://github.com/YOUR_USERNAME/TelegramBrowser.git
cd TelegramBrowser
pip install -r requirements.txt

# Create .env from .env.example and fill in your keys
cp .env.example .env

# Run (polling mode)
python main.py
```

## How It Works

1. You send a link to the bot
2. Bot scrapes the page (title, text, images)
3. AI (Gemini or Poe) analyzes the content
4. Bot sends you a summary plus important images
