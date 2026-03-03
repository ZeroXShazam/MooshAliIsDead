"""Telegram Link Analyzer Bot - Polling mode (Railway, local)."""

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from bot import extract_urls, process_link
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, _context) -> None:
    await update.message.reply_text(
        "👋 Hi! Send me any link and I'll analyze it with AI, then send you "
        "a full explanation with important pictures.\n\n"
        "Just paste a URL and I'll do the rest!"
    )


async def handle_message(update: Update, context) -> None:
    urls = extract_urls(update.message.text or "")
    if not urls:
        await update.message.reply_text(
            "Please send a valid link (e.g. https://example.com)"
        )
        return
    for url in urls:
        await process_link(context.bot, update.effective_chat.id, url)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required. Set it in .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
