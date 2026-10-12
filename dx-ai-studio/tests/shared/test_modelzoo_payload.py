"""The public ModelZoo payload parser exists once, in `shared/`.

dx_modelzoo reads the payload to fill its catalog, and dx_app reads it to build
the SETUP page's download list. The two modules do not import each other, so if
the parser lived in one, the other would have to copy it, and a change to the
public page's format would get fixed on one side only.

What is guarded here: the delegation is only a re-export. Called through the
`dx_modelzoo` path or the `shared` path, it is the same parser.
"""
from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE = (
    Path(__file__).resolve().parents[1]
    / "dx_modelzoo"
    / "fixtures"
    / "public_modelzoo_payload.html"
)


def _html() -> str:
    return FIXTURE.read_text(encoding="utf-8")


def test_shared_module_is_the_implementation():
    from shared import modelzoo_payload

    assert hasattr(modelzoo_payload, "parse_public_payload")
    assert hasattr(modelzoo_payload, "parse_public_modelzoo_html")


def test_dx_modelzoo_path_carries_no_implementation_of_its_own():
    """Parsing logic in the delegating file would make two copies.

    Object identity (`is`) cannot catch this: tests/shared/conftest.py puts
    `shared/` itself on sys.path, so one file can exist as two module objects,
    `shared.modelzoo_payload` and `modelzoo_payload`, with distinct function
    objects. That is harmless for a stateless parser, but identity is not a
    property this repository guarantees.

    So check what matters: the delegating file only re-exports.
    """
    from dx_modelzoo.metadata import _public_parser

    src = Path(_public_parser.__file__).read_text(encoding="utf-8")
    body = "\n".join(
        line for line in src.splitlines() if not line.lstrip().startswith("#")
    )
    assert "from shared.modelzoo_payload import" in body, "공유 구현을 가져오지 않는다"
    for smell in ("json.loads", "def parse_public_payload", "__MODEL_ZOO_DATA__"):
        assert smell not in body, (
            f"위임 파일에 구현이 돌아왔다 ({smell!r}) — 지식이 두 벌이 된다"
        )


def test_both_import_paths_agree():
    """Either import path must give the same result."""
    from dx_modelzoo.metadata import _public_parser
    from shared import modelzoo_payload

    html = _html()
    assert _public_parser.parse_public_payload(html) == modelzoo_payload.parse_public_payload(html)


def test_payload_carries_all_four_tiers():
    """Reads every tier up to Q-Master; dx_app's install flow relies on it."""
    from shared.modelzoo_payload import parse_public_payload

    rows = parse_public_payload(_html())
    assert rows, "픽스처에서 한 건도 못 읽었다"

    artifact_keys = set()
    for row in rows:
        artifact_keys |= set(row.get("artifacts", {}))
    for tier in ("qlite_dxnn", "qpro_dxnn", "qmaster_dxnn"):
        assert tier in artifact_keys, f"{tier} 를 아무 행에서도 못 찾았다"


def test_missing_global_raises_rather_than_returning_a_thin_catalog():
    from shared.modelzoo_payload import parse_public_payload

    with pytest.raises(ValueError):
        parse_public_payload("<html><body><table><tr><th>Name</th></tr></table></body></html>")
