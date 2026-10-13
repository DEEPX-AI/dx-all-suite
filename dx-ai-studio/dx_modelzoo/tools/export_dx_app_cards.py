"""Write the dx_app example cards: README.md in every python and cpp example dir, model.html and result.webp in
the python dir, MODELS.md and config/model_cards.json at the dx_app root.

    python -m dx_modelzoo.tools.export_dx_app_cards [--dx-app PATH] [--check] [--only VARIANT ...] [--report FILE]

--check writes nothing into the dx_app checkout and exits 1 when any file would change; --report FILE is still
written, since it lives outside dx_app. The catalog must carry its generated_at date (the cards' "as of").
A variant whose python example dir is missing is skipped and reported (no_python_dir), never created.
Contract: tests/dx_modelzoo/test_export_dx_app_cards.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath

from dx_modelzoo.core.model_card import build_card, load_benchmark, load_registry, load_setup_names, rel_dir
from dx_modelzoo.core.model_card_html import render_html
from dx_modelzoo.core.model_card_image import example_image, webp_bytes
from dx_modelzoo.core.model_card_md import render_index, render_markdown
from dx_modelzoo.core.model_card_studio import category_label

INDEX_FIELDS = ("variant", "zoo_name", "setup_name", "zoo_id", "zoo_task", "name", "task", "family", "input",
                "dataset", "fps", "fps_per_watt", "license", "paths", "downloads")


def build_outputs(dx_app_root, models, categories, benchmark_rows, data_dir, asof, only=None):
    root = Path(dx_app_root)
    registry = load_registry(root)
    names, setup_names = load_setup_names(root)
    by_variant = {}
    for model in models:
        py = ((model.get("demo") or {}).get("python_example") or "").rstrip("/")
        if py:
            by_variant.setdefault(PurePosixPath(py).name, model)
    outputs, cards = {}, []
    report = {"count": 0, "no_studio_model": [], "missing_image": [], "unpublished": [], "setup_name_missing": [],
              "sample_is_dir": [], "no_sample": [], "accuracy_warnings": [], "metric_count_mismatch": [],
              "no_python_dir": []}
    for variant in sorted(registry):
        if only and variant not in only:
            continue
        row, model = registry[variant], by_variant.get(variant)
        if model is None:
            report["no_studio_model"].append(variant)
            continue
        card = build_card(model, row, root, benchmark_rows=benchmark_rows,
                          setup_name=setup_names.get(PurePosixPath(row["dxnn_file"]).name),
                          task_label=category_label(categories, model.get("category"), "en"), asof=asof)
        py, cpp = card["paths"]["python"], card["paths"]["cpp"]
        if not (root / py).is_dir():
            report["no_python_dir"].append(variant)
            continue
        image = example_image(model, data_dir)
        card["has_image"] = image is not None
        if image is not None:
            outputs[f"{py}/result.webp"] = webp_bytes(image)
        else:
            report["missing_image"].append(variant)
        outputs[f"{py}/README.md"] = render_markdown(card, "python").encode("utf-8")
        outputs[f"{py}/model.html"] = render_html(
            card, image_src="result.webp", other_href=rel_dir(py, cpp) + "README.md" if card["has_cpp"] else None,
        ).encode("utf-8")
        if card["has_cpp"]:
            outputs[f"{cpp}/README.md"] = render_markdown(card, "cpp").encode("utf-8")
        if not card["published"]:
            report["unpublished"].append(variant)
        if card["setup_name"].lower() not in names:
            report["setup_name_missing"].append(f"{variant}: {card['setup_name']}")
        if not card["sample"]:
            report["no_sample"].append(variant)
        elif (root / card["sample"]).is_dir():
            report["sample_is_dir"].append(f"{variant}: {card['sample']}")
        if card["accuracy"]["metric_count_mismatch"]:
            counts = card["accuracy"]["metric_counts"]
            report["metric_count_mismatch"].append(f"{variant}: {counts['names']} metric names, {counts['values']} values")
        for w in card["accuracy"]["warnings"]:
            report["accuracy_warnings"].append(f"{variant}: {w['tier']} −{w['drop']:.2f} on {w['metric']}")
        cards.append(card)
    report["count"] = len(cards)
    if not only:
        outputs["MODELS.md"] = render_index(cards, asof).encode("utf-8")
        index = {"generated_from": "DX Model Zoo publish table", "asof": asof,
                 "models": [{k: c[k] for k in INDEX_FIELDS} for c in cards]}
        outputs["config/model_cards.json"] = (json.dumps(index, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return outputs, report


def write_outputs(dx_app_root, outputs):
    root = Path(dx_app_root)
    for rel, data in outputs.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.is_file() or path.read_bytes() != data:
            path.write_bytes(data)


def changed_outputs(dx_app_root, outputs):
    root = Path(dx_app_root)
    return sorted(rel for rel, data in outputs.items()
                  if not (root / rel).is_file() or (root / rel).read_bytes() != data)


def main(argv=None):
    from dx_modelzoo.core.catalog import get_catalog, load_generated_catalog
    from dx_modelzoo.core.config import DATA_DIR
    from shared.paths import DX_APP_ROOT, STUDIO_ROOT

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dx-app", default=str(DX_APP_ROOT))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    generated = load_generated_catalog() or {}
    asof = str(generated.get("generated_at") or "")[:10]
    if not asof:
        parser.error("the generated catalog has no generated_at date; regenerate it before exporting cards")
    catalog = get_catalog()
    outputs, report = build_outputs(args.dx_app, catalog["models"], catalog.get("categories") or {},
                                    load_benchmark(STUDIO_ROOT / "dx_benchmark" / "dataset.json"), DATA_DIR, asof,
                                    only=set(args.only) if args.only else None)
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.check:
        changed = changed_outputs(args.dx_app, outputs)
        for rel in changed:
            print(f"would change: {rel}")
        print(f"{report['count']} cards, {len(changed)} files would change")
        return 1 if changed else 0
    write_outputs(args.dx_app, outputs)
    print(f"{report['count']} cards, {len(outputs)} files written to {args.dx_app}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
