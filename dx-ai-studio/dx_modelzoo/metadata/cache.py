"""Atomic read/write of the catalog cache."""

import json
import os
import tempfile
from pathlib import Path

from dx_modelzoo.metadata.schema import SCHEMA_VERSION


def atomic_write_json(path, data):
    """Write a JSON file atomically (tmp → fsync → rename)."""
    path = Path(path)
    content = json.dumps(data, ensure_ascii=False, indent=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())
        tmp_path.replace(path)
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def load_catalog_cache(path):
    """Load the cache file; return None if it is missing or corrupt."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    # Compatibility check
    if not isinstance(data, dict):
        return None
    if data.get("schema_version") != SCHEMA_VERSION:
        return None
    return data
