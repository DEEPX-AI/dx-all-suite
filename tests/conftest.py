"""
Shared utilities and configuration for all test suites.
"""

import os
import re
import shlex
import shutil

# Prevent pytest from crawling sub-project test directories that have missing
# dependencies (dx-modelzoo, pybind11, pydxs, etc.).  This is defence-in-depth:
# the autopilot cases in test.sh also pass an explicit path, but this guard
# protects against future scope creep or combined runs.
collect_ignore_glob = [
    "../dx-modelzoo/tests/*",
    "../dx-runtime/dx_rt/extern/*",
    "../dx-runtime/dx_app/tests/*",
    "../dx-runtime/dx_stream/test/*",
]

def pytest_configure(config):
    """Register custom markers to suppress PytestUnknownMarkWarning."""
    markers = [
        "docker_install: Docker image build validation tests",
        "local_install: Local installation validation tests",
        "getting_started: End-to-end getting-started workflow tests",
        "sanity: Quick prerequisite validation tests",
        "compiler: Compiler-related tests",
        "runtime: Runtime-related tests",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)

import subprocess
import sys
import time
from pathlib import Path
import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = REPO_ROOT  # Alias for compatibility
GETTING_STARTED_DIR = REPO_ROOT / "getting-started"
DEFAULT_TIMEOUT = int(os.getenv("DX_TEST_GETTING_STARTED_TIMEOUT", "3600"))

# Expected NPU stack version files (authoritative source of truth).
DRIVER_RELEASE_VER = REPO_ROOT / "dx-runtime" / "dx_rt_npu_linux_driver" / "release.ver"
FW_RELEASE_VER = REPO_ROOT / "dx-runtime" / "dx_fw" / "release.ver"

# Host-level locks. Shared across xdist workers AND separate test sessions so that
# NPU driver install / firmware flash never run concurrently (see plan sections 4-1, 4-2, 5-1).
HOST_NPU_LOCK = os.getenv("DX_HOST_NPU_LOCK", "/tmp/dx-host-npu.lock")
HOST_EXCLUSIVE_LOCK = os.getenv("DX_HOST_EXCLUSIVE_LOCK", "/tmp/dx-host-exclusive.lock")
ARCHIVE_LOCK = os.getenv("DX_ARCHIVE_LOCK", "/tmp/dx-archive.lock")


def is_verbose() -> bool:
    """Check if verbose/debug mode is enabled."""
    return os.getenv("DX_TEST_VERBOSE", "0").lower() in {"1", "true", "yes", "y"}

def container_name(os_type: str, version: str, component: str = "") -> str:
    """Generate container name from component, os_type and version string."""
    if component:
        return f"dx-local-install-test-{component}-{os_type}-{version.replace('.', '-')}"
    return f"dx-local-install-test-{os_type}-{version.replace('.', '-')}"


def compose_project_name(component: str, os_type: str, version: str) -> str:
    """Unique docker-compose project name per (component, os, version) combo.

    Tests run in parallel (pytest-xdist) but share one docker-compose service
    (`dx-local-install-test`). Without a distinct project per combo, concurrent
    `docker compose up -d` calls recreate/remove each other's containers within
    the default project, causing "removal is already in progress" / "No such
    container" races. Isolating each combo into its own project prevents this.
    """
    raw = f"dxlit-{component}-{os_type}-{version.replace('.', '-')}"
    return raw.lower()


def is_container_running(container_name_str: str) -> bool:
    """Check if a docker container is running."""
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.State.Running}}", container_name_str],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def path_exists_in_container(container_name_str: str, path: str) -> bool:
    """Check if a file or directory exists inside a container."""
    result = subprocess.run(
        ["docker", "exec", "-i", container_name_str, "bash", "-lc", f"test -f {path}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def get_base_image(os_type: str, version: str) -> str:
    """
    Get the base docker image for a given OS type and version.

    Maps os_type/version to the correct registry image path.
    - rhel 9 → redhat/ubi9:latest
    - rhel 10 → redhat/ubi10:latest
    - centos stream9 → quay.io/centos/centos:stream9
    - centos stream10 → quay.io/centos/centos:stream10
    - others → {os_type}:{version}
    """
    if os_type == "rhel":
        return f"redhat/ubi{version}:latest"
    elif os_type == "centos":
        # version is "stream9" or "stream10"
        return f"quay.io/centos/centos:{version}"
    else:
        return f"{os_type}:{version}"


def check_docker_image_exists(os_type: str, version: str) -> bool:
    """
    Check if a local install docker image exists.

    Args:
        os_type: OS type (ubuntu or debian)
        version: OS version (24.04, 22.04, etc.)

    Returns:
        True if image exists, False otherwise
    """
    image_name = f"dx-local-install-test-{os_type}:{version}"
    result = subprocess.run(
        ["docker", "images", "-q", image_name],
        capture_output=True,
        text=True,
    )
    return bool(result.stdout.strip())

def run_in_container(
    container_name: str,
    cmd: str,
    banner_msg: str = "",
    timeout: int = 7200,
    capsys=None,
) -> subprocess.CompletedProcess:
    """
    Execute a command inside a container with optional live output streaming.

    When DX_TEST_VERBOSE=1 (set by ./test.sh --debug), this function will stream
    output in real-time, making it easy to debug container commands.

    Args:
        container_name: Name of the container
        cmd: Command to execute
        banner_msg: Optional message to display in banner (e.g., "Installing dx-runtime")
        timeout: Timeout in seconds (default: 7200 = 2 hours)
        capsys: pytest capsys fixture for output control

    Returns:
        CompletedProcess object with the result
    """
    # A shared module-scoped container can be removed/OOM-killed by an earlier
    # heavy step. Without this guard, every later exec fails with a misleading
    # "No such container" assertion that looks like a product bug. Skip instead,
    # so the dead-container cascade is reported as infrastructure, not failure.
    if not is_container_running(container_name):
        pytest.skip(
            f"container '{container_name}' is not running — likely removed or "
            f"OOM-killed by a prior step; cannot exec: {banner_msg or cmd}"
        )

    # Use banner_msg if provided, otherwise don't show banner
    if is_verbose():
        if capsys is not None:
            capsys.disabled()

        if banner_msg:
            banner = (
                f"\n{'=' * 80}\n"
                f"🚀 {banner_msg} in container: {container_name}\n"
                f"{'=' * 80}\n"
            )
            print(banner, file=sys.stdout, flush=True)
            print(banner, file=sys.stderr, flush=True)

    # Wrap docker exec -it with script -qec to allocate PTY
    docker_cmd = ["docker", "exec", "-it", container_name, "bash", "-lc", cmd]
    wrapped_cmd = ["script", "-qec", " ".join(shlex.quote(arg) for arg in docker_cmd), "/dev/null"]

    if is_verbose():
        # Live output mode - stream output in real-time
        process = subprocess.Popen(
            wrapped_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            cwd=PROJECT_ROOT,
        )

        output_lines = []
        for line in process.stdout:
            line = line.replace("\r", "")
            if capsys is not None:
                with capsys.disabled():
                    print(line, end="", file=sys.stdout, flush=True)
            else:
                print(line, end="", file=sys.stdout, flush=True)
            output_lines.append(line.rstrip())

        process.wait(timeout=timeout)

        # Show summary if banner_msg was provided
        if banner_msg:
            summary = f"\n{'=' * 80}\n"
            if process.returncode == 0:
                summary += f"✅ {banner_msg} succeeded in {container_name}\n"
            else:
                summary += f"❌ {banner_msg} failed in {container_name} (exit code: {process.returncode})\n"
            summary += f"{'=' * 80}\n"
            print(summary, file=sys.stdout, flush=True)

        return subprocess.CompletedProcess(
            args=docker_cmd,
            returncode=process.returncode,
            stdout="\n".join(output_lines),
            stderr=None,
        )
    else:
        # Quiet mode - capture output and return
        return subprocess.run(
            wrapped_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=PROJECT_ROOT,
            timeout=timeout,
        )

def run_command(
    cmd: list[str],
    banner_msg: str = "",
    timeout: int = 1800,
    cwd: str | Path | None = None,
    capsys=None,
) -> subprocess.CompletedProcess:
    """
    Execute a command with optional live output streaming.

    When DX_TEST_VERBOSE=1 (set by ./test.sh --debug), this function will stream
    output in real-time. Otherwise, it runs in quiet mode and only shows output on failure.

    Args:
        cmd: Command list to execute
        banner_msg: Optional message to display in banner (e.g., "Building dx-runtime")
        timeout: Timeout in seconds (default: 1800 = 30 minutes)
        cwd: Working directory for command execution (default: PROJECT_ROOT)

    Returns:
        CompletedProcess object with the result
    """
    use_cwd = str(cwd) if cwd is not None else str(PROJECT_ROOT)

    # Prepare environment with DX_USERNAME and DX_PASSWORD
    env = os.environ.copy()
    if os.getenv("DX_USERNAME"):
        env["DX_USERNAME"] = os.getenv("DX_USERNAME")
    if os.getenv("DX_PASSWORD"):
        env["DX_PASSWORD"] = os.getenv("DX_PASSWORD")
    # ponytail: plain progress avoids ANSI cursor-movement codes in piped output
    env["BUILDKIT_PROGRESS"] = "plain"

    # Show banner when in verbose mode and banner_msg is provided
    if is_verbose() and banner_msg:
        banner = (
            f"\n{'=' * 80}\n"
            f"🚀 {banner_msg}\n"
            f"{'=' * 80}\n"
        )
        print(banner, file=sys.stdout, flush=True)

    # Wrap command with script -qec to allocate PTY
    script_cmd = ["script", "-qec", " ".join(shlex.quote(arg) for arg in cmd), "/dev/null"]

    if is_verbose():
        # Live output mode - stream output in real-time
        process = subprocess.Popen(
            script_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            cwd=use_cwd,
            env=env,
        )

        output_lines = []
        for line in process.stdout:
            line = line.replace("\r", "")
            if capsys is not None:
                with capsys.disabled():
                    print(line, end="", file=sys.stdout, flush=True)
            else:
                print(line, end="", file=sys.stdout, flush=True)
            output_lines.append(line.rstrip())

        process.wait(timeout=timeout)

        # Show summary if banner_msg was provided
        if banner_msg:
            summary = f"\n{'=' * 80}\n"
            if process.returncode == 0:
                summary += f"✅ {banner_msg} succeeded\n"
            else:
                summary += f"❌ {banner_msg} failed (exit code: {process.returncode})\n"
            summary += f"{'=' * 80}\n"
            print(summary, file=sys.stdout, flush=True)

        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout="\n".join(output_lines),
            stderr=None,
        )
    else:
        # Quiet mode - capture both stdout and stderr separately
        result = subprocess.run(
            script_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=use_cwd,
            timeout=timeout,
            env=env,
        )

        # Combine stdout and stderr for complete output
        combined_output = ""
        if result.stdout:
            combined_output += result.stdout
        if result.stderr:
            if combined_output:
                combined_output += "\n" + "=" * 80 + "\nSTDERR:\n" + "=" * 80 + "\n"
            combined_output += result.stderr

        # Return with combined output in stdout field for consistent access
        return subprocess.CompletedProcess(
            args=result.args,
            returncode=result.returncode,
            stdout=combined_output,
            stderr=result.stderr,
        )


# ============================================================================
# Version parsing helpers (NPU driver / firmware / runtime)
# ============================================================================

def read_first_line(path) -> str | None:
    """Read and return the first non-empty line of a file, or None if missing."""
    try:
        with open(path, "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    return stripped
    except (FileNotFoundError, OSError):
        return None
    return None


def normalize_version(value: str | None) -> str | None:
    """Normalize a version string to a canonical 'vX.Y.Z' form for exact comparison."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    return value if value.startswith("v") else f"v{value}"


def parse_dxrt_cli_versions(output: str) -> dict:
    """
    Parse `dxrt-cli -s` output into a dict of normalized versions.

    Returns keys when present: 'dx-rt', 'dx-fw', 'npu-driver'.
    Expected source lines look like:
        DXRT vX.Y.Z
        * FW version   : vX.Y.Z
        * RT Driver version : vX.Y.Z
    """
    versions: dict = {}
    for line in (output or "").splitlines():
        m = re.search(r"DXRT\s+v?([0-9][0-9.]*)", line)
        if m:
            versions["dx-rt"] = normalize_version(m.group(1))
        m = re.search(r"FW\s*version\s*:\s*v?([0-9][0-9.]*)", line, re.IGNORECASE)
        if m:
            versions["dx-fw"] = normalize_version(m.group(1))
        m = re.search(r"RT\s*Driver\s*version\s*:\s*v?([0-9][0-9.]*)", line, re.IGNORECASE)
        if m:
            versions["npu-driver"] = normalize_version(m.group(1))
    return versions


def get_installed_npu_versions() -> dict:
    """Query installed NPU stack versions via `dxrt-cli -s`. Empty dict if unavailable."""
    if shutil.which("dxrt-cli") is None:
        return {}
    try:
        result = subprocess.run(
            ["dxrt-cli", "-s"], capture_output=True, text=True, timeout=60
        )
    except (subprocess.TimeoutExpired, OSError):
        return {}
    if result.returncode != 0:
        return {}
    return parse_dxrt_cli_versions(result.stdout)


# ============================================================================
# Host NPU stack (driver / firmware) — version-gated, lock-serialized install
# ============================================================================

def _filelock():
    """Import filelock lazily so collection works even before deps are installed."""
    from filelock import FileLock
    return FileLock


def _run_host_install(target: str, banner: str, capsys=None):
    cmd = ["./dx-runtime/install.sh", f"--target={target}"]
    result = run_command(cmd, banner, cwd=PROJECT_ROOT, capsys=capsys)
    if result.returncode != 0:
        pytest.fail(
            f"Host install failed: {' '.join(cmd)}\n{result.stdout or ''}"
        )


def _ensure_host_npu_stack_impl(capsys=None) -> None:
    """
    Ensure the host NPU stack matches the expected release versions, exactly once,
    serialized across xdist workers / sessions via the shared host NPU lock.

    Version source of truth: dx-runtime/.../release.ver. Installed versions are read
    from `dxrt-cli -s` (which ships with dx_rt), so dx_rt is bootstrapped on the host
    first if `dxrt-cli` is missing. Firmware is flashed only when DX_EXCLUDE_FW != 1.
    """
    expected_driver = normalize_version(read_first_line(DRIVER_RELEASE_VER))
    if expected_driver is None:
        pytest.skip(f"driver release.ver not found: {DRIVER_RELEASE_VER}")
    expected_fw = normalize_version(read_first_line(FW_RELEASE_VER))
    flash_fw = os.getenv("DX_EXCLUDE_FW", "0") != "1"

    def _gates_satisfied() -> bool:
        if shutil.which("dxrt-cli") is None:
            return False
        versions = get_installed_npu_versions()
        if versions.get("npu-driver") != expected_driver:
            return False
        if flash_fw and versions.get("dx-fw") != expected_fw:
            return False
        return True

    # Fast path: everything already at the expected version, no lock contention.
    if _gates_satisfied():
        return

    FileLock = _filelock()
    with FileLock(HOST_NPU_LOCK):
        # Double-check inside the lock (another worker may have just finished).
        if _gates_satisfied():
            return

        # Bootstrap dxrt-cli (driver + dx_rt) so version gating is possible.
        if shutil.which("dxrt-cli") is None:
            _run_host_install("dx_rt_npu_linux_driver",
                              "Installing NPU driver (host bootstrap)", capsys)
            _run_host_install("dx_rt", "Installing dx_rt (host bootstrap)", capsys)

        # Driver version gate.
        if get_installed_npu_versions().get("npu-driver") != expected_driver:
            _run_host_install("dx_rt_npu_linux_driver",
                              "Updating NPU driver (host, once)", capsys)
            installed = get_installed_npu_versions().get("npu-driver")
            if installed != expected_driver:
                pytest.fail(
                    f"Host NPU driver version mismatch after install: "
                    f"expected {expected_driver}, got {installed}"
                )

        # Firmware version gate (irreversible flash; strictly serialized).
        if flash_fw and get_installed_npu_versions().get("dx-fw") != expected_fw:
            _run_host_install("dx_fw", "Flashing NPU firmware (host, once)", capsys)


@pytest.fixture(scope="session")
def install_host_npu_stack():
    """
    Session-scoped prerequisite: ensure host NPU driver/dx_rt (and firmware unless
    excluded) are present at the expected versions exactly once, serialized across
    workers.

    Returns a callable so tests can trigger it explicitly inside their own capsys scope.
    """
    def _install(capsys=None):
        _ensure_host_npu_stack_impl(capsys=capsys)

    return _install


# ============================================================================
# host_exclusive serialization (across xdist workers)
# ============================================================================

@pytest.fixture(autouse=True)
def _host_exclusive_serialize(request):
    """Serialize any test marked host_exclusive behind a shared filelock."""
    if request.node.get_closest_marker("host_exclusive") is None:
        yield
        return
    FileLock = _filelock()
    with FileLock(HOST_EXCLUSIVE_LOCK):
        yield


# ============================================================================
# Auto-assign xdist groups so parallel runs stay safe (see plan section 6)
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """
    Assign xdist_group markers based on suite/parameters so that, under
    `-n <N> --dist loadgroup`, dependent/host-mutating tests stay on one worker.
    """
    for item in items:
        # local_install: pin each OS-version pipeline (build->run->install) to one worker.
        if item.get_closest_marker("local_install"):
            params = getattr(getattr(item, "callspec", None), "params", {}) or {}
            os_type = params.get("os_type")
            version = params.get("version")
            if os_type and version:
                item.add_marker(pytest.mark.xdist_group(f"{os_type}-{version}"))

        # getting-started: single group + host_exclusive (sequential workflow, host mutating).
        if item.get_closest_marker("getting_started"):
            item.add_marker(pytest.mark.xdist_group("getting_started"))
            item.add_marker(pytest.mark.host_exclusive)

        # install_option: single group, shared workspace -> serialize within suite.
        if item.get_closest_marker("install_option"):
            item.add_marker(pytest.mark.xdist_group("install_option"))


# ============================================================================
# Reusable local-install docker helpers (image build + container start)
# ============================================================================

def compose_env(component: str, os_type: str, version: str) -> dict:
    """Build the environment dict used by the local-install docker-compose file."""
    env = os.environ.copy()
    env["COMPOSE_BAKE"] = "true"
    env["BUILDKIT_PROGRESS"] = "plain"  # ponytail: plain avoids ANSI cursor-movement codes in piped output
    env["HOST_UID"] = str(os.getuid())
    env["HOST_GID"] = str(os.getgid())
    env["TARGET_USER"] = "deepx"
    env["TARGET_HOME"] = "/deepx"
    env["OS_TYPE"] = os_type
    env["VERSION"] = version
    env["VERSION_DASH"] = version.replace(".", "-")
    env["COMPONENT"] = component
    env["BASE_IMAGE"] = get_base_image(os_type, version)
    env["COMPOSE_PROJECT_NAME"] = compose_project_name(component, os_type, version)
    env["LOCAL_VOLUME_PATH"] = os.getenv("LOCAL_VOLUME_PATH", str(PROJECT_ROOT))
    env["DOCKER_VOLUME_PATH"] = os.getenv("DOCKER_VOLUME_PATH", "/deepx/workspace")

    if not env.get("XAUTHORITY"):
        dummy_xauth = "/tmp/dummy"
        Path(dummy_xauth).touch(exist_ok=True)
        env["XAUTHORITY"] = dummy_xauth
        env["XAUTHORITY_TARGET"] = dummy_xauth
    else:
        env["XAUTHORITY_TARGET"] = "/tmp/.docker.xauth"

    for key in ("USE_INTRANET", "CA_FILE_NAME", "DISPLAY"):
        if not env.get(key):
            env[key] = ""
    return env


def compose_config_args(env: dict) -> list[str]:
    """Compose -f config file args, honoring optional GPU/internal overlays."""
    args = ["-f", "tests/docker/docker-compose.local.install.test.yml"]
    if env.get("DX_TEST_NVIDIA_GPU", "0").lower() in {"1", "true", "yes", "y"}:
        args.extend(["-f", "docker/docker-compose.nvidia_gpu.yml"])
    if env.get("DX_TEST_INTERNAL", "0").lower() in {"1", "true", "yes", "y"}:
        args.extend(["-f", "docker/docker-compose.internal.yml"])
    return args


def build_local_install_image(component: str, os_type: str, version: str) -> None:
    """Build the local-install docker image if it does not already exist."""
    if check_docker_image_exists(os_type, version):
        return
    env = compose_env(component, os_type, version)
    no_cache = []
    if env.get("DX_TEST_NO_CACHE", "0").lower() in {"1", "true", "yes", "y"}:
        no_cache = ["--no-cache"]
    cmd = ["docker", "compose", *compose_config_args(env), "build", *no_cache,
           "dx-local-install-test"]
    result = subprocess.run(cmd, capture_output=True, text=True,
                            cwd=str(PROJECT_ROOT), env=env, timeout=1800)
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to build image for {os_type}:{version}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def _container_exists(name: str) -> bool:
    """Return True if a container with this exact name exists (any state)."""
    result = subprocess.run(
        ["docker", "inspect", "-f", "{{.Id}}", name],
        capture_output=True, text=True,
    )
    return result.returncode == 0


def remove_container_and_wait(name: str, timeout: int = 60) -> None:
    """Force-remove a container and block until its name is free.

    `docker rm -f` returns once removal is *initiated*; the daemon may still be
    tearing the container down. Immediately recreating a container with the same
    name then races and fails with "container is marked for removal" or
    "name ... is already in use". Polling until the name disappears makes the
    subsequent `docker compose up` deterministic.
    """
    subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True)
    deadline = time.monotonic() + timeout
    while _container_exists(name):
        if time.monotonic() >= deadline:
            break
        time.sleep(1)
        subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True)


def start_local_install_container(component: str, os_type: str, version: str) -> str:
    """(Re)create and start a local-install container, returning its name."""
    name = container_name(os_type, version, component)
    env = compose_env(component, os_type, version)
    cmd = ["docker", "compose", *compose_config_args(env), "up", "-d",
           "--force-recreate", "dx-local-install-test"]

    last_result = None
    for attempt in range(3):
        remove_container_and_wait(name)
        last_result = subprocess.run(cmd, capture_output=True, text=True,
                                     cwd=str(PROJECT_ROOT), env=env, timeout=600)
        if last_result.returncode == 0:
            return name
        transient = (
            "marked for removal" in last_result.stderr
            or "is already in use" in last_result.stderr
            or "already in progress" in last_result.stderr
        )
        if not transient:
            break
        time.sleep(2)

    raise RuntimeError(
        f"Failed to start container {name}\n"
        f"STDOUT:\n{last_result.stdout}\nSTDERR:\n{last_result.stderr}"
    )


def remove_container(name: str) -> None:
    """Force-remove a container, ignoring errors."""
    subprocess.run(["docker", "rm", "-f", name], capture_output=True, text=True)


# ============================================================================
# Archive-once prerequisite for parallel docker_install (see plan section 7, Phase 0)
# ============================================================================

@pytest.fixture(scope="session")
def archive_once():
    """
    Produce the shared archives/*.tar.gz, serialized across workers via a lock.

    docker_build.sh writes OS-independent archives to the repo-shared archives/ dir;
    running it per-build in parallel races on those files. This fixture builds them
    once up front so every parallel docker build can safely pass --skip-archive.
    """
    FileLock = _filelock()
    with FileLock(ARCHIVE_LOCK):
        archive_cmds = [
            ["./scripts/archive_dx-compiler.sh"],
            ["./scripts/archive_git_repos.sh", "--target=dx-runtime"],
            ["./scripts/archive_git_repos.sh", "--target=dx-modelzoo"],
        ]
        for cmd in archive_cmds:
            result = run_command(cmd, f"Archiving (once): {' '.join(cmd)}",
                                 cwd=PROJECT_ROOT, timeout=7200)
            if result.returncode != 0:
                pytest.fail(
                    f"archive_once failed: {' '.join(cmd)}\n{result.stdout or ''}"
                )
