from pathlib import Path

import pytest

from parser import parse_page, validate_guide_url


FIXTURE = Path(__file__).parent / "fixtures" / "page.html"
URL = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"


def test_parse_text_and_allowlisted_images():
    guide = parse_page(FIXTURE.read_text(encoding="utf-8"), URL)
    assert guide.title == "埃塞尔城攻略"
    assert guide.description == "失落之剑阿瓦隆攻略"
    assert guide.headings == ("城门攻略图",)
    assert guide.paragraphs == ("对应阵容与出手顺序。",)
    assert guide.images == ("https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city.png",)


@pytest.mark.parametrize(
    "url",
    [
        "http://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/",
        "https://example.com/games/lost-sword/guides/avalon/ethel-city/",
        "https://fanqiebox.com/api/private",
        "javascript:alert(1)",
    ],
)
def test_reject_unsafe_urls(url):
    with pytest.raises(ValueError):
        validate_guide_url(url)
