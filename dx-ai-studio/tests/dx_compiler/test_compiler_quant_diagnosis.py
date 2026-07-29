"""Tests for quant diagnosis and QXNN resume compiler features."""

import inspect
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _reset_imports():
    for name in list(sys.modules):
        if name == "dx_compiler" or name.startswith("dx_compiler."):
            del sys.modules[name]
    root_str = str(ROOT)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


def test_run_compile_forwards_quant_diagnosis_when_compiler_accepts(monkeypatch):
    """quant_diagnosis is forwarded only when dx_com.compile accepts the kwarg."""
    _reset_imports()
    from dx_compiler.core import compiler_bridge

    captured = {}

    def fake_compile(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(compiler_bridge, "_resolve", lambda _name: fake_compile)

    compiler_bridge.run_compile(
        model="m.onnx",
        config="c.json",
        output_dir="/tmp/out",
        quant_diagnosis=True,
    )
    assert captured.get("quant_diagnosis") is True
    assert "use_q_pro" not in captured


def test_run_compile_raises_when_quant_diagnosis_unsupported(monkeypatch):
    """Unsupported quant_diagnosis must fail fast with a clear runtime error."""
    _reset_imports()
    from dx_compiler.core import compiler_bridge

    def fake_compile(**kwargs):
        return None

    fake_compile.__signature__ = inspect.Signature(
        parameters=[
            inspect.Parameter("model", inspect.Parameter.KEYWORD_ONLY, default=None),
            inspect.Parameter("output_dir", inspect.Parameter.KEYWORD_ONLY),
        ]
    )
    monkeypatch.setattr(compiler_bridge, "_resolve", lambda _name: fake_compile)

    with pytest.raises(RuntimeError, match="quant_diagnosis"):
        compiler_bridge.run_compile(
            model="m.onnx",
            config="c.json",
            output_dir="/tmp/out",
            quant_diagnosis=True,
        )


def test_run_compile_forwards_use_q_pro_when_compiler_accepts(monkeypatch):
    _reset_imports()
    from dx_compiler.core import compiler_bridge

    captured = {}

    def fake_compile(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(compiler_bridge, "_resolve", lambda _name: fake_compile)

    compiler_bridge.run_compile(
        model="m.onnx",
        config="c.json",
        output_dir="/tmp/out",
        use_q_pro=True,
    )
    assert captured.get("use_q_pro") is True


def test_run_compile_raises_when_enhanced_scheme_unsupported(monkeypatch):
    _reset_imports()
    from dx_compiler.core import compiler_bridge

    def fake_compile(*, model=None, config=None, output_dir=None):
        return None

    monkeypatch.setattr(compiler_bridge, "_resolve", lambda _name: fake_compile)

    with pytest.raises(RuntimeError, match="enhanced_scheme"):
        compiler_bridge.run_compile(
            model="m.onnx",
            config="c.json",
            output_dir="/tmp/out",
            enhanced_scheme={"DXQ-P0": {}},
        )


def test_mask_compile_error_returns_fixed_message():
    _reset_imports()
    from dx_compiler.core.compiler_bridge import MASKED_COMPILE_ERROR, mask_compile_error

    assert mask_compile_error(RuntimeError("internal stack trace")) == MASKED_COMPILE_ERROR


def test_server_registers_quant_diagnosis_routes():
    source = (ROOT / "dx_compiler" / "server.py").read_text(encoding="utf-8")
    assert 'path == "/compile/resume"' in source
    assert "_compile_qxnn_resume" in source
    assert 'path.endswith("/quant-diagnosis/report")' in source
    assert "_quant_diagnosis_report" in source
    assert "_qxnn_payload" in source
    assert 'self.send_sse("qxnn_available"' in source


def test_server_qxnn_resume_route_precedes_node_selection_resume():
    """POST /compile/resume must not be captured by /compile/{id}/resume."""
    source = (ROOT / "dx_compiler" / "server.py").read_text(encoding="utf-8")
    resume_idx = source.index('path == "/compile/resume"')
    node_resume_idx = source.index('path.startswith("/compile/") and path.endswith("/resume")')
    assert resume_idx < node_resume_idx


def test_compile_job_has_qxnn_fields():
    _reset_imports()
    from dx_compiler.core.compiler_service import CompileJob

    job = CompileJob(job_id="qxnn-fields")
    assert hasattr(job, "quant_diagnosis")
    assert hasattr(job, "use_q_pro")
    assert hasattr(job, "qxnn_path")
    assert hasattr(job, "diagnosis_report_path")
    assert job.mode == "compile"


def test_compiler_service_has_submit_resume():
    _reset_imports()
    from dx_compiler.core.compiler_service import CompilerService

    assert hasattr(CompilerService, "submit_resume")
    assert hasattr(CompilerService, "_run_resume")


def test_finalize_success_records_diagnosis_before_status_done(tmp_path):
    """Regression: the diagnosis report must be recorded BEFORE status flips to "done".

    The /progress SSE loop emits the terminal `complete` event (carrying the quant
    payload) the instant it polls job.status == "done", then stops polling. When the
    artifact stores ran *after* _finalize_success set status="done", a poll landing in
    that window shipped `complete` with the report still unrecorded — so a
    diagnosis_report.html that genuinely exists on disk was surfaced as "not generated".
    _finalize_success must therefore leave diagnosis_report_path set by the time it
    returns True (i.e. before the status write that the SSE loop keys off).
    """
    _reset_imports()
    import time

    from dx_compiler.core.compiler_service import CompileJob, CompilerService

    svc = CompilerService(job_root=tmp_path / "jobs")
    job = CompileJob(job_id="diag-order")
    job.requested_output_dir = str(tmp_path / "out")
    job.output_dir = job.requested_output_dir
    job.quant_diagnosis = True
    job.start_time = time.time() - 1.0

    # Stage a fresh final .dxnn + the diagnosis report exactly where dx_com writes them.
    work_dir = svc._job_directory(job) / "work"
    (work_dir / "quant_diagnosis").mkdir(parents=True, exist_ok=True)
    (work_dir / "model.dxnn").write_bytes(b"DXNN")
    report = work_dir / "quant_diagnosis" / "diagnosis_report.html"
    report.write_text("<html>diag</html>", encoding="utf-8")
    job.work_dir = str(work_dir)

    assert svc._finalize_success(job) is True
    assert job.status == "done"
    # The report path is recorded and points at the on-disk report.
    assert job.diagnosis_report_path == str(report)


def test_run_compile_signature_includes_checkpoint_for_qxnn_resume():
    _reset_imports()
    from dx_compiler.core.compiler_bridge import run_compile

    sig = inspect.signature(run_compile)
    assert "checkpoint" in sig.parameters
    assert "recalibration_method" in sig.parameters
    assert "dataset_path" in sig.parameters
    assert "quant_diagnosis" in sig.parameters
    assert "use_q_pro" in sig.parameters
