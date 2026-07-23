"""어댑터 결과 계약 정의.

모든 메타데이터 어댑터 함수는 AdapterResult 형태의 dict를 반환해야 한다.
Python stdlib typing만 사용하며 외부 의존성 없음.
"""

from __future__ import annotations

from typing import TypedDict


class AdapterResult(TypedDict, total=True):
    """어댑터 반환값의 필수 필드 계약.

    Required fields:
        adapter: 어댑터 이름 (예: "local_runtime")
        profile: 소스 프로필 (예: "local", "internal")
        fetched_at: ISO 8601 타임스탬프
        ok: 성공 여부
        models: 모델 ID → 필드 dict 매핑
        errors: 오류 메시지 목록
        warnings: 경고 메시지 목록
    """

    adapter: str
    profile: str
    fetched_at: str
    ok: bool
    models: dict[str, dict]
    errors: list[str]
    warnings: list[str]


ADAPTER_RESULT_REQUIRED_KEYS: set[str] = set(AdapterResult.__annotations__)
