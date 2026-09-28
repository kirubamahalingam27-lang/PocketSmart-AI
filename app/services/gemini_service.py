import json
from typing import Any
from app.config import settings
from app.services.recommendation_service import fallback_home, fallback_party, fallback_jewelry

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

SYSTEM = """You are PocketSmart AI, a budget-aware recommendation assistant. Return ONLY valid JSON.
Never invent a claim that a live marketplace API verified a product. Product URLs should be search URLs, not fabricated product pages.
Respect the user's budget.
Use this schema:
{
  "planner": "home"|"party"|"jewelry",
  "budget": number,
  "allocated_budget": number,
  "summary": "string",
  "tips": ["string"],
  "recommendations": [
    {
      "category": "string",
      "title": "string",
      "description": "string",
      "estimated_price": number,
      "quantity": number,
      "platform": "Amazon"|"Flipkart"|"IKEA"|"Swiggy"|"Zomato"|"OYO",
      "url": "string",
      "why": "string"
    }
  ]
}"""

def _client():
    if not settings.gemini_api_key or genai is None:
        return None
    try:
        return genai.Client(api_key=settings.gemini_api_key)
    except Exception:
        return None

def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)

def generate(planner: str, data: dict[str, Any], image_bytes: bytes | None = None, mime_type: str | None = None) -> tuple[dict[str, Any], str]:
    fallback_map = {"home": fallback_home, "party": fallback_party, "jewelry": fallback_jewelry}
    fallback_func = fallback_map.get(planner, fallback_home)
    fallback = fallback_func(data)

    client = _client()
    if client is None:
        return fallback, "fallback"

    prompt = SYSTEM + f"\nPlanner: {planner}\nUser input:\n" + json.dumps(data, ensure_ascii=False)
    contents: Any = [prompt]
    if image_bytes and types:
        contents.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type or "image/jpeg"))
        contents.append("Analyze the outfit image only for visible color/style coordination. Do not identify the person.")

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=contents,
            config=types.GenerateContentConfig(temperature=0.2, response_mime_type="application/json")
        )
        if not response or not response.text:
            return fallback, "fallback"

        result = _extract_json(response.text)
        if not isinstance(result, dict) or not isinstance(result.get("recommendations"), list):
            return fallback, "fallback"

        result["planner"] = planner
        result["budget"] = float(result.get("budget", data.get("budget", 0)))
        result["allocated_budget"] = float(result.get("allocated_budget", result["budget"]))
        return result, "gemini"
    except Exception:
        return fallback, "fallback"
