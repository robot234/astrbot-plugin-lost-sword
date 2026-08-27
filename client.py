"""Async HTTP client with conservative caching for Fanqiebox."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass

import httpx

try:  # Works both as an AstrBot package and when loaded from a plugin folder.
    from .parser import Code, Guide, parse_codes_page, parse_page, validate_guide_url
except ImportError:
    from parser import Code, Guide, parse_codes_page, parse_page, validate_guide_url


@dataclass
class _CacheEntry:
    expires_at: float
    guide: Guide


class FanqieboxClient:
    def __init__(self, *, timeout: float = 20.0, cache_ttl: float = 300.0, min_interval: float = 1.0) -> None:
        self.timeout = timeout
        self.cache_ttl = cache_ttl
        self.min_interval = max(0.0, min_interval)
        self._request_lock = asyncio.Lock()
        self._last_request_at = 0.0
        self._cache: dict[str, _CacheEntry] = {}
        self._code_cache: dict[str, tuple[float, tuple[Code, ...]]] = {}

    async def fetch(self, url: str) -> Guide:
        url = validate_guide_url(url)
        now = time.monotonic()
        cached = self._cache.get(url)
        if cached and cached.expires_at > now:
            return cached.guide

        headers = {
            "User-Agent": "astrbot-plugin-lost-sword/0.1 (+https://fanqiebox.com/)",
            "Accept": "text/html,application/xhtml+xml",
        }
        # Serialize cache misses and keep a polite minimum interval between requests.
        async with self._request_lock:
            now = time.monotonic()
            cached = self._cache.get(url)
            if cached and cached.expires_at > now:
                return cached.guide
            wait_for = self.min_interval - (time.monotonic() - self._last_request_at)
            if wait_for > 0:
                await asyncio.sleep(wait_for)
            async with httpx.AsyncClient(follow_redirects=True, timeout=self.timeout, headers=headers) as client:
                response = await client.get(url)
                self._last_request_at = time.monotonic()
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if "html" not in content_type:
                    raise ValueError("目标页面不是 HTML")
                guide = parse_page(response.text, str(response.url))
            self._cache[url] = _CacheEntry(expires_at=time.monotonic() + self.cache_ttl, guide=guide)

        return guide

    async def fetch_codes(self, url: str) -> tuple[Code, ...]:
        url = validate_guide_url(url)
        now = time.monotonic()
        cached = self._code_cache.get(url)
        if cached and cached[0] > now:
            return cached[1]
        headers = {
            "User-Agent": "astrbot-plugin-lost-sword/0.2 (+https://fanqiebox.com/)",
            "Accept": "text/html,application/xhtml+xml",
        }
        async with self._request_lock:
            now = time.monotonic()
            cached = self._code_cache.get(url)
            if cached and cached[0] > now:
                return cached[1]
            wait_for = self.min_interval - (time.monotonic() - self._last_request_at)
            if wait_for > 0:
                await asyncio.sleep(wait_for)
            async with httpx.AsyncClient(follow_redirects=True, timeout=self.timeout, headers=headers) as client:
                response = await client.get(url)
                self._last_request_at = time.monotonic()
                response.raise_for_status()
                if "html" not in response.headers.get("content-type", "").lower():
                    raise ValueError("目标页面不是 HTML")
                final_url = validate_guide_url(str(response.url))
                codes = parse_codes_page(response.text, final_url)
            self._code_cache[url] = (time.monotonic() + self.cache_ttl, codes)
            return codes
