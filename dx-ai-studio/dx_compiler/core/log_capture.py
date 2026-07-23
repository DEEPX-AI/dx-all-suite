"""Shared log capture helpers for DX Compiler."""

import io
import re
import threading
from typing import Any, Dict, List, Optional, Protocol, TextIO, runtime_checkable

__all__ = ["LogBuffer", "LogCapture", "TqdmProgressTarget"]

# Strip ANSI escape sequences (cursor movement, colors, etc.)
_ANSI_RE = re.compile(r"\x1b\[[^a-zA-Z]*[a-zA-Z]")

# Matches tqdm progress bar output:
#   "50%|####"           - percentage + bar
#   "| 10/280 ["         - count/total bracket
#   "19.70step/s]"       - rate suffixes (tqdm-specific)
_TQDM_RE = re.compile(
    r"\d+%\|"
    r"|\|\s*[\d.]+/[\d.]+\s*\["
    r"|[\d.]+(?:step|model|op|data|node|schedule|layer|it|connection)/s[\]\s,)]"
)

# Parses structured tqdm info: "Preparing Frontend IR:  92%|####| 668/727 [..."
# Groups: label, percent, current, total
_TQDM_PARSE_RE = re.compile(
    r"^(.+?):\s*(\d+)%\|[^|]*\|\s*([\d.]+)/([\d.]+)"
)


@runtime_checkable
class TqdmProgressTarget(Protocol):
    tqdm_sub: Optional[Dict[str, Any]]


class LogBuffer:
    """Thread-safe shared log line buffer."""

    def __init__(self):
        self._buf: List[str] = []
        self._lock = threading.Lock()

    def append(self, line: str):
        with self._lock:
            self._buf.append(line)

    def get_new_lines(self, since: int) -> List[str]:
        with self._lock:
            return list(self._buf[since:])


class LogCapture(io.TextIOBase):
    """Wraps a stream, copying output into a shared LogBuffer.

    With ``handle_cr=True`` (for stderr), uses CR-aware processing and
    filters out tqdm progress bar lines so the web log panel stays clean.
    tqdm output is still passed to the original terminal stream.
    """

    def __init__(
        self,
        original: Optional[TextIO],
        buffer: LogBuffer,
        handle_cr: bool = False,
        job: Optional[TqdmProgressTarget] = None,
    ):
        self.original = original
        self._buffer = buffer
        self._handle_cr = handle_cr
        self._job = job
        self._pending = ""
        self._lock = threading.Lock()

    def write(self, s):
        if self.original:
            self.original.write(s)
        if not s:
            return 0
        with self._lock:
            if self._handle_cr:
                self._write_cr(s)
            else:
                self._write_simple(s)
        return len(s)

    def _write_simple(self, s):
        """Standard capture: split by newlines, store non-empty lines."""
        for line in s.split("\n"):
            stripped = line.strip()
            if stripped:
                self._buffer.append(stripped)

    def _write_cr(self, s):
        r"""CR-aware capture: \r resets pending, \n commits. Filters tqdm but
        parses sub-task bars into job.tqdm_sub for the GUI sub-progress bar.

        tqdm nested bars emit \x1b[A\n (cursor up + newline) between updates,
        so we never clear tqdm_sub on \n - the frontend hides it on completion."""
        for ch in s:
            if ch == "\r":
                self._try_parse_tqdm(self._pending)
                self._pending = ""
            elif ch == "\n":
                line = _ANSI_RE.sub("", self._pending).strip()
                if line:
                    self._try_parse_tqdm(line)
                    if not _TQDM_RE.search(line):
                        self._buffer.append(line)
                self._pending = ""
            else:
                self._pending += ch

    def _try_parse_tqdm(self, line: str) -> bool:
        """Parse a tqdm progress line and update job.tqdm_sub when applicable."""
        if not self._job or not line:
            return False
        clean = _ANSI_RE.sub("", line).strip()
        m = _TQDM_PARSE_RE.match(clean)
        if m:
            label = m.group(1).strip()
            if "compiling model" in label.lower():
                return False
            self._job.tqdm_sub = {
                "label": label,
                "percent": int(m.group(2)),
                "current": m.group(3),
                "total": m.group(4),
            }
            return True
        return False

    def flush(self):
        if self.original:
            self.original.flush()

    def flush_pending(self):
        """Commit any remaining pending content (call when capture ends)."""
        with self._lock:
            line = self._pending.strip()
            # Preserve legacy teardown behavior: final partial tqdm fragments are dropped.
            if line and not _TQDM_RE.search(line):
                self._buffer.append(line)
            self._pending = ""

    def isatty(self):
        return self.original.isatty() if self.original else False
