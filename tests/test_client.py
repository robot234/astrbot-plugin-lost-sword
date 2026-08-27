import asyncio

import client


class _Response:
    url = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"
    headers = {"content-type": "text/html; charset=utf-8"}
    text = "<html><h1>测试攻略</h1></html>"

    def raise_for_status(self):
        return None


class _AsyncClient:
    calls = 0

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def get(self, url):
        type(self).calls += 1
        return _Response()


class _CodeResponse(_Response):
    url = "https://fanqiebox.com/games/lost-sword/tools/codes/"
    text = '<html><article class="code-card"><div class="code-meta"><span>有效</span><span>国际服</span></div><strong>ABC123</strong><p>钻石</p></article></html>'


def test_cache_prevents_duplicate_request(monkeypatch):
    _AsyncClient.calls = 0
    monkeypatch.setattr(client.httpx, "AsyncClient", _AsyncClient)
    api = client.FanqieboxClient(min_interval=0)
    url = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"
    asyncio.run(api.fetch(url))
    asyncio.run(api.fetch(url))
    assert _AsyncClient.calls == 1


def test_concurrent_same_url_is_deduplicated(monkeypatch):
    _AsyncClient.calls = 0
    monkeypatch.setattr(client.httpx, "AsyncClient", _AsyncClient)
    api = client.FanqieboxClient(min_interval=0)
    url = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"

    async def run():
        return await asyncio.gather(api.fetch(url), api.fetch(url))

    asyncio.run(run())
    assert _AsyncClient.calls == 1


def test_fetch_codes_uses_code_cache(monkeypatch):
    _AsyncClient.calls = 0

    class CodeClient(_AsyncClient):
        async def get(self, url):
            type(self).calls += 1
            return _CodeResponse()

    monkeypatch.setattr(client.httpx, "AsyncClient", CodeClient)
    api = client.FanqieboxClient(min_interval=0)
    url = "https://fanqiebox.com/games/lost-sword/tools/codes/"
    first = asyncio.run(api.fetch_codes(url))
    second = asyncio.run(api.fetch_codes(url))
    assert [item.code for item in first] == ["ABC123"]
    assert second == first
    assert CodeClient.calls == 1
