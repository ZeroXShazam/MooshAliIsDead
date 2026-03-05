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

### Railway (recommended)

Runs `python main.py` as a long-lived process. No webhook setup.

1. [Deploy on Railway](https://railway.app/new?repository=https://github.com/ZeroXShazam/MooshAliIsDead)
2. Add env vars in Variables
3. Deploy

### Vercel (webhook)

1. [Deploy with Vercel](https://vercel.com/new/clone?repository-url=https://github.com/ZeroXShazam/MooshAliIsDead)
2. Add env vars in Project → Settings → Environment Variables
3. Set webhook — either:
   - Visit `https://<your-app>.vercel.app/api/setup_webhook`, or
   - Call: `https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<your-app>.vercel.app/api/webhook`

## Commands

- `/start` — Welcome
- `/help` — How it works
- `/new` — Clear chat history and start fresh

## License

MIT
