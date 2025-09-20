import landstac as ls

def test_stac_search_monkeypatched(monkeypatch):
    # Fake pystac-client surface
    class FakeSearch:
        def __init__(self, items):
            self._items = items
        def get_items(self):
            return self._items
    class FakeClient:
        def __init__(self): ...
        def search(self, **kw):
            # Return two dummy items
            from tests.conftest import DummyItem
            return FakeSearch([DummyItem("SCENE1", {}), DummyItem("SCENE2", {})])

    # Monkeypatch Client.open to return our FakeClient
    import landstac.stac as stacmod
    opened = {}
    def fake_open(url):
        opened["url"] = url
        return FakeClient()

    monkeypatch.setattr(stacmod, "Client", type("C", (), {"open": staticmethod(fake_open)}))
    client = ls.LandsatLookSTAC()
    items = client.search(collections=["landsat-c2l2-sr"], max_items=2)
    assert len(items) == 2
    assert opened["url"] == stacmod.LANDSATLOOK_STAC
