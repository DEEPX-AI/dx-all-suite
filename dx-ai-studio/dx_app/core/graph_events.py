"""Events of a graph run: the `[EVENT] {json}` lines dx_app prints on stdout and the `--events <file.jsonl>` file
(the same objects, one per line):

    {"frame": 12, "time": 0.48, "stream": "cam", "node": "zone", "event": "enter", "track_id": 3, "data": {...}}

`EventLog` keeps what a running job has printed (bounded, with counts per node and event, each event numbered so a
poll asks only for the new ones); `read_jsonl` reads a finished run's file. A line that is not such an object is
skipped. Contract: tests/dx_app/test_graph_events.py
"""
from __future__ import annotations

import json
import threading
from collections import deque
from pathlib import Path

PREFIX = "[EVENT] "
KEEP = 2000            # events a running job keeps for the page (the file has all of them)
PAGE = 200             # events one poll hands out at most
LIST_MAX = 5000        # events a finished run's result lists (the file has all of them)


def clean(obj):
    """The event if `obj` is one (node and event are non-empty strings), with typed fields; else None."""
    if not isinstance(obj, dict):
        return None
    node, name = obj.get("node"), obj.get("event")
    if not isinstance(node, str) or not node or not isinstance(name, str) or not name:
        return None

    def num(v, kind):
        if isinstance(v, bool) or not isinstance(v, (int, float)):
            return None
        try:
            return kind(v)
        except (OverflowError, ValueError):
            return None

    data = obj.get("data")
    return {"frame": num(obj.get("frame"), int), "time": num(obj.get("time"), float),
            "stream": obj.get("stream") if isinstance(obj.get("stream"), str) else None,
            "node": node, "event": name, "track_id": num(obj.get("track_id"), int),
            "data": data if isinstance(data, dict) else {}}


def parse_event_line(line: str):
    """The event of one `[EVENT] {...}` stdout line, else None."""
    s = (line or "").strip()
    if not s.startswith(PREFIX):
        return None
    try:
        return clean(json.loads(s[len(PREFIX):]))
    except ValueError:
        return None


def _count(counts: dict, ev: dict) -> None:
    per = counts.setdefault(ev["node"], {})
    per[ev["event"]] = per.get(ev["event"], 0) + 1


class EventLog:
    """Events a running job printed: the last KEEP, numbered from 1 (`seq`), and counts over all of them."""

    def __init__(self, keep: int = KEEP):
        self._lock = threading.Lock()
        self._events = deque(maxlen=keep)
        self.total = 0
        self.counts: dict = {}

    def add(self, ev: dict) -> None:
        with self._lock:
            self.total += 1
            _count(self.counts, ev)
            self._events.append(dict(ev, seq=self.total))

    def feed(self, text: str) -> int:
        """Add the events of a chunk of stdout; returns how many."""
        n = 0
        for line in (text or "").splitlines():
            ev = parse_event_line(line)
            if ev:
                self.add(ev)
                n += 1
        return n

    def since(self, after: int = 0, limit: int = PAGE) -> list:
        """Events numbered after `after`, oldest first, at most `limit` (the page asks again for the rest)."""
        with self._lock:
            return [dict(e) for e in self._events if e["seq"] > after][:limit]

    def snapshot(self) -> dict:
        with self._lock:
            return {"event_total": self.total, "event_counts": json.loads(json.dumps(self.counts))}

    def listing(self, limit: int = LIST_MAX) -> dict:
        with self._lock:
            events = [dict(e) for e in self._events][:limit]
            return {"events": events, "total": self.total, "counts": json.loads(json.dumps(self.counts)),
                    "truncated": self.total > len(events)}


def read_jsonl(path: Path, limit: int = LIST_MAX) -> dict:
    """{events (the first `limit`, numbered), total, counts, truncated} of an --events file; empty if unreadable."""
    out = {"events": [], "total": 0, "counts": {}, "truncated": False}
    try:
        f = open(path, "r", encoding="utf-8", errors="replace")
    except OSError:
        return out
    with f:
        for line in f:
            if not line.strip():
                continue
            try:
                ev = clean(json.loads(line))
            except ValueError:
                ev = None
            if ev is None:
                continue
            out["total"] += 1
            _count(out["counts"], ev)
            if len(out["events"]) < limit:
                out["events"].append(dict(ev, seq=out["total"]))
    out["truncated"] = out["total"] > len(out["events"])
    return out
