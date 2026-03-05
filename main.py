"""Telegram AI Chat Bot - Polling mode."""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot import process_chat
from config import REPO_URL, TELEGRAM_BOT_TOKEN
from conversation import clear_history

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
        "👋 Hi! I'm your AI assistant. Chat with me about anything.\n\n"
        "Use /new to start a fresh conversation.",
        reply_markup=get_start_keyboard(),
    )


async def help_command(update: Update, _context) -> None:
    await update.message.reply_text(
        "<b>How it works</b>\n\n"
        "Just chat with me like a normal conversation. I remember our chat history.\n\n"
        "/new — clear history and start fresh\n\n"
        "Powered by Gemini or Poe API",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 View source", url=REPO_URL)],
        ]),
    )


async def new_command(update: Update, _context) -> None:
    clear_history(update.effective_chat.id)
    await update.message.reply_text("🆕 Conversation cleared. Let's start fresh!")


async def help_callback(update: Update, _context) -> None:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "<b>How it works</b>\n\n"
        "Just chat with me like a normal conversation. I remember our chat history.\n\n"
        "/new — clear history and start fresh\n\n"
        "Powered by Gemini or Poe API",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 View source", url=REPO_URL)],
        ]),
    )


async def handle_message(update: Update, context) -> None:
    text = (update.message.text or "").strip()
    if not text:
        await update.message.reply_text("Send a message to chat.")
        return

    status_msg = await update.message.reply_text("🤔 Thinking...")
    await process_chat(context.bot, update.effective_chat.id, text)
    try:
        await status_msg.delete()
    except Exception:
        pass


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is required. Set it in .env")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("new", new_command))
    app.add_handler(CallbackQueryHandler(help_callback, pattern="^help$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot starting (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
