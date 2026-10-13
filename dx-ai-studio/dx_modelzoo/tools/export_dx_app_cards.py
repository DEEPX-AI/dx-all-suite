"""Write the dx_app example cards: README.md in every python and cpp example dir, model.html and result.webp in
the python dir, MODELS.md and config/model_cards.json at the dx_app root.

    python -m dx_modelzoo.tools.export_dx_app_cards [--dx-app PATH] [--check] [--verify-links] [--only VARIANT ...]
                                                     [--report FILE]

--check writes nothing into the dx_app checkout and exits 1 when any file would change; --report FILE is still
written, since it lives outside dx_app. The catalog must carry its generated_at date (the cards' "as of").
A variant whose python example dir is missing is skipped and reported (no_python_dir), never created.
--verify-links sends a HEAD to every download URL; one that does not answer 200 is left off the card, listed in
the report's dead_links and stored in config/model_cards.json. Without it (--check included) the stored list is
applied again, so a run without the network writes the same cards; Studio's Save as HTML applies it too.
Contract: tests/dx_modelzoo/test_export_dx_app_cards.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from dx_modelzoo.core.model_card import (build_card, catalog_date, drop_dead_links, known_dead, load_benchmark,
                                         load_dead_links, load_manifest_urls, load_registry, load_setup_names,
                                         manifest_url_for, rel_dir)
from dx_modelzoo.core.model_card_html import render_html
from dx_modelzoo.core.model_card_image import example_image, webp_bytes
from dx_modelzoo.core.model_card_md import render_index, render_markdown
from dx_modelzoo.core.model_card_studio import category_label

INDEX_FIELDS = ("variant", "zoo_name", "setup_name", "zoo_id", "zoo_task", "name", "task", "family", "input",
                "dataset", "fps", "fps_per_watt", "license", "paths", "downloads")

LINK_CHECK_THREADS = 8
LINK_CHECK_TIMEOUT = 30


class _KeepHead(HTTPRedirectHandler):
    """Follow a redirect with HEAD again; urllib's default turns it into a GET of the whole model file."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None:
            new.method = req.get_method()
        return new


def head_status(url, timeout=LINK_CHECK_TIMEOUT):
    """(alive, status) for one download URL: alive only on HTTP 200; status is the code or the error's name."""
    request = Request(url, method="HEAD", headers={"User-Agent": "DX-ModelZoo-Cards/1.0"})
    try:
        with build_opener(_KeepHead).open(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
    except HTTPError as exc:
        status = exc.code
    except Exception as exc:  # noqa: BLE001 — any network failure means the link is not usable
        return False, type(exc).__name__
    return status == 200, status


def stored_dead_links(dx_app_root):
    """url_ok that applies the dead links the last --verify-links run stored in config/model_cards.json, so a run
    without the network (--check included) writes the same cards; None without an index."""
    dead = load_dead_links(dx_app_root)
    return None if dead is None else known_dead(dead)


def build_outputs(dx_app_root, models, categories, benchmark_rows, data_dir, asof, only=None, url_ok=None):
    """url_ok: callable url -> (alive, status) used to drop dead download links (head_status for real); None skips
    the check."""
    root = Path(dx_app_root)
    registry = load_registry(root)
    names, setup_names = load_setup_names(root)
    manifest_urls = load_manifest_urls(root)
    by_variant = {}
    for model in models:
        py = ((model.get("demo") or {}).get("python_example") or "").rstrip("/")
        if py:
            by_variant.setdefault(PurePosixPath(py).name, model)
    outputs, cards = {}, []
    report = {"count": 0, "no_studio_model": [], "missing_image": [], "unpublished": [], "setup_name_missing": [],
              "sample_is_dir": [], "no_sample": [], "accuracy_warnings": [], "metric_count_mismatch": [],
              "no_python_dir": [], "dead_links": []}
    for variant in sorted(registry):
        if only and variant not in only:
            continue
        row, model = registry[variant], by_variant.get(variant)
        if model is None:
            report["no_studio_model"].append(variant)
            continue
        card = build_card(model, row, root, benchmark_rows=benchmark_rows,
                          setup_name=setup_names.get(PurePosixPath(row["dxnn_file"]).name),
                          manifest_url=manifest_url_for(manifest_urls, row),
                          task_label=category_label(categories, model.get("category"), "en"), asof=asof)
        if not (root / card["paths"]["python"]).is_dir():
            report["no_python_dir"].append(variant)
            continue
        cards.append((card, model))
    dead_urls = []
    if url_ok is not None:
        report["dead_links"], dead_urls = drop_dead_links([card for card, _ in cards], url_ok,
                                                                    LINK_CHECK_THREADS)
    for card, model in cards:
        variant, py, cpp = card["variant"], card["paths"]["python"], card["paths"]["cpp"]
        image = example_image(model, data_dir)
        card["has_image"] = image is not None
        if image is not None:
            outputs[f"{py}/result.webp"] = webp_bytes(image)
        else:
            report["missing_image"].append(variant)
        outputs[f"{py}/README.md"] = render_markdown(card, "python").encode("utf-8")
        outputs[f"{py}/model.html"] = render_html(
            card, image_src="result.webp", other_href=rel_dir(py, cpp) + "README.md" if card["has_cpp"] else None,
            marker=True,
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
    cards = [card for card, _ in cards]
    report["count"] = len(cards)
    if not only:
        outputs["MODELS.md"] = render_index(cards, asof).encode("utf-8")
        index = {"generated_from": "DX Model Zoo publish table", "asof": asof, "dead_links": dead_urls,
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
    parser.add_argument("--verify-links", action="store_true",
                        help="HEAD every download URL and leave dead ones off the cards")
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--report")
    args = parser.parse_args(argv)
    generated = load_generated_catalog() or {}
    asof = catalog_date(generated.get("generated_at"))
    if not asof:
        parser.error("the generated catalog has no generated_at date; regenerate it before exporting cards")
    catalog = get_catalog()
    outputs, report = build_outputs(args.dx_app, catalog["models"], catalog.get("categories") or {},
                                    load_benchmark(STUDIO_ROOT / "dx_benchmark" / "dataset.json"), DATA_DIR, asof,
                                    only=set(args.only) if args.only else None,
                                    url_ok=head_status if args.verify_links else stored_dead_links(args.dx_app))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.check:
        changed = changed_outputs(args.dx_app, outputs)
        for rel in changed:
            print(f"would change: {rel}")
        print(f"{report['count']} cards, {len(changed)} files would change, "
              f"{len(report['dead_links'])} dead links left off")
        return 1 if changed else 0
    write_outputs(args.dx_app, outputs)
    print(f"{report['count']} cards, {len(outputs)} files written to {args.dx_app}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
