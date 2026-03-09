import logging

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OllamaUnavailableError(RuntimeError):
    pass


def generate_text(prompt: str) -> str:
    settings = get_settings()
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    try:
        response = httpx.post(url, json=payload, timeout=settings.ollama_timeout_seconds)
        response.raise_for_status()
        body = response.json()
        text = body.get("response", "").strip()
        if not text:
            raise OllamaUnavailableError("Empty response received from Ollama.")
        return text
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Ollama call failed: %s", exc)
        raise OllamaUnavailableError(str(exc)) from exc
