# Telegram Link Analyzer Bot — Guide & Reference

A Telegram bot that analyzes web links with AI and returns summaries with key images. **Conversational** — ask follow-up questions about the page; the bot remembers context.

## Quick Start

1. **Get a Telegram bot token** — [@BotFather](https://t.me/BotFather) → `/newbot`
2. **Get an AI API key** — [Gemini](https://aistudio.google.com/apikey) or [Poe](https://poe.com/api_key)
3. **Configure** — Copy `.env.example` to `.env` and fill in your keys
4. **Run** — `pipenv run python main.py`

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Telegram   │────▶│  main.py     │────▶│  bot.py     │────▶│  ai_agent.py │
│  (user)     │     │  (handlers)  │     │  (logic)    │     │  (Gemini/Poe)│
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                            │                    │
                            │                    ▼
                            │             ┌─────────────┐     ┌──────────────────┐
                            │             │  scraper.py  │     │  conversation.py │
                            │             │  (fetch URL) │     │  (context store)  │
                            │             └─────────────┘     └──────────────────┘
                            ▼
                    ┌──────────────┐
                    │  config.py   │
                    │  (.env)      │
                    └──────────────┘
```

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point, Telegram handlers (start, messages, callbacks) |
| `bot.py` | Link processing + follow-up answers (with buttons) |
| `conversation.py` | In-memory context store per chat |
| `ai_agent.py` | AI integration: Gemini & Poe, prompt building |
| `scraper.py` | Web scraping: extract text + images from URLs |
| `config.py` | Environment variables, model fallbacks |
| `api/webhook.py` | Vercel serverless webhook handler |
| `api/setup_webhook.py` | One-time webhook registration |
| `scripts/list_models.py` | List available Gemini models |

## Flow

1. **User sends URL** → `handle_message` extracts URLs
2. **For each URL** → `process_link`:
   - Sends "Fetching and analyzing..."
   - `scraper.scrape_url()` fetches page content + images
   - `ai_agent.analyze_content()` calls Gemini or Poe
   - Stores context in `conversation` for follow-ups
   - Sends summary (HTML) + images + "View source" + "New link" buttons
3. **User sends text (no URL)** → `process_followup`:
   - Uses stored context (url, content, summary)
   - `ai_agent.answer_followup()` answers based on page content
   - Sends reply + "View source" + "New link" buttons
4. **Commands**: `/start`, `/help`, `/new` (clear context)

## AI Prompt Format

The bot instructs the LLM to output **Telegram HTML**:
- Allowed: `<b>`, `<i>`, `<code>`, `<a href="">`
- Avoid: `*`, `_`, `` ` ``, `[`, `]` (break parsing)
- Escape: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | From @BotFather |
| `GEMINI_API_KEY` | Yes* | Google AI Studio |
| `GEMINI_MODEL` | No | Default: gemini-3-flash-preview |
| `POE_API_KEY` | Yes* | Poe API |
| `POE_MODEL` | No | e.g. shazambot, gpt-4o |
| `AI_PROVIDER` | No | `gemini` or `poe` |
| `REPO_URL` | No | For "View source" button |

## Deployment

- **Railway** — Long-running, polling. Use `main.py`.
- **Vercel** — Serverless webhook. Deploy `api/webhook.py`, then visit `/api/setup_webhook`.

## Troubleshooting

- **404 model** — Run `pipenv run python -m scripts.list_models` to see valid models
- **Image error** — Bot falls back to text-only if images fail
- **Parse error** — Bot falls back to plain text if HTML fails
