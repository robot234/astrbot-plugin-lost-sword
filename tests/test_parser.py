from pathlib import Path

import pytest

from parser import parse_codes_page, parse_page, validate_guide_url


FIXTURE = Path(__file__).parent / "fixtures" / "page.html"
CODES_FIXTURE = Path(__file__).parent / "fixtures" / "codes.html"
URL = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"


def test_parse_text_and_allowlisted_images():
    guide = parse_page(FIXTURE.read_text(encoding="utf-8"), URL)
    assert guide.title == "埃塞尔城攻略"
    assert guide.description == "失落之剑阿瓦隆攻略"
    assert guide.headings == ("城门攻略图",)
    assert guide.paragraphs == ("对应阵容与出手顺序。",)
    assert guide.images == ("https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city.png",)


def test_parse_codes_cards_and_deduplicate():
    codes = parse_codes_page(CODES_FIXTURE.read_text(encoding="utf-8"), "https://fanqiebox.com/games/lost-sword/tools/codes/")
    assert [item.code for item in codes] == ["LIGHTOFLIBERTY", "SECOND-CODE"]
    assert codes[0].reward == "钻石 ×1,000"
    assert codes[0].status == "有效"
    assert codes[0].server == "国际服 / 韩服"
    assert codes[0].published == "2026/08/14"
    assert codes[0].expires == "2026/08/31 22:59"
    assert codes[0].source_url.startswith("https://www.reddit.com/")
    assert codes[1].source_url == ""


@pytest.mark.parametrize(
    "url",
    [
        "http://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/",
        "https://example.com/games/lost-sword/guides/avalon/ethel-city/",
        "https://fanqiebox.com:444/games/lost-sword/guides/avalon/ethel-city/",
        "https://fanqiebox.com/api/private",
        "https://fanqiebox.com/games/lost-sword/../private",
        "https://fanqiebox.com/games/lost-sword/%2e%2e/private",
        "javascript:alert(1)",
    ],
)
def test_reject_unsafe_urls(url):
    with pytest.raises(ValueError):
        validate_guide_url(url)
