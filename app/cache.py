import hashlib
import time
from typing import Any

TTL_SECONDS = 3600

_cache: dict[str, tuple[Any, float]] = {}

def _key(github_url: str) -> str:
    return hashlib.md5(github_url.lower().strip().encode()).hexdigest()

def get(github_url: str) -> Any | None:
    key = _key(github_url)
    if key in _cache:
        value, ts = _cache[key]
        if time.time() - ts < TTL_SECONDS:
            return value
        del _cache[key]
    return None

def set(github_url: str, value: Any) -> None:
    _cache[_key(github_url)] = (value, time.time())
