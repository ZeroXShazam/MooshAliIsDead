"""Telegram Link Analyzer Bot - Polling mode (Railway, local)."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot import extract_urls, process_link
from config import REPO_URL, TELEGRAM_BOT_TOKEN

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 How it works", callback_data="help")],
        [InlineKeyboardButton("🔗 View source", url=REPO_URL)],
    ])


async def start(update: Update, _context) -> None:
    await update.message.reply_text(
        "👋 Hi! Send me any link and I'll analyze it with AI, then send you "
        "a full explanation with important pictures.\n\n"
        "Just paste a URL and I'll do the rest!",
        reply_markup=get_start_keyboard(),
    )


async def help_command(update: Update, _context) -> None:
    """Handle /help command."""
    await update.message.reply_text(
        "<b>How it works</b>\n\n"
        "1️⃣ Send any http(s) link\n"
        "2️⃣ Bot scrapes the page (text + images)\n"
        "3️⃣ AI analyzes and summarizes the content\n"
        "4️⃣ You get a formatted summary + key images\n\n"
        "Supports: Gemini & Poe API",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 View source", url=REPO_URL)],
        ]),
    )


async def help_callback(update: Update, _context) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "<b>How it works</b>\n\n"
        "1️⃣ Send any http(s) link\n"
        "2️⃣ Bot scrapes the page (text + images)\n"
        "3️⃣ AI analyzes and summarizes the content\n"
        "4️⃣ You get a formatted summary + key images\n\n"
        "Supports: Gemini & Poe API",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 View source", url=REPO_URL)],
        ]),
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
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
