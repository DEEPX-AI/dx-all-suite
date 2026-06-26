# SPDX-License-Identifier: Apache-2.0
"""Registry of showcases under reproducibility verification.

Single source of truth tying each showcase to: its verbatim end-user prompt,
the sub-project it routes to (the runner ``workdir`` is always the suite root —
the prompt itself drives /dx-skill-router routing), the ``scenario_key`` the
autopilot runner uses for output-dir detection, the equivalence checker, and the
ground-truth thresholds parsed from the showcase's expected_output.txt / session.log.

All showcases are ACTIVE (each verified at least once with claude-code + cursor). To pause
one, set ``active=False`` and it is skipped by ``active_showcases()`` / the driver default.
See README.md in this directory for how to add or refresh a showcase.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(frozen=True)
class ShowcaseSpec:
    name: str
    prompt: str            # verbatim end-user prompt (sole input)
    route: str             # "compiler" | "dx_app" | "dx_stream" | "suite"
    scenario_key: str      # runner output-dir detection key
    checker: str           # checks.py checker id: "export" | "squat" | ...
    active: bool = True
    ground_truth: Dict = field(default_factory=dict)


SHOWCASES: Dict[str, ShowcaseSpec] = {
    # ----------------------------- ACTIVE pilots ----------------------------- #
    "ultralytics-yolo-deepx-export": ShowcaseSpec(
        name="ultralytics-yolo-deepx-export",
        prompt=(
            "Export the Ultralytics YOLO26n detection model to DeepX NPU format "
            "using the one-shot format=deepx export path, then run inference on "
            "the Ultralytics bus sample image."
        ),
        route="compiler",
        scenario_key="compiler",
        checker="export",
        active=True,
        ground_truth={
            "dxnn_size_bytes": 6_890_634,
            "dxnn_size_tolerance": 0.20,   # ±20%
            "expected_detections": 5,
            "detections_tolerance": 2,     # ±2 objects
            "expected_classes": ["bus", "person"],
        },
    ),
    "mini-game-squat-fitness": ShowcaseSpec(
        name="mini-game-squat-fitness",
        # The original showcase prompt said "validate with sample/squat_demo.mp4" —
        # but that relative path only resolved because a REAL squat clip was staged in
        # the creation env. A fresh end user has no such file, so agents fabricated a
        # bogus/synthetic clip → 0 reps. The original clip is now committed at
        # dx-agent-dev-showcase/mini-game-squat-fitness/sample/squat_demo.mp4, so we
        # point the prompt at that suite-root-relative path (runner workdir = suite
        # root) — reproducible and portable (no machine-specific absolute path).
        prompt=(
            "Build a squat-counting fitness mini-game using yolo26n-pose on DEEPX NPU, "
            "validate with dx-agent-dev-showcase/mini-game-squat-fitness/sample/squat_demo.mp4"
        ),
        route="dx_app",
        scenario_key="dx_app",
        checker="squat",
        active=True,
        ground_truth={
            "min_squats_counted": 1,       # original counted 4; "works" = >=1
            "ifactory_methods": [
                "create_preprocessor", "create_postprocessor",
                "create_visualizer", "get_model_name", "get_task_type",
            ],
        },
    ),

    # ------------------- Heavy: GPU 40-epoch retrain × 4 ------------------ #
    # GPU 40-epoch retrain + INT8 NPU + 4-way eval — heavy; verify with both
    # claude-code and cursor in a later cycle (user-requested TODO).
    "ultralytics-retrain-eval-deepx-export-braintumor": ShowcaseSpec(
        name="ultralytics-retrain-eval-deepx-export-braintumor",
        prompt=(
            "Using the Ultralytics Python package, adapt the base yolo26n model for a medical "
            "edge device that screens MRI/CT brain scans for tumors. The stock yolo26n is a "
            "general COCO-trained detector that does not recognize brain tumors, so fine-tune "
            "(retrain) it on the Ultralytics brain-tumor dataset (classes: negative, positive) "
            "on the local GPU for about 40 epochs to produce a domain-optimized tumor-detection "
            "model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model "
            "and the retrained model in two forms each: (a) the PyTorch model in fp32 on the "
            "GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). "
            "Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with "
            "a short analysis of the accuracy gain and the INT8 quantization effect. Work "
            "autonomously to completion without asking for confirmation or approval; make "
            "default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (both "
            ".dxnn model dirs, the measured FPS/mAP numbers, report.md), not just a plan."
        ),
        route="suite", scenario_key="suite", checker="retrain_eval", active=True,
    ),
    "ultralytics-retrain-eval-deepx-export-pills": ShowcaseSpec(
        name="ultralytics-retrain-eval-deepx-export-pills",
        prompt=(
            "Using the Ultralytics Python package, adapt the base yolo26n model for a "
            "pharmaceutical pill identification/counting station. The stock yolo26n is a general "
            "COCO-trained detector that does not recognize medical pills as a dedicated class, "
            "so fine-tune (retrain) it on the Ultralytics medical-pills dataset (class: pill) on "
            "the local GPU for about 40 epochs to produce a domain-optimized pill-detection "
            "model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model "
            "and the retrained model in two forms each: (a) the PyTorch model in fp32 on the "
            "GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). "
            "Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a "
            "short analysis of the accuracy gain and the INT8 quantization effect. Work "
            "autonomously to completion without asking for confirmation or approval; make "
            "default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (both "
            ".dxnn model dirs, the measured FPS/mAP numbers, report.md), not just a plan. Before "
            "writing any code, READ the dx-compiler knowledge base toolsets "
            "dx-compiler/.deepx/toolsets/ultralytics-train-eval.md and "
            "dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md and follow them. Also, "
            "after evaluation, save an annotated detection SAMPLE IMAGE — the retrained model "
            "run on a representative validation image with bounding boxes + class labels drawn — "
            "as sample_detect.jpg in the session directory. Respond in English."
        ),
        route="suite", scenario_key="suite", checker="retrain_eval", active=True,
    ),
    "ultralytics-retrain-eval-deepx-export-ppe": ShowcaseSpec(
        name="ultralytics-retrain-eval-deepx-export-ppe",
        prompt=(
            "Using the Ultralytics Python package, adapt the base yolo26n model for a "
            "construction/factory site-safety camera that checks PPE (personal protective "
            "equipment) compliance. The stock yolo26n is a general COCO-trained detector that "
            "does not recognize construction PPE items, so fine-tune (retrain) it on the "
            "Ultralytics construction-ppe dataset (classes: helmet, gloves, vest, boots, "
            "goggles) on the local GPU for about 40 epochs to produce a domain-optimized "
            "PPE-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the "
            "base model and the retrained model in two forms each: (a) the PyTorch model in fp32 "
            "on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via "
            "format=deepx). Write report.md comparing all four results (base vs retrained, fp32 "
            "vs INT8) with a short analysis of the accuracy gain and the INT8 quantization "
            "effect. Work autonomously to completion without asking for confirmation or "
            "approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL "
            "ARTIFACTS (both .dxnn model dirs, the measured FPS/mAP numbers, report.md), not "
            "just a plan."
        ),
        route="suite", scenario_key="suite", checker="retrain_eval", active=True,
    ),
    "ultralytics-retrain-eval-deepx-export-wildlife": ShowcaseSpec(
        name="ultralytics-retrain-eval-deepx-export-wildlife",
        prompt=(
            "Using the Ultralytics Python package, adapt the base yolo26n model for a "
            "wildlife-monitoring / safari camera scenario. The stock yolo26n is a general "
            "COCO-trained detector that does not reliably recognize African wildlife species, "
            "so fine-tune (retrain) it on the Ultralytics african-wildlife dataset (classes: "
            "buffalo, elephant, rhino, zebra) on the local GPU for about 40 epochs to produce a "
            "domain-optimized model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH "
            "the base model and the retrained model in two forms each: (a) the PyTorch model in "
            "fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via "
            "format=deepx). Write report.md comparing all four results (base vs retrained, fp32 "
            "vs INT8) with a short analysis of the accuracy gain and the INT8 quantization "
            "effect. Work autonomously to completion without asking for confirmation or "
            "approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL "
            "ARTIFACTS (both .dxnn model dirs, the measured FPS/mAP numbers, report.md), not "
            "just a plan. Before writing any code, READ the dx-compiler knowledge base toolsets "
            "dx-compiler/.deepx/toolsets/ultralytics-train-eval.md and "
            "dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md and follow them. Also, "
            "after evaluation, save an annotated detection SAMPLE IMAGE — the retrained model "
            "run on a representative validation image with bounding boxes + class labels drawn — "
            "as sample_detect.jpg in the session directory. Respond in English."
        ),
        route="suite", scenario_key="suite", checker="retrain_eval", active=True,
    ),
    # FULL verbatim prompt (the README abbreviates it). Original validated on
    # /tmp/sc-build/ocr_input/ocr_demo.mp4 (build-time temp, absent for a fresh user);
    # repathed to the committed suite-root sample (runner workdir = suite root).
    "paddleocr-video-ocr": ShowcaseSpec(
        name="paddleocr-video-ocr",
        prompt=(
            "Build an OCR inference app whose text detection + recognition runs on the "
            "DEEPX DX-M1 NPU. The app must accept BOTH a video file (--source <path.mp4>) "
            "and a live webcam (--source <camera_index>), run NPU OCR on each frame, "
            "overlay the detected text boxes and the recognized strings, and write an "
            "annotated output video (optionally show a live window). Save one annotated "
            "sample frame as sample_detect.jpg. Validate it on the provided demo video at "
            "dx-agent-dev-showcase/paddleocr-video-ocr/sample/ocr_demo.mp4. Provide "
            "setup.sh, run.sh, and a short README reporting the measured per-frame "
            "latency / FPS on the NPU."
        ),
        route="dx_app", scenario_key="dx_app", checker="ocr", active=True,
        ground_truth={"min_texts": 1},
    ),
    # Verbatim prompt (no input-path issue: the agent creates its own sample_input.pdf).
    # Self-contained requires vendoring the fork's `rapid_doc/` package into the app.
    "rapiddoc-pdf2md": ShowcaseSpec(
        name="rapiddoc-pdf2md",
        prompt=(
            "Build a PDF-to-Markdown app whose document-parsing pipeline (layout analysis + "
            "OCR + table/formula recognition) runs on the DEEPX DX-M1 NPU. Input a PDF "
            "(digital or scanned), output structured Markdown (+ JSON) preserving headings and "
            "tables. Support --parse-method auto|txt|ocr. Provide setup.sh, run.sh, a sample "
            "input PDF + its rendered Markdown output (sample_output.md), and a README "
            "reporting NPU stage timings."
        ),
        route="dx_app", scenario_key="dx_app", checker="generic_app", active=True,
    ),
    # FULL verbatim prompt (the README abbreviates it with "..."). Original validated on
    # /tmp/sc-build/stretch_input/stretching_demo.mp4 (build-time temp, absent for a fresh
    # user); repathed to the committed suite-root sample (runner workdir = suite root).
    "mini-game-stretching-coach": ShowcaseSpec(
        name="mini-game-stretching-coach",
        prompt=(
            "Using the yolo26n-pose model on the DEEPX NPU, build a simple arcade-style "
            "stretching mini-game. The game guides the user through three stretch poses, "
            "one stage at a time: (1) extend both arms straight overhead, (2) bend forward "
            "at the waist (forward fold), and (3) pull the head to one side with one hand "
            "for a neck stretch.\n\n"
            "For each stage, render a small coach avatar in a top-left panel that "
            "demonstrates the current target stretch. IMPORTANT — the coach must look like "
            "a REAL PERSON, not a stick figure: draw it as a FILLED, PROCEDURAL HUMANOID "
            "built from the pose keypoints — a round head, a filled torso/pelvis body, and "
            "tapered LIMB CAPSULES (filled rounded segments for upper-arm/forearm and "
            "thigh/shin) with smooth filled joints, shaded so it reads as a human body "
            "silhouette. Do NOT draw it as thin stick-figure lines or a bare keypoint "
            "skeleton. Animate the coach so it feels alive — cycle smoothly between a "
            "neutral standing pose and the full target stretch pose (a looped "
            "demonstration). Show the stretch name and a short text instruction next to "
            "the coach.\n\n"
            "Recognize each pose from the player's body keypoints (wrists above the head "
            "for the overhead reach; torso folded forward with shoulders dropped toward "
            "hips for the waist bend; one hand raised beside the head for the neck "
            "stretch). When the user holds the matching pose briefly, advance to the next "
            "stage; clear the game when all three are done.\n\n"
            "Overlay an arcade-style UI on each frame: STAGE n/3, the animated humanoid "
            "coach avatar, the target stretch name + instruction, a HOLD progress "
            "indicator, and GOOD! / CLEAR! feedback. The generated app must support both a "
            "video-file input and a live camera input, selectable at runtime (e.g. "
            "--video <file> or --camera <id>). Implement and validate it using the "
            "provided demo video at "
            "dx-agent-dev-showcase/mini-game-stretching-coach/sample/stretching_demo.mp4, "
            "which contains a person performing the three stretches in sequence; derive "
            "the coach target-pose shapes as needed (procedurally or from representative "
            "frames of that video). When run on a video file, save an annotated output "
            "video so the result can be reviewed.\n\n"
            "Work autonomously to completion without asking for confirmation or approval; "
            "make default decisions per the knowledge base and PRODUCE THE ACTUAL "
            "ARTIFACTS (runnable app + setup.sh + run.sh, validated headless --no-display "
            "--save on the demo video). Respond in English."
        ),
        route="dx_app", scenario_key="dx_app", checker="stretch", active=True,
        ground_truth={
            "ifactory_methods": [
                "create_preprocessor", "create_postprocessor",
                "create_visualizer", "get_model_name", "get_task_type",
            ],
        },
    ),
}


def active_showcases() -> Dict[str, ShowcaseSpec]:
    return {k: v for k, v in SHOWCASES.items() if v.active}
