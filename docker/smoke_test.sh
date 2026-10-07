#!/usr/bin/env bash
# Smoke test for released DEEPX Docker images.
#
# No NPU hardware required: every check is an import / file-existence / plugin
# registration probe. Nothing here opens an NPU device, so this runs on a plain
# GitHub Actions runner as well as on a developer machine.
#
# Usage: docker/smoke_test.sh <image_ref> <component> [variant]
#   component : runtime | compiler | modelzoo
#   variant   : rt | rt-app | rt-stream | rt-app-stream   (runtime only; default rt-app-stream)
#
# The image must already be present locally (built with `--load`, or pulled by
# the caller). This script never pulls, so it cannot silently test an image
# other than the one the caller just built.
#
# Exit codes: 0 = all checks passed
#             1 = a check failed, or the image is not present locally
#             2 = usage error (missing/unknown arguments)
#
# All progress and results go to stdout, so `smoke_test.sh … > smoke.log` keeps a
# complete transcript including failure detail. stderr carries only usage and
# preflight errors.
set -euo pipefail

usage() {
    cat >&2 <<'EOF'
Usage: smoke_test.sh <image_ref> <component> [variant]
  component : runtime | compiler | modelzoo
  variant   : rt | rt-app | rt-stream | rt-app-stream   (runtime only; default rt-app-stream)

Examples:
  smoke_test.sh dx-runtime:ubuntu-24.04 runtime rt-app-stream   # local docker_build.sh output
  smoke_test.sh dx-runtime:ubuntu-24.04-rt runtime rt           # local, non-default variant
  smoke_test.sh ghcr.io/deepx-ai/dx-compiler:latest compiler    # published image (docker pull it first)
EOF
    exit 2
}

[ $# -ge 2 ] || usage

IMAGE="$1"
COMPONENT="$2"
# `${3:-}` (not `${3-}`) on purpose: callers pass "" for compiler/modelzoo, and
# a present-but-empty variant must still fall back to the default.
VARIANT="${3:-rt-app-stream}"

FAILED=0

# check <label> <bash snippet executed inside the image>
# The snippet runs under `set -euo pipefail` so that any failing command in it --
# including in a pipeline a future probe might use -- exits the container non-zero.
# Failures print the snippet and the captured container output, so a CI log shows
# exactly which probe broke and why.
check() {
    local label="$1" snippet="$2" out rc=0
    out=$(docker run --rm --entrypoint bash "$IMAGE" -c "set -euo pipefail
$snippet" 2>&1) || rc=$?
    if [ "$rc" -eq 0 ]; then
        printf '  [ OK ] %s\n' "$label"
        return
    fi
    # `exit=` not `container exit=`: 125/126/127 are docker's own codes, not the
    # container's. Indent every line of both the snippet and the output so a
    # multi-line probe stays visually distinct from the container's output.
    printf '  [FAIL] %s (exit=%d)\n' "$label" "$rc"
    printf '%s\n' "$snippet" | sed 's/^/         probe: /'
    if [ -n "$out" ]; then
        printf '%s\n' "$out" | sed 's/^/         | /'
    fi
    FAILED=1
}

# dx_stream installs its plugin to /usr/local/lib/<arch>/gstreamer-1.0, which is
# outside gst's default scan path, and exports GST_PLUGIN_PATH only from
# /root/.bashrc (which early-returns for non-interactive shells). So locate the
# .so and point GST_PLUGIN_PATH at it before asking gst whether the element exists.
# `-print -quit` (same idiom as Dockerfile.dx-compiler:372) instead of `| head -1`:
# under pipefail a second match makes head close the pipe, find dies of SIGPIPE
# and a healthy image would FAIL.
# shellcheck disable=SC2016  # intentional: this expands inside the container, not here
GST_PROBE='SO=$(find /usr/local/lib /usr/lib -name libgstdxstream.so -print -quit 2>/dev/null)
test -n "$SO" || { echo "libgstdxstream.so not found under /usr/local/lib /usr/lib" >&2; exit 1; }
export GST_PLUGIN_PATH="$(dirname "$SO")"
gst-inspect-1.0 --exists dxpreprocess'

# variant only means something for the runtime image
LABEL="$COMPONENT"
if [ "$COMPONENT" = runtime ]; then
    LABEL="$COMPONENT $VARIANT"
fi

echo "SMOKE TEST: $IMAGE ($LABEL)"

# Preflight: one clear line instead of the same docker-level error repeated once
# per probe. A tag mismatch between the smoke step and the push step is the most
# likely real-world failure, and it should read as "image missing", not as N
# confusing exit=125 blocks.
docker image inspect "$IMAGE" >/dev/null 2>&1 \
    || { echo "ERROR: image not present locally: $IMAGE" >&2; exit 1; }

case "$COMPONENT" in
runtime)
    # Reject a bad variant before spending any container run, so usage lands at
    # the top of the CI log instead of below a wall of check output.
    case "$VARIANT" in
    rt | rt-app | rt-stream | rt-app-stream) ;;
    *)
        echo "ERROR: unknown variant: $VARIANT" >&2
        usage
        ;;
    esac
    check "dxrtd binary present"        'test -x /usr/local/bin/dxrtd'
    # Must succeed without an NPU driver. If this fails, find the real cause —
    # do not weaken it to a file-existence check. It must not open a device.
    check "dx_engine imports in venv"   'source /venv-dxnn/bin/activate && python -c "import dx_engine"'
    case "$VARIANT" in
    rt)
        check "dx_app absent"           'test ! -d /deepx/dx-runtime/dx_app'
        check "dx_stream absent"        'test ! -d /deepx/dx-runtime/dx_stream'
        ;;
    rt-app)
        check "dx_app present"          'test -d /deepx/dx-runtime/dx_app'
        check "dx_stream absent"        'test ! -d /deepx/dx-runtime/dx_stream'
        ;;
    rt-stream)
        check "dx_app absent"           'test ! -d /deepx/dx-runtime/dx_app'
        check "dx_stream present"       'test -d /deepx/dx-runtime/dx_stream'
        check "dxpreprocess registered" "$GST_PROBE"
        ;;
    rt-app-stream)
        check "dx_app present"          'test -d /deepx/dx-runtime/dx_app'
        check "dx_stream present"       'test -d /deepx/dx-runtime/dx_stream'
        check "dxpreprocess registered" "$GST_PROBE"
        ;;
    *)
        # Unreachable via the guard above; kept so that adding a variant to the
        # guard but not here fails loudly instead of passing on the two common
        # checks alone.
        echo "ERROR: variant $VARIANT has no checks defined" >&2
        exit 1
        ;;
    esac
    ;;
compiler)
    # Image ends on `USER deepx` with an init-workspace.sh entrypoint; --entrypoint
    # bash skips the workspace chown, and /venv-dxnn stays world-readable, so the
    # import works as the unprivileged user.
    check "dx_com imports in venv"      'source /venv-dxnn/bin/activate && python -c "import dx_com"'
    check "compiler examples present"   'test -d /deepx/dx-compiler/example'
    ;;
modelzoo)
    # dx-modelzoo is pip-installed into the venv (Dockerfile.dx-modelzoo), so import
    # it rather than byte-compiling the source. torch is asserted CPU-only: the
    # [cpu] extra does not prevent the CUDA build, the Dockerfile does, and a
    # regression there would silently add several GB of nvidia wheels.
    check "dxrtd binary present"        'test -x /usr/local/bin/dxrtd'
    check "dx_engine imports in venv"   'source /venv-dxnn/bin/activate && python -c "import dx_engine"'
    check "dx_modelzoo imports in venv" 'source /venv-dxnn/bin/activate && python -c "import dx_modelzoo"'
    check "onnxruntime available"       'source /venv-dxnn/bin/activate && python -c "import onnxruntime"'
    check "torch is cpu-only"           'source /venv-dxnn/bin/activate && python -c "import torch,sys; sys.exit(1) if torch.version.cuda else None"'
    ;;
*)
    echo "ERROR: unknown component: $COMPONENT" >&2
    usage
    ;;
esac

if [ "$FAILED" -ne 0 ]; then
    echo "SMOKE TEST FAILED: $IMAGE ($LABEL)"
    exit 1
fi
echo "SMOKE TEST PASSED: $IMAGE ($LABEL)"
