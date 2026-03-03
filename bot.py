"""Shared bot logic for processing links and sending responses."""

import re
from io import BytesIO

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.error import BadRequest, TelegramError

from ai_agent import analyze_content
from config import IMAGE_MAX_SIZE_KB, MAX_CONTENT_LENGTH, MAX_IMAGES
from scraper import scrape_url


def extract_urls(text: str) -> list[str]:
    """Extract http(s) URLs from text."""
    pattern = r"https?://[^\s<>\"']+"
    return list(dict.fromkeys(re.findall(pattern, text)))


async def process_link(bot: Bot, chat_id: int, url: str) -> None:
    """
    Scrape URL, analyze with AI, and send summary + images to the user.
    """
    status_msg = await bot.send_message(chat_id, "🔍 Fetching and analyzing the link...")

    content = scrape_url(
        url,
        max_content_length=MAX_CONTENT_LENGTH,
        max_images=MAX_IMAGES,
        image_max_size_kb=IMAGE_MAX_SIZE_KB,
    )

    if not content.success:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text=f"❌ {content.error}",
        )
        return

    result = analyze_content(content)

    if not result.success:
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg.message_id,
            text=f"❌ {result.error}",
        )
        return

    # Delete status message
    try:
        await status_msg.delete()
    except TelegramError:
        pass

    # Send summary (Telegram has 4096 char limit)
    summary = result.summary
    if len(summary) > 4000:
        summary = summary[:3997] + "..."

    # Escape HTML in title for Telegram parse_mode
    title_safe = content.title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    msg = f"📄 <b>{title_safe}</b>\n\n{summary}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 View source", url=content.url)],
    ])
    try:
        await bot.send_message(chat_id, msg, parse_mode="HTML", reply_markup=keyboard)
    except BadRequest:
        await bot.send_message(chat_id, f"📄 {content.title}\n\n{summary}", reply_markup=keyboard)

    # Send images if we have them
    if content.images:
        media = []
        for _img_url, img_bytes in content.images[:10]:  # Telegram allows max 10 media per group
            if len(img_bytes) <= 10 * 1024 * 1024:  # 10MB limit per photo
                media.append(InputMediaPhoto(media=BytesIO(img_bytes)))
        if media:
            try:
                await bot.send_media_group(chat_id=chat_id, media=media)
            except TelegramError:
                # Fallback: send first image only
                if content.images:
                    await bot.send_photo(chat_id=chat_id, photo=BytesIO(content.images[0][1]))
