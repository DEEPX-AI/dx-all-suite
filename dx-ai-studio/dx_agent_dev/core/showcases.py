"""Load the showcase catalog. Uses the bundled fallback JSON."""
import json

from dx_agent_dev.core.config import STATIC_DIR

_CATALOG = STATIC_DIR / "data" / "showcase_catalog.json"


def load_showcases() -> list:
    try:
        with open(_CATALOG, encoding="utf-8") as f:
            return json.load(f).get("showcases", [])
    except (OSError, json.JSONDecodeError):
        return []
