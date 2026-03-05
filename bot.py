"""Shared bot logic for chat."""

import re
from io import BytesIO

from telegram import Bot
from telegram.error import BadRequest, TelegramError

from ai_agent import chat
from conversation import get_history, set_history
from response_parser import download_image, parse_response


def _markdown_to_html(text: str) -> str:
    """Convert common Markdown to Telegram HTML (fallback when AI uses ** instead of <b>)."""
    # **bold** -> <b>bold</b>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # [text](url) -> <a href="url">text</a> (for links not converted to images)
    text = re.sub(r'\[([^\]]+)\]\((https?://[^\)]+)\)', r'<a href="\2">\1</a>', text)
    return text


async def process_chat(bot: Bot, chat_id: int, message: str) -> None:
    """Process user message and return AI response. Parses images, preserves formatting."""
    history = get_history(chat_id)
    result, new_history = chat(chat_id, message, history)

    if not result.success:
        await bot.send_message(chat_id, f"❌ {result.error}")
        return

    set_history(chat_id, new_history)
    blocks = parse_response(result.text)

    i = 0
    while i < len(blocks):
        block = blocks[i]
        if block.kind == "text":
            # Peek: is next block an image? If so, use this text as caption for the image
            next_img = blocks[i + 1] if i + 1 < len(blocks) and blocks[i + 1].kind == "image" else None
            if next_img:
                img_bytes = download_image(next_img.content)
                if img_bytes:
                    caption = block.content[:1024] + ("..." if len(block.content) > 1024 else "")
                    caption = _markdown_to_html(caption)
                    try:
                        await bot.send_photo(chat_id, photo=BytesIO(img_bytes), caption=caption, parse_mode="HTML")
                    except (BadRequest, TelegramError):
                        try:
                            await bot.send_photo(chat_id, photo=BytesIO(img_bytes), caption=caption)
                        except (BadRequest, TelegramError):
                            await bot.send_message(chat_id, caption, parse_mode="HTML")
                            await bot.send_photo(chat_id, photo=BytesIO(img_bytes))
                    i += 2  # skip the image block
                    continue
            # No image after, send text normally
            text = block.content[:4000] + "..." if len(block.content) > 4000 else block.content
            if text.strip():
                text = _markdown_to_html(text)
                try:
                    await bot.send_message(chat_id, text, parse_mode="HTML")
                except BadRequest:
                    await bot.send_message(chat_id, text)

        elif block.kind == "image":
            img_bytes = download_image(block.content)
            if img_bytes:
                caption = (block.caption or "")[:1024] if block.caption else None
                if caption:
                    caption = _markdown_to_html(caption)
                try:
                    if caption:
                        await bot.send_photo(chat_id, photo=BytesIO(img_bytes), caption=caption, parse_mode="HTML")
                    else:
                        await bot.send_photo(chat_id, photo=BytesIO(img_bytes))
                except (BadRequest, TelegramError):
                    try:
                        await bot.send_photo(chat_id, photo=BytesIO(img_bytes), caption=caption)
                    except (BadRequest, TelegramError):
                        await bot.send_message(
                            chat_id,
                            f"📷 <a href=\"{block.content}\">Image</a>" + (f": {block.caption}" if block.caption else ""),
                            parse_mode="HTML",
                        )
            else:
                await bot.send_message(
                    chat_id,
                    f"📷 <a href=\"{block.content}\">Image</a>" + (f": {block.caption}" if block.caption else ""),
                    parse_mode="HTML",
                )
        i += 1
