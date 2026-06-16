"""Showcase manifest — single source of truth for the showcase catalog.

`dx-agent-dev-showcase/showcases.json` lists every showcase in display order.
The doc builders in `augment.py` render the root-README card grid, the showcase
catalog README, and the docs/source/00_Agent_Driven_Development table from it, so a new
showcase is added in ONE place and regenerated everywhere via `dx-showcase-gen
regen-docs`. This is what keeps the three doc surfaces from drifting as showcases
are added (the recurring "long README" / "missing from the table" problem).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Dict, List

MANIFEST_REL = "dx-agent-dev-showcase/showcases.json"
SHOWCASE_DIR = "dx-agent-dev-showcase"


@dataclass
class Showcase:
    name: str          # showcase directory name
    kind: str          # game | export | retrain
    category: str      # category id (see Manifest.categories)
    title_en: str
    title_ko: str
    tagline_en: str
    tagline_ko: str
    what_en: str
    what_ko: str
    highlight_en: str
    highlight_ko: str
    model: str
    build: str
    turns: str
    tokens: str
    cost: str
    # card media: which asset the card grid / catalog shows for this showcase.
    #   gif    -> `gif`    (games: the gameplay GIF)
    #   sample -> `sample` (retrain: the annotated detection sample image)
    #   video  -> `video` (+ `poster`) (export: an mp4 clip)
    card_media: str = "gif"
    gif: str = ""      # basename under docs/source/img/
    sample: str = ""   # basename under docs/source/img/
    video: str = ""    # basename under docs/source/img/
    poster: str = ""   # basename under docs/source/img/
    build_gif: str = ""  # optional build-capture GIF for the feature-first 2nd cell
                         # (when the primary `gif` is a gameplay/demo, not the build)

    def card_asset(self) -> str:
        """Basename of the primary card media (the gif/sample/video)."""
        return {"gif": self.gif, "sample": self.sample,
                "video": self.video}.get(self.card_media, self.gif)

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
class Category:
    id: str
    status: str        # active | coming-soon
    title_en: str
    title_ko: str
    blurb_en: str = ""
    blurb_ko: str = ""
    note_en: str = ""
    note_ko: str = ""
    root_layout: str = ""   # "" = uniform grid; "feature-first" = first showcase gets a
                            # 2-cell feature row (primary media | its build GIF)

    def title(self, lang: str) -> str:
        return self.title_ko if lang == "ko" else self.title_en

    def blurb(self, lang: str) -> str:
        return self.blurb_ko if lang == "ko" else self.blurb_en

    def note(self, lang: str) -> str:
        return self.note_ko if lang == "ko" else self.note_en


@dataclass
class Manifest:
    section: Dict[str, str]
    showcases: List[Showcase]
    categories: List[Category] = field(default_factory=list)

    def title(self, lang: str) -> str:
        return self.section["title_ko" if lang == "ko" else "title_en"]

    def catchphrase(self, lang: str) -> str:
        return self.section["catchphrase_ko" if lang == "ko" else "catchphrase_en"]

    def announcement(self, lang: str) -> str:
        return self.section.get("announcement_ko" if lang == "ko" else "announcement_en", "")

    def by_category(self, cat_id: str) -> List[Showcase]:
        return [s for s in self.showcases if s.category == cat_id]


_FIELDS = {f.name for f in fields(Showcase)}
_CAT_FIELDS = {f.name for f in fields(Category)}


def load_manifest(repo_root: str) -> Manifest:
    data = json.loads((Path(repo_root) / MANIFEST_REL).read_text())
    scs = [Showcase(**{k: v for k, v in s.items() if k in _FIELDS})
           for s in data["showcases"]]
    cats = [Category(**{k: v for k, v in c.items() if k in _CAT_FIELDS})
            for c in data.get("categories", [])]
    return Manifest(section=data["section"], showcases=scs, categories=cats)


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
