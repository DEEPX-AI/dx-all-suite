"""모델 ID 정규화 유틸리티."""

import re
from pathlib import Path


_MISSING_SENTINELS = {"", "-", "none", "null", "n/a", "na", "not provided"}


def is_missing_source_value(value):
    """값이 플레이스홀더(빈 값, '-', 'None' 등)인지 판별."""
    if value is None:
        return True
    if isinstance(value, str):
        return " ".join(value.split()).strip().lower() in _MISSING_SENTINELS
    return False


def normalize_source_value(value):
    """플레이스홀더를 None으로, 문자열을 strip하여 정규화."""
    if is_missing_source_value(value):
        return None
    if isinstance(value, str):
        return " ".join(value.split()).strip()
    return value


def canonical_model_id(value):
    """파일명이나 모델명을 정규화된 소문자 ID로 변환."""
    stem = Path(str(value)).stem
    return re.sub(r"[^a-z0-9]+", "_", stem.lower()).strip("_")
