"""AstrBot plugin entry point for Lost Sword guides."""

from __future__ import annotations

import re

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Image
from astrbot.api.star import Context, Star, register

try:  # AstrBot normally imports the folder as a package.
    from .client import FanqieboxClient
    from .parser import ALLOWED_HOST, ALLOWED_PATH_PREFIX, Code, validate_guide_url
except ImportError:  # Keep direct smoke tests and legacy loaders working.
    from client import FanqieboxClient
    from parser import ALLOWED_HOST, ALLOWED_PATH_PREFIX, Code, validate_guide_url


DEFAULT_URL = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"
CODES_URL = "https://fanqiebox.com/games/lost-sword/tools/codes/"
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

    @staticmethod
    def _code_query(message: str) -> str:
        return re.sub(r"^\s*/?ls\b", "", message, flags=re.IGNORECASE).strip()

    @filter.command("ls")
    async def ls(self, event: AstrMessageEvent):
        """抓取 Lost Sword 兑换码；使用 /ls 或 /ls 兑换码。"""
        query = self._code_query(event.message_str or "")
        if query and query.casefold() not in {"兑换码", "code", "codes"}:
            yield event.plain_result("用法：/ls 兑换码")
            return
        try:
            codes = await self.client.fetch_codes(CODES_URL)
        except Exception as exc:
            logger.warning("Lost Sword code fetch failed: %s", exc)
            yield event.plain_result(f"兑换码抓取失败：{exc}")
            return
        if not codes:
            yield event.plain_result("暂未抓到兑换码，请稍后重试。")
            return
        lines = [f"失落之剑兑换码（{len(codes)} 条）", f"来源：{CODES_URL}"]
        for item in codes:
            lines.append(f"\n{item.code}")
            if item.reward:
                lines.append(f"奖励：{item.reward}")
            if item.status or item.server:
                lines.append("状态/区服：" + " · ".join(x for x in (item.status, item.server) if x))
            if item.published:
                lines.append(f"发布：{item.published}")
            if item.expires:
                lines.append(f"截止：{item.expires}")
            if item.source_url:
                lines.append(f"出处：{item.source_url}")
        yield event.plain_result("\n".join(lines))

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
