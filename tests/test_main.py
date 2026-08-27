import pytest

try:
    from main import DEFAULT_URL, LostSwordPlugin
except ModuleNotFoundError as exc:  # AstrBot's optional runtime deps may be absent in CI.
    pytest.skip(f"AstrBot runtime unavailable: {exc}", allow_module_level=True)


def test_resolve_alias_and_slug():
    assert LostSwordPlugin._resolve("埃塞尔城") == DEFAULT_URL
    assert LostSwordPlugin._resolve("ethel-city") == DEFAULT_URL
    assert LostSwordPlugin._resolve("avalon/ethel-city") == DEFAULT_URL


def test_resolve_site_url():
    url = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"
    assert LostSwordPlugin._resolve(url) == url
