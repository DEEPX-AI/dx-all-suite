import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GETTING_STARTED_DIR = REPO_ROOT / "getting-started"
VERBOSE_OUTPUT = os.getenv("DX_TEST_VERBOSE", "0").lower() in {"1", "true", "yes", "y"}
DEFAULT_TIMEOUT = int(os.getenv("DX_TEST_GETTING_STARTED_TIMEOUT", "3600"))


def run_script(script_name: str, extra_env: dict | None = None, timeout: int | None = None) -> None:
    script_path = GETTING_STARTED_DIR / script_name
    if not script_path.exists():
        pytest.fail(f"Script not found: {script_path}")

    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    cmd = ["bash", str(script_path)]
    cwd = str(GETTING_STARTED_DIR)
    use_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT

    if VERBOSE_OUTPUT:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            cwd=cwd,
            env=env,
        )
        output_lines = []
        for line in process.stdout:
            print(line, end="", file=sys.stdout, flush=True)
            print(line, end="", file=sys.stderr, flush=True)
            output_lines.append(line.rstrip())
        process.wait(timeout=use_timeout)
        if process.returncode != 0:
            pytest.fail("\n".join(output_lines) or f"Script failed: {script_name}")
    else:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd,
            env=env,
            timeout=use_timeout,
        )
        if result.returncode != 0:
            output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
            pytest.fail(output or f"Script failed: {script_name}")
