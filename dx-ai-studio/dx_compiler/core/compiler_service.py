import json
import logging
import os
import queue
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from shared.paths import var_dir
from dx_compiler.core.config import SCRIPT_DIR
from dx_compiler.core.log_capture import LogBuffer, LogCapture

_log = logging.getLogger(__name__)

_ANSI_RE = re.compile(r"\x1b\[[^a-zA-Z]*[a-zA-Z]")
_TQDM_RE = re.compile(
    r"\d+%\|"
    r"|\|\s*[\d.]+/[\d.]+\s*\["
    r"|[\d.]+(?:step|model|op|data|node|schedule|layer|it|connection)/s[\]\s,)]"
)
_TQDM_PARSE_RE = re.compile(r"^(.+?):\s*(\d+)%\|[^|]*\|\s*([\d.]+)/([\d.]+)")


def _phase_name(phase: Any) -> str:
    """Return a stable phase name from strings or enum-like labels."""
    if phase is None:
        return ""
    if isinstance(phase, str):
        return phase
    return getattr(phase, "name", str(phase))


NODE_SELECTION_UNSUPPORTED_KEY = "node_selection_unsupported_subprocess"
NODE_SELECTION_UNSUPPORTED_MESSAGE = (
    "Node selection is unavailable in subprocess compile mode. "
    "Compilation will continue without range selection."
)
DEFAULT_COMPLETED_JOB_TTL_SECONDS = 24 * 60 * 60
DEFAULT_COMPLETED_JOB_MAX_COUNT = 100
_COMPLETION_MARKER = ".completed"


@dataclass
class CompileJob:
    job_id: str
    status: str = "pending"
    progress: float = 0.0
    current_phase: str = ""
    error: Optional[str] = None
    output_dir: str = ""
    requested_output_dir: str = ""
    work_dir: str = ""
    model_path: str = ""
    dxnn_path: Optional[str] = None
    canonical_dxnn_path: Optional[str] = None
    artifact_ready: bool = False
    completed_at: Optional[float] = None
    start_time: float = field(default_factory=time.time)
    start_monotonic: float = field(default_factory=time.monotonic)
    log_buffer: Optional[LogBuffer] = field(default=None, repr=False)
    # Latest tqdm sub-task state: {label, percent, current, total} or None
    tqdm_sub: Optional[Dict[str, Any]] = field(default=None, repr=False)
    # In-memory graph data from GUI callback (phase_name -> graph_json_dict)
    gui_graphs: Dict[str, Any] = field(default_factory=dict)
    gui_graphs_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    gui_graphs_ready: List[str] = field(default_factory=list)
    # Compile Range Selection (compile-pause feature)
    node_selection_enabled: bool = False
    pause_event: threading.Event = field(default_factory=threading.Event, repr=False)
    paused: bool = False
    selected_input_nodes: List[str] = field(default_factory=list)
    selected_output_nodes: List[str] = field(default_factory=list)
    prepared_graph_ir: Any = field(default=None, repr=False)
    last_cpu_reasons: Optional[Dict[str, Any]] = field(default=None, repr=False)
    # QXNN quant debug metadata discovered from QUANTIZATION phase events
    qxnn_path: Optional[str] = None
    qxnn_work_path: Optional[str] = field(default=None, repr=False)
    qxnn_debug_graphs: List[str] = field(default_factory=list)
    qxnn_metadata: Dict[str, Any] = field(default_factory=dict)
    diagnosis_report_path: Optional[str] = None
    qxnn_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)
    # Subprocess compile tracking
    _total_phases: int = field(default=6, repr=False)
    _completed_phases: int = field(default=0, repr=False)

    # Compile options (stored for HTML summary)
    config_path: str = ""
    opt_level: int = 1
    aggressive_partitioning: bool = False
    quant_debug: bool = False
    quant_diagnosis: bool = False
    use_q_pro: bool = False
    enhanced_scheme: Optional[Dict] = field(default=None, repr=False)
    # QXNN resume (re-quantization) mode
    mode: str = "compile"  # "compile" | "resume"
    qxnn_checkpoint_path: str = ""
    recalibration_method: Optional[str] = None
    dataset_path: Optional[str] = None
    process: Any = field(default=None, repr=False)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    warnings: List[Dict[str, str]] = field(default_factory=list)
    status_lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def __post_init__(self) -> None:
        """Keep the legacy public output directory compatible with new job data."""
        if not self.requested_output_dir:
            self.requested_output_dir = self.output_dir
        elif not self.output_dir:
            self.output_dir = self.requested_output_dir

    def mark_error(self, error: str) -> bool:
        with self.status_lock:
            if self.status in ("done", "error"):
                return False
            self.status = "error"
            self.error = error
            return True

    def mark_running(self) -> bool:
        with self.status_lock:
            if self.status in ("done", "error"):
                return False
            self.status = "running"
            return True

    def mark_done(self) -> bool:
        with self.status_lock:
            if self.status == "error" or not self.artifact_ready:
                return False
            self.status = "done"
            self.progress = 100.0
            return True


class CompilerService:
    def __init__(self, job_root: Optional[Path] = None):
        self.jobs: Dict[str, CompileJob] = {}
        self._direct_compile_lock = threading.Lock()
        self.job_root = Path(job_root) if job_root is not None else var_dir("compiler", "jobs")
        self.job_root.mkdir(parents=True, exist_ok=True)
        self.job_root = self.job_root.resolve()
        self.cleanup_completed_jobs()

    def get_job(self, job_id: str) -> Optional[CompileJob]:
        return self.jobs.get(job_id)

    def _job_directory(self, job: CompileJob) -> Path:
        if Path(job.job_id).name != job.job_id:
            raise ValueError("Invalid compiler job ID")
        path = (self.job_root / job.job_id).resolve()
        try:
            path.relative_to(self.job_root)
        except ValueError as exc:
            raise ValueError("Invalid compiler job directory") from exc
        return path

    def _prepare_job_staging(
        self, job: CompileJob, requested_output_dir: Optional[str] = None
    ) -> bool:
        """Allocate this job's private compiler work directory."""
        requested = (
            job.requested_output_dir
            or job.output_dir
            or requested_output_dir
            or ""
        )
        if not requested:
            job.mark_error("Requested output directory is required")
            return False
        try:
            work_dir = self._job_directory(job) / "work"
            work_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, ValueError) as exc:
            job.mark_error(f"Failed to create compiler staging directory: {exc}")
            return False
        job.requested_output_dir = requested
        job.output_dir = requested
        job.work_dir = str(work_dir)
        return True

    @staticmethod
    def _is_final_dxnn(path: Path) -> bool:
        name = path.name.lower()
        return (
            path.is_file()
            and name.endswith(".dxnn")
            and "checkpoint" not in name
            and "optimized_ckpt" not in name
        )

    def _final_dxnn_candidates(self, job: CompileJob) -> List[Path]:
        if not job.work_dir:
            return []
        try:
            work_dir = Path(job.work_dir).resolve()
            expected_work_dir = self._job_directory(job) / "work"
            if work_dir != expected_work_dir:
                return []
            candidates = []
            for path in work_dir.glob("*.dxnn"):
                if not self._is_final_dxnn(path):
                    continue
                resolved = path.resolve()
                try:
                    resolved.relative_to(work_dir)
                except ValueError:
                    continue
                candidates.append(resolved)
            return candidates
        except (OSError, ValueError):
            return []

    def _write_completion_marker(self, job: CompileJob) -> bool:
        """Persist a conservative cleanup marker for an already-finalized job."""
        if job.completed_at is None:
            return False
        try:
            job_dir = self._job_directory(job)
            marker = job_dir / _COMPLETION_MARKER
            temporary = job_dir / f"{_COMPLETION_MARKER}.{uuid.uuid4().hex}.tmp"
            temporary.write_text(f"{job.completed_at:.6f}\n", encoding="ascii")
            os.replace(temporary, marker)
            return True
        except (OSError, ValueError) as exc:
            _log.warning("Failed to write completion marker for job %s: %s", job.job_id, exc)
            return False

    def _finalize_success(self, job: CompileJob) -> bool:
        """Publish exactly one staged DXNN before making a job externally complete."""
        with job.status_lock:
            if job.status in ("done", "error"):
                return False
            candidates = self._final_dxnn_candidates(job)
            if not candidates:
                job.status = "error"
                job.error = "Compilation produced a missing final DXNN artifact."
                return False
            if len(candidates) != 1:
                job.status = "error"
                job.error = "Compilation produced ambiguous final DXNN artifacts."
                return False

            canonical = candidates[0]
            requested_dir = Path(job.requested_output_dir)
            destination = requested_dir / canonical.name
            temporary = requested_dir / f".{canonical.name}.{uuid.uuid4().hex}.tmp"
            try:
                requested_dir.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(canonical, temporary)
                os.replace(temporary, destination)
            except OSError as exc:
                try:
                    temporary.unlink(missing_ok=True)
                except OSError as cleanup_exc:
                    _log.warning(
                        "Failed to clean temporary compiler artifact for job %s: %s",
                        job.job_id,
                        cleanup_exc,
                    )
                job.status = "error"
                job.error = f"Failed to publish compiler artifact: {exc}"
                return False

            job.canonical_dxnn_path = str(canonical)
            job.dxnn_path = job.canonical_dxnn_path
            job.artifact_ready = True
            job.completed_at = time.time()
            job.status = "done"
            job.progress = 100.0
            self._write_completion_marker(job)
            return True

    def is_ready_artifact(self, job: CompileJob) -> bool:
        """Return whether a job exposes an authorized canonical DXNN artifact."""
        if job.status != "done" or not job.artifact_ready:
            return False
        canonical_path = job.canonical_dxnn_path or job.dxnn_path
        if not canonical_path:
            return False
        try:
            canonical = Path(canonical_path).resolve()
            canonical.relative_to(self._job_directory(job))
            return self._is_final_dxnn(canonical)
        except (OSError, ValueError):
            return False

    def cleanup_completed_jobs(
        self,
        *,
        now: Optional[float] = None,
        ttl_seconds: int = DEFAULT_COMPLETED_JOB_TTL_SECONDS,
        max_count: int = DEFAULT_COMPLETED_JOB_MAX_COUNT,
    ) -> List[str]:
        """Conservatively delete only completed job-owned staging directories."""
        now = time.time() if now is None else now
        completed: List[Tuple[float, str, Path]] = []
        try:
            directories = list(self.job_root.iterdir())
        except OSError as exc:
            _log.warning("Unable to scan compiler job staging root: %s", exc)
            return []

        for directory in directories:
            marker = directory / _COMPLETION_MARKER
            if not directory.is_dir() or not marker.is_file():
                continue
            try:
                directory.resolve().relative_to(self.job_root)
                completed_at = float(marker.read_text(encoding="ascii").strip())
            except (OSError, ValueError):
                continue
            completed.append((completed_at, directory.name, directory))

        expired = [
            entry for entry in completed if now - entry[0] > ttl_seconds
        ]
        retained = sorted(
            (entry for entry in completed if entry not in expired),
            key=lambda entry: entry[0],
            reverse=True,
        )
        expired.extend(retained[max_count:])
        removed: List[str] = []
        for _completed_at, job_id, directory in expired:
            try:
                shutil.rmtree(directory)
            except OSError as exc:
                _log.warning("Failed to remove completed compiler job %s: %s", job_id, exc)
                continue
            self.jobs.pop(job_id, None)
            removed.append(job_id)
        return removed

    def _terminate_process(self, job: CompileJob) -> bool:
        """Terminate the compile worker process tracked on ``job.process``.

        The worker is launched with ``start_new_session=True`` so it becomes the
        leader of its own process group (pgid == pid). We signal that group so the
        worker *and any children it spawned* (e.g. dx_com sub-processes) are killed
        — a targeted kill by tracked pid, never a broad ``pkill``. Returns True if a
        live process was signalled.
        """
        proc = getattr(job, "process", None)
        if proc is None:
            return False
        try:
            if proc.poll() is not None:
                return False  # already exited
        except Exception:
            pass

        def _signal_group(sig) -> bool:
            try:
                os.killpg(os.getpgid(proc.pid), sig)
                return True
            except (ProcessLookupError, PermissionError, OSError, AttributeError):
                return False

        signalled = False
        try:
            if _signal_group(signal.SIGTERM):
                signalled = True
            else:
                proc.terminate()
                signalled = True
            try:
                proc.wait(timeout=5)
            except Exception:
                # Escalate to SIGKILL if it did not exit in time.
                if not _signal_group(signal.SIGKILL):
                    try:
                        proc.kill()
                    except Exception:
                        _log.warning("Failed to SIGKILL compile worker", exc_info=True)
        except Exception:
            _log.warning("Failed to terminate compile worker", exc_info=True)
        return signalled

    def terminate_job(self, job: CompileJob, message: str) -> bool:
        """Mark ``job`` errored with ``message`` and terminate its worker process.

        Shared by the SSE timeout branch and :meth:`cancel`. Returns True if the
        job status transitioned to error (i.e. it was still active).
        """
        marked = job.mark_error(message)
        self._terminate_process(job)
        return marked

    def cancel(self, job_id: str) -> bool:
        """Cancel a running compile: terminate its worker and mark it errored.

        Returns True if a known, still-active job was cancelled.
        """
        job = self.get_job(job_id)
        if job is None:
            return False
        return self.terminate_job(job, "Compile cancelled by user.")

    def _store_qxnn_metadata(self, job: CompileJob, metadata: Dict[str, Any]) -> None:
        qxnn_path = metadata.get("qxnn_path")
        if not qxnn_path:
            return
        debug_graphs = metadata.get("debug_graphs") or []
        if not isinstance(debug_graphs, (list, tuple)):
            debug_graphs = []
        stored_graphs = [str(name) for name in debug_graphs]
        debug_level_policy = metadata.get("debug_level_policy") or {}
        with job.qxnn_lock:
            job.qxnn_work_path = str(qxnn_path)
            job.qxnn_debug_graphs = stored_graphs
            job.qxnn_metadata = {
                "phase": "QUANTIZATION",
                "status": metadata.get("status"),
                "qxnn_filename": Path(qxnn_path).name,
                "debug_graphs": list(job.qxnn_debug_graphs),
                "debug_level_policy": debug_level_policy,
            }

    def _store_qxnn_artifact(self, job: CompileJob) -> None:
        with job.qxnn_lock:
            already_stored = bool(job.qxnn_path)
        if already_stored or not job.output_dir:
            return
        search_dirs = [
            Path(job.work_dir) / "quant_diagnosis",
            Path(job.work_dir) / "quant_debug",
        ]

        def _mtime(path: Path) -> float:
            try:
                return path.stat().st_mtime
            except OSError:
                return -1.0

        try:
            candidates = sorted(
                (
                    path
                    for search_dir in search_dirs
                    for path in search_dir.glob("*.qxnn")
                    if path.is_file()
                ),
                key=_mtime,
                reverse=True,
            )
        except OSError as exc:
            _log.warning("Failed to inspect staged QXNN artifacts for job %s: %s", job.job_id, exc)
            return
        with job.qxnn_lock:
            metadata_candidate = Path(job.qxnn_work_path) if job.qxnn_work_path else None
        if metadata_candidate is not None and metadata_candidate.is_file():
            candidates.insert(0, metadata_candidate)
        if not candidates:
            return
        selected = candidates[0]
        try:
            work_dir = Path(job.work_dir).resolve()
            selected = selected.resolve()
            relative = selected.relative_to(work_dir)
            target = Path(job.requested_output_dir) / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.parent / f".{target.name}.{uuid.uuid4().hex}.tmp"
            shutil.copyfile(selected, temporary)
            os.replace(temporary, target)
        except (OSError, ValueError) as exc:
            _log.warning("Failed to publish QXNN artifact for job %s: %s", job.job_id, exc)
            return
        with job.qxnn_lock:
            job.qxnn_path = str(target)

    def _store_diagnosis_report(self, job: CompileJob) -> None:
        if not job.work_dir:
            return
        report_path = Path(job.work_dir) / "quant_diagnosis" / "diagnosis_report.html"
        if not report_path.is_file():
            return
        with job.qxnn_lock:
            job.diagnosis_report_path = str(report_path)

    def _start_phase_event_consumer(
        self,
        job: CompileJob,
        event_queue,
        compile_finished: threading.Event,
        selection_done: Optional[threading.Event] = None,
        selection_result: Optional[Dict[str, Any]] = None,
    ) -> threading.Thread:
        """Start a thread that consumes compiler phase events."""

        def _consume_phase_events():
            completed_phases = 0
            total_phases = 1
            while True:
                try:
                    event = event_queue.get(timeout=0.5)
                except Exception:
                    if compile_finished.is_set():
                        break
                    continue
                try:
                    phase_name = _phase_name(getattr(event, "phase", ""))
                    metadata = getattr(event, "metadata", {}) or {}

                    if phase_name == "__init__":
                        total_phases = metadata.get("total_phases", 1)
                        continue

                    if phase_name == "QUANTIZATION" and metadata.get("qxnn_path"):
                        self._store_qxnn_metadata(job, metadata)

                    if metadata.get("status") == "completed":
                        completed_phases += 1
                        job.current_phase = phase_name
                        job.progress = (completed_phases / total_phases) * 100.0

                    if getattr(event, "model", None) is None:
                        continue

                    from dx_compiler.core.onnx_parser import parse_onnx_model

                    graph_data = parse_onnx_model(event.model)

                    if phase_name == "PREPARE" and job.node_selection_enabled:
                        job.prepared_graph_ir = metadata.get("ir_graph") or event.model
                        with job.gui_graphs_lock:
                            job.gui_graphs["prepared"] = graph_data
                            job.gui_graphs_ready.append("prepared")
                        job.paused = True
                        job.pause_event.wait()
                        job.paused = False
                        _log.info("Range selection — input: %s", job.selected_input_nodes)
                        _log.info("Range selection — output: %s", job.selected_output_nodes)
                        if selection_result is not None:
                            selection_result["input_nodes"] = job.selected_input_nodes or None
                            selection_result["output_nodes"] = job.selected_output_nodes or None
                        if selection_done is not None:
                            selection_done.set()
                    else:
                        cpu_reasons = metadata.get("cpu_reasons")
                        if cpu_reasons:
                            job.last_cpu_reasons = cpu_reasons
                            for sg in graph_data.get("subgraphs", []):
                                if sg["id"] in cpu_reasons:
                                    sg["cpu_reasons"] = cpu_reasons[sg["id"]]
                        with job.gui_graphs_lock:
                            job.gui_graphs[phase_name] = graph_data
                            job.gui_graphs_ready.append(phase_name)
                except Exception:
                    _log.warning(
                        "Failed to parse phase %s",
                        getattr(event, "phase", ""),
                        exc_info=True,
                    )

        consumer = threading.Thread(target=_consume_phase_events, daemon=True)
        consumer.start()
        return consumer

    def submit(
        self,
        model_path: str,
        config_path: str,
        output_dir: str,
        opt_level: int = 1,
        aggressive_partitioning: bool = False,
        gen_log: bool = False,
        quant_debug: bool = False,
        quant_diagnosis: bool = False,
        enhanced_scheme: Optional[Dict] = None,
        node_selection: bool = False,
        use_q_pro: bool = False,
    ) -> CompileJob:
        self.cleanup_completed_jobs()
        job_id = str(uuid.uuid4())
        job = CompileJob(
            job_id=job_id,
            output_dir=output_dir,
            requested_output_dir=output_dir,
            model_path=model_path,
        )
        job.capabilities["node_selection"] = True
        job.node_selection_enabled = node_selection
        job.config_path = config_path
        job.opt_level = opt_level
        job.aggressive_partitioning = aggressive_partitioning
        job.quant_debug = quant_debug
        job.quant_diagnosis = quant_diagnosis
        job.use_q_pro = use_q_pro
        job.enhanced_scheme = enhanced_scheme
        self.jobs[job_id] = job
        if not self._prepare_job_staging(job):
            return job

        thread = threading.Thread(
            target=self._run_compile,
            args=(
                job,
                model_path,
                config_path,
                output_dir,
                opt_level,
                aggressive_partitioning,
                gen_log,
                quant_debug,
                quant_diagnosis,
                None,
                None,
                enhanced_scheme,
                use_q_pro,
            ),
            daemon=True,
        )
        thread.start()
        return job

    def submit_resume(
        self,
        qxnn_path: str,
        output_dir: str,
        recalibration_method: Optional[str] = None,
        enhanced_scheme: Optional[Dict] = None,
        use_q_pro: bool = False,
        dataset_path: Optional[str] = None,
    ) -> CompileJob:
        """Submit a QXNN resume (re-quantization) job."""
        self.cleanup_completed_jobs()
        job_id = str(uuid.uuid4())
        job = CompileJob(
            job_id=job_id,
            output_dir=output_dir,
            requested_output_dir=output_dir,
            model_path=qxnn_path,
        )
        job.mode = "resume"
        job.qxnn_checkpoint_path = qxnn_path
        job.recalibration_method = recalibration_method
        job.dataset_path = dataset_path
        job.use_q_pro = use_q_pro
        job.enhanced_scheme = enhanced_scheme
        self.jobs[job_id] = job
        if not self._prepare_job_staging(job):
            return job

        thread = threading.Thread(
            target=self._run_resume,
            args=(
                job,
                qxnn_path,
                output_dir,
                recalibration_method,
                enhanced_scheme,
                use_q_pro,
                dataset_path,
            ),
            daemon=True,
        )
        thread.start()
        return job

    def _run_compile(
        self,
        job: CompileJob,
        model_path: str,
        config_path: str,
        output_dir: str,
        opt_level: int,
        aggressive_partitioning: bool,
        gen_log: bool,
        quant_debug: bool,
        quant_diagnosis: bool,
        input_nodes,
        output_nodes,
        enhanced_scheme=None,
        use_q_pro: bool = False,
    ):
        if not self._prepare_job_staging(job, output_dir):
            return
        if not job.mark_running():
            return
        self._run_compile_locked(
            job,
            model_path,
            config_path,
            job.work_dir,
            opt_level,
            aggressive_partitioning,
            gen_log,
            quant_debug,
            quant_diagnosis,
            input_nodes,
            output_nodes,
            enhanced_scheme,
            use_q_pro,
        )

    def _run_compile_locked(
        self,
        job: CompileJob,
        model_path: str,
        config_path: str,
        output_dir: str,
        opt_level: int,
        aggressive_partitioning: bool,
        gen_log: bool,
        quant_debug: bool,
        quant_diagnosis: bool,
        input_nodes,
        output_nodes,
        enhanced_scheme,
        use_q_pro: bool,
    ):

        # venv에만 dx_com이 있는 경우 → subprocess 방식
        from dx_compiler.core.setup_service import setup_service
        venv_python = setup_service.get_venv_python()
        if venv_python and not self._is_dx_com_available():
            job.capabilities["node_selection"] = False
            if job.node_selection_enabled:
                log_buf = LogBuffer()
                job.log_buffer = log_buf
                log_buf.append("WARNING: Node selection is not supported in subprocess compile mode. Proceeding without it.")
                job.warnings.append({
                    "key": NODE_SELECTION_UNSUPPORTED_KEY,
                    "message": NODE_SELECTION_UNSUPPORTED_MESSAGE,
                })
                job.node_selection_enabled = False
            return self._run_compile_subprocess(
                job, venv_python, model_path, config_path, output_dir,
                opt_level, aggressive_partitioning, gen_log,
                quant_debug, quant_diagnosis, enhanced_scheme, use_q_pro,
                input_nodes, output_nodes,
            )

        from dx_compiler.core.compiler_bridge import mask_compile_error, run_compile

        # stdout/stderr are process-global; retain exclusive ownership until the
        # in-process compiler and the capture cleanup have both completed.
        with self._direct_compile_lock:
            # Capture stdout/stderr into shared buffer for log streaming.
            # stderr uses CR-aware mode to collapse tqdm progress bar updates.
            log_buf = LogBuffer()
            stdout_cap = LogCapture(sys.stdout, log_buf)
            stderr_cap = LogCapture(sys.stderr, log_buf, handle_cr=True, job=job)
            job.log_buffer = log_buf
            old_stdout, old_stderr = sys.stdout, sys.stderr
            sys.stdout = stdout_cap
            sys.stderr = stderr_cap

            # Phase output: dx_com populates events at phase boundaries.
            # A consumer thread reads events and stores parsed graphs for the viewer.
            event_queue = queue.Queue()
            selection_done = threading.Event()
            selection_result = {}
            compile_finished = threading.Event()
            consumer = None
            compile_succeeded = False
            try:
                consumer = self._start_phase_event_consumer(
                    job,
                    event_queue,
                    compile_finished,
                    selection_done=selection_done,
                    selection_result=selection_result,
                )
                run_compile(
                    model=model_path,
                    config=config_path,
                    output_dir=output_dir,
                    opt_level=opt_level,
                    aggressive_partitioning=aggressive_partitioning,
                    gen_log=gen_log,
                    quant_debug=quant_debug,
                    quant_diagnosis=quant_diagnosis,
                    input_nodes=input_nodes,
                    output_nodes=output_nodes,
                    enhanced_scheme=enhanced_scheme,
                    use_q_pro=use_q_pro,
                    event_queue=event_queue,
                    pause_for_selection=job.node_selection_enabled,
                    selection_done=selection_done,
                    selection_result=selection_result,
                )
                compile_succeeded = True
            except Exception as e:
                job.mark_error(mask_compile_error(e))
            finally:
                compile_finished.set()
                if consumer is not None:
                    consumer.join(timeout=5)
                if compile_succeeded and self._finalize_success(job):
                    self._store_qxnn_artifact(job)
                    self._store_diagnosis_report(job)
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                stderr_cap.flush_pending()
                job.tqdm_sub = None

    def _is_dx_com_available(self) -> bool:
        """현재 프로세스에서 dx_com을 import할 수 있는지 확인"""
        try:
            import importlib.util
            return importlib.util.find_spec("dx_com") is not None
        except Exception:
            return False

    def _run_compile_subprocess(self, job, venv_python, model_path, config_path, output_dir,
                                 opt_level, aggressive_partitioning, gen_log,
                                 quant_debug, quant_diagnosis, enhanced_scheme, use_q_pro,
                                 input_nodes=None, output_nodes=None):
        """venv Python의 compile_worker.py를 subprocess로 실행."""
        if not self._prepare_job_staging(job, output_dir):
            return
        output_dir = job.work_dir
        if not job.log_buffer:
            job.log_buffer = LogBuffer()
        job._completed_phases = 0

        worker_path = SCRIPT_DIR / "core" / "compile_worker.py"
        params = {
            "model": model_path,
            "config": config_path,
            "output_dir": output_dir,
            "opt_level": opt_level,
            "aggressive_partitioning": aggressive_partitioning,
            "gen_log": gen_log,
            "quant_debug": quant_debug,
            "quant_diagnosis": quant_diagnosis,
            "use_q_pro": use_q_pro,
            "enhanced_scheme": enhanced_scheme,
            "input_nodes": input_nodes,
            "output_nodes": output_nodes,
        }

        compile_succeeded = False
        try:
            # stderr → STDOUT: the worker (and dx_com) can emit large volumes on stderr
            # (tqdm progress bars, warnings). A separate stderr PIPE that is only drained
            # after proc.wait() deadlocks once the ~64KB pipe buffer fills — the child
            # blocks writing stderr, stops writing stdout, and this loop hangs forever.
            # Merging into stdout means the single reader below drains everything (F-02).
            # start_new_session=True → the worker leads its own process group so a
            # timeout/cancel can kill the worker *and* its children via os.killpg
            # (targeted by the tracked pid, never a broad pkill).
            proc = subprocess.Popen(
                [str(venv_python), str(worker_path)],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, cwd=str(SCRIPT_DIR), start_new_session=True,
            )
            job.process = proc
            proc.stdin.write(json.dumps(params))
            proc.stdin.close()

            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    job.log_buffer.append(line)
                    continue

                event_type = event.get("type", "")
                phase = event.get("phase", "")

                if event_type == "error":
                    job.mark_error(event.get("message", "Unknown error"))
                    return
                if event_type == "done":
                    compile_succeeded = True
                    break

                meta = event.get("metadata", {})
                if phase == "QUANTIZATION" and meta.get("qxnn_path"):
                    self._store_qxnn_metadata(job, meta)
                if phase == "__init__":
                    job._total_phases = meta.get("total_phases", 6)
                elif meta.get("status") == "completed":
                    job._completed_phases += 1
                    job.progress = min(99.0, (job._completed_phases / job._total_phases) * 100)
                    job.current_phase = phase

            proc.wait()
            if proc.returncode != 0:
                # stderr is merged into stdout and already captured in log_buffer; surface
                # its tail (proc.stderr is None under stderr=STDOUT).
                tail = "\n".join(job.log_buffer[-20:]) if getattr(job, "log_buffer", None) else ""
                job.mark_error(tail or f"Worker exited with code {proc.returncode}")
            elif job.status != "error":
                compile_succeeded = True

        except Exception as e:
            job.mark_error(str(e))
        finally:
            job.process = None
            if compile_succeeded and self._finalize_success(job):
                self._store_qxnn_artifact(job)
                self._store_diagnosis_report(job)

    _RESUME_MARKERS = (
        ("QXNN resume: loading", 10.0, "LOADING"),
        ("re-quantization complete", 30.0, "RE-QUANTIZED"),
        ("finalize_quant + IR conversion complete", 35.0, "IR CONVERSION"),
        ("executing phases", 45.0, "OPTIMIZE"),
    )
    _RESUME_PCT_RE = re.compile(r"Compiling Model\s*:\s*([\d.]+)%")

    def _run_resume(
        self,
        job: CompileJob,
        qxnn_path: str,
        output_dir: str,
        recalibration_method: Optional[str],
        enhanced_scheme: Optional[Dict],
        use_q_pro: bool,
        dataset_path: Optional[str],
    ):
        if not self._prepare_job_staging(job, output_dir):
            return
        if not job.mark_running():
            return
        self._run_resume_locked(
            job,
            qxnn_path,
            job.work_dir,
            recalibration_method,
            enhanced_scheme,
            use_q_pro,
            dataset_path,
        )

    def _run_resume_locked(
        self,
        job: CompileJob,
        qxnn_path: str,
        output_dir: str,
        recalibration_method: Optional[str],
        enhanced_scheme: Optional[Dict],
        use_q_pro: bool,
        dataset_path: Optional[str],
    ):
        """Run a QXNN resume re-quantization in a fresh subprocess."""
        job.current_phase = "RESUME"
        job.progress = 5.0

        log_buf = LogBuffer()
        job.log_buffer = log_buf

        opts: Dict[str, Any] = {}
        if recalibration_method:
            opts["recalibration_method"] = recalibration_method
        if dataset_path:
            opts["dataset_path"] = dataset_path
        if use_q_pro:
            opts["use_q_pro"] = True
        elif enhanced_scheme:
            opts["enhanced_scheme"] = enhanced_scheme

        payload = json.dumps(
            {"checkpoint": qxnn_path, "output_dir": output_dir, "kwargs": opts}
        )
        runner = (
            "import os, json, dx_com;"
            "a = json.loads(os.environ['DX_COMPILER_RESUME_ARGS']);"
            "dx_com.compile(checkpoint=a['checkpoint'], output_dir=a['output_dir'], **a['kwargs'])"
        )
        env = dict(os.environ)
        env["DX_COMPILER_RESUME_ARGS"] = payload

        from dx_compiler.core.setup_service import setup_service
        venv_python = setup_service.get_venv_python()
        python_exe = str(venv_python) if venv_python else sys.executable

        resume_succeeded = False
        try:
            proc = subprocess.Popen(
                [python_exe, "-c", runner],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                env=env,
                text=True,
                bufsize=1,
                start_new_session=True,
            )
            job.process = proc
            self._consume_subprocess_output(job, proc, log_buf)
            returncode = proc.wait()
            resume_succeeded = returncode == 0
            if not resume_succeeded:
                job.mark_error(self._extract_resume_error(log_buf, returncode))
        except Exception as e:
            job.mark_error(f"Failed to launch resume subprocess: {e}")
        finally:
            job.process = None
            if resume_succeeded:
                if self._finalize_success(job):
                    job.current_phase = "DONE"
                    self._store_qxnn_artifact(job)
                    self._store_diagnosis_report(job)
            job.tqdm_sub = None

    def _consume_subprocess_output(self, job: CompileJob, proc, log_buf: LogBuffer) -> None:
        if proc.stdout is None:
            return
        buf = ""
        while True:
            ch = proc.stdout.read(1)
            if ch == "":
                break
            if ch in ("\n", "\r"):
                if buf:
                    self._handle_resume_line(job, buf, log_buf)
                buf = ""
            else:
                buf += ch
        if buf:
            self._handle_resume_line(job, buf, log_buf)

    def _handle_resume_line(self, job: CompileJob, raw: str, log_buf: LogBuffer) -> None:
        line = _ANSI_RE.sub("", raw).rstrip()
        if not line:
            return
        for marker, pct, phase in self._RESUME_MARKERS:
            if marker in line:
                job.progress = max(job.progress, pct)
                job.current_phase = phase
                break
        m = self._RESUME_PCT_RE.search(line)
        if m:
            try:
                pct = float(m.group(1))
                job.progress = max(job.progress, min(99.0, 45.0 + pct * 0.54))
            except ValueError:
                pass
        sub = _TQDM_PARSE_RE.match(line)
        if sub:
            job.tqdm_sub = {
                "label": sub.group(1).strip(),
                "percent": float(sub.group(2)),
                "current": sub.group(3),
                "total": sub.group(4),
            }
        if not _TQDM_RE.search(line):
            log_buf.append(line)

    @staticmethod
    def _extract_resume_error(log_buf: LogBuffer, returncode: int) -> str:
        lines = log_buf.get_new_lines(0)
        for line in reversed(lines):
            stripped = line.strip()
            if not stripped or set(stripped) == {"="}:
                continue
            if (
                "Error" in stripped
                or "Exception" in stripped
                or "contact DEEPX" in stripped
            ):
                return f"Resume failed (exit {returncode}): {stripped}"
        return f"Resume failed (exit {returncode})."
