#!/bin/bash
# Regression check for the dx-runtime '--variant' image tag suffix.
#
# Builds nothing: a stub 'docker' on PATH captures the RUNTIME_VARIANT /
# IMAGE_TAG_SUFFIX that docker_build.sh hands to 'docker compose build'.
#
# Locked invariants:
#   1. no --variant       -> stage rt-app-stream, tag ubuntu-24.04 (backward compatible)
#   2. --variant=rt-app   -> stage rt-app,        tag ubuntu-24.04-rt-app
#   3. runtime then modelzoo in one shell -> modelzoo keeps the plain tag (no leak)
#   4. runtime built twice in one shell   -> suffix applied once (no double append)
#
# Run: bash tests/test_docker_install/variant_tag_check.sh
# Also runs as part of: ./test.sh docker_install   (see test_docker_install.py)

set -u

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd -P)"
cd "$REPO_ROOT" || exit 1

FAIL=0
check() { # check <label> <expected> <actual>
    if [ "$2" = "$3" ]; then
        echo "  PASS  $1"
    else
        echo "  FAIL  $1"
        echo "        expected: $2"
        echo "        actual  : $3"
        FAIL=1
    fi
}

# Stub docker: capture the build env, no-op for everything else (compose version, buildx use)
STUB_DIR="$(mktemp -d)"
TMP_SCRIPT="${REPO_ROOT}/.variant_tag_check_seq_$$.sh"
trap 'rm -rf "$STUB_DIR"; rm -f "$TMP_SCRIPT"' EXIT

cat > "$STUB_DIR/docker" <<'STUB'
#!/bin/bash
for a in "$@"; do
    if [ "$a" = "build" ]; then
        echo "CAPTURE ${*: -1} RUNTIME_VARIANT=${RUNTIME_VARIANT:-} IMAGE_TAG_SUFFIX=${IMAGE_TAG_SUFFIX:-}"
        exit 0
    fi
done
exit 0
STUB
chmod +x "$STUB_DIR/docker"
export PATH="$STUB_DIR:$PATH"

# --- Invariants 1 & 2: through the real CLI (arg parser + guards + docker_build_impl) ---
cli_capture() {
    ./docker_build.sh --target=dx-runtime --ubuntu_version=24.04 --skip-archive "$@" 2>/dev/null | grep '^CAPTURE'
}

check "no --variant -> full stage, plain tag" \
    "CAPTURE dx-runtime RUNTIME_VARIANT=rt-app-stream IMAGE_TAG_SUFFIX=ubuntu-24.04" \
    "$(cli_capture)"

check "--variant=rt-app -> rt-app stage, -rt-app tag" \
    "CAPTURE dx-runtime RUNTIME_VARIANT=rt-app IMAGE_TAG_SUFFIX=ubuntu-24.04-rt-app" \
    "$(cli_capture --variant=rt-app)"

# The stage compose builds is 'target: ${RUNTIME_VARIANT:-rt-app-stream}', so the
# RUNTIME_VARIANT captured above *is* the stage. Assert that wiring still exists.
check "compose dx-runtime build target is driven by RUNTIME_VARIANT" \
    "1" \
    "$(grep -c 'target: \${RUNTIME_VARIANT:-rt-app-stream}' docker/docker-compose.yml)"

# --- Invariants 3 & 4: repeated docker_build_impl calls in ONE shell ---
# Not reachable from the CLI (--all rejects --variant), so call the function directly.
# The copy must sit in the repo root: docker_build.sh derives DX_AS_PATH from $0.
{
    sed '/^main$/,$d' docker_build.sh
    cat <<'CALLS'
BASE_IMAGE_NAME=ubuntu; OS_VERSION=24.04; IMAGE_TAG_SUFFIX=""; RUNTIME_VARIANT=rt-app
docker_build_impl "runtime"  "-f docker/docker-compose.yml"
docker_build_impl "modelzoo" "-f docker/docker-compose.yml"
docker_build_impl "runtime"  "-f docker/docker-compose.yml"
CALLS
} > "$TMP_SCRIPT"

check "repeated builds: suffix on dx-runtime only, applied once" \
"CAPTURE dx-runtime RUNTIME_VARIANT=rt-app IMAGE_TAG_SUFFIX=ubuntu-24.04-rt-app
CAPTURE dx-modelzoo RUNTIME_VARIANT=rt-app IMAGE_TAG_SUFFIX=ubuntu-24.04
CAPTURE dx-runtime RUNTIME_VARIANT=rt-app IMAGE_TAG_SUFFIX=ubuntu-24.04-rt-app" \
"$(bash "$TMP_SCRIPT" 2>/dev/null | grep '^CAPTURE')"

# --- Rejected combinations (must fail before any build starts) ---
reject_check() { # reject_check <label> <args...>
    local label="$1"; shift
    if ./docker_build.sh "$@" >/dev/null 2>&1; then
        echo "  FAIL  $label (expected non-zero exit)"
        FAIL=1
    else
        echo "  PASS  $label"
    fi
}
reject_check "--variant=bogus rejected"      --target=dx-runtime --ubuntu_version=24.04 --variant=bogus
reject_check "--variant with --all rejected" --all --ubuntu_version=24.04 --variant=rt-app
reject_check "--variant with --nvidia_gpu rejected" \
    --target=dx-runtime --ubuntu_version=24.04 --variant=rt --nvidia_gpu

[ "$FAIL" -eq 0 ] && echo "variant tag checks: ALL PASS" || echo "variant tag checks: FAILED"
exit "$FAIL"
