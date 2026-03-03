"""Telegram Link Analyzer Bot - Polling mode (Railway, local)."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot import extract_urls, process_followup, process_link
from config import REPO_URL, TELEGRAM_BOT_TOKEN
from conversation import clear_context

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
        "👋 Hi! Chat with me anytime, or send a link and I'll analyze it with AI.\n\n"
        "💬 I can answer questions, analyze web pages, and remember context.\n"
        "Use /new to clear page context.",
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
        "💬 Chat anytime, or ask follow-ups about the last page.\n"
        "/new — clear page context\n\n"
        "Supports: Gemini & Poe API",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 View source", url=REPO_URL)],
        ]),
    )


async def new_command(update: Update, _context) -> None:
    """Clear page context and start fresh."""
    clear_context(update.effective_chat.id)
    await update.message.reply_text("🆕 Page context cleared. Chat or send a new link!")


async def new_link_callback(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    clear_context(update.effective_chat.id)
    try:
        await query.edit_message_text("🆕 Page context cleared. Chat or send a new link!")
    except Exception:
        await context.bot.send_message(update.effective_chat.id, "🆕 Page context cleared. Chat or send a new link!")


async def help_callback(update: Update, _context) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "<b>How it works</b>\n\n"
        "1️⃣ Send any http(s) link\n"
        "2️⃣ Bot scrapes the page (text + images)\n"
        "3️⃣ AI analyzes and summarizes the content\n"
        "4️⃣ You get a formatted summary + key images\n\n"
        "💬 Chat anytime, or ask follow-ups about the last page.\n"
        "/new — clear page context\n\n"
        "Supports: Gemini & Poe API",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 View source", url=REPO_URL)],
        ]),
    )


async def handle_message(update: Update, context) -> None:
    text = (update.message.text or "").strip()
    urls = extract_urls(text)

    if urls:
        for url in urls:
            await process_link(context.bot, update.effective_chat.id, url)
    elif text:
        await process_followup(context.bot, update.effective_chat.id, text)
    else:
        await update.message.reply_text("Send a message or link to get started.")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required. Set it in .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("new", new_command))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    app.add_handler(CallbackQueryHandler(new_link_callback, pattern="^new_link$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
