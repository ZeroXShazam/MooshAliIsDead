# MooshAliIsDead — Guide

A Telegram bot that acts as a normal AI chat assistant with conversation memory.

## Architecture

```
User → main.py (handlers) → bot.py (process_chat) → ai_agent.py (Gemini/Poe)
                                    ↓
                            conversation.py (history)
```

## Flow

1. User sends message
2. Bot loads chat history for that user
3. AI (Gemini or Poe) gets message + history, returns response
4. Response is parsed: extract `![alt](url)` images, preserve text
5. Bot sends: text blocks (HTML) + downloaded images (as photos)
6. History is updated and stored

## Rich Output

- **Formatting**: AI uses Telegram HTML (`<b>`, `<i>`, `<code>`, `<a>`)
- **Images**: AI can include `![caption](image_url)` — bot downloads and sends as photos

## Project Structure

| File | Purpose |
|------|---------|
| `main.py` | Telegram handlers, commands |
| `bot.py` | process_chat — sends to AI, sends response |
| `ai_agent.py` | Gemini/Poe chat with history |
| `conversation.py` | In-memory chat history per user |
| `config.py` | Env vars |
| `api/webhook.py` | Vercel serverless webhook |

## History

- Stored per `chat_id`
- Last 20 exchanges kept (40 messages) to avoid token limits
- Cleared with `/new`
