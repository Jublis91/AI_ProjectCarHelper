import os

def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip().lower()
    return v in ("1", "true", "yes", "y", "on")

def env_str(name: str, default: str) -> str:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default

def env_int(name: str, default: int, min_value: int | None = None, max_value: int | None = None) -> int:
    v = os.getenv(name)
    if v is None or not v.strip():
        return default
    try:
        n = int(v.strip())
    except Exception:
        return default
    if min_value is not None and n < min_value:
        return default
    if max_value is not None and n > max_value:
        return default
    return n

def env_float(name: str, default:float, min_value: float| None = None, max_value: float | None = None) -> float:
    raw = (os.getenv(name) or "").strip()
    try:
        v = float(raw) if raw else float(default)
    except Exception:
        v = float(default)
    
    if min_value is not None and v < min_value:
        v = min_value
    if max_value is not None and v > max_value:
        v = max_value

    return v

USE_OLLAMA = env_bool("USE_OLLAMA", default=False)
OLLAMA_BASE_URL = env_str("OLLAMA_BASE_URL", default="http://127.0.0.1:11434")
OLLAMA_MODEL = env_str("OLLAMA_MODEL", default="llama3.1:8b")
OLLAMA_TIMEOUT_SEC = env_int("OLLAMA_TIMEOUT_SEC", default=30, min_value=1, max_value=600)
MAX_CONTEXT_CHARS = env_int("MAX_CONTEXT_CHARS", default=6000, min_value=500, max_value=50000)
MIN_SCORE = env_float("MIN_SCORE", default=0.28, min_value=0.0, max_value=1.0)