from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from .config import LANGUAGES


@dataclass(frozen=True)
class AuditRecord:
    module: str
    surface: str
    route_or_state: str
    source_file: str
    selector_or_key: str
    text_role: str
    texts: Mapping[str, str]
    brand_terms: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "texts", MappingProxyType(dict(self.texts)))

    def __hash__(self) -> int:
        return hash((
            self.module,
            self.surface,
            self.route_or_state,
            self.source_file,
            self.selector_or_key,
            self.text_role,
            tuple((lang, self.texts.get(lang, "")) for lang in LANGUAGES),
            self.brand_terms,
        ))

    @property
    def record_id(self) -> str:
        return f"{self.module}:{self.surface}:{self.source_file}:{self.selector_or_key}"

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "record_id": self.record_id,
            "module": self.module,
            "surface": self.surface,
            "route_or_state": self.route_or_state,
            "source_file": self.source_file,
            "selector_or_key": self.selector_or_key,
            "text_role": self.text_role,
            "brand_terms": list(self.brand_terms),
        }
        for lang in LANGUAGES:
            data[lang] = self.texts.get(lang, "")
        return data


@dataclass(frozen=True)
class Finding:
    record_id: str
    issue_type: str
    severity: str
    message: str
    suggested_fix: str = ""
    verification_method: str = "static inventory"

    def to_dict(self) -> dict[str, str]:
        return {
            "record_id": self.record_id,
            "issue_type": self.issue_type,
            "severity": self.severity,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
            "verification_method": self.verification_method,
        }


@dataclass(frozen=True)
class CoverageState:
    module: str
    state: str
    route: str
    locales_checked: tuple[str, ...] = field(default_factory=tuple)
    evidence: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "state": self.state,
            "route": self.route,
            "locales_checked": list(self.locales_checked),
            "evidence": list(self.evidence),
        }
