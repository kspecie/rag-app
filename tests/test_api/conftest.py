import pytest

class _MockCollection:
    def __init__(self, name):
        self.name = name
        self.metadata = {}
    def add(self, **kwargs):
        return None
    def get(self, include=None):
        return {"metadatas": []}
    def query(self, **kwargs):
        return {"documents": [[]], "metadatas": [[]], "distances": [[]]}
    def update(self, metadata=None):
        return None

class _MockChroma:
    def __init__(self):
        self._cols = {}
    def get_or_create_collection(self, name):
        self._cols.setdefault(name, _MockCollection(name))
        return self._cols[name]
    def list_collections(self):
        return list(self._cols.values())
    def delete_collection(self, name):
        self._cols.pop(name, None)
    def get_collection(self, name):
        return self.get_or_create_collection(name)

@pytest.fixture
def mock_chroma(monkeypatch):
    client = _MockChroma()
    monkeypatch.setattr("chromadb.HttpClient", lambda *a, **k: client)
    return client

