#!/usr/bin/env python3
"""DX Compiler Server — stdlib HTTP server for ONNX compiler GUI.

Pure Python stdlib http.server implementation (no FastAPI/Flask): graph
visualization, compile workflow, config wizard, model summary export, and
SSE progress streaming.
"""
from __future__ import annotations

import glob as glob_mod
import re
import importlib.util
import json
import os
import sys
import threading
import time
import uuid
from pathlib import Path


_STUDIO_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _STUDIO_DIR.parent

from shared.dx_server import DXBaseHandler, DXServer, RequestBodyError
from shared.chat import ChatEngine

from dx_compiler.core.config import (
    SCRIPT_DIR, STATIC_DIR, TEMPLATES_DIR, UPLOAD_DIR,
    DEFAULT_PORT, SERVER_NAME, SUITE_ROOT, is_safe_path, static_version,
)
from dx_compiler.core.compiler_service import (
    CompilerService,
    NODE_SELECTION_UNSUPPORTED_KEY,
    NODE_SELECTION_UNSUPPORTED_MESSAGE,
)
from dx_compiler.core.setup_service import setup_service
from dx_compiler.core import fs_browse

# Replaces Jinja2 so DX AI Studio has ZERO third-party runtime dependencies.
# Supports exactly the constructs the compiler templates use:
#   {% extends "base.html" %} + {% block content %}...{% endblock %}
#   {% include "partials/x.html" %}   (resolved recursively)
#   {{ var }}                          (substituted from the render context)
_EXTENDS_RE = re.compile(r'\s*\{%\s*extends\s+"([^"]+)"\s*%\}')
_BLOCK_RE = re.compile(r'\{%\s*block\s+content\s*%\}(.*?)\{%\s*endblock\s*%\}', re.S)
_INCLUDE_RE = re.compile(r'\{%\s*include\s+"([^"]+)"\s*%\}')
_VAR_RE = re.compile(r'\{\{\s*(\w+)\s*\}\}')


def _render_template(name, ctx):
    src = (TEMPLATES_DIR / name).read_text(encoding="utf-8")
    ext = _EXTENDS_RE.match(src)
    if ext:
        block = _BLOCK_RE.search(src)
        content = block.group(1) if block else ""
        base = (TEMPLATES_DIR / ext.group(1)).read_text(encoding="utf-8")
        src = _BLOCK_RE.sub(lambda _m: content, base)
    while True:
        inc = _INCLUDE_RE.search(src)
        if not inc:
            break
        partial = (TEMPLATES_DIR / inc.group(1)).read_text(encoding="utf-8")
        src = src[:inc.start()] + partial + src[inc.end():]
    return _VAR_RE.sub(lambda m: str(ctx.get(m.group(1), "")), src)

compiler_service = CompilerService()

STATIC_VERSION = static_version()

PHASE_NAMES = ["PREPARE", "SURGERY", "PARTITION", "QUANTIZATION", "OPTIMIZE", "CODEGEN"]
DEFAULT_COMPILER_MAX_JOB_SECONDS = 60 * 60
ALLOWED_UPLOAD_EXTENSIONS = frozenset((".onnx", ".json"))


def _find_fresh_dxnn(output_dir: str, start_time: float):
    """Return path to the most recently created .dxnn file, or None."""
    dxnn_files = glob_mod.glob(str(Path(output_dir) / "*.dxnn"))
    fresh = [f for f in dxnn_files if Path(f).stat().st_mtime >= start_time
             and "optimized_ckpt" not in Path(f).name]
    return max(fresh, key=lambda f: (Path(f).stat().st_mtime_ns, f), default=None)


def _safe_download_stem(value: str | None) -> str:
    """Return an attachment-safe stem for a user-controlled path or filename."""
    stem = re.sub(r"[^A-Za-z0-9._-]", "_", Path(value or "").stem)
    return stem or "download"


_chat_engine = ChatEngine(
    app_name="dx_compiler",
    fallback_rules=[
        (["compile", "컴파일", "onnx", "dxnn"], {
            "ko": "컴파일 폼에서 ONNX 파일을 업로드하고 옵션을 설정한 후 Submit을 누르세요.",
            "en": "Upload an ONNX file in the compile form, set options, and click Submit.",
        }),
        (["graph", "그래프", "시각화"], {
            "ko": "왼쪽 패널에서 컴파일 단계별 그래프 변화를 실시간으로 확인할 수 있습니다.",
            "en": "View real-time graph changes per compilation phase in the left panel.",
        }),
        (["quantization", "양자화", "INT8"], {
            "ko": "DXQ 설정에서 P0~P5 프리셋과 weight/activation dtype을 선택할 수 있습니다.",
            "en": "Select P0–P5 presets and weight/activation dtypes in the DXQ settings.",
        }),
    ]
)


def _extract_preprocess_ops(log_buffer) -> list:
    """Parse preprocessing ops from compilation log buffer."""
    ops = []
    if not log_buffer:
        return ops
    for line in log_buffer.get_new_lines(0):
        stripped = line.strip()
        if "Added nodes:" in stripped:
            after = stripped.split("Added nodes:")[-1].strip()
            for op in after.split(" -> "):
                op = op.strip()
                if op:
                    ops.append(op)
    return ops


def _compiler_max_job_seconds() -> float:
    raw = os.environ.get("DX_COMPILER_MAX_JOB_SECONDS", str(DEFAULT_COMPILER_MAX_JOB_SECONDS))
    try:
        seconds = float(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("DX_COMPILER_MAX_JOB_SECONDS must be a number") from exc
    if seconds <= 0:
        raise ValueError("DX_COMPILER_MAX_JOB_SECONDS must be positive")
    return seconds


def _node_selection_unsupported_warning() -> dict:
    return {
        "key": NODE_SELECTION_UNSUPPORTED_KEY,
        "message": NODE_SELECTION_UNSUPPORTED_MESSAGE,
    }


def _find_diagnosis_report(job) -> str | None:
    """Locate the HTML quantization diagnosis report on disk."""
    candidates: list[Path] = []
    if getattr(job, "diagnosis_report_path", None):
        candidates.append(Path(job.diagnosis_report_path))
    if getattr(job, "output_dir", ""):
        candidates.append(Path(job.output_dir) / "quant_diagnosis" / "diagnosis_report.html")
    for candidate in candidates:
        if candidate.name != "diagnosis_report.html":
            continue
        path = str(candidate)
        if is_safe_path(path) and candidate.is_file():
            return path
    return None


def _qxnn_payload(job, include_path: bool = False) -> dict:
    """Build the quantization-diagnosis availability payload for SSE events."""
    diagnosis_report_path = _find_diagnosis_report(job)
    payload: dict = {
        "available": bool(diagnosis_report_path),
        "diagnosis_report_available": bool(diagnosis_report_path),
        "quant_diagnosis_requested": bool(getattr(job, "quant_diagnosis", False)),
    }
    if diagnosis_report_path:
        payload["diagnosis_report_filename"] = Path(diagnosis_report_path).name
        payload["diagnosis_report_url"] = f"/compile/{job.job_id}/quant-diagnosis/report"
        if include_path:
            payload["diagnosis_report_path"] = diagnosis_report_path
    qxnn_path = getattr(job, "qxnn_path", None)
    if qxnn_path:
        payload["qxnn_path"] = qxnn_path
        payload["qxnn_available"] = True
        if job.output_dir:
            payload["suggested_output_dir"] = str(Path(job.output_dir) / "resume")
    return payload


def _compiler_feature_status() -> dict:
    has_dx_com = importlib.util.find_spec("dx_com") is not None
    compile_available = has_dx_com
    if not compile_available:
        venv_py = setup_service.get_venv_python()
        if venv_py:
            compile_available = bool(setup_service.check_status().get("dx_com_installed"))

    warnings = []
    if compile_available and not has_dx_com:
        warnings.append(_node_selection_unsupported_warning())

    return {
        "compile": compile_available,
        "setup_available": True,
        "capabilities": {
            "node_selection": has_dx_com,
        },
        "warnings": warnings,
    }


class CompilerHandler(DXBaseHandler):
    """Route HTTP requests for DX Compiler GUI."""

    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    log_filter = ["/static/"]

    def _render(self, template_name, **ctx):
        ctx.setdefault("v", STATIC_VERSION)
        return _render_template(template_name, ctx)


    def route(self):
        path = self.url_path

        if self.handle_chat_routes(_chat_engine):
            return

        if self.command == "GET" and path in ("/", "/index.html"):
            html = self._render("index.html")
            html = self.render_html_with_asset_hashes(html, asset_scope="dx_compiler")
            return self.send_html_no_cache(html)

        if self.route_common():
            return

        if self.command == "GET":
            if path == "/feature-check":
                return self.send_json(_compiler_feature_status())

            if path == "/agentic/session-dxnn":
                session_dir = self.query.get("dir", [None])[0]
                return self._agentic_session_dxnn(session_dir)

            if path.startswith("/progress/"):
                job_id = path.split("/progress/", 1)[1]
                return self._sse_progress(job_id)

            if path.startswith("/compile/") and path.endswith("/quant-diagnosis/report"):
                job_id = path[len("/compile/"):-len("/quant-diagnosis/report")]
                return self._quant_diagnosis_report(job_id)

            if path.startswith("/compile/") and path.endswith("/dxnn"):
                job_id = path[len("/compile/"):-len("/dxnn")]
                return self._compile_dxnn(job_id)

            if path == "/model/inspect":
                model_path = self.query.get("path", [None])[0]
                return self._inspect_model(model_path)

            if path == "/api/listdir":
                return self._list_dir()

            if path == "/setup/status":
                return self.send_json(setup_service.check_status())

            if path == "/setup/sample-models":
                return self.send_json(setup_service.get_sample_models())

        elif self.command == "POST":
            if path == "/compile":
                return self._compile()

            if path == "/compile/resume":
                return self._compile_qxnn_resume()

            # /compile/{job_id}/resume — node selection resume (must follow /compile/resume)
            if path.startswith("/compile/") and path.endswith("/resume"):
                job_id = path[len("/compile/"):-len("/resume")]
                return self._compile_resume(job_id)

            # /compile/{job_id}/cancel — stop a running compile and kill its worker
            if path.startswith("/compile/") and path.endswith("/cancel"):
                job_id = path[len("/compile/"):-len("/cancel")]
                return self._compile_cancel(job_id)

            if path.startswith("/compile/") and path.endswith("/calculate-exclude"):
                job_id = path[len("/compile/"):-len("/calculate-exclude")]
                return self._calc_exclude(job_id)

            if path.startswith("/compile/") and path.endswith("/summary"):
                job_id = path[len("/compile/"):-len("/summary")]
                return self._compile_summary(job_id)

            if path == "/upload":
                return self._upload_file()

            if path == "/api/mkdir":
                return self._mkdir()

            if path == "/config/generate":
                return self._config_generate()

            if path == "/viewer/parse":
                return self._viewer_parse()

            if path == "/setup/install-sdk":
                return self._sse_setup(setup_service.install_sdk)

            if path == "/setup/download-samples":
                return self._sse_setup(setup_service.download_samples)

        self.send_error_json(404, "Not found")


    def _compile(self):
        """Submit a compile job (form-data). Return progress HTML partial."""
        fields, _files = self.parse_multipart()
        model_path = fields.get("model_path", "")
        config_path = fields.get("config_path", "")
        output_dir = fields.get("output_dir", "")
        opt_level = int(fields.get("opt_level", "1"))
        aggressive_partitioning = fields.get("aggressive_partitioning", "false") == "true"
        gen_log = fields.get("gen_log", "false") == "true"
        quant_diagnosis = fields.get("quant_diagnosis", "false") == "true"
        node_selection = fields.get("node_selection", "false") == "true"
        use_q_pro = fields.get("use_q_pro", "false") == "true"
        enhanced_scheme_raw = fields.get("enhanced_scheme", "")

        parsed_scheme = None
        if enhanced_scheme_raw:
            try:
                parsed_scheme = json.loads(enhanced_scheme_raw)
            except json.JSONDecodeError:
                parsed_scheme = None

        if use_q_pro:
            parsed_scheme = None

        if not model_path or not config_path or not output_dir:
            return self.send_error_json(400, "model_path, config_path, and output_dir are required")

        job = compiler_service.submit(
            model_path=model_path,
            config_path=config_path,
            output_dir=output_dir,
            opt_level=opt_level,
            aggressive_partitioning=aggressive_partitioning,
            gen_log=gen_log,
            quant_diagnosis=quant_diagnosis,
            enhanced_scheme=parsed_scheme or None,
            node_selection=node_selection,
            use_q_pro=use_q_pro,
        )
        html = self._render("partials/progress.html", job_id=job.job_id)
        self.send_html(html)

    def _compile_cancel(self, job_id):
        """Cancel a running compile: terminate the worker process and mark it errored."""
        job = compiler_service.get_job(job_id)
        if job is None:
            return self.send_error_json(404, "Job not found")
        cancelled = compiler_service.cancel(job_id)
        return self.send_json({"status": "cancelled" if cancelled else job.status})

    def _compile_resume(self, job_id):
        """Resume a paused compile with selected input/output nodes."""
        job = compiler_service.get_job(job_id)
        if job is None:
            return self.send_error_json(404, "Job not found")
        if not job.paused:
            return self.send_error_json(400, "Job is not paused")

        body = self.read_json_body()
        job.selected_input_nodes = body.get("input_nodes", [])
        job.selected_output_nodes = body.get("output_nodes", [])
        job.pause_event.set()
        self.send_json({"status": "resumed"})

    def _compile_qxnn_resume(self):
        """Submit a QXNN resume (re-quantization) job from JSON body."""
        try:
            body = self.read_json_body()
        except RequestBodyError:
            raise
        except Exception:
            return self.send_error_json(400, "Invalid JSON body")

        qxnn_path = (body.get("qxnn_path") or "").strip()
        output_dir = (body.get("output_dir") or "").strip()
        if not qxnn_path or not qxnn_path.lower().endswith(".qxnn"):
            return self.send_error_json(400, "qxnn_path must point to a .qxnn file")
        if not output_dir:
            return self.send_error_json(400, "output_dir is required")

        recalibration_method = body.get("recalibration_method") or None
        if recalibration_method == "":
            recalibration_method = None
        valid_recal = {"minmax", "ema", "iqr"}
        if recalibration_method is not None and recalibration_method not in valid_recal:
            return self.send_error_json(
                400,
                f"recalibration_method must be one of {sorted(valid_recal)}",
            )

        dataset_path = (body.get("dataset_path") or "").strip() or None
        use_q_pro = bool(body.get("use_q_pro", False))
        enhanced_scheme = body.get("enhanced_scheme")
        if use_q_pro:
            enhanced_scheme = None
        elif enhanced_scheme is not None and not isinstance(enhanced_scheme, dict):
            return self.send_error_json(400, "enhanced_scheme must be a JSON object")
        if use_q_pro and body.get("enhanced_scheme"):
            return self.send_error_json(400, "use_q_pro and enhanced_scheme are mutually exclusive")

        job = compiler_service.submit_resume(
            qxnn_path=qxnn_path,
            output_dir=output_dir,
            recalibration_method=recalibration_method,
            enhanced_scheme=enhanced_scheme,
            use_q_pro=use_q_pro,
            dataset_path=dataset_path,
        )
        html = self._render("partials/progress.html", job_id=job.job_id)
        self.send_html(html)

    def _quant_diagnosis_report(self, job_id):
        """Serve the HTML quantization diagnosis report for a job."""
        job = compiler_service.get_job(job_id)
        if job is None:
            return self.send_error_json(404, "Job not found")
        report_path = _find_diagnosis_report(job)
        if not report_path:
            return self.send_error_json(404, "Quantization diagnosis report not available")
        try:
            body = Path(report_path).read_text(encoding="utf-8").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Disposition", 'inline; filename="diagnosis_report.html"')
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self' 'unsafe-inline' data:; script-src 'none'; object-src 'none'; base-uri 'none'",
            )
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except OSError as e:
            return self.send_error_json(500, f"Quantization diagnosis report load failed: {e}")

    def _calc_exclude(self, job_id):
        """Calculate nodes excluded by a compile range selection."""
        job = compiler_service.get_job(job_id)
        if job is None:
            return self.send_error_json(404, "Job not found")
        if job.prepared_graph_ir is None:
            return self.send_error_json(400, "No prepared graph available")

        body = self.read_json_body()
        input_nodes = body.get("input_nodes", [])
        output_nodes = body.get("output_nodes", [])

        if not input_nodes and not output_nodes:
            return self.send_json({
                "excluded_nodes": [],
                "included_count": len(job.prepared_graph_ir.nodes),
                "total_count": len(job.prepared_graph_ir.nodes),
            })

        try:
            from dx_compiler.core.compiler_bridge import (
                collect_downstream_nodes, collect_upstream_nodes, validate_target_nodes
            )
            graph = job.prepared_graph_ir
            node_map = {node.name: node for node in graph.nodes}
            all_node_names = set(node_map.keys())
            total = len(graph.nodes)
            excluded_set = set()

            if input_nodes and output_nodes:
                input_existing = validate_target_nodes(set(input_nodes), node_map)
                output_existing = validate_target_nodes(set(output_nodes), node_map)
                if input_existing and output_existing:
                    forward_from_input = collect_downstream_nodes(input_existing, node_map)
                    backward_from_output = collect_upstream_nodes(output_existing, node_map)
                    included = (forward_from_input & backward_from_output) | input_existing | output_existing
                    excluded_set = all_node_names - included
            elif output_nodes:
                existing = validate_target_nodes(set(output_nodes), node_map)
                if existing:
                    excluded_set.update(collect_downstream_nodes(existing, node_map))
            elif input_nodes:
                existing = validate_target_nodes(set(input_nodes), node_map)
                if existing:
                    excluded_set.update(collect_upstream_nodes(existing, node_map))

            return self.send_json({
                "excluded_nodes": list(excluded_set),
                "included_count": total - len(excluded_set),
                "total_count": total,
            })
        except Exception as e:
            return self.send_error_json(500, str(e))

    def _compile_summary(self, job_id):
        """Generate and download an HTML compilation summary."""
        job = compiler_service.get_job(job_id)
        if job is None:
            return self.send_error_json(404, "Job not found")
        if job.status != "done":
            return self.send_error_json(400, "Compilation not complete")
        # QXNN resume jobs carry a .qxnn as model_path (no source ONNX), so the
        # ONNX-based summary parser cannot run. Guard here to return a clear 400
        # instead of a 500 from the ONNX parser choking on the .qxnn.
        if getattr(job, "mode", "compile") == "resume":
            return self.send_error_json(
                400, "Summary is not available for QXNN resume jobs (no source ONNX model)."
            )

        try:
            from dx_compiler.core.html_export import generate_summary_html
            # Pass a superset of params; html_export._filter_kwargs drops whatever the
            # installed dx_com doesn't accept. dx_com 2.4's generate_summary_html replaced
            # `enhanced_scheme` with `use_q_pro`/`calibration_method`, while 2.3 used
            # `enhanced_scheme` — sending both keeps the studio compatible with either.
            html = generate_summary_html(
                model_path=job.model_path,
                output_dir=job.output_dir,
                config_path=job.config_path,
                opt_level=job.opt_level,
                aggressive_partitioning=job.aggressive_partitioning,
                enhanced_scheme=job.enhanced_scheme,
                use_q_pro=job.use_q_pro,
                calibration_method=job.recalibration_method,
                cpu_reasons=job.last_cpu_reasons,
                preprocess_ops=_extract_preprocess_ops(job.log_buffer),
            )
        except Exception as e:
            return self.send_error_json(500, f"Failed to generate summary: {e}")

        filename = f"{_safe_download_stem(job.model_path)}_summary.html"
        body = html.encode("utf-8")
        self.send_bytes(body, "text/html; charset=utf-8", filename=filename)

    def _compile_dxnn(self, job_id):
        """Stream the compiled .dxnn artifact as a browser download.

        Only a finalized, job-owned canonical artifact is downloadable. The
        requested output directory remains a compatibility copy, never a source
        for this endpoint.
        """
        job = compiler_service.get_job(job_id)
        if job is None:
            return self.send_error_json(404, "Job not found")
        if job.status != "done" or not getattr(job, "artifact_ready", False):
            return self.send_error_json(400, "Compilation not complete")
        if not compiler_service.is_ready_artifact(job):
            return self.send_error_json(404, "No .dxnn artifact found for this job")
        dxnn_path = job.canonical_dxnn_path or job.dxnn_path
        try:
            body = Path(dxnn_path).read_bytes()
        except OSError as e:
            return self.send_error_json(500, f"Failed to read .dxnn: {e}")
        stem = _safe_download_stem(job.model_path or dxnn_path)
        self.send_bytes(body, "application/octet-stream", filename=f"{stem}.dxnn")

    def _sse_progress(self, job_id):
        """Stream compile progress via Server-Sent Events."""
        self.start_sse()
        try:
            job = compiler_service.get_job(job_id)
            if not job:
                self.send_sse("error", {"error": "Job not found"})
                return

            sent_phases = set()
            log_cursor = 0
            paused_emitted = False
            qxnn_emitted = False
            max_job_seconds = None

            while True:
                if job.status not in ("done", "error"):
                    if max_job_seconds is None:
                        try:
                            max_job_seconds = _compiler_max_job_seconds()
                        except ValueError as e:
                            job.mark_error(str(e))
                    if job.status not in ("done", "error"):
                        start_monotonic = getattr(job, "start_monotonic", None)
                        if start_monotonic is None:
                            start_monotonic = time.monotonic()
                            job.start_monotonic = start_monotonic
                        elapsed = time.monotonic() - start_monotonic
                        if elapsed > max_job_seconds:
                            # Actually terminate the running worker (and its children),
                            # not just report — otherwise the compile keeps running.
                            compiler_service.terminate_job(
                                job, f"Compile timed out after {max_job_seconds:g} seconds."
                            )

                if job.status == "done" or getattr(job, "diagnosis_report_path", None):
                    qxnn_payload = _qxnn_payload(job)
                else:
                    qxnn_payload = {
                        "available": False,
                        "diagnosis_report_available": False,
                        "quant_diagnosis_requested": bool(getattr(job, "quant_diagnosis", False)),
                    }

                progress_data = {
                    "status": job.status,
                    "progress": round(job.progress, 1),
                    "phase": job.current_phase,
                    "error": job.error,
                    "tqdm_sub": job.tqdm_sub,
                    "output_dir": job.output_dir,
                    "job_id": job.job_id,
                    "capabilities": getattr(job, "capabilities", {}),
                    "warnings": getattr(job, "warnings", []),
                    "qxnn": qxnn_payload,
                }

                # Emit new log lines
                if job.log_buffer:
                    new_lines = job.log_buffer.get_new_lines(log_cursor)
                    if new_lines:
                        log_cursor += len(new_lines)
                        if not self.send_sse("log", {"lines": new_lines}):
                            return

                # Emit in-memory graph data from PhaseEvent consumer
                with job.gui_graphs_lock:
                    ready = list(job.gui_graphs_ready)
                    job.gui_graphs_ready.clear()
                for phase_name in ready:
                    graph_data = job.gui_graphs.get(phase_name)
                    if graph_data:
                        if not self.send_sse("model_ready", {"phase": phase_name, "graph": graph_data}):
                            return
                        sent_phases.add(phase_name)

                if qxnn_payload["available"] and not qxnn_emitted:
                    qxnn_emitted = True
                    if not self.send_sse("qxnn_available", qxnn_payload):
                        return

                # Emit paused event when compilation is waiting for node selection
                if job.paused and not paused_emitted:
                    paused_emitted = True
                    if not self.send_sse("paused", {"phase": "PREPARE"}):
                        return
                elif not job.paused:
                    paused_emitted = False

                if job.status == "done":
                    if not getattr(job, "artifact_ready", False):
                        progress_data["status"] = "error"
                        progress_data["error"] = (
                            "Compilation completed without a finalized artifact."
                        )
                        self.send_sse("error", progress_data)
                        break
                    # Reuse PARTITION graph as the DXNN tab view
                    partition_graph = job.gui_graphs.get("PARTITION")
                    if partition_graph:
                        self.send_sse("model_ready", {"phase": "DXNN", "graph": partition_graph})
                    dxnn_path = job.dxnn_path
                    if dxnn_path:
                        progress_data["dxnn_path"] = Path(dxnn_path).name
                        progress_data["dxnn_download_url"] = f"/compile/{job.job_id}/dxnn"
                    if qxnn_payload["available"]:
                        progress_data["qxnn"] = qxnn_payload
                    self.send_sse("complete", progress_data)
                    break
                elif job.status == "error":
                    self.send_sse("error", progress_data)
                    break
                else:
                    if not self.send_sse("progress", progress_data):
                        return

                time.sleep(0.5)

        except (BrokenPipeError, ConnectionResetError):
            pass  # Client disconnected
        finally:
            self.end_sse()

    def _sse_setup(self, generator_fn):
        """Setup 작업의 SSE 스트리밍 (install-sdk, download-samples)"""
        self.start_sse()
        try:
            for event in generator_fn():
                event_type = event.get("type", "progress")
                self.send_sse(event_type, event)
                if event_type in ("complete", "error"):
                    break
        except Exception as e:
            self.send_sse("error", {"type": "error", "message": str(e)})
        finally:
            self.end_sse()

    def _list_dir(self):
        """GET /api/listdir?path= — list sub-directories for the folder picker."""
        req_path = self.query.get("path", [None])[0]
        try:
            return self.send_json(fs_browse.list_directory(req_path))
        except ValueError as exc:
            return self.send_error_json(400, str(exc))

    def _mkdir(self):
        """POST /api/mkdir {path, name} — create a sub-directory from the picker."""
        try:
            body = self.read_json_body()
        except RequestBodyError:
            raise
        except Exception:
            return self.send_error_json(400, "Invalid JSON")
        try:
            return self.send_json(
                fs_browse.make_directory(body.get("path", ""), body.get("name", ""))
            )
        except ValueError as exc:
            return self.send_error_json(400, str(exc))

    def _upload_file(self):
        """Handle file upload via multipart/form-data."""
        _fields, files = self.parse_multipart()
        if "file" not in files:
            return self.send_error_json(400, "No file provided")
        f = files["file"]
        if not f["filename"]:
            return self.send_error_json(400, "No file provided")
        safe_name = Path(f["filename"]).name
        suffixes = Path(safe_name).suffixes
        if not suffixes or any(suffix.lower() not in ALLOWED_UPLOAD_EXTENSIONS for suffix in suffixes):
            allowed = ", ".join(sorted(ALLOWED_UPLOAD_EXTENSIONS))
            return self.send_error_json(400, f"Unsupported upload file type. Allowed: {allowed}")
        dest = UPLOAD_DIR / safe_name
        dest.write_bytes(f["data"])
        self.send_json({"path": str(dest), "filename": safe_name})

    def _inspect_model(self, path):
        """Read ONNX model input shapes/types."""
        if not path:
            return self.send_error_json(400, "path parameter required")
        if not is_safe_path(path):
            return self.send_error_json(403, "Access denied")
        try:
            if not Path(path).is_file():
                return self.send_error_json(404, "File not found")
        except (PermissionError, OSError):
            return self.send_error_json(404, "File not found")

        try:
            import onnx
            model = onnx.load(path, load_external_data=False)
            inputs = {}
            all_static = True
            for inp in model.graph.input:
                name = inp.name
                shape = []
                is_dynamic = False
                try:
                    dims = inp.type.tensor_type.shape.dim
                except Exception:
                    dims = []
                for dim in dims:
                    if getattr(dim, "dim_param", None):
                        shape.append(-1)
                        is_dynamic = True
                    else:
                        try:
                            dv = int(dim.dim_value)
                            if dv <= 0:
                                shape.append(-1)
                                is_dynamic = True
                            else:
                                shape.append(dv)
                        except Exception:
                            shape.append(-1)
                            is_dynamic = True
                if not shape:
                    is_dynamic = True
                inputs[name] = {"shape": shape, "dynamic": is_dynamic}
                if is_dynamic:
                    all_static = False
            self.send_json({"auto_detected": all_static, "inputs": inputs})
        except Exception as e:
            self.send_error_json(400, str(e))

    def _config_generate(self):
        """Generate a temporary config JSON file from wizard data."""
        try:
            config_data = self.read_json_body()
        except RequestBodyError:
            raise
        except Exception:
            return self.send_error_json(400, "Invalid JSON")

        config = {"inputs": config_data.get("input_shapes", {})}

        if config_data.get("loader_mode") == "default":
            default_loader = {}
            if config_data.get("dataset_path"):
                default_loader["dataset_path"] = config_data["dataset_path"]
            if config_data.get("file_extensions"):
                default_loader["file_extensions"] = config_data["file_extensions"]
            if config_data.get("preprocessings"):
                default_loader["preprocessings"] = config_data["preprocessings"]
            config["default_loader"] = default_loader

        if config_data.get("calibration_num"):
            try:
                config["calibration_num"] = int(config_data["calibration_num"])
            except (ValueError, TypeError):
                return self.send_error_json(400, "Invalid calibration_num")
        if config_data.get("calibration_method"):
            config["calibration_method"] = config_data["calibration_method"]

        config_dir = UPLOAD_DIR / "configs"
        config_dir.mkdir(parents=True, exist_ok=True)
        filename = f"config_{uuid.uuid4().hex[:8]}.json"
        dest = config_dir / filename
        dest.write_text(json.dumps(config, indent=2))
        self.send_json({"path": str(dest), "config": config})

    def _agentic_session_dxnn(self, session_dir: str | None):
        """Return the newest *.dxnn path under an agentic session directory.

        Security: ``session_dir`` MUST resolve under
        ``<suite>/dx-compiler/dx-agent-dev/``.  Any other path is rejected
        with 403.
        """
        if not session_dir:
            return self.send_error_json(400, "dir parameter required")

        # Guard: resolve and verify the requested dir is under dx-agent-dev/
        _agent_dev_root = (SUITE_ROOT / "dx-compiler" / "dx-agent-dev").resolve()
        try:
            resolved = Path(session_dir).resolve()
        except (OSError, ValueError):
            return self.send_error_json(400, "Invalid directory path")

        # Must be under the dx-agent-dev root (or equal to it, though unlikely)
        try:
            resolved.relative_to(_agent_dev_root)
        except ValueError:
            return self.send_error_json(403, "Access denied: dir must be under dx-compiler/dx-agent-dev/")

        if not resolved.is_dir():
            return self.send_json({"ok": False, "dxnn_path": None,
                                   "error": "Session directory not found"})

        # Find the newest *.dxnn (excluding optimized_ckpt intermediates)
        dxnn_files = [
            p for p in resolved.glob("*.dxnn")
            if "optimized_ckpt" not in p.name
        ]
        if not dxnn_files:
            return self.send_json({"ok": False, "dxnn_path": None,
                                   "error": "No .dxnn file found in session directory"})

        newest = max(dxnn_files, key=lambda p: p.stat().st_mtime)
        return self.send_json({"ok": True, "dxnn_path": str(newest)})

    def _viewer_parse(self):
        """Parse a model file and return graph JSON for the viewer."""
        try:
            body = self.read_json_body()
        except RequestBodyError:
            raise
        except Exception:
            return self.send_error_json(400, "Invalid JSON")

        path = body.get("path", "").strip()
        if not path:
            return self.send_error_json(400, "Missing 'path' field")
        if not is_safe_path(path):
            return self.send_error_json(403, "Access denied")
        try:
            if not Path(path).is_file():
                return self.send_error_json(404, "File not found")
        except (PermissionError, OSError):
            return self.send_error_json(404, "File not found")

        try:
            # Lazy import: onnx_parser pulls in numpy + onnx (not stdlib, not declared deps).
            # Importing it here — not at module top — keeps the DX Compiler server bootable on a
            # stdlib-only / offline install; only this ONNX-graph endpoint degrades (→ 400) when
            # numpy/onnx are absent, instead of crashing the whole server at startup.
            from dx_compiler.core.onnx_parser import parse_onnx_model
            graph_data = parse_onnx_model(path)
            self.send_json(graph_data)
        except Exception as e:
            self.send_error_json(400, f"Parse error: {type(e).__name__}")


def create_server(port=DEFAULT_PORT):
    """테스트용 서버 팩토리: HTTPServer 인스턴스를 반환."""
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", port), CompilerHandler)
    srv.daemon_threads = True
    return srv


if __name__ == "__main__":
    DXServer(CompilerHandler, SERVER_NAME, DEFAULT_PORT).start()
