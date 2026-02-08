from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

import requests

@dataclass
class OllamaError(Exception):
    message: str
    code: str ="ollama_error"
    status_code: Optional[int] = None

    def __str__(self) -> str:
        return self.message

class OllamaConnectionError(OllamaError):
    def __init__(self, message: str = "Ollama connection failed"):
        super().__init__(message=message, code="connection_error")

class OllamaTimeoutError(OllamaError):
    def __init__(self, message: str = "Ollama request timed out"):
        super().__init__(message=message, code="timeout")

class OllamaBadResponseError(OllamaError):
    def __init__(self, message: str = "Ollama returned bad response", status_code: Optional[int] = None):
        super().__init__(message=message, code="bad_response", status_code=status_code)

def ollama_generate(
        *,
        base_url: str,
        model: str,
        prompt: str,
        timeout_sec: int = 30,
) -> str:
    """
    Calls Ollama  /api/generate endpoit (non-stream) and returns a response text.
    Gives OllamaError message if HTTP != 200 or answer is not the right shape.
    """
    url = base_url.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        r = requests.post(url, json=payload, timeout=timeout_sec)
    except requests.Timeout as e:
        raise OllamaError(f"Ollama request timed out") from e
    except requests.ConnectionError as e:
        raise OllamaError("Ollama connection failed") from e
    except requests.RequestException as e:
        raise OllamaError("Ollama request failed") from e
    
    if r.status_code != 200:
        text = (r.text or "").strip()
        msg = f"Ollama returned non-200: {text[:500]}" if text else "Ollama returned non-200"
        raise OllamaError(msg, status_code=r.status_code)

    try:
        data: Any = r.json()
    except Exception as e:
        raise OllamaError("Ollama response was not valid JSON") from e
    
    out = data.get("response")
    if not isinstance(out, str) or not out.strip():
        raise OllamaError("Ollama returned empty response")

    return out.strip()