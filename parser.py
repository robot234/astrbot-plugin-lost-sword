"""Pure HTML parser for Fanqiebox Lost Sword guide pages."""

from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from urllib.parse import unquote, urljoin, urlparse
from pathlib import PurePosixPath

from bs4 import BeautifulSoup


ALLOWED_HOST = "fanqiebox.com"
ALLOWED_PATH_PREFIX = "/games/lost-sword/"


@dataclass(frozen=True)
class Guide:
    url: str
    title: str
    description: str
    headings: tuple[str, ...]
    paragraphs: tuple[str, ...]
    images: tuple[str, ...]


def validate_guide_url(url: str) -> str:
    """Return a normalized URL or raise ValueError for an unsafe URL."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != ALLOWED_HOST:
        raise ValueError("只允许抓取 fanqiebox.com 的 HTTPS Lost Sword 页面")
    try:
        if parsed.port not in (None, 443):
            raise ValueError("只允许使用 HTTPS 默认端口")
    except ValueError as exc:
        raise ValueError("URL 端口无效") from exc
    decoded_path = unquote(parsed.path)
    if any(part in {".", ".."} for part in decoded_path.split("/")):
        raise ValueError("URL 路径不允许目录跳转")
    if not decoded_path.startswith(ALLOWED_PATH_PREFIX):
        raise ValueError("URL 必须位于 fanqiebox.com/games/lost-sword/ 下")
    return url.split("#", 1)[0]


def _clean(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(unescape(value).split())


def parse_page(html: str, url: str) -> Guide:
    """Parse server-rendered HTML, including the Next.js RSC fallback text."""
    normalized_url = validate_guide_url(url)
    soup = BeautifulSoup(html, "html.parser")

    title = _clean((soup.find("h1") or soup.find("title")).get_text(" ", strip=True) if (soup.find("h1") or soup.find("title")) else "失落之剑攻略")
    description = _clean((soup.find("meta", attrs={"name": "description"}) or {}).get("content") if soup.find("meta", attrs={"name": "description"}) else "")

    headings: list[str] = []
    for node in soup.find_all(["h2", "h3"]):
        text = _clean(node.get_text(" ", strip=True))
        if text and text not in headings:
            headings.append(text)

    paragraphs: list[str] = []
    for node in soup.find_all("p"):
        text = _clean(node.get_text(" ", strip=True))
        if text and text not in paragraphs:
            paragraphs.append(text)

    images: list[str] = []
    for node in soup.find_all("img"):
        source = node.get("src") or node.get("data-src")
        if not source:
            continue
        absolute = urljoin(normalized_url, source)
        parsed = urlparse(absolute)
        filename = PurePosixPath(parsed.path).name.lower()
        try:
            safe_image_url = validate_guide_url(absolute)
        except ValueError:
            continue
        if (
            parsed.path.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
            and not filename.startswith("author-")
            and safe_image_url not in images
        ):
            images.append(safe_image_url)

    return Guide(
        url=normalized_url,
        title=title,
        description=description,
        headings=tuple(headings),
        paragraphs=tuple(paragraphs),
        images=tuple(images),
    )
