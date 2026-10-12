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
    if not images_found and model is None:
        # 원본이 없으면 **소리 내어** 실패한다. 예전에는 처리 0건으로 조용히
        # 성공했다 — `data/thumbnails` 와 `data/examples` 를 git 에서 뺀 뒤
        # (2026-09-21) 새로 clone 한 사람이 보게 될 모습이 바로 이것이고,
        # "아무 일도 안 일어났는데 성공" 은 이 스크립트의 원래 결함(출력이
        # 있으면 무조건 스킵)과 같은 종류의 침묵이다.
        raise FileNotFoundError(
            f"No source images under {source_root}. "
            "thumbnails/ and examples/ are not tracked in git — regenerate them first "
            "with `python -m dx_modelzoo.scripts.generate_thumbnails` "
            "(needs the dx_app server on port 8080 and the .dxnn models installed).")

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

        # 출력이 **있고 원본보다 새로울 때만** 스킵한다.
        #
        # 예전에는 존재 여부만 봤다. 그래서 썸네일을 재생성해도 최적화본은 영원히
        # 갱신되지 않았다 — 2026-09-21 에 11개를 다시 만들고 돌렸더니 778개 스킵,
        # 내 파일은 하나도 안 바뀌었다. catalog.js 가 .webp → .jpg → 원본 순으로
        # 시도하므로 브라우저는 계속 옛 그림을 받는다. --force 는 우회이지 해법이
        # 아니다(매번 1578개를 전부 다시 만든다).
        # 계약: tests/dx_modelzoo/test_optimize_images_staleness.py
        safe_stem = f"{stem}-{img_path.suffix.lstrip('.').lower()}"
        if not force:
            outputs = [out_subdir / f"{safe_stem}.webp", out_subdir / f"{safe_stem}.jpg"]
            if all(o.exists() for o in outputs):
                source_mtime = img_path.stat().st_mtime
                if all(o.stat().st_mtime >= source_mtime for o in outputs):
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
        output_root.mkdir(parents=True, exist_ok=True)
        manifest_path = output_root / "manifest.json"
        # 이번에 처리한 것만 적으면 부분 실행이 나머지 기록을 지운다. `--model` 로
        # 하나씩 11번 돌렸더니 실제로 1578개 중 2개만 남은 manifest 가 커밋됐다 —
        # tools/perf_audit.py 가 `manifest.is_file()` 만 보므로 아무도 몰랐다.
        # 기존 기록에 **덮어쓰기(merge)** 한다.
        src_root = Path(source_root).resolve()
        out_root = Path(output_root).resolve()

        def _rel(value, root):
            """Paths go in relative (sources to the source root, outputs to the output root) — an absolute path
            records one developer's checkout and is wrong everywhere else."""
            p = Path(value)
            try:
                return p.resolve().relative_to(root).as_posix() if p.is_absolute() else p.as_posix()
            except ValueError:
                return p.as_posix()

        def _portable(entry):
            e = dict(entry)
            e["source"] = _rel(e["source"], src_root)
            for key in ("webp_path", "jpg_path"):
                if e.get(key):
                    e[key] = _rel(e[key], out_root)
            return e

        merged: dict[str, dict] = {}
        if manifest_path.is_file():
            try:
                previous = json.loads(manifest_path.read_text())
            except (json.JSONDecodeError, OSError):
                previous = {}
            for entry in previous.get("images", []):
                source = entry.get("source")
                if not source:
                    continue
                absolute = Path(source) if Path(source).is_absolute() else src_root / source
                # A record whose source is gone is dropped; keeping it would skew the totals.
                if absolute.is_file():
                    portable = _portable(entry)
                    merged[portable["source"]] = portable
        for entry in report["images"]:
            portable = _portable(entry)
            merged[portable["source"]] = portable

        images = sorted(merged.values(), key=lambda e: e["source"])
        manifest = {
            "images": images,
            "total_source_bytes": sum(e.get("source_bytes", 0) for e in images),
            "total_output_bytes": sum(
                e.get("webp_bytes", 0) + e.get("jpg_bytes", 0) for e in images),
        }
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
