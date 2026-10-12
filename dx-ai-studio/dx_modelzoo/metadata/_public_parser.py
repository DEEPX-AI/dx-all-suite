"""Public ModelZoo payload reader — the implementation lives in `shared/modelzoo_payload.py`.

dx_app's SETUP catalog reads the same payload. The two modules are independent servers on
their own ports and do not import each other, so the tier and field knowledge lives once in
`shared/`. What remains here delegates to it so existing import paths keep working.
"""
from shared.modelzoo_payload import (  # noqa: F401
    parse_public_modelzoo_html,
    parse_public_payload,
)

__all__ = ["parse_public_modelzoo_html", "parse_public_payload"]
