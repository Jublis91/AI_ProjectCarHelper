from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import subprocess
import time
import requests


@dataclass
class OllamaProcHandle:
    proc: Optional[subprocess.Popen]
    owned: bool


def _tags_ok(base_url: str) -> bool:
    url = base_url.rstrip("/") + "/api/tags"
    try:
        r = requests.get(url, timeout=1)
        return r.status_code == 200
    except Exception:
        return False


def start_ollama(*, base_url: str, timeout_sec: int = 15) -> OllamaProcHandle:
    # Jos API on jo käynnissä, älä käynnistä uutta, älä omista prosessia
    if _tags_ok(base_url):
        return OllamaProcHandle(proc=None, owned=False)

    # Käynnistä Ollama
    proc = subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
    )

    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        if _tags_ok(base_url):
            return OllamaProcHandle(proc=proc, owned=True)
        time.sleep(0.3)

    # Ei noussut ylös ajoissa
    try:
        proc.terminate()
        proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

    raise RuntimeError("Ollama did not start in time")


def stop_ollama(handle: OllamaProcHandle) -> None:
    if not handle.owned:
        return
    proc = handle.proc
    if proc is None:
        return
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()
