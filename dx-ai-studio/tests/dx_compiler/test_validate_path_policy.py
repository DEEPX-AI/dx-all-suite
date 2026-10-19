"""The dataset-path advisory warns about a folder compile would refuse.

The file picker's roots (a UX guardrail: /home, /tmp, /data, /mnt, /opt) are wider than the compile path policy
(suite, studio var, home, /media, /mnt), so without this a /tmp path passes the advisory and then compile refuses it."""
from __future__ import annotations

import importlib
import json
import urllib.request

from tests.server_helpers import start_module_server


def test_a_folder_outside_the_compile_roots_gets_an_advisory(tmp_path, monkeypatch):
    pp = importlib.import_module("dx_compiler.core.path_policy")
    monkeypatch.setattr(pp, "allowed_roots", lambda: [(tmp_path / "allowed").resolve()])
    (tmp_path / "allowed" / "ds").mkdir(parents=True)
    (tmp_path / "elsewhere").mkdir()
    server, port = start_module_server("dx_compiler")
    try:
        pp2 = importlib.import_module("dx_compiler.core.path_policy")
        monkeypatch.setattr(pp2, "allowed_roots", lambda: [(tmp_path / "allowed").resolve()])

        def get(path):
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/validate/path?kind=dir&path={path}") as r:
                return json.loads(r.read())
        assert get(tmp_path / "allowed" / "ds")["warnings"] == []
        assert get(tmp_path / "elsewhere")["warnings"] == ["dataset_path is outside the allowed folders"]
    finally:
        server.shutdown()
