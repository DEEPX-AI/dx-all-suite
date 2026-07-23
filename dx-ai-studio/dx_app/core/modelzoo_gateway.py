"""ModelZooGateway — integration boundary for DX-APP ModelZoo operations.

Wraps the low-level modelzoo functions behind a dependency-injected adapter
so that server.py routes never call modelzoo internals directly.
"""


class _DefaultModelZooAdapter:
    """Adapter that delegates to the existing modelzoo module functions."""

    def __init__(self):
        from dx_app.core.modelzoo import modelzoo_list, modelzoo_download, modelzoo_status, modelzoo_stop
        self._list = modelzoo_list
        self._download = modelzoo_download
        self._status = modelzoo_status
        self._stop = modelzoo_stop

    def list_models(self, source="public"):
        return self._list(source)

    def download(self, items, source="public"):
        return self._download(items, source)

    def status(self):
        return self._status()

    def stop(self):
        return self._stop()


class ModelZooGateway:
    """Thin gateway that delegates all modelzoo operations to an adapter."""

    def __init__(self, adapter=None):
        self._adapter = adapter or _DefaultModelZooAdapter()

    def list_models(self, source="public"):
        return self._adapter.list_models(source)

    def download(self, items, source="public"):
        return self._adapter.download(items, source)

    def status(self):
        return self._adapter.status()

    def stop(self):
        return self._adapter.stop()
