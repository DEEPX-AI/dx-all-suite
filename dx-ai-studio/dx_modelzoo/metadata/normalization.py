"""Model id normalization utilities."""

import re
from pathlib import Path


_MISSING_SENTINELS = {"", "-", "none", "null", "n/a", "na", "not provided"}


def is_missing_source_value(value):
    """Whether a value is a placeholder (empty, '-', 'None', ...)."""
    if value is None:
        return True
    if isinstance(value, str):
        return " ".join(value.split()).strip().lower() in _MISSING_SENTINELS
    return False


def normalize_source_value(value):
    """Normalize: placeholders become None, strings are stripped."""
    if is_missing_source_value(value):
        return None
    if isinstance(value, str):
        return " ".join(value.split()).strip()
    return value


def canonical_model_id(value):
    """Turn a file or model name into a normalized lowercase id."""
    stem = Path(str(value)).stem
    return re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
