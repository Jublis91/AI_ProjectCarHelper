from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional

import requests

@dataclass
class OllamaError(Exception):
    message: str
    status_code: Optional[int] = None

    def __str__(self) -> str:
        if self.status_code is None:
            return self.message
        return f"{self.message} (status_code={self.status_code})"
    

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
    except requests.RequestException as e:
        raise OllamaError(f"Ollama request failed {e}") from e
    
    if r.status_code != 200:
        text = (r.text or "").strip()
        msg = f"Ollama returned non-200: {text[:500]}" if text else "Ollama returned non-200"
        raise OllamaError(msg, status_code=r.status_code)

    try:
        data: Any = r.json()
    except Exception as e:
        raise OllamaError("Ollama response was not valid JSON") from e
    
    out = data.get("response")
    if not isinstance(out, str):
        raise OllamaError("Ollama JSON missing 'response' string")

    return out.strip()