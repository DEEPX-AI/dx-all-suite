"""DX-APP Filesystem browser."""

import os
from pathlib import Path

# 허용된 루트 목록: 사용자 홈 디렉토리 하위만 탐색 가능
_FS_ALLOWED_ROOTS = (Path.home(),)


def _is_under_allowed_roots(p: Path) -> bool:
    """경로가 허용된 루트 중 하나의 하위인지 검증."""
    resolved = p.resolve()
    for root in _FS_ALLOWED_ROOTS:
        r = root.resolve()
        if resolved == r or r in resolved.parents:
            return True
    return False


def fs_list(path):
    """Return directory listing for file browser."""
    try:
        p=Path(path).expanduser().resolve()
        if not _is_under_allowed_roots(p):
            return{"error":f"Path is outside allowed roots: {path}"}
        if not p.exists():return{"error":f"Path not found: {path}"}
        if not p.is_dir():return{"error":"Not a directory"}
        entries=[]
        for item in sorted(p.iterdir(),key=lambda x:(not x.is_dir(),x.name.lower())):
            try:
                is_dir=item.is_dir()
                e={"name":item.name,"path":str(item),"type":"dir" if is_dir else "file",
                   "ext":item.suffix.lower() if not is_dir else None}
                if not is_dir:
                    try:e["size"]=item.stat().st_size
                    except:e["size"]=0
                entries.append(e)
            except:pass
        parent=str(p.parent) if str(p)!=str(p.parent) else None
        return{"path":str(p),"parent":parent,"entries":entries}
    except Exception as e:
        return{"error":str(e)}
