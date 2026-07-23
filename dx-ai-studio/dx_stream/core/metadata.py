"""모델 메타데이터 추출 — dx_rt의 parse_model 래퍼.

.dxnn 모델 파일에서 그래프 정보, 입출력 텐서, 컴파일 옵션 등을 추출한다.
"""
import os
import subprocess
import json
import tempfile
from pathlib import Path
from shared.runtime import dx_rt_cli_python, dx_rt_cli_pythonpath


def get_model_metadata(model_path: str) -> dict:
    """parse_model을 호출하여 .dxnn 메타데이터 추출."""
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
