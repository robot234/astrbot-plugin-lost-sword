"""AstrBot plugin entry point for Lost Sword guides."""

from __future__ import annotations

import re

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Image
from astrbot.api.star import Context, Star, register

try:  # AstrBot normally imports the folder as a package.
    from .client import FanqieboxClient
    from .parser import ALLOWED_HOST, ALLOWED_PATH_PREFIX, validate_guide_url
except ImportError:  # Keep direct smoke tests and legacy loaders working.
    from client import FanqieboxClient
    from parser import ALLOWED_HOST, ALLOWED_PATH_PREFIX, validate_guide_url


DEFAULT_URL = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"
ALIASES = {
    "埃塞尔城": DEFAULT_URL,
    "ethel": DEFAULT_URL,
    "ethel-city": DEFAULT_URL,
    "avalon/ethel-city": DEFAULT_URL,
}


@register(
    "astrbot_plugin_lost_sword",
    "robot234",
    "抓取番茄盒子 Lost Sword 攻略网页并返回摘要与攻略图片",
    "0.1.0",
    repo="https://github.com/robot234/astrbot-plugin-lost-sword",
)
class LostSwordPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.client = FanqieboxClient()

    @staticmethod
    def _query(message: str) -> str:
        return re.sub(r"^\s*/?(?:lost_sword|失落之剑|lsword)\b", "", message, flags=re.IGNORECASE).strip()

    @staticmethod
    def _resolve(query: str) -> str:
        if not query:
            return DEFAULT_URL
        if query in ALIASES:
            return ALIASES[query]
        if query.startswith("http://") or query.startswith("https://"):
            return validate_guide_url(query)
        slug = query.strip("/ ").replace(" ", "-")
        if slug.startswith("games/lost-sword/"):
            return validate_guide_url("https://" + ALLOWED_HOST + "/" + slug)
        return validate_guide_url(f"https://{ALLOWED_HOST}{ALLOWED_PATH_PREFIX}guides/{slug}/")

    @filter.command("lost_sword")
    async def lost_sword(self, event: AstrMessageEvent):
        """查询失落之剑攻略；可用 /lost_sword 埃塞尔城 或站内完整 URL。"""
        try:
            url = self._resolve(self._query(event.message_str or ""))
            guide = await self.client.fetch(url)
        except Exception as exc:
            logger.warning("Lost Sword guide fetch failed: %s", exc)
            yield event.plain_result(f"攻略抓取失败：{exc}")
            return

        lines = [f"{guide.title}", f"来源：{guide.url}"]
        if guide.description:
            lines.append(guide.description)
        if guide.headings:
            lines.append("章节：" + "、".join(guide.headings[:8]))
        for paragraph in guide.paragraphs[:4]:
            lines.append(paragraph)
        lines.append(f"攻略图片：{len(guide.images)} 张")
        yield event.plain_result("\n".join(lines))
        for image_url in guide.images[:3]:
            yield event.chain_result([Image.fromURL(image_url)])
