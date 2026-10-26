#!/usr/bin/env bash
# Contract + behavior checks for getting-started/modelzoo-*.sh, ModelZoo docs, and Dockerfile.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd -P)"
GS="$ROOT/getting-started"
SCRIPTS=(modelzoo-0_install_dx-modelzoo.sh modelzoo-1_prepare_assets.sh
         modelzoo-2_run_first_npu_model.sh modelzoo-clean.sh)
fail() { echo "FAIL: $*" >&2; exit 1; }

# --- static contract: follow existing compiler-/runtime- script conventions ---
for s in "${SCRIPTS[@]}"; do
  f="$GS/$s"
  [[ -x "$f" ]] || fail "$s not executable"
  bash -n "$f" || fail "$s syntax"
  grep -q 'DX_AS_PATH=' "$f" || fail "$s missing DX_AS_PATH"
  grep -q 'scripts/color_env.sh' "$f" || fail "$s missing color_env.sh"
done
for s in modelzoo-0_install_dx-modelzoo.sh modelzoo-1_prepare_assets.sh modelzoo-2_run_first_npu_model.sh; do
  out="$("$GS/$s" --help)" || fail "$s --help exit"
  grep -q 'Usage:' <<<"$out" || fail "$s --help missing Usage"
done
! grep -n 'dx-modelzoo_test\|\.\./dx-modelzoo' "$GS"/modelzoo-*.sh || fail "stale ModelZoo source path"
grep -q 'DX_AS_PATH}/dx-modelzoo' "$GS/modelzoo-0_install_dx-modelzoo.sh" || fail "source must be suite submodule"
! grep -q 'dx-compiler' "$GS/modelzoo-0_install_dx-modelzoo.sh" || fail "modelzoo-0 must not require dx-compiler"
grep -q 'runtime-0_install_dx-runtime.sh' "$GS/modelzoo-0_install_dx-modelzoo.sh" || fail "modelzoo-0 must point to runtime-0"
grep -q -- '--profile onnx' "$GS/modelzoo-2_run_first_npu_model.sh" || fail "ONNX eval before compile"
grep -q -- '--dx-com-wheel' "$GS/modelzoo-2_run_first_npu_model.sh" || fail "dx_com wheel option"
! grep -q 'list --all' "$GS/modelzoo-2_run_first_npu_model.sh" || fail "noisy dxmz list"
grep -q '! -name "modelzoo-\*.sh"' "$GS/modelzoo-clean.sh" || fail "clean must keep modelzoo-*.sh only"

# --- Dockerfile ---
DF="$ROOT/docker/Dockerfile.dx-modelzoo"
! grep -q 'set -E' "$DF" || fail "dash does not support set -E"
grep -q 'dxmz --help' "$DF" || fail "dxmz smoke check"
grep -q '^COPY getting-started /deepx/getting-started' "$DF" || fail "COPY getting-started"
grep -q '^RUN /deepx/getting-started/modelzoo-clean.sh' "$DF" || fail "modelzoo-clean in image"

# --- GPU support (dx-modelzoo only) ---
grep -q 'pip install .* -e ".\[cpu\]"' "$DF" || fail "cpu extra install"
grep -q '^ARG CUDA_VERSION=' "$DF" || fail "CUDA_VERSION arg"
! grep -q 'MODELZOO_EXTRA' "$DF" || fail "MODELZOO_EXTRA removed"
! grep -q 'ld.so.conf.d\|ldconfig' "$DF" || fail "gpu libs come from nvidia/cuda base; no ldconfig"
grep -q 'CUDAExecutionProvider' "$DF" || fail "gpu provider check"
grep -q '^ARG FROM_IMAGE=${BASE_IMAGE_NAME}' "$DF" || fail "GPU base must preserve distro detection"
python3 - "$ROOT/docker/docker-compose.nvidia_gpu.yml" <<'PYEOF' || fail "nvidia overlay CUDA_VERSION"
import sys, yaml
args = yaml.safe_load(open(sys.argv[1]))["services"]["dx-modelzoo"]["build"]["args"]
assert args["CUDA_VERSION"] and "MODELZOO_EXTRA" not in args, args
PYEOF
! grep -rq 'all\]' "$DF" "$GS"/modelzoo-*.sh || fail "all extra conflicts with gpu"
grep -q 'onnxruntime-gpu' "$GS/modelzoo-0_install_dx-modelzoo.sh" || fail "cpu/gpu runtime conflict handling"
grep -q 'LD_LIBRARY_PATH' "$GS/modelzoo-0_install_dx-modelzoo.sh" || fail "gpu LD_LIBRARY_PATH guidance"
for f in 02_Setting_Up_Environment.md 02_Setting_Up_Environment_kor.md; do
  grep -q -- '--nvidia_gpu' "$ROOT/docs/source/$f" || fail "$f GPU docker build"
done

# --- docs placed inside existing structure (EN + KOR) ---
D="$ROOT/docs/source"
for f in 02_Setting_Up_Environment.md 02_Setting_Up_Environment_kor.md; do
  grep -q '^#### C. DX-ModelZoo' "$D/$f" || fail "$f Docker C section"
  grep -q '^### DX-ModelZoo Installation' "$D/$f" || fail "$f Local section"
  grep -q 'getting-started/modelzoo-0_install_dx-modelzoo.sh' "$D/$f" || fail "$f script usage"
  grep -q '\.env\.example' "$D/$f" || fail "$f dotenv"
done
for f in 03_Running_Your_First_NPU_Model.md 03_Running_Your_First_NPU_Model_kor.md; do
  grep -q '^## DX-ModelZoo: Model Evaluation Scripts Guide' "$D/$f" || fail "$f ModelZoo guide"
  grep -q 'modelzoo-2_run_first_npu_model.sh' "$D/$f" || fail "$f runner"
done
for f in 05_FAQ_Troubleshooting_Guide.md 05_FAQ_Troubleshooting_Guide_kor.md; do
  grep -q '^- Q7\.' "$D/$f" || fail "$f TOC Q7"
  grep -q '^## Q8\.' "$D/$f" || fail "$f Q8"
done

# --- behavior: run scripts in a throwaway fake suite ---
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/suite/getting-started" "$T/suite/scripts" "$T/suite/dx-modelzoo"
cp "$GS"/modelzoo-*.sh "$T/suite/getting-started/"
cp "$ROOT/scripts/color_env.sh" "$ROOT/scripts/common_util.sh" "$T/suite/scripts/"
touch "$T/suite/getting-started/runtime-0_install_dx-runtime.sh"
echo 'MODEL_ROOT=download/models' > "$T/suite/dx-modelzoo/.env.example"
S="$T/suite/getting-started"

# modelzoo-0 fails clearly when runtime venv is missing (host mode)
if DX_CONTAINER_MODE=false "$S/modelzoo-0_install_dx-modelzoo.sh" >"$T/m0.log" 2>&1; then fail "modelzoo-0 should fail without runtime venv"; fi
grep -q 'runtime-0_install_dx-runtime.sh' "$T/m0.log" || fail "modelzoo-0 hint missing"

# modelzoo-1 host mode: symlink to workspace/modelzoo + .env created once
"$S/modelzoo-1_prepare_assets.sh" >/dev/null
[[ -L "$S/modelzoo" && "$(readlink -f "$S/modelzoo")" == "$T/suite/workspace/modelzoo" ]] || fail "host symlink"
for d in models datasets result; do [[ -d "$S/modelzoo/$d" ]] || fail "missing $d"; done
[[ -f "$T/suite/dx-modelzoo/.env" ]] || fail ".env not created"
echo 'MODEL_ROOT=/custom' > "$T/suite/dx-modelzoo/.env"
"$S/modelzoo-1_prepare_assets.sh" >/dev/null
grep -q '/custom' "$T/suite/dx-modelzoo/.env" || fail ".env overwritten"

# modelzoo-1 container mode: symlink to DOCKER_VOLUME_PATH/modelzoo
rm "$S/modelzoo"
DX_CONTAINER_MODE=true DOCKER_VOLUME_PATH="$T/vol" "$S/modelzoo-1_prepare_assets.sh" >/dev/null
[[ "$(readlink -f "$S/modelzoo")" == "$T/vol/modelzoo" ]] || fail "container symlink"

# modelzoo-clean: host = no-op, container = keep modelzoo-*.sh only
touch "$S/compiler-0_install_dx-compiler.sh"
DX_CONTAINER_MODE=false "$S/modelzoo-clean.sh" >/dev/null
[[ -e "$S/compiler-0_install_dx-compiler.sh" ]] || fail "host clean must not delete"
DX_CONTAINER_MODE=true "$S/modelzoo-clean.sh" >/dev/null
[[ ! -e "$S/compiler-0_install_dx-compiler.sh" && ! -e "$S/runtime-0_install_dx-runtime.sh" ]] || fail "container clean"
for s in "${SCRIPTS[@]}"; do [[ -e "$S/$s" ]] || fail "clean removed $s"; done

# modelzoo-0 cpu<->gpu switching with a stub venv (no real downloads)
V="$T/stubvenv"; mkdir -p "$V/bin" "$V/state"; touch "$T/suite/dx-modelzoo/pyproject.toml"
echo "export PATH=\"$V/bin:\$PATH\"" > "$V/bin/activate"
cat > "$V/bin/pip" <<STUB
#!/bin/bash
echo "pip \$*" >> "$V/pip.log"
case "\$1" in
  show) [ -e "$V/state/\$2" ] ;;
  uninstall) rm -f "$V/state/\$3" ;;
  install) e=\${3##*[}; e=\${e%]}; touch "$V/state/dx_modelzoo"
           if [ "\$e" = gpu ]; then touch "$V/state/onnxruntime-gpu"; else touch "$V/state/onnxruntime"; fi ;;
esac
STUB
cat > "$V/bin/python" <<STUB
#!/bin/bash
m=\$(sed -n 's/^import \([a-z_]*\).*/\1/p' <<<"\$2"); [ -e "$V/state/\$m" ]
STUB
printf '#!/bin/bash\nexit 0\n' > "$V/bin/dxmz"; chmod +x "$V/bin/"*
touch "$V/state/dx_modelzoo" "$V/state/onnxruntime"
M0="$S/modelzoo-0_install_dx-modelzoo.sh"
DX_CONTAINER_MODE=false "$M0" --venv "$V" >/dev/null || fail "cpu skip run"
! grep -q '^pip install' "$V/pip.log" 2>/dev/null || fail "cpu already installed must skip"
out="$(DX_CONTAINER_MODE=false "$M0" --venv "$V" --extra gpu)" || fail "gpu switch run"
grep -q '^pip uninstall -y onnxruntime$' "$V/pip.log" || fail "gpu must remove onnxruntime"
grep -q 'pip install -e .*\[gpu\]' "$V/pip.log" || fail "gpu install"
[[ -e "$V/state/onnxruntime-gpu" && ! -e "$V/state/onnxruntime" ]] || fail "gpu state"
grep -q 'LD_LIBRARY_PATH' <<<"$out" || fail "gpu LD_LIBRARY_PATH hint"
: > "$V/pip.log"; DX_CONTAINER_MODE=false "$M0" --venv "$V" --extra gpu >/dev/null || fail "gpu skip run"
! grep -q '^pip install' "$V/pip.log" || fail "gpu already installed must skip"
DX_CONTAINER_MODE=false "$M0" --venv "$V" >/dev/null || fail "cpu switch run"
grep -q '^pip uninstall -y onnxruntime-gpu$' "$V/pip.log" || fail "cpu must remove onnxruntime-gpu"
[[ -e "$V/state/onnxruntime" && ! -e "$V/state/onnxruntime-gpu" ]] || fail "cpu state"

# modelzoo-2 cds into the workspace, so relative --dx-com-wheel / --model paths must be absolutized first
V2="$T/stubvenv2"; mkdir -p "$V2/bin" "$V2/state" "$T/caller"; touch "$V2/state/dx_engine"
echo "export PATH=\"$V2/bin:\$PATH\"" > "$V2/bin/activate"
printf '#!/bin/bash\necho "pip $*" >> "%s/pip.log"\n' "$V2" > "$V2/bin/pip"
printf '#!/bin/bash\necho "dxmz $*" >> "%s/dxmz.log"\n' "$V2" > "$V2/bin/dxmz"
cat > "$V2/bin/python" <<STUB
#!/bin/bash
m=\$(sed -n 's/^import \([a-z_]*\).*/\1/p' <<<"\$2"); [ -e "$V2/state/\$m" ]
STUB
chmod +x "$V2/bin/"*; touch "$T/caller/w.whl" "$T/caller/my.yaml"
DX_CONTAINER_MODE=false "$S/modelzoo-1_prepare_assets.sh" >/dev/null || fail "modelzoo-1 rerun"
(cd "$T/caller" && DX_CONTAINER_MODE=false "$S/modelzoo-2_run_first_npu_model.sh" --venv "$V2" --skip-onnx \
    --dx-com-wheel ./w.whl --model ./my.yaml >"$T/m2.log" 2>&1) || fail "modelzoo-2 stub run: $(tail -3 "$T/m2.log")"
grep -q "^pip install $T/caller/w.whl " "$V2/pip.log" || fail "#11 relative --dx-com-wheel must be absolutized: $(cat "$V2/pip.log")"
grep -q "^dxmz info $T/caller/my.yaml$" "$V2/dxmz.log" || fail "#11 relative --model YAML must be absolutized: $(head -1 "$V2/dxmz.log")"
DX_CONTAINER_MODE=false "$S/modelzoo-2_run_first_npu_model.sh" --venv "$V2" --skip-onnx --skip-compile >/dev/null 2>&1 || fail "modelzoo-2 name run"
grep -q "^dxmz info resnet50_224x224$" "$V2/dxmz.log" || fail "#11 model names must stay unchanged"

# a missing --dx-com-wheel must be reported as such (not as "pass --dx-com-wheel")
if (cd "$T/caller" && DX_CONTAINER_MODE=false "$S/modelzoo-2_run_first_npu_model.sh" --venv "$V2" --skip-onnx \
    --dx-com-wheel ./nope/x.whl >"$T/m2bad.log" 2>&1); then fail "#12 missing wheel must fail"; fi
grep -q "dx_com wheel not found: $T/caller/nope/x.whl" "$T/m2bad.log" || fail "#12 missing wheel message: $(tail -1 "$T/m2bad.log")"

# --- review fixes: docs match measured dx-modelzoo behavior ---
grep -q '^export DATA_ROOT MODEL_ROOT' "$GS/modelzoo-2_run_first_npu_model.sh" || fail "#1 dxmz info must see same roots"
for f in 05_FAQ_Troubleshooting_Guide.md 05_FAQ_Troubleshooting_Guide_kor.md; do
  grep -q 'Failed to download model from' "$D/$f" || fail "#3 $f download failure message"
  ! grep -q 'resnet50_224x224.onnx -> ' "$D/$f" || fail "#3 $f log arrow"
  grep -q 'Dataset not found: ILSVRC2012' "$D/$f" || fail "#4 $f dataset message"
  ! grep -q 'Dataset directory structure is invalid' "$D/$f" || fail "#4 $f stale dataset message"
  grep -q 'dx_engine is required for DxRuntimeSession' "$D/$f" || fail "#5 $f dx_engine message"
done
for f in 02_Setting_Up_Environment.md 02_Setting_Up_Environment_kor.md; do
  ! grep -q 'DXMZ_MODEL_URL` | .*(default' "$D/$f" || fail "#6 $f no built-in DXMZ_MODEL_URL default"
done
grep -q 'skip-onnx' <(sed -n '/Essential Check/,/^---/p' "$D/03_Running_Your_First_NPU_Model.md") || fail "#7 runtime note"

# --- #2: --nvidia_gpu build/run resolve a real CUDA base tag and the same image tag ---
G="$T/gpu"; mkdir -p "$G/dx-compiler" "$G/bin"
cp -a "$ROOT/docker_build.sh" "$ROOT/docker_run.sh" "$ROOT/scripts" "$ROOT/docker" "$G/"
printf 'COM_VERSION=0\nTRON_VERSION=0\n' > "$G/dx-compiler/compiler.properties"
cat > "$G/bin/docker" <<'STUB'
#!/bin/bash
case "$*" in
  "compose version"*|"buildx use default") exit 0 ;;
  "info --format "* ) echo "nvidia runc"; exit 0 ;;
  images*) echo "dx-modelzoo:${GPU_IMAGE_TAG}"; exit 0 ;;
  compose*) echo "COMPOSE TAG_NAME=${CUDA_VERSION:-12.8.1}-cudnn-runtime-ubuntu${UBUNTU_VERSION} IMAGE=dx-modelzoo:${CUDA_VERSION:-12.8.1}-cudnn-runtime-ubuntu${UBUNTU_VERSION}"; exit 0 ;;
esac
exit 0
STUB
printf '#!/bin/bash\nexit 0\n' > "$G/bin/nvidia-smi"
chmod +x "$G/bin/docker"
chmod +x "$G/bin/nvidia-smi"
out="$(cd "$G" && PATH="$G/bin:$PATH" ./docker_build.sh --target=dx-modelzoo --ubuntu_version=24.04 --nvidia_gpu --skip-archive 2>&1)"
grep -q 'TAG_NAME=12.8.1-cudnn-runtime-ubuntu24.04 ' <<<"$out" || fail "#2 GPU base tag: $(grep COMPOSE <<<"$out")"
out="$(cd "$G" && GPU_IMAGE_TAG=12.8.1-cudnn-runtime-ubuntu24.04 XDG_SESSION_TYPE=x11 PATH="$G/bin:$PATH" ./docker_run.sh --target=dx-modelzoo --ubuntu_version=24.04 --nvidia_gpu 2>&1)"
grep -q '^COMPOSE ' <<<"$out" && ! grep -q 'not found' <<<"$out" || fail "#2 docker_run must find GPU image"

# docker-compose.nvidia_gpu.yml only has Ubuntu-based nvidia/cuda images
for sh in "docker_build.sh --skip-archive" docker_run.sh; do
    if out="$(cd "$G" && PATH="$G/bin:$PATH" ./${sh} --target=dx-modelzoo --debian_version=12 --nvidia_gpu 2>&1)"; then
        fail "#13 ${sh} --nvidia_gpu with --debian_version must fail"
    fi
    ! grep -q '^COMPOSE ' <<<"$out" || fail "#13 ${sh} must not call compose for non-Ubuntu GPU"
    grep -q -- '--nvidia_gpu requires --ubuntu_version' <<<"$out" || fail "#13 ${sh} message: $(grep -i error <<<"$out" | head -1)"
done

# modelzoo-2 overrides .env DATA_ROOT, so Q9 must tell script users to link an existing dataset
for f in 05_FAQ_Troubleshooting_Guide.md 05_FAQ_Troubleshooting_Guide_kor.md; do
    q9="$(sed -n '/^## Q9\./,/^---/p' "${ROOT}/docs/source/${f}")"
    grep -q 'ln -s ' <<<"${q9}" || fail "#10 ${f} Q9 must show ln -s for an existing dataset"
    grep -q '\[1\]' <<<"${q9}" || fail "#10 ${f} Q9 must point to the runner [1] Model info output"
done

echo "modelzoo getting-started contract: PASS"
