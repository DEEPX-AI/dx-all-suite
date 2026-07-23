"""카탈로그 캐시 원자적 읽기/쓰기."""

import json
import os
import tempfile
from pathlib import Path

from dx_modelzoo.metadata.schema import SCHEMA_VERSION


def atomic_write_json(path, data):
    """원자적으로 JSON 파일 작성 (tmp → fsync → rename)."""
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
    """캐시 파일 로드. 없거나 손상되었으면 None 반환."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    # 호환성 검사
    if not isinstance(data, dict):
        return None
    if data.get("schema_version") != SCHEMA_VERSION:
        return None
    return data
