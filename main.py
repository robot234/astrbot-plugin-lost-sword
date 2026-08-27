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
CODES_URL = "https://fanqiebox.com/games/lost-sword/tools/codes/"
BRAWL_URL = "https://fanqiebox.com/games/lost-sword/guides/brawl/"
ALIASES = {
    "埃塞尔城": DEFAULT_URL,
    "ethel": DEFAULT_URL,
    "ethel-city": DEFAULT_URL,
    "avalon/ethel-city": DEFAULT_URL,
}
GUIDE_ALIASES = {
    # 阿瓦隆工会战：按阶段只发送对应的阵容图。
    "城门": (DEFAULT_URL, ("ethel-titania-gate-common.png",)),
    "gate": (DEFAULT_URL, ("ethel-titania-gate-common.png",)),
    "冰法": (DEFAULT_URL, ("ethel-city-ice-boss-2026-08-16.png",)),
    "冰法boss": (DEFAULT_URL, ("ethel-city-ice-boss-2026-08-16.png",)),
    "ice": (DEFAULT_URL, ("ethel-city-ice-boss-2026-08-16.png",)),
    "暗法": (DEFAULT_URL, ("titan-city-dark-boss-2026-08-16.png",)),
    "暗法boss": (DEFAULT_URL, ("titan-city-dark-boss-2026-08-16.png",)),
    "dark": (DEFAULT_URL, ("titan-city-dark-boss-2026-08-16.png",)),
    # 大乱斗：默认发送页面列出的四类岛屿作业图。
    "大乱斗": (BRAWL_URL, ("water-catfolk-island.png", "goatfolk-island.png", "fire-island.png", "black-wolf-island.png")),
    "brawl": (BRAWL_URL, ("water-catfolk-island.png", "goatfolk-island.png", "fire-island.png", "black-wolf-island.png")),
    "水猫岛": (BRAWL_URL, ("water-catfolk-island.png",)),
    "水猫": (BRAWL_URL, ("water-catfolk-island.png",)),
    "water-catfolk": (BRAWL_URL, ("water-catfolk-island.png",)),
    "山羊岛": (BRAWL_URL, ("goatfolk-island.png",)),
    "山羊": (BRAWL_URL, ("goatfolk-island.png",)),
    "goatfolk": (BRAWL_URL, ("goatfolk-island.png",)),
    "火岛": (BRAWL_URL, ("fire-island.png",)),
    "火": (BRAWL_URL, ("fire-island.png",)),
    "fire": (BRAWL_URL, ("fire-island.png",)),
    "黑狼岛": (BRAWL_URL, ("black-wolf-island.png",)),
    "黑狼": (BRAWL_URL, ("black-wolf-island.png",)),
    "black-wolf": (BRAWL_URL, ("black-wolf-island.png",)),
}


@register(
    "astrbot_plugin_lost_sword",
    "robot234",
    "抓取番茄盒子 Lost Sword 兑换码与攻略网页并返回摘要",
    "0.2.0",
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

    @staticmethod
    def _guide_spec(query: str):
        """Return (page URL, image filenames) for a short guide keyword."""
        return GUIDE_ALIASES.get(query.casefold())

    @filter.command("ls")
    async def ls(self, event: AstrMessageEvent):
        """查询兑换码或阵容图；例如 /ls 兑换码、/ls 城门、/ls 水猫岛。"""
        query = self._code_query(event.message_str or "")
        code_queries = {"兑换码", "code", "codes"}
        if query and query.casefold() not in code_queries:
            spec = self._guide_spec(query)
            if spec is None:
                yield event.plain_result("用法：/ls 兑换码、/ls 城门、/ls 冰法、/ls 暗法、/ls 大乱斗、/ls 水猫岛、/ls 山羊岛、/ls 火岛、/ls 黑狼岛")
                return
            url, image_names = spec
            try:
                guide = await self.client.fetch(url)
            except Exception as exc:
                logger.warning("Lost Sword guide fetch failed: %s", exc)
                yield event.plain_result(f"攻略图抓取失败：{exc}")
                return
            images = tuple(
                image_url
                for image_url in guide.images
                if any(image_url.lower().endswith("/" + name) for name in image_names)
            )
            if not images:
                yield event.plain_result("页面暂未找到对应攻略图，请稍后重试。")
                return
            yield event.plain_result(f"{guide.title}\n来源：{guide.url}\n攻略图：{len(images)} 张")
            for image_url in images:
                yield event.chain_result([Image.fromURL(image_url)])
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
