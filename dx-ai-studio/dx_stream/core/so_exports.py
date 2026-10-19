"""Function names a postprocess library (.so) exports — the pipeline builder's function-name list.

DxPostprocess's function-name differs per library (libpostprocess_ppu.so has YOLOV5S_PPU ·
SCRFD500M_PPU …, the others have PostProcess), so the list must come from the library itself.
Some boards have no binutils (nm), so the ELF .dynsym is read directly.
"""
from __future__ import annotations

import struct
from functools import lru_cache
from pathlib import Path

_SHT_DYNSYM = 11
_STT_FUNC = 2
_STB_GLOBAL, _STB_WEAK = 1, 2


def exported_functions(path: str | Path) -> list[str]:
    """Defined global function names, minus internal symbols that start with an underscore. [] if unreadable."""
    p = Path(path)
    try:
        mtime = p.stat().st_mtime_ns
    except OSError:
        return []
    return list(_read(str(p), mtime))


@lru_cache(maxsize=64)
def _read(path: str, _mtime: int) -> tuple[str, ...]:
    try:
        data = Path(path).read_bytes()
        if data[:4] != b"\x7fELF" or data[4] != 2:  # ELF64 only
            return ()
        end = "<" if data[5] == 1 else ">"
        (shoff,) = struct.unpack_from(end + "Q", data, 0x28)
        shentsize, shnum = struct.unpack_from(end + "HH", data, 0x3A)
        secs = [struct.unpack_from(end + "IIQQQQIIQQ", data, shoff + i * shentsize) for i in range(shnum)]
        names = set()
        for sec in secs:
            if sec[1] != _SHT_DYNSYM:
                continue
            stroff = secs[sec[6]][4]
            for off in range(sec[4], sec[4] + sec[5], 24):
                st_name, st_info, _other, st_shndx = struct.unpack_from(end + "IBBH", data, off)
                if (st_info & 0xF) != _STT_FUNC or (st_info >> 4) not in (_STB_GLOBAL, _STB_WEAK) or st_shndx == 0:
                    continue
                start = stroff + st_name
                name = data[start:data.index(b"\0", start)].decode("ascii", "replace")
                if name and not name.startswith("_"):
                    names.add(name)
        return tuple(sorted(names))
    except (struct.error, ValueError, IndexError):
        return ()
