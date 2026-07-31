#!/usr/bin/env bash
# dx-benchmark data setup — download benchmark models and videos (no sudo needed).
# Usage: ./setup_data.sh [all|models|videos]   (default: all)
#
# For one-time privileged host provisioning (system dependency install +
# passwordless sudo for dxrt crash recovery / incident log collection /
# systemd-journal membership), run the separate script: sudo ./setup_host.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
MODEL_DIR="$SCRIPT_DIR/benchmark/assets/models"
VIDEO_DIR="$SCRIPT_DIR/benchmark/assets/videos"

phase_models() {
    mkdir -p "$MODEL_DIR"
    # Download benchmark models listed in model_list.json to $MODEL_DIR.
    local BASE_URL="https://sdk.deepx.ai/modelzoo/dxnn"
    local MODEL_LIST_JSON="$SCRIPT_DIR/benchmark/model_list.json"
    local OUTPUT_DIR="$MODEL_DIR"

    if ! command -v jq >/dev/null 2>&1; then
        echo "[ERROR] jq is required. Install with: sudo apt-get install -y jq"
        exit 1
    fi

    if [ ! -f "$MODEL_LIST_JSON" ]; then
        echo "[ERROR] model_list.json not found: $MODEL_LIST_JSON"
        exit 1
    fi

    local MODEL_VERSION
    MODEL_VERSION=$(jq -r '.version' "$MODEL_LIST_JSON")
    local MODEL_FILES
    mapfile -t MODEL_FILES < <(jq -r '.models[].file' "$MODEL_LIST_JSON")

    mkdir -p "$OUTPUT_DIR"

    echo "[INFO] Downloading ${#MODEL_FILES[@]} models (version=$MODEL_VERSION) to $OUTPUT_DIR"

    local model dest url tmp_dest
    for model in "${MODEL_FILES[@]}"; do
        dest="$OUTPUT_DIR/$model"
        if [ -s "$dest" ]; then
            echo "  [SKIP] $model (already exists)"
            continue
        fi
        if [ -e "$dest" ]; then
            echo "  [REDO] $model (empty or incomplete file)"
        fi
        url="$BASE_URL/$MODEL_VERSION/$model"
        tmp_dest=$(mktemp "$OUTPUT_DIR/.${model}.XXXXXX.part")
        echo "  [GET]  $model"
        if ! curl -fSL -o "$tmp_dest" "$url"; then
            echo "[ERROR] Failed to download $url"
            rm -f "$tmp_dest"
            exit 1
        fi
        mv "$tmp_dest" "$dest"
    done

    for model in "${MODEL_FILES[@]}"; do
        dest="$OUTPUT_DIR/$model"
        if [ ! -s "$dest" ]; then
            echo "[ERROR] Required model is still missing or empty: $dest"
            exit 1
        fi
    done

    echo "[OK] All models ready in $OUTPUT_DIR"
}

phase_videos() {
    mkdir -p "$VIDEO_DIR"
    # Download benchmark videos and extract to $VIDEO_DIR.
    local BASE_URL="https://sdk.deepx.ai"
    local SOURCE_PATH="res/video/benchmark_videos.tar.gz"
    local OUTPUT_DIR="$VIDEO_DIR"
    local REQUIRED_VIDEOS=(
        "od_benchmark_video.mp4"
        "obb_benchmark_video.mp4"
    )

    mkdir -p "$OUTPUT_DIR"

    local missing_videos=()
    local video
    for video in "${REQUIRED_VIDEOS[@]}"; do
        if [ ! -s "$OUTPUT_DIR/$video" ]; then
            missing_videos+=("$video")
        fi
    done

    if [ ${#missing_videos[@]} -eq 0 ]; then
        echo "[OK] Benchmark videos already ready in $OUTPUT_DIR"
        ls -lh "$OUTPUT_DIR"/*.mp4 2>/dev/null || true
        return 0
    fi

    local ARCHIVE EXTRACT_DIR
    ARCHIVE=$(mktemp "$OUTPUT_DIR/.benchmark_video.XXXXXX.tar.gz")
    EXTRACT_DIR=$(mktemp -d "$OUTPUT_DIR/.benchmark_video_extract.XXXXXX")

    cleanup() {
        rm -f "${ARCHIVE:-}"
        rm -rf "${EXTRACT_DIR:-}"
    }

    trap cleanup INT TERM EXIT

    echo "[INFO] Missing benchmark videos: ${missing_videos[*]}"
    echo "[INFO] Downloading benchmark videos archive to $OUTPUT_DIR"
    if ! curl -fSL -o "$ARCHIVE" "$BASE_URL/$SOURCE_PATH"; then
        echo "[ERROR] Failed to download $BASE_URL/$SOURCE_PATH"
        exit 1
    fi

    echo "[INFO] Extracting ..."
    tar -xzf "$ARCHIVE" -C "$EXTRACT_DIR"

    local extracted
    for video in "${REQUIRED_VIDEOS[@]}"; do
        extracted=$(find "$EXTRACT_DIR" -type f -name "$video" -print -quit)
        if [ -z "$extracted" ]; then
            echo "[ERROR] Required benchmark video not found after extraction: $video"
            exit 1
        fi
        mv "$extracted" "$OUTPUT_DIR/$video"
    done

    echo "[OK] Benchmark videos ready in $OUTPUT_DIR"
    ls -lh "$OUTPUT_DIR"/*.mp4 2>/dev/null || true

    # Clean the temp archive/extract dir now and drop the EXIT trap, so it does
    # not fire at script exit when these function-locals are out of scope
    # (which tripped 'ARCHIVE: unbound variable' under `set -u`).
    cleanup
    trap - INT TERM EXIT
}

case "${1:-all}" in
    all)    phase_models; phase_videos ;;
    models) phase_models ;;
    videos) phase_videos ;;
    *) echo "Usage: $0 [all|models|videos]" >&2; exit 1 ;;
esac
echo "[setup_data.sh] done: ${1:-all}"
