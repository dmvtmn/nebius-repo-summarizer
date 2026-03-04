import time
from unittest.mock import patch
from app.cache import get, set, _cache, TTL_SECONDS

def setup_function():
    _cache.clear()

def test_cache_miss_returns_none():
    assert get("https://github.com/a/b") is None

def test_cache_set_and_get():
    url = "https://github.com/a/b"
    set(url, "my_value")
    assert get(url) == "my_value"

def test_cache_ttl_expiry():
    url = "https://github.com/a/b"
    set(url, "my_value")

    with patch("time.time", return_value=time.time() + TTL_SECONDS + 1):
        assert get(url) is None

def test_cache_key_normalizes_url():
    url1 = "https://github.com/A/B"
    url2 = "  https://github.com/a/b  "
    set(url1, "value")
    assert get(url2) == "value"

def test_cache_hit_returns_correct_value():
    url = "https://github.com/a/b"
    val = {"test": 123}
    set(url, val)
    assert get(url) == val
