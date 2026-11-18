"""Studio maintenance jobs, run as Setup steps (sudo shim, log, stop come from setup_steps.setup_run).

clean-build    remove other-arch C++ build dirs, then build.sh --clean --minimal for this machine
runtime-reset  dx-runtime/uninstall.sh --target=all, then remove the Studio inference venv

dx-runtime is only called, never edited. Downloaded models/videos (workspace/res) are not touched."""
import shutil
import subprocess
import sys

from dx_app.core.config import DX_APP_ROOT, DX_RUNTIME_ROOT
from shared.paths import _KNOWN_ARCHES, host_arch
from shared.runtime import STUDIO_INFER_VENV


def remove_other_arch_builds():
    """A build for another CPU (e.g. build_x86_64 on a Raspberry Pi) — dx_app build output, not source."""
    removed = []
    for arch in _KNOWN_ARCHES:
        d = DX_APP_ROOT / f"build_{arch}"
        if arch != host_arch() and d.is_dir():
            shutil.rmtree(d)
            removed.append(d)
    return removed


def _run(argv, cwd):
    print("$ " + " ".join(str(a) for a in argv), flush=True)
    return subprocess.run([str(a) for a in argv], cwd=str(cwd), stdin=subprocess.DEVNULL).returncode


def clean_build():
    for d in remove_other_arch_builds():
        print(f"Removed a leftover build for another architecture: {d}", flush=True)
    return _run(["bash", DX_APP_ROOT / "build.sh", "--clean", "--minimal", "--type", "Release",
                 "--arch", host_arch()], DX_APP_ROOT)


def runtime_reset():
    code = _run(["bash", DX_RUNTIME_ROOT / "uninstall.sh", "--target=all"], DX_RUNTIME_ROOT)
    if STUDIO_INFER_VENV.exists():
        shutil.rmtree(STUDIO_INFER_VENV, ignore_errors=True)
        print(f"Removed {STUDIO_INFER_VENV}", flush=True)
    print("Kept: downloaded models and videos (workspace/res).", flush=True)
    return code


JOBS = {"clean-build": clean_build, "runtime-reset": runtime_reset}


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    job = JOBS.get(args[0] if args else "")
    if job is None:
        print("usage: python -m dx_app.core.maintenance {" + "|".join(JOBS) + "}", file=sys.stderr)
        return 2
    return job()


if __name__ == "__main__":
    sys.exit(main())
