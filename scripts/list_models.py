"""List Gemini models that support generateContent. Run: pipenv run python -m scripts.list_models"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
print("Models supporting generateContent:\n")
for m in genai.list_models():
    if "generateContent" in (m.supported_generation_methods or []):
        print(m.name.replace("models/", ""))
