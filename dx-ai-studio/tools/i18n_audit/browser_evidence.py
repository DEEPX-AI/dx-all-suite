from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

VOLATILE_TELEMETRY_RE = re.compile(
    r"^\d+(?:\.\d+)?\s*(?:°C|%|W|V|A|MHz|GHz|MB/s|GB/s)$"
)


@dataclass(frozen=True)
class BrowserObservation:
    module: str
    state: str
    route: str
    locale: str
    document_lang: str
    body_has_lang_class: bool
    visible_text_sample: tuple[str, ...] = ()
    issue_type: str = "observed"


def stable_visible_text_sample(text: str, *, limit: int = 8) -> tuple[str, ...]:
    lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if len(line) == 1:
            continue
        if VOLATILE_TELEMETRY_RE.match(line):
            continue
        lines.append(line)
        if len(lines) >= limit:
            break
    return tuple(lines)


def write_browser_observation(directory: Path, obs: BrowserObservation) -> Path:
    data: dict[str, Any] = {
        "module": obs.module,
        "state": obs.state,
        "route": obs.route,
        "locale": obs.locale,
        "document_lang": obs.document_lang,
        "body_has_lang_class": obs.body_has_lang_class,
        "visible_text_sample": list(obs.visible_text_sample),
        "issue_type": obs.issue_type,
    }
    filename = f"{obs.module}-{obs.state}-{obs.locale}.json"
    path = directory / filename
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_browser_evidence(directory: Path | None) -> list[dict[str, Any]]:
    if directory is None or not directory.is_dir():
        return []
    results: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        try:
            results.append(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return results
