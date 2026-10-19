"""DX-APP Filesystem browser."""

import os
from pathlib import Path

# Allowed roots: only paths under the user's home directory can be browsed
_FS_ALLOWED_ROOTS = (Path.home(),)


def _is_under_allowed_roots(p: Path) -> bool:
    """Check that the path lies under one of the allowed roots."""
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
                    except Exception:e["size"]=0
                entries.append(e)
            except Exception:pass
        parent=str(p.parent) if str(p)!=str(p.parent) else None
        return{"path":str(p),"parent":parent,"entries":entries}
    except Exception as e:
        return{"error":str(e)}
