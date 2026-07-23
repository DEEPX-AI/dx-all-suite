"""Import helpers for dx_stream tests — bare ``core`` namespace is shared across modules."""
from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

_STREAM_ROOT = str(Path(__file__).resolve().parent.parent.parent / "dx_stream")


def _alias_core_tree() -> None:
    """Alias bare ``core.*`` (test convention) onto the installed ``dx_stream.core.*``
    module objects.

    Source now imports via the qualified ``dx_stream.core...`` form. Without this alias, a
    test's bare ``import core.status as status`` would load a SECOND, distinct module
    instance of the same file, so ``monkeypatch.setattr(core.status, ...)`` would patch an
    object the server/core code never reads — silently diverging from source's
    ``dx_stream.core.status`` singleton. Pre-registering the exact dotted names in
    sys.modules makes bare imports resolve to the SAME objects the source uses.
    """
    import dx_stream.core as _root
    sys.modules["core"] = _root
    for modinfo in pkgutil.walk_packages(_root.__path__, _root.__name__ + "."):
        mod = importlib.import_module(modinfo.name)
        alias = "core" + modinfo.name[len("dx_stream.core"):]
        sys.modules[alias] = mod


def pin_stream_core() -> None:
    """Ensure ``core.*`` resolves to dx_stream, not another module's top-level core."""
    for mod_name in list(sys.modules):
        if mod_name == "core" or mod_name.startswith("core."):
            del sys.modules[mod_name]
    while _STREAM_ROOT in sys.path:
        sys.path.remove(_STREAM_ROOT)
    sys.path.insert(0, _STREAM_ROOT)
    _alias_core_tree()
