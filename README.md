# Telegram Link Analyzer Bot

Send a link to this bot and get an AI-powered full explanation with important pictures.

**Supports:** Gemini API and Poe API

## One-Click Deploy

### Deploy on Railway (recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?repository=https://github.com/YOUR_USERNAME/TelegramBrowser)

1. Click the button and connect your GitHub repo
2. Add environment variables in Railway dashboard
3. Deploy — the bot starts automatically

### Deploy on Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/YOUR_USERNAME/TelegramBrowser)

1. Import your repo and add environment variables
2. Deploy
3. **Set webhook:** Visit `https://your-app.vercel.app/api/setup_webhook`

> Replace `YOUR_USERNAME` with your GitHub username in the deploy URLs.

## Quick Start (Local)

```bash
git clone https://github.com/YOUR_USERNAME/TelegramBrowser.git
cd TelegramBrowser
pipenv install
cp .env.example .env   # Edit with your keys
pipenv run python main.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | From [@BotFather](https://t.me/BotFather) |
| `GEMINI_API_KEY` | Yes* | From [Google AI Studio](https://aistudio.google.com/apikey) |
| `POE_API_KEY` | Yes* | From [Poe](https://poe.com/api_key) |
| `AI_PROVIDER` | No | `gemini` (default) or `poe` |
| `POE_MODEL` | No | Poe bot name, e.g. `shazambot` |
| `GEMINI_MODEL` | No | e.g. `gemini-3-flash-preview` |
| `REPO_URL` | No | For "View source" button |

\* One of `GEMINI_API_KEY` or `POE_API_KEY` depending on `AI_PROVIDER`.

## How It Works

1. Send a link to the bot
2. Bot scrapes the page (title, text, images)
3. AI (Gemini or Poe) analyzes the content
4. You get a formatted summary + key images + buttons

## Documentation

- **[Guide & Reference](docs/GUIDE.md)** — Architecture, flow, troubleshooting

## License

MIT
