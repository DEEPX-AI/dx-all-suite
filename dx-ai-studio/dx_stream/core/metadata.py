"""Model metadata — a wrapper around dx_rt's parse_model.

Reads graph info, input/output tensors and compile options from a .dxnn file.
"""
import os
import subprocess
import json
import tempfile
from pathlib import Path
from shared.runtime import dx_rt_cli_python, dx_rt_cli_pythonpath


def get_model_metadata(model_path: str) -> dict:
    """Run parse_model and return the .dxnn metadata."""
    model_file = Path(model_path)
    if not model_file.is_file():
        return {"error": f"Model file not found: {model_path}"}

    python = dx_rt_cli_python()
    pythonpath = str(dx_rt_cli_pythonpath())

    metadata = {"raw_output": "", "graph_info": None, "rmap_info": []}

    try:
        # Text output for human-readable info
        cmd_text = [python, "-m", "cli.parse_model", "-m", str(model_file)]
        result_text = subprocess.run(
            cmd_text, capture_output=True, text=True, timeout=30,
            env={**os.environ, "PYTHONPATH": pythonpath}
        )
        metadata["raw_output"] = result_text.stdout + result_text.stderr
    except Exception as e:
        metadata["raw_output"] = f"[ERROR] {e}"

    try:
        # JSON extraction to temp dir
        with tempfile.TemporaryDirectory() as tmpdir:
            cmd_json = [python, "-m", "cli.parse_model", "-m", str(model_file), "-j"]
            subprocess.run(
                cmd_json, capture_output=True, text=True, timeout=30,
                cwd=tmpdir, env={**os.environ, "PYTHONPATH": pythonpath}
            )
            for json_file in Path(tmpdir).glob("*.json"):
                try:
                    data = json.loads(json_file.read_text())
                    if "graph_info" in json_file.name:
                        metadata["graph_info"] = data
                    elif "rmap_info" in json_file.name:
                        metadata["rmap_info"].append(data)
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass

    return metadata
