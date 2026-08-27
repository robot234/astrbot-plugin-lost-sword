import pytest

try:
    from main import BRAWL_URL, DEFAULT_URL, LostSwordPlugin
except ModuleNotFoundError as exc:  # AstrBot's optional runtime deps may be absent in CI.
    pytest.skip(f"AstrBot runtime unavailable: {exc}", allow_module_level=True)


def test_resolve_alias_and_slug():
    assert LostSwordPlugin._resolve("埃塞尔城") == DEFAULT_URL
    assert LostSwordPlugin._resolve("ethel-city") == DEFAULT_URL
    assert LostSwordPlugin._resolve("avalon/ethel-city") == DEFAULT_URL


def test_resolve_site_url():
    url = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"
    assert LostSwordPlugin._resolve(url) == url


def test_ls_guide_keyword_specs_select_expected_images():
    assert LostSwordPlugin._guide_spec("城门") == (DEFAULT_URL, ("ethel-titania-gate-common.png",))
    assert LostSwordPlugin._guide_spec("冰法")[1] == ("ethel-city-ice-boss-2026-08-16.png",)
    assert LostSwordPlugin._guide_spec("暗法")[1] == ("titan-city-dark-boss-2026-08-16.png",)
    assert LostSwordPlugin._guide_spec("水猫岛") == (BRAWL_URL, ("water-catfolk-island.png",))
    assert len(LostSwordPlugin._guide_spec("大乱斗")[1]) == 4
