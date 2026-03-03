"""AI agent for analyzing webpage content. Supports Gemini and Poe."""

import base64
from dataclasses import dataclass

from config import AI_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL, POE_API_KEY, POE_MODEL
from scraper import ScrapedContent


@dataclass
class AnalysisResult:
    """Result of AI analysis."""

    summary: str
    success: bool
    error: str | None = None


def _guess_mime(img_bytes: bytes) -> str:
    """Detect image MIME type from magic bytes."""
    if img_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if img_bytes[:2] == b"\xff\xd8":
        return "image/jpeg"
    if img_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if img_bytes[:4] == b"RIFF" and img_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _build_prompt(content: ScrapedContent) -> str:
    """Build the prompt for the AI."""
    return f"""Analyze this webpage and provide a clear, comprehensive explanation.

URL: {content.url}
Title: {content.title}

Content (excerpt):
{content.text}

Provide:
1. A brief overview (2-3 sentences) of what the page is about
2. Key points and main takeaways
3. Important details, facts, or data mentioned
4. Any notable images described (we'll attach the actual images separately)

FORMATTING RULES (strict - your response will be sent to Telegram):
- Use Telegram HTML format only. Allowed tags: <b>bold</b>, <i>italic</i>, <code>inline code</code>, <a href="URL">link</a>
- For section headers use <b>Header</b>
- For bullet lists use • or - (no markdown asterisks)
- NEVER use: *, _, `, [, ] as formatting - they break Telegram
- In regular text, escape: & as &amp;  < as &lt;  > as &gt;
- Keep it clean and readable. Be concise but thorough.
- If content is in another language, summarize in that language or English."""


def _analyze_with_gemini(content: ScrapedContent) -> AnalysisResult:
    """Use Gemini to analyze content."""
    import google.generativeai as genai

    if not GEMINI_API_KEY:
        return AnalysisResult(
            summary="",
            success=False,
            error="GEMINI_API_KEY is not configured. Add it to your .env file.",
        )

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        prompt = _build_prompt(content)

        if content.images:
            parts = [prompt]
            for _img_url, img_bytes in content.images:
                mime = _guess_mime(img_bytes)
                parts.append({"mime_type": mime, "data": img_bytes})
            try:
                response = model.generate_content(parts)
            except Exception as img_err:
                if "Unable to process input image" in str(img_err) or "400" in str(img_err):
                    response = model.generate_content(prompt)
                else:
                    raise img_err
        else:
            response = model.generate_content(prompt)

        if not response.text:
            return AnalysisResult(summary="", success=False, error="Gemini returned an empty response.")
        return AnalysisResult(summary=response.text.strip(), success=True)
    except Exception as e:
        return AnalysisResult(summary="", success=False, error=f"Gemini failed: {str(e)}")


def _analyze_with_poe(content: ScrapedContent) -> AnalysisResult:
    """Use Poe API (OpenAI-compatible) to analyze content."""
    from openai import OpenAI

    if not POE_API_KEY:
        return AnalysisResult(
            summary="",
            success=False,
            error="POE_API_KEY is not configured. Add it to your .env file.",
        )

    try:
        client = OpenAI(
            api_key=POE_API_KEY,
            base_url="https://api.poe.com/v1",
        )

        prompt = _build_prompt(content)
        message_content: list[dict] = [{"type": "text", "text": prompt}]

        # Add images as base64 (OpenAI format)
        for _img_url, img_bytes in content.images:
            b64 = base64.standard_b64encode(img_bytes).decode("utf-8")
            message_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
            })

        chat = client.chat.completions.create(
            model=POE_MODEL,
            messages=[{"role": "user", "content": message_content}],
        )

        text = chat.choices[0].message.content
        if not text:
            return AnalysisResult(summary="", success=False, error="Poe returned an empty response.")
        return AnalysisResult(summary=text.strip(), success=True)
    except Exception as e:
        return AnalysisResult(summary="", success=False, error=f"Poe failed: {str(e)}")


def analyze_content(content: ScrapedContent) -> AnalysisResult:
    """
    Analyze scraped webpage content using the configured AI provider (Gemini or Poe).

    Returns a structured summary suitable for sending back to the user.
    """
    if not content.success:
        return AnalysisResult(
            summary="",
            success=False,
            error=content.error or "Failed to scrape the page.",
        )

    if AI_PROVIDER == "poe":
        return _analyze_with_poe(content)
    return _analyze_with_gemini(content)
