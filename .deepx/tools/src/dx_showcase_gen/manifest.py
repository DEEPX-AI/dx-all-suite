"""Showcase manifest — single source of truth for the showcase catalog.

`dx-agentic-dev-showcase/showcases.json` lists every showcase in display order.
The doc builders in `augment.py` render the root-README card grid, the showcase
catalog README, and the docs/source/00_Agentic_Development table from it, so a new
showcase is added in ONE place and regenerated everywhere via `dx-showcase-gen
regen-docs`. This is what keeps the three doc surfaces from drifting as showcases
are added (the recurring "long README" / "missing from the table" problem).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Dict, List

MANIFEST_REL = "dx-agentic-dev-showcase/showcases.json"
SHOWCASE_DIR = "dx-agentic-dev-showcase"


@dataclass
class Showcase:
    name: str          # showcase directory name
    kind: str          # game | export | retrain
    title_en: str
    title_ko: str
    tagline_en: str
    tagline_ko: str
    gif: str           # basename under docs/source/img/
    what_en: str
    what_ko: str
    highlight_en: str
    highlight_ko: str
    model: str
    build: str
    turns: str
    tokens: str
    cost: str

    def _pick(self, stem: str, lang: str) -> str:
        return getattr(self, f"{stem}_{'ko' if lang == 'ko' else 'en'}")

    def title(self, lang: str) -> str:
        return self._pick("title", lang)

    def tagline(self, lang: str) -> str:
        return self._pick("tagline", lang)

    def what(self, lang: str) -> str:
        return self._pick("what", lang)

    def highlight(self, lang: str) -> str:
        return self._pick("highlight", lang)

    def readme(self, lang: str) -> str:
        return "README-ko.md" if lang == "ko" else "README.md"


@dataclass
class Manifest:
    section: Dict[str, str]
    showcases: List[Showcase]

    def title(self, lang: str) -> str:
        return self.section["title_ko" if lang == "ko" else "title_en"]

    def catchphrase(self, lang: str) -> str:
        return self.section["catchphrase_ko" if lang == "ko" else "catchphrase_en"]


_FIELDS = {f.name for f in fields(Showcase)}


def load_manifest(repo_root: str) -> Manifest:
    data = json.loads((Path(repo_root) / MANIFEST_REL).read_text())
    scs = [Showcase(**{k: v for k, v in s.items() if k in _FIELDS})
           for s in data["showcases"]]
    return Manifest(section=data["section"], showcases=scs)


def showcase_dirs(repo_root: str) -> List[str]:
    """Every showcase directory (has a README.md), sorted — used by verify to
    catch a showcase that exists on disk but is missing from the manifest."""
    base = Path(repo_root) / SHOWCASE_DIR
    if not base.is_dir():
        return []
    return sorted(p.name for p in base.iterdir()
                  if p.is_dir() and (p / "README.md").exists())


def missing_from_manifest(repo_root: str) -> List[str]:
    """Showcase dirs present on disk but absent from the manifest (the
    'ultralytics-yolo-deepx-export was missing from the table' class of bug)."""
    man = load_manifest(repo_root)
    listed = {s.name for s in man.showcases}
    return [d for d in showcase_dirs(repo_root) if d not in listed]
