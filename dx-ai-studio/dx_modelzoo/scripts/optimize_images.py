#!/usr/bin/env python3
"""ModelZoo 이미지 최적화 도구.

thumbnails/examples 이미지를 WebP/JPG로 변환하여 optimized/ 디렉토리에 저장합니다.
기본 동작은 dry-run(보고만 수행)이며 --write 플래그로 실제 파일 생성을 활성화합니다.

Pillow는 오프라인 툴링 의존성입니다. 런타임 requirements.txt에 추가하지 않습니다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

# 서브디렉토리별 최대 너비 설정
_MAX_WIDTHS = {
    "thumbnails": 420,
    "examples": 960,
}

_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
_WEBP_QUALITY = 80
_JPG_QUALITY = 85


def _load_pillow():
    try:
        from PIL import Image
        return Image
    except ImportError as exc:
        raise SystemExit(
            "Pillow is required for image optimization. "
            "Install tooling dependency `pillow`."
        ) from exc


def _discover_images(
    source_root: Path,
    model: str | None = None,
    limit: int | None = None,
) -> list[tuple[str, Path]]:
    """source_root 아래 thumbnails/, examples/ 에서 이미지 파일을 탐색합니다."""
    results: list[tuple[str, Path]] = []
    for subdir in ("thumbnails", "examples"):
        dir_path = source_root / subdir
        if not dir_path.is_dir():
            continue
        for img_path in sorted(dir_path.iterdir()):
            if img_path.suffix.lower() not in _IMAGE_EXTENSIONS:
                continue
            if model and model.lower() not in img_path.stem.lower():
                continue
            results.append((subdir, img_path))
            if limit and len(results) >= limit:
                return results
    return results


def _resize_and_save(
    Image,
    src_path: Path,
    out_dir: Path,
    max_width: int,
) -> dict:
    """이미지를 리사이즈하고 WebP/JPG로 저장합니다. 원본 비율을 유지합니다."""
    img = Image.open(src_path)
    orig_size = src_path.stat().st_size

    # RGB 변환 (RGBA/P 모드 처리) — M-1: 알파 채널은 흰 배경 위에 합성
    if img.mode == "RGBA":
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    if w > max_width:
        ratio = max_width / w
        new_size = (max_width, int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    out_dir.mkdir(parents=True, exist_ok=True)

    # I-4: 충돌 방지 — 원본 확장자를 stem에 포함
    safe_stem = f"{src_path.stem}-{src_path.suffix.lstrip('.').lower()}"
    webp_path = out_dir / f"{safe_stem}.webp"
    jpg_path = out_dir / f"{safe_stem}.jpg"

    img.save(webp_path, "WEBP", quality=_WEBP_QUALITY)
    img.save(jpg_path, "JPEG", quality=_JPG_QUALITY)

    webp_size = webp_path.stat().st_size
    jpg_size = jpg_path.stat().st_size

    return {
        "webp_path": str(webp_path),
        "jpg_path": str(jpg_path),
        "source_bytes": orig_size,
        "webp_bytes": webp_size,
        "jpg_bytes": jpg_size,
    }


def optimize_images(
    source_root: Path | str,
    output_root: Path | str,
    *,
    write: bool = False,
    force: bool = False,
    limit: int | None = None,
    model: str | None = None,
) -> dict:
    """이미지를 최적화하고 보고서를 반환합니다.

    Args:
        source_root: thumbnails/, examples/ 가 있는 루트 디렉토리.
        output_root: 최적화 결과를 저장할 디렉토리.
        write: True면 실제 파일 생성, False면 dry-run.
        force: True면 기존 파일도 재생성.
        limit: 처리할 최대 이미지 수.
        model: 필터링할 모델 이름 부분 문자열.

    Returns:
        processed, written, skipped, source_bytes, output_bytes, images 키를 포함하는 dict.
    """
    source_root = Path(source_root)
    output_root = Path(output_root)
    Image = _load_pillow()

    images_found = _discover_images(source_root, model=model, limit=limit)

    report = {
        "processed": 0,
        "written": 0,
        "skipped": 0,
        "source_bytes": 0,
        "output_bytes": 0,
        "images": [],
    }

    for subdir, img_path in images_found:
        max_width = _MAX_WIDTHS.get(subdir, 960)
        out_subdir = output_root / subdir
        stem = img_path.stem

        # I-2 & I-4: 이미 존재하면 스킵 (force가 아닌 경우, dry-run 포함)
        safe_stem = f"{stem}-{img_path.suffix.lstrip('.').lower()}"
        if not force:
            webp_exists = (out_subdir / f"{safe_stem}.webp").exists()
            jpg_exists = (out_subdir / f"{safe_stem}.jpg").exists()
            if webp_exists and jpg_exists:
                report["skipped"] += 1
                continue

        source_size = img_path.stat().st_size
        report["processed"] += 1
        report["source_bytes"] += source_size

        entry = {
            "source": str(img_path),
            "subdir": subdir,
            "source_bytes": source_size,
        }

        if write:
            result = _resize_and_save(Image, img_path, out_subdir, max_width)
            entry.update(result)
            out_bytes = result["webp_bytes"] + result["jpg_bytes"]
            report["output_bytes"] += out_bytes
            report["written"] += 1

        report["images"].append(entry)

    if write and report["written"] > 0:
        manifest = {
            "images": report["images"],
            "total_source_bytes": report["source_bytes"],
            "total_output_bytes": report["output_bytes"],
        }
        output_root.mkdir(parents=True, exist_ok=True)
        manifest_path = output_root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    return report


def main():
    parser = argparse.ArgumentParser(
        description="ModelZoo 이미지 최적화 도구",
    )
    default_source = Path(__file__).resolve().parent.parent / "data"
    default_output = default_source / "optimized"

    parser.add_argument(
        "--source-root",
        type=Path,
        default=default_source,
        help="thumbnails/, examples/ 가 있는 루트 디렉토리",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=default_output,
        help="최적화 결과를 저장할 디렉토리",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="실제 파일 생성 (기본: dry-run)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="기존 파일도 재생성",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="처리할 최대 이미지 수",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="필터링할 모델 이름 부분 문자열",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        default=False,
        help="JSON 형식으로 출력",
    )

    args = parser.parse_args()
    report = optimize_images(
        args.source_root,
        args.output_root,
        write=args.write,
        force=args.force,
        limit=args.limit,
        model=args.model,
    )

    if args.json_output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        mode = "WRITE" if args.write else "DRY-RUN"
        print(f"[{mode}] 처리: {report['processed']}, 저장: {report['written']}, "
              f"스킵: {report['skipped']}")
        if report["source_bytes"]:
            print(f"  원본: {report['source_bytes']:,} bytes")
        if report["output_bytes"]:
            if report["source_bytes"] > 0:
                print(f"  출력: {report['output_bytes']:,} bytes "
                      f"({report['output_bytes'] / report['source_bytes'] * 100:.1f}%)")
            else:
                print(f"  출력: {report['output_bytes']:,} bytes")


if __name__ == "__main__":
    main()
