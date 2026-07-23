"""ModelZoo 메타데이터 동기화 CLI."""

import argparse
import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_DX_AI_STUDIO_ROOT = _SCRIPT_DIR.parents[1]

from dx_modelzoo.metadata.sync import resolve_source_profile, run_sync


def _resolve_metadata_config_path(dx_ai_studio_root):
    """메타데이터 동기화 config의 preferred/legacy 경로를 결정."""
    preferred_config_path = dx_ai_studio_root / "dx_modelzoo" / "data" / "metadata_sync_config.json"
    legacy_config_path = dx_ai_studio_root / "metadata_sync_config.json"
    if not preferred_config_path.exists() and legacy_config_path.exists():
        return legacy_config_path
    return preferred_config_path


def main():
    parser = argparse.ArgumentParser(description="ModelZoo 메타데이터 동기화")
    parser.add_argument("--source", default=None, help="소스 프로필 (local/internal/public)")
    parser.add_argument("--output", default=None, help="출력 카탈로그 경로")
    parser.add_argument("--cache", default=None, help="캐시 파일 경로")
    parser.add_argument("--report", default=None, help="동기화 리포트 경로")
    parser.add_argument("--offline", action="store_true", help="오프라인 모드")
    parser.add_argument(
        "--no-verify-tls",
        action="store_true",
        help="내부 인증서 환경에서만 TLS 검증을 명시적으로 비활성화",
    )
    args = parser.parse_args()

    suite_root = _DX_AI_STUDIO_ROOT.parent

    # 소스 프로필 결정: 선호 경로 → legacy fallback
    config_path = _resolve_metadata_config_path(_DX_AI_STUDIO_ROOT)
    source_profile = resolve_source_profile(
        cli_source=args.source,
        env=os.environ,
        config_path=config_path,
    )

    output_path = args.output or str(
        _DX_AI_STUDIO_ROOT / "dx_modelzoo" / "data" / "generated_catalog.json"
    )
    cache_path = args.cache or str(
        _DX_AI_STUDIO_ROOT / "dx_modelzoo" / "data" / "generated_catalog.cache.json"
    )
    report_path = args.report or str(
        _DX_AI_STUDIO_ROOT / "dx_modelzoo" / "data" / "sync_report.json"
    )

    adapter_kwargs = {}
    if args.no_verify_tls:
        print("WARNING: TLS verification disabled (--no-verify-tls)", file=sys.stderr)
        adapter_kwargs["internal_modelzoo"] = {"verify_tls": False}

    result = run_sync(
        source_profile=source_profile,
        suite_root=suite_root,
        output_path=output_path,
        cache_path=cache_path,
        report_path=report_path,
        offline=args.offline,
        adapter_kwargs=adapter_kwargs,
    )

    model_count = result["report"]["model_count"]
    errors = result["report"]["adapter_errors"]
    print(f"Sync complete: {model_count} models, {len(errors)} errors")
    if errors:
        for e in errors:
            print(f"  ERROR: {e}", file=sys.stderr)
        sys.exit(1 if not result["catalog"]["models"] else 0)


if __name__ == "__main__":
    main()
