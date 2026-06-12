#!/usr/bin/env python3
# Copyright (C) 2018- DEEPX Ltd. All rights reserved.
"""
Common argument parser for DX-APP inference examples.

Consolidates per-model ``parse_args()`` into one reusable function so that
camera, RTSP, save, loop, and dump-tensors options are available uniformly
across **all** models without touching each thin wrapper individually.

Usage (from any model wrapper)::

    from common.runner import parse_common_args

    # Minimal — description only
    args = parse_common_args("YOLOv5 Sync Inference")

    # SR / depth / denoising models that need --output
    args = parse_common_args("ESPCN Sync Inference", include_output=True)
"""

import argparse


def parse_common_args(
    description: str = "DX-APP Inference",
    *,
    include_output: bool = False,
) -> argparse.Namespace:
    """Parse common inference arguments.

    Standard options (always available):

    ===============  ========================================
    Option           Description
    ===============  ========================================
    --model, -m      Model path (``.dxnn``)
    --image, -i      Input image **or directory** path
    --video, -v      Input video path
    --camera, -c     Camera device ID (e.g. ``0``)
    --rtsp, -r       RTSP stream URL
    --display        Show output window (default on)
    --no-display     Disable display output
    --save, -s       Save output frames / images
    --save-dir       Output save directory (default: auto)
    --loop, -l       Inference loop count (default 1, bare --loop = 2)
    --dump-tensors   Dump raw inference tensors
    --config         Path to config.json (auto-detected)
    ===============  ========================================

    Args:
        description: ``argparse`` description string.
        include_output: If ``True``, add ``--output`` argument
            (used by super-resolution / depth / denoising models).

    Returns:
        Parsed :class:`argparse.Namespace`.
    """
    parser = argparse.ArgumentParser(
        description=description, allow_abbrev=False)

    # ---- Model path ----
    parser.add_argument(
        "--model", "-m", type=str, required=True, help="Model path (.dxnn)"
    )

    # ---- Input source (mutually exclusive) ----
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--image", "-i", type=str, default=None,
        help="Input image path or directory (default: task-appropriate sample)"
    )
    input_group.add_argument(
        "--video", "-v", type=str, default=None, help="Input video path"
    )
    input_group.add_argument(
        "--camera", "-c", type=int, default=None, help="Camera device ID (e.g. 0)"
    )
    input_group.add_argument(
        "--rtsp", "-r", type=str, default=None, help="RTSP stream URL"
    )

    # ---- Display ----
    parser.add_argument(
        "--display", action="store_true", default=True,
        help="Show output window (default: True)",
    )
    parser.add_argument(
        "--no-display", dest="display", action="store_false",
        help="Disable display output",
    )

    # ---- Save / Loop / Dump ----
    parser.add_argument(
        "--save", "-s", action="store_true", default=False,
        help="Save output frames / images",
    )
    parser.add_argument(
        "--save-dir", type=str, default=None,
        help="Output save directory (default: artifacts/python_example/)",
    )
    parser.add_argument(
        "--loop", "-l", type=int, nargs="?", const=2, default=1,
        help="Number of inference loops (default: 1). "
             "Use --loop without a value for 2 loops, or --loop N.",
    )
    parser.add_argument(
        "--dump-tensors", action="store_true", default=False,
        help="Dump raw inference tensors for debugging",
    )

    # ---- Config ----
    parser.add_argument(
        "--config", type=str, default=None,
        help="Path to config.json (auto-detected if omitted)",
    )

    # ---- Verbosity ----
    parser.add_argument(
        "--show-log", action="store_true", default=False,
        help="Show detailed per-frame/image [INFO] logs (default: quiet)",
    )

    # ---- Optional: output path (SR / depth / denoising) ----
    if include_output:
        parser.add_argument(
            "--output", "-o", type=str, help="Output file path"
        )

    return parser.parse_args()
