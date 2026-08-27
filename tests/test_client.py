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


def test_cache_prevents_duplicate_request(monkeypatch):
    _AsyncClient.calls = 0
    monkeypatch.setattr(client.httpx, "AsyncClient", _AsyncClient)
    api = client.FanqieboxClient(min_interval=0)
    url = "https://fanqiebox.com/games/lost-sword/guides/avalon/ethel-city/"
    asyncio.run(api.fetch(url))
    asyncio.run(api.fetch(url))
    assert _AsyncClient.calls == 1
