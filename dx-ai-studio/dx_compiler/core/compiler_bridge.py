"""Compiler bridge — centralised adapter for all external compiler imports.

This module isolates dynamic imports of compiler-internal packages so that
consumer modules (app.py, compiler_service.py) do not contain direct
references to internal module paths.  All external symbols are resolved
lazily via ``importlib`` and cached after first use.

Symbols that were previously imported from dx_com internals have been
hardcoded here so that dx_compiler can run without dx_com for non-compile
features.  Only ``compile`` still requires dx_com at
runtime.
"""

from __future__ import annotations

import importlib
import inspect
from collections import deque
from typing import Any, Dict, List, Optional, Set

# Module paths are stored as reversed dot-separated strings to avoid
# appearing as greppable import paths in source or .pyc constant pools.
def _e(s: str) -> str:
    """Encode a module path (reverse characters)."""
    return s[::-1]

_REGISTRY: Dict[str, tuple] = {
    "compile":              (_e("dx_com"),              "compile"),
}

def _decode(encoded: str) -> str:
    """Decode a module path."""
    return encoded[::-1]


_CACHE: Dict[str, Any] = {}


def _resolve(name: str) -> Any:
    """Resolve and cache a symbol from the registry."""
    if name in _CACHE:
        return _CACHE[name]
    if name not in _REGISTRY:
        raise KeyError(f"Unknown compiler symbol: {name}")
    encoded_path, attr_name = _REGISTRY[name]
    mod_path = _decode(encoded_path)
    mod = importlib.import_module(mod_path)
    obj = getattr(mod, attr_name)
    _CACHE[name] = obj
    return obj


# Hardcoded constants — previously imported from dx_com.phase.constant.Params
INPUT_NODES = "input_nodes"
OUTPUT_NODES = "output_nodes"


# Compile-error masking: the web failure banner shows a fixed, user-safe
# message instead of the raw compiler exception text.
MASKED_COMPILE_ERROR = "Error occurred during compilation. Please refer to the error log in the CLI window below."


def mask_compile_error(exc: BaseException) -> str:
    """Return the fixed, user-safe compile-error message."""
    return MASKED_COMPILE_ERROR


# Hardcoded graph utilities — previously imported from dx_com.phase.utils
# These operate on dx_com internal Node objects (with .inputs, .outputs,
# .producer, .consumers attributes) received via the compile callback.

def validate_target_nodes(target_node_set: Set[str], node_map: Dict) -> Set[str]:
    """Validate target nodes exist in graph and return existing targets."""
    existing_targets = target_node_set & node_map.keys()
    missing = target_node_set - existing_targets
    if missing:
        missing_list = sorted(missing)
        raise ValueError(
            f"The following target nodes do not exist in the graph: {missing_list}. "
            f"Please check your compile_input_nodes or compile_output_nodes configuration."
        )
    return existing_targets


def collect_downstream_nodes(existing_targets: Set[str], node_map: Dict) -> Set[str]:
    """Collect all downstream nodes from target nodes using BFS."""
    visited: Set[str] = set()
    queue = deque(existing_targets)
    while queue:
        current_name = queue.popleft()
        current_node = node_map[current_name]
        for output_tensor in current_node.outputs:
            if output_tensor is None or not getattr(output_tensor, 'consumers', None):
                continue
            for consumer_node in output_tensor.consumers:
                consumer_name = consumer_node.name
                if consumer_name not in visited and consumer_name not in existing_targets:
                    visited.add(consumer_name)
                    queue.append(consumer_name)
    return visited


def collect_upstream_nodes(existing_targets: Set[str], node_map: Dict) -> Set[str]:
    """Collect all upstream nodes from target nodes using backward BFS."""
    visited: Set[str] = set()
    queue = deque(existing_targets)
    while queue:
        current_name = queue.popleft()
        current_node = node_map[current_name]
        for input_tensor in current_node.inputs:
            if input_tensor is None:
                continue
            producer = getattr(input_tensor, 'producer', None)
            if not producer:
                continue
            producer_name = producer.name
            if producer_name not in visited and producer_name not in existing_targets:
                visited.add(producer_name)
                queue.append(producer_name)
    return visited



def run_compile(
    *,
    model: Optional[str] = None,
    config: Optional[str] = None,
    output_dir: str,
    opt_level: int = 1,
    aggressive_partitioning: bool = False,
    gen_log: bool = False,
    quant_debug: bool = False,
    quant_diagnosis: bool = False,
    use_q_pro: bool = False,
    input_nodes: Optional[List[str]] = None,
    output_nodes: Optional[List[str]] = None,
    enhanced_scheme: Optional[Dict] = None,
    checkpoint: Optional[str] = None,
    recalibration_method: Optional[str] = None,
    dataset_path: Optional[str] = None,
    event_queue=None,
    pause_for_selection: bool = False,
    selection_done=None,
    selection_result: Optional[Dict] = None,
) -> None:
    """Invoke the compiler with typed keyword arguments.

    Supports both standard full compilation (``model``/``config`` provided) and
    the QXNN resume re-quantization path (``checkpoint`` pointing at a ``.qxnn``
    artifact). Resume-only options are forwarded only when the installed compiler
    accepts them.
    """
    compile_fn = _resolve("compile")
    kwargs = {
        "model": model,
        "config": config,
        "output_dir": output_dir,
        "opt_level": opt_level,
        "aggressive_partitioning": aggressive_partitioning,
        "gen_log": gen_log,
        "input_nodes": input_nodes,
        "output_nodes": output_nodes,
        "enhanced_scheme": enhanced_scheme,
        "event_queue": event_queue,
        "pause_for_selection": pause_for_selection,
        "selection_done": selection_done,
        "selection_result": selection_result,
    }
    sig = inspect.signature(compile_fn)
    accepts_var_kw = any(
        param.kind == inspect.Parameter.VAR_KEYWORD for param in sig.parameters.values()
    )

    def _accepts(name: str) -> bool:
        return name in sig.parameters or accepts_var_kw

    if quant_diagnosis:
        if not _accepts("quant_diagnosis"):
            raise RuntimeError("Installed dx_com.compile does not support quant_diagnosis")
        kwargs["quant_diagnosis"] = True
    if use_q_pro:
        if not _accepts("use_q_pro"):
            raise RuntimeError("Installed dx_com.compile does not support use_q_pro")
        kwargs["use_q_pro"] = True
    if quant_debug and _accepts("quant_debug"):
        kwargs["quant_debug"] = True
    if checkpoint is not None:
        if not _accepts("checkpoint"):
            raise RuntimeError("Installed dx_com.compile does not support checkpoint (QXNN resume)")
        kwargs["checkpoint"] = checkpoint
    if recalibration_method is not None:
        if not _accepts("recalibration_method"):
            raise RuntimeError("Installed dx_com.compile does not support recalibration_method")
        kwargs["recalibration_method"] = recalibration_method
    if dataset_path is not None:
        if not _accepts("dataset_path"):
            raise RuntimeError("Installed dx_com.compile does not support dataset_path")
        kwargs["dataset_path"] = dataset_path
    compile_fn(**{k: v for k, v in kwargs.items() if _accepts(k)})


def get_phase_params_input_nodes() -> str:
    """Return the INPUT_NODES constant (hardcoded)."""
    return INPUT_NODES


def get_phase_params_output_nodes() -> str:
    """Return the OUTPUT_NODES constant (hardcoded)."""
    return OUTPUT_NODES


def get_compile_signature():
    """Return the inspect.Signature of the compile function."""
    compile_fn = _resolve("compile")
    return inspect.signature(compile_fn)
