# MooshAliIsDead — Telegram AI Chat Bot

A Telegram bot that chats with you like a normal AI assistant. Powered by Gemini or Poe.

## Quick Start

```bash
git clone https://github.com/ZeroXShazam/MooshAliIsDead.git
cd MooshAliIsDead
pipenv install
cp .env.example .env   # Add your keys
pipenv run python main.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | From [@BotFather](https://t.me/BotFather) |
| `GEMINI_API_KEY` | Yes* | From [Google AI Studio](https://aistudio.google.com/apikey) |
| `POE_API_KEY` | Yes* | From [Poe](https://poe.com/api_key) |
| `AI_PROVIDER` | No | `gemini` (default) or `poe` |
| `POE_MODEL` | No | e.g. `shazambot`, `gpt-4o` |
| `GEMINI_MODEL` | No | e.g. `gemini-3-flash-preview` |

\* One of `GEMINI_API_KEY` or `POE_API_KEY` depending on `AI_PROVIDER`.

## Deploy

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?repository=https://github.com/ZeroXShazam/MooshAliIsDead)

### Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/ZeroXShazam/MooshAliIsDead)

After deploy, visit `/api/setup_webhook` to register the webhook.

## Commands

- `/start` — Welcome
- `/help` — How it works
- `/new` — Clear chat history and start fresh

## License

MIT
