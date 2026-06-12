#!/usr/bin/env python3
# =============================================================================
# pdf_to_markdown.py
#
# Standalone PDF -> Markdown converter running the document-parsing pipeline
# (layout analysis + OCR + table/formula recognition) on the DEEPX DX-M1 NPU.
#
# This is OUR OWN entry program. It imports the vendored `rapid_doc` package
# (DEEPX RapidDoc fork, branch rapid_doc_deepx — PP-StructureV3 pipeline) as a
# library and drives it directly. It is NOT a wrapper around the fork's
# demo/demo_offline.py; the orchestration here is modeled on that demo but is
# our standalone code.
#
# Engines (per the DEEPX fork's supported matrix):
#   Layout  : PP-DocLayout-L      -> DX Engine (NPU)
#   OCR      : PP-OCRv5 det+rec   -> DX Engine (NPU)   [--parse-method drives det mode]
#   Table    : UNET (wired)        -> DX Engine (NPU)
#   Formula  : PP-FormulaNet+ M    -> ONNX Runtime (CPU; not supported on DX Engine)
#
# Output (per input PDF, under <output-dir>/<stem>/<parse-method>/):
#   <stem>.md                  structured Markdown (headings, HTML <table>, formulas)
#   <stem>_content_list.json   structured JSON content list
#   performance_summary.md     per-stage NPU timings
# =============================================================================
import argparse
import copy
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Make the vendored ./rapid_doc importable without installing anything.
APP_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(APP_DIR))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pdf_to_markdown")

# Per-stage pipeline labels (matches the keys returned by pipeline_doc_analyze).
STAGE_ORDER = ["layout", "formula", "pdf_det", "ocr_det", "table", "ocr_rec"]
STAGE_LABELS = {
    "layout": "Layout (NPU)",
    "formula": "Formula (ONNX/CPU)",
    "pdf_det": "PDF text-det",
    "ocr_det": "OCR det (NPU)",
    "table": "Table (NPU)",
    "ocr_rec": "OCR rec (NPU)",
}


def _require_env():
    """The DX-RT pipeline needs the threading env from deepx_scripts/set_env.sh.

    run.sh sources it; if pdf_to_markdown.py is launched directly without it, fail
    early with the exact remedy instead of a deep device-init error.
    """
    required = {
        "CUSTOM_INTER_OP_THREADS_COUNT": "1",
        "CUSTOM_INTRA_OP_THREADS_COUNT": "2",
        "DXRT_DYNAMIC_CPU_THREAD": "1",
        "DXRT_TASK_MAX_LOAD": None,          # existence check
        "NFH_INPUT_WORKER_THREADS": "2",
        "NFH_OUTPUT_WORKER_THREADS": "4",
    }
    missing = [k for k, v in required.items() if os.environ.get(k) is None]
    if missing:
        logger.error("Missing DX-RT env vars: %s", ", ".join(missing))
        logger.error("Run via ./run.sh, or first: source deepx_scripts/set_env.sh 1 2 1 3 2 4")
        sys.exit(2)


def _block_network():
    """Closed-network mode: use only locally downloaded models, never fetch."""
    os.environ["MINERU_MODEL_SOURCE"] = "local"
    import requests
    import urllib.request

    def _blocked(*_a, **_k):
        raise requests.exceptions.ConnectionError("Network access blocked (offline NPU app)")

    def _blocked_url(*_a, **_k):
        import urllib.error
        raise urllib.error.URLError("Network access blocked (offline NPU app)")

    requests.get = _blocked
    urllib.request.urlopen = _blocked_url
    urllib.request.urlretrieve = _blocked_url


def build_engine_configs(output_dir, parse_method):
    """Build the per-model engine configs. Layout/OCR/Table -> DX-M1 NPU."""
    from rapid_doc.model.layout.rapid_layout_self import ModelType as LayoutModelType
    from rapid_doc.model.layout.rapid_layout_self.utils.typings import EngineType as LayoutEngineType
    from rapid_doc.model.formula.rapid_formula_self import ModelType as FormulaModelType
    from rapid_doc.model.formula.rapid_formula_self.utils.typings import EngineType as FormulaEngineType
    from rapid_doc.model.table.rapid_table_self import ModelType as TableModelType

    dxnn = APP_DIR / "dxnn_models"
    onnx = APP_DIR / "onnx_models"
    char_dict = APP_DIR / "value_compare" / "recognition" / "character_dict_from_onnx.txt"

    layout_config = {
        "model_type": LayoutModelType.PP_DOCLAYOUT_L,
        "engine_type": LayoutEngineType.DXENGINE,
        "model_dir_or_path": str(dxnn / "pp_doclayout_l_part1.dxnn"),
        "sub_model_path": str(onnx / "pp_doclayout_l_part2.onnx"),
    }

    ocr_config = {
        "use_det_mode": parse_method,          # auto: text-first->OCR | txt: text-only | ocr: always OCR
        "engine_type": "dxengine",
        "Det.model_path": str(dxnn / "det_v5_640_640.dxnn"),
        "Rec.model_path": str(dxnn / "rec_v5_ratio_10.dxnn"),
        "char_dict_path": str(char_dict),
        "use_multi_det_model": True,
        "Det.model_paths": {
            1: str(dxnn / "det_v5_640_640.dxnn"),
            2: str(dxnn / "det_v5_320_640.dxnn"),
            4: str(dxnn / "det_v5_160_640.dxnn"),
            10: str(dxnn / "det_v5_64_640.dxnn"),
        },
        "use_multi_rec_model": True,
        "Rec.model_paths": {
            3: str(dxnn / "rec_v5_ratio_3.dxnn"),
            5: str(dxnn / "rec_v5_ratio_5.dxnn"),
            10: str(dxnn / "rec_v5_ratio_10.dxnn"),
            15: str(dxnn / "rec_v5_ratio_15.dxnn"),
            25: str(dxnn / "rec_v5_ratio_25.dxnn"),
            35: str(dxnn / "rec_v5_ratio_35.dxnn"),
        },
        "save_debug_images": False,
        "debug_save_dir": os.path.join(output_dir, "ocr_debug"),
    }

    # Formula recognition is ONNX-only on this fork (not supported on DX Engine).
    formula_config = {
        "model_type": FormulaModelType.PP_FORMULANET_PLUS_M,
        "engine_type": FormulaEngineType.ONNXRUNTIME,
        "model_dir_or_path": str(onnx / "pp_formulanet_plus_m.onnx"),
    }

    # UNET wired-table recognition on the NPU.
    table_config = {
        "model_type": TableModelType.UNET,
        "engine_type": "dxengine",
        "unet.model_dir_or_path": str(dxnn / "unet.dxnn"),
    }

    return layout_config, ocr_config, formula_config, table_config


def build_perf_summary(all_pdf_perf_stats, file_names, wall_time, mode_label, model_load_times=None):
    agg = {}
    total_pages = 0
    for stats in all_pdf_perf_stats.values():
        total_pages += stats.get("layout", {}).get("count", 0)
        for key, s in stats.items():
            agg.setdefault(key, {"time": 0.0, "count": 0})
            agg[key]["time"] += s["time"]
            agg[key]["count"] += s["count"]
    total_stage_time = sum(s["time"] for s in agg.values())

    lines = [
        "# RapidDoc PDF->Markdown — NPU Performance Summary",
        "",
        f"- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Pipeline Mode**: {mode_label}",
        f"- **Files**: {len(file_names)} ({', '.join(file_names)})",
        f"- **Total Pages**: {total_pages}",
        f"- **Wall Time**: {wall_time:.2f} s",
    ]
    if total_pages and wall_time:
        lines.append(f"- **Throughput**: {total_pages / wall_time:.2f} pages/s")
    lines.append("")
    if model_load_times:
        lines.append("## Model Loading")
        lines.append("")
        lines.append("| Model | Load Time |")
        lines.append("|:---|---:|")
        for name, t in model_load_times.items():
            lines.append(f"| {name} | {t:.2f} s |")
        lines.append("")
    lines.append("## Per-Stage Performance (NPU pipeline)")
    lines.append("")
    lines.append("| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |")
    lines.append("|:---|---:|---:|---:|---:|---:|")
    for key in STAGE_ORDER:
        if key not in agg or agg[key]["time"] <= 0:
            continue
        s = agg[key]
        t, c = s["time"], s["count"]
        avg_ms = (t / max(c, 1)) * 1000
        fps = c / max(t, 1e-3)
        ratio = (t / total_stage_time * 100) if total_stage_time else 0
        lines.append(f"| {STAGE_LABELS.get(key, key)} | {c} | {avg_ms:.2f} ms | {fps:.1f} FPS | {t:.2f} | {ratio:.1f}% |")
    lines.append("")
    lines.append(f"- **Total Stage Time**: {total_stage_time:.2f} s")
    if total_pages:
        lines.append(f"- **Avg per Page**: {total_stage_time / total_pages:.2f} s")
    lines.append("")
    return "\n".join(lines)


def convert(pdf_path, output_dir, parse_method, pipeline_mode, formula_enable):
    from rapid_doc.cli.common import convert_pdf_bytes_to_bytes_by_pypdfium2, prepare_env, read_fn
    from rapid_doc.data.data_reader_writer import FileBasedDataWriter
    from rapid_doc.utils.enum_class import MakeMode
    from rapid_doc.backend.pipeline.pipeline_analyze import doc_analyze as pipeline_doc_analyze
    from rapid_doc.backend.pipeline.pipeline_middle_json_mkcontent import union_make as pipeline_union_make
    from rapid_doc.backend.pipeline.model_json_to_middle_json import result_to_middle_json as pipeline_result_to_middle_json

    os.makedirs(output_dir, exist_ok=True)
    stem = Path(pdf_path).stem
    pdf_bytes = read_fn(Path(pdf_path))
    pdf_bytes = convert_pdf_bytes_to_bytes_by_pypdfium2(pdf_bytes, 0, None)

    layout_config, ocr_config, formula_config, table_config = build_engine_configs(output_dir, parse_method)

    logger.info("Running document-parsing pipeline on DX-M1 NPU (method=%s, mode=%s) ...",
                parse_method, pipeline_mode)
    t0 = time.time()
    (infer_results, all_image_lists, all_page_dicts, lang_list,
     ocr_enabled_list, all_pdf_perf_stats, model_load_times) = pipeline_doc_analyze(
        [pdf_bytes],
        parse_method=parse_method,
        formula_enable=formula_enable,
        table_enable=True,
        layout_config=layout_config,
        ocr_config=ocr_config,
        formula_config=formula_config,
        table_config=table_config,
        checkbox_config={"checkbox_enable": False},
        use_async_pipeline=pipeline_mode,
        hybrid=False,
    )
    wall_time = time.time() - t0

    middle_ocr_config = {**ocr_config, "use_async": True} if pipeline_mode in (True, "finegrained") else ocr_config
    image_config = {"extract_original_image": False, "extract_original_image_iou_thresh": 0.5}

    model_list = infer_results[0]
    local_image_dir, local_md_dir = prepare_env(output_dir, stem, parse_method)
    image_writer, md_writer = FileBasedDataWriter(local_image_dir), FileBasedDataWriter(local_md_dir)

    middle_json = pipeline_result_to_middle_json(
        copy.deepcopy(model_list), all_image_lists[0], all_page_dicts[0], image_writer,
        lang_list[0], ocr_enabled_list[0], formula_enable,
        ocr_config=middle_ocr_config, image_config=image_config,
    )
    pdf_info = middle_json["pdf_info"]
    image_dir = os.path.basename(local_image_dir)

    md_str = pipeline_union_make(pdf_info, MakeMode.MM_MD, image_dir)
    md_writer.write_string(f"{stem}.md", md_str)

    content_list = pipeline_union_make(pdf_info, MakeMode.CONTENT_LIST, image_dir)
    md_writer.write_string(f"{stem}_content_list.json", json.dumps(content_list, ensure_ascii=False, indent=2))

    mode_label = {False: "sync", True: "async", "finegrained": "finegrained"}.get(pipeline_mode, str(pipeline_mode))
    perf_md = build_perf_summary(all_pdf_perf_stats, [stem], wall_time, mode_label, model_load_times)
    perf_path = os.path.join(output_dir, "performance_summary.md")
    with open(perf_path, "w", encoding="utf-8") as f:
        f.write(perf_md)

    md_path = os.path.join(local_md_dir, f"{stem}.md")
    json_path = os.path.join(local_md_dir, f"{stem}_content_list.json")
    logger.info("Markdown : %s", md_path)
    logger.info("JSON     : %s", json_path)
    logger.info("Timings  : %s", perf_path)
    print("\n" + perf_md)
    return md_path, json_path, perf_path


def main():
    p = argparse.ArgumentParser(
        description="Convert a PDF to structured Markdown (+JSON) on the DEEPX DX-M1 NPU "
                    "(RapidDoc PP-StructureV3: layout + OCR + table/formula).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "parse-method:\n"
            "  auto  text layer first, OCR fallback per page (default; digital or scanned)\n"
            "  txt   PDF text layer only (fastest; digital PDFs)\n"
            "  ocr   force full OCR on every page (scanned PDFs)\n"
        ),
    )
    p.add_argument("input", help="Input PDF file path")
    p.add_argument("--parse-method", choices=["auto", "txt", "ocr"], default="auto",
                   help="Text extraction method (default: auto)")
    p.add_argument("--output-dir", default=str(APP_DIR / "output"),
                   help="Output directory (default: ./output)")
    p.add_argument("--no-formula", action="store_true", help="Disable formula recognition")
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--finegrained", dest="pipeline_mode", action="store_const", const="finegrained",
                      help="7-stage per-page streaming pipeline (default)")
    mode.add_argument("--use-async", dest="pipeline_mode", action="store_const", const=True,
                      help="Batch async pipeline")
    mode.add_argument("--no-async", dest="pipeline_mode", action="store_const", const=False,
                      help="Synchronous pipeline")
    p.set_defaults(pipeline_mode="finegrained")
    args = p.parse_args()

    pdf_path = Path(args.input).expanduser().resolve()
    if not pdf_path.is_file() or pdf_path.suffix.lower() != ".pdf":
        logger.error("Input is not a PDF file: %s", pdf_path)
        sys.exit(1)

    _require_env()
    _block_network()

    logger.info("Input        : %s", pdf_path)
    logger.info("Parse method : %s", args.parse_method)
    logger.info("Output dir   : %s", args.output_dir)
    logger.info("Formula      : %s", "disabled" if args.no_formula else "enabled (ONNX/CPU)")

    convert(str(pdf_path), args.output_dir, args.parse_method, args.pipeline_mode,
            formula_enable=not args.no_formula)
    logger.info("Done.")


if __name__ == "__main__":
    main()
