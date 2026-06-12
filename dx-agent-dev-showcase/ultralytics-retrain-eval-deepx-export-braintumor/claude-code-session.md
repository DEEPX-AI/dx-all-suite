# Fine-tune YOLO for brain tumor detection and evaluate models

## Session summary

| Metric | Value |
|---|---|
| Model | `claude-opus-4-8` |
| Wall-clock | ~8.6 min |
| Agent turns | 91 |
| Output tokens | 103,326 |
| Cost (reported) | $3.74 |
| Tools | Bash×15, Read×9, Write×8, Skill×5, TaskCreate×1 |
| Skills | dx-skill-router → dx-agentic-brainstorm → dx-swe-writing-plans → dx-agentic-tdd → dx-agentic-verify |
| Toolsets | `ultralytics-train-eval`, `ultralytics-deepx-export` |


## Session Info

- **Session ID:** `821ce4fb-77f1-4d26-8ef5-cac0f2c14b9e`
- **Working Dir:** `/data/home/dhyang/github/dx-all-suite-ultralytics`
- **Branch:** feature/ultralytics-integration
- **Claude Code:** v2.1.156
- **Permission Mode:** bypassPermissions
- **Start:** 2026-06-11T01:22:18.182Z
- **End:** 2026-06-11T01:34:58.271Z

## Conversation

### Turn 1 [2026-06-11 01:22:18 UTC]

**User:**

> Using the Ultralytics Python package, adapt the base yolo26n model for a medical edge device that screens MRI/CT brain scans for tumors. The stock yolo26n is a general COCO-trained detector that does not recognize brain tumors, so fine-tune (retrain) it on the Ultralytics brain-tumor dataset (classes: negative, positive) on the local GPU for about 40 epochs to produce a domain-optimized tumor-detection model. Then evaluate accuracy (mAP50-95) and speed (FPS) for BOTH the base model and the retrained model in two forms each: (a) the PyTorch model in fp32 on the GPU, and (b) its DeepX export (.dxnn, INT8 on the DX-M1 NPU, via format=deepx). Write report.md comparing all four results (base vs retrained, fp32 vs INT8) with a short analysis of the accuracy gain and the INT8 quantization effect. Work autonomously to completion without asking for confirmation or approval; make default decisions per the knowledge base and PRODUCE THE ACTUAL ARTIFACTS (both .dxnn model dirs, the measured FPS/mAP numbers, report.md), not just a plan. Before writing any code, READ the dx-compiler knowledge base toolsets dx-compiler/.deepx/toolsets/ultralytics-train-eval.md and dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md and follow them. Also, after evaluation, save an annotated detection SAMPLE IMAGE — the retrained model run on a representative validation image with bounding boxes + class labels drawn — as sample_detect.jpg in the session directory. Respond in English.

✅ **Skill** `dx-skill-router`
  > Launching skill: dx-skill-router

**Claude:**

`[DX-AGENTIC-DEV: START]`

```
 ███████████   █████████ ████████ ████████  ████      ████
 ███     █████ ███░░░░░░░███░░░░░░███   ███  ░████   ████░░
 ███        ██░███░      ██░░     ███   ███░   █████████░░
 ███        ████████████ ████████ ████████░░    ░█████░░░
 ███        ██░███░░░░░░░██░░░░░░░███░░░░░░  ██████████
 ███     █████░███░      ██░      ███░   ████████░░░░████
 ███████████░░░█████████ ████████ ██████████░░░░░░    ████
  ░░░░░░░░░░░   ░░░░░░░░░ ░░░░░░░░ ░░░░░░░░░░          ░░░░
        DX-AGENTIC-DEV · on-device NPU
```

Per the universal pre-flight HARD GATE, my first action is to invoke the skill router.

---

### Turn 2 [2026-06-11 01:22:29 UTC]

**User:**

> Base directory for this skill: /data/home/dhyang/github/dx-all-suite-ultralytics/.claude/skills/dx-skill-router

<!-- Thin Claude Code wrapper — canonical skill doc lives in .deepx/ -->

Read and follow the complete skill documentation at `.deepx/skills/dx-skill-router/SKILL.md`.


✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/.deepx/skills/dx-skill-router/SKILL.md`
  > 1	---
2	name: dx-skill-router
3	description: Use when starting any conversation - establishes how to discover and invoke dx-* skills, requiring skill invocation before ANY response including clarifyi…

✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/.deepx/toolsets/ultralytics-train-eva…`
  > 1	# Ultralytics Retrain + Evaluate (domain optimization) → DeepX
2	
3	> How to **adapt a base YOLO model to a specific domain** with the Ultralytics Python
4	> package and **evaluate it fairly** — bo…

✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/.deepx/toolsets/ultralytics-deepx-exp…`
  > 1	# Ultralytics → DeepX Export Reference
2	
3	> One-shot `format=deepx` exporter built into Ultralytics YOLO. Converts a YOLO
4	> `.pt` to a deployable DeepX NPU model (`.dxnn`) in a single command —…

✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/CLAUDE.md`
  > 1	# DEEPX DX-COM Compiler — Claude Code Entry Point
2	
3	> Self-contained entry point for Claude Code / OpenCode. Read this file first.
4	
5	## Response Language
6	
7	Match your response language to …

✅ **Skill** `dx-agentic-brainstorm`
  > Launching skill: dx-agentic-brainstorm

**Claude:**

This is a cross-project autonomous task (Ultralytics retrain + DeepX export + evaluation). The user explicitly requires reading two dx-compiler KB toolsets before any code. Let me read those plus the compiler routing context first.
I've read both mandatory KB toolsets and the dx-compiler routing context. I'm running as **Opus 4.8** (a recommended model), so no model notice is needed.

This is a **dx-compiler-only** session (the entire flow uses Ultralytics' own train/val/export backend — no dx_app IFactory app is requested). Per the Mandatory Process Skill Sequence and Autopilot Mode rules, I'll proceed: brainstorm (KB defaults, self-review) → plan → tdd → verify. Let me start the brainstorm.

---

### Turn 3 [2026-06-11 01:23:10 UTC]

**User:**

> Base directory for this skill: /data/home/dhyang/github/dx-all-suite-ultralytics/.claude/skills/dx-agentic-brainstorm

<!-- Thin Claude Code wrapper — canonical skill doc lives in .deepx/ -->

Read and follow the complete skill documentation at `.deepx/skills/dx-agentic-brainstorm/SKILL.md`.


✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/.deepx/skills/dx-agentic-brainstorm/SKILL.md`
  > 1	---
2	name: dx-agentic-brainstorm
3	description: "DEEPX build brainstorming with model registry check and sub-project routing."
4	---
5	
6	# Skill: DEEPX Build Brainstorming
7	
8	> For the general …

✅ **Bash** `echo "=== date ==="; date +%Y%m%d-%H%M%S
echo "=== GPU ==="; nvidia-smi --query-gpu=name,memory.tot…`
  > === date ===
20260611-102324
=== GPU ===
name, memory.total [MiB], memory.used [MiB]
NVIDIA GeForce RTX 5060 Ti, 16311 MiB, 15 MiB
=== venvs in suite root ===
/data/home/dhyang/github/dx-all-suite-ul…

✅ **Bash** `VENV=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-runtime/venv-dx-runtime
source "$VENV/bin…`
  > === python ===
/data/home/dhyang/github/dx-all-suite-ultralytics/dx-runtime/venv-dx-runtime/bin/python
Python 3.12.3
=== imports ===
OK   torch 2.12.0+cu130
OK   ultralytics 8.4.63
OK   dx_com 2.3.0-…

✅ **Bash** `cd /data/home/dhyang/github/dx-all-suite-ultralytics
bash dx-runtime/scripts/sanity_check.sh --dx_r…`
  > [44m[INFO][0m[94m Checking required packages for SanityCheck... [0m
[44m[INFO][0m[94m ✅ lsmod command is available (kmod package is installed). [0m
[44m[INFO][0m[94m ✅ lspci command is ava…

✅ **Bash** `VENV=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-runtime/venv-dx-runtime
source "$VENV/bin…`
  > brain-tumor.yaml exists: True
---
# Ultralytics 🚀 AGPL-3.0 License - https://ultralytics.com/license

# Brain-tumor dataset by Ultralytics
# Documentation: https://docs.ultralytics.com/datasets/detec…

✅ **TaskCreate** `{"tasks": "[\n{\"task\":\"Brainstorm spec + plan (autopilot, KB defaults)\",\"status\":\"in_progres…`
  > <tool_use_error>InputValidationError: TaskCreate failed due to the following issues:
The required parameter `subject` is missing
The required parameter `description` is missing
An unexpected paramete…

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/docs/superpowers/specs/2026-06-11-yolo26n-braintu…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/docs/superpowers/specs/2026-06-11-yolo26n-braintumor-retrain-eval-design.md (file state is current in your context — no…

✅ **Skill** `dx-swe-writing-plans`
  > Launching skill: dx-swe-writing-plans

**Claude:**

The brainstorm skill's model-registry/sub-project routing is for dx_app/dx_stream; this is a dx-compiler Ultralytics flow, so I'll ground the spec in real environment facts. Let me probe the environment (this is not code generation — it informs the spec) and create a task list.
Everything is present in `venv-dx-runtime`: torch+CUDA, ultralytics 8.4.63, dx_com 2.3.0-rc.5, dx_engine 3.3.2. Now the mandatory NPU sanity check (needed for INT8 `.dxnn` eval) and dataset config:
All prerequisites pass: **NPU sanity check PASSED**, brain-tumor.yaml present (classes `negative`/`positive`, 893 train / 223 val, auto-downloads), GPU + full software stack ready. Now I'll write the brainstorm spec (autopilot: KB defaults + self-review), set up task tracking, then the plan.
Task tool is deferred; I'll track progress inline to save overhead. Writing the brainstorm spec now (self-reviewed against KB defaults):
Spec written and self-approved (autopilot self-review). Now the plan (step 3):

---

### Turn 4 [2026-06-11 01:24:28 UTC]

**User:**

> Base directory for this skill: /data/home/dhyang/github/dx-all-suite-ultralytics/.claude/skills/dx-swe-writing-plans

<!-- Thin Claude Code wrapper — canonical skill doc lives in .deepx/ -->

Read and follow the complete skill documentation at `.deepx/skills/dx-swe-writing-plans/SKILL.md`.


✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/.deepx/skills/dx-swe-writing-plans/SKILL.md`
  > 1	---
2	name: dx-swe-writing-plans
3	description: Use when you have a spec or requirements for a multi-step task, before touching code
4	---
5	
6	# Writing Plans
7	
8	## Overview
9	
10	Write comprehe…

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/docs/superpowers/plans/2026-06-11-yolo26n-braintu…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/docs/superpowers/plans/2026-06-11-yolo26n-braintumor-retrain-eval.md (file state is current in your context — no need t…

✅ **Skill** `dx-agentic-tdd`
  > Launching skill: dx-agentic-tdd

**Claude:**

All prerequisites verified. Writing the implementation plan now (autopilot: self-approved against KB):
**Plan (saved to `docs/superpowers/plans/2026-06-11-yolo26n-braintumor-retrain-eval.md`):**

A background `pipeline.py` runs the long GPU/NPU work sequentially — base fp32 eval → train 40 epochs → retrained fp32 eval → export both to DeepX (INT8 `.dxnn`) → both NPU INT8 evals → annotated sample image — writing `metrics.json` and real stdout to `session.log`. While it runs I generate the mandatory artifacts (setup.sh/run.sh/verify.py/README.md), then build `report.md` from `metrics.json` and run the verify gate. Session dir: `dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/`.

Now the TDD step (define acceptance criteria → generate → verify):

---

### Turn 5 [2026-06-11 01:25:48 UTC]

**User:**

> Base directory for this skill: /data/home/dhyang/github/dx-all-suite-ultralytics/.claude/skills/dx-agentic-tdd

<!-- Thin Claude Code wrapper — canonical skill doc lives in .deepx/ -->

Read and follow the complete skill documentation at `.deepx/skills/dx-agentic-tdd/SKILL.md`.


✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/.deepx/skills/dx-agentic-tdd/SKILL.md`
  > 1	---
2	name: dx-agentic-tdd
3	description: "DEEPX build validation order — factory, pipeline, and integration checks."
4	---
5	
6	# Skill: DEEPX Build Validation Order
7	
8	> For the general Red-Gre…

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > created: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/pipeline.py (file state is current in your …

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > py_compile OK

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > Command running in background with ID: bd24t3vqe. Output is being written to: /tmp/claude-1000/claude-1000/-data-home-dhyang-github-dx-all-suite-ultralytics/821ce4fb-77f1-4d26-8ef5-cac0f2c14b9e/tasks…

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/setup.sh (file state is current in your con…

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/run.sh (file state is current in your conte…

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/verify.py (file state is current in your co…

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/README.md (file state is current in your co…

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > === bash -n setup.sh ===
OK
=== bash -n run.sh ===
OK
=== py_compile verify.py ===
OK

✅ **Bash** `tail -40 /tmp/claude-1000/claude-1000/-data-home-dhyang-github-dx-all-suite-ultralytics/821ce4fb-77…`
  > <persisted-output>
Output too large (37KB). Full output saved to: /home/dhyang/.claude/projects/-data-home-dhyang-github-dx-all-suite-ultralytics/821ce4fb-77f1-4d26-8ef5-cac0f2c14b9e/tool-results/bg5…

✅ **Bash** `sleep 1; echo "waiting on background pipeline bd24t3vqe"`
  > waiting on background pipeline bd24t3vqe

**Claude:**

TDD acceptance criteria (RED) for this session: `pipeline.py` compiles; `metrics.json` is valid JSON with all 4 points carrying numeric `map`/`map50`/`fps`, retrained-fp32 mAP > base-fp32 mAP (domain gain); both `*_deepx_model/*.dxnn` exist; `report.md` has the 4-row table; `sample_detect.jpg` is a valid non-empty image; shell scripts pass `bash -n`; `verify.py` compiles and exits PASS. Now GREEN — create the session dir and pipeline driver:
`pipeline.py` compiles. Launching it in the background (harness will re-invoke me on completion — no sleep-polling):
Pipeline running in the background. Now I'll generate the mandatory artifacts while it runs (per the compilation-parallel workflow rule). Writing `setup.sh`, `run.sh`, `verify.py`, `README.md`:
Now verify the artifacts (syntax checks) and check pipeline progress:
All artifacts pass syntax checks. Let me check the pipeline's progress so far:
Progress is healthy — base fp32 eval done, training now at **epoch 8/40** (~5 s/epoch on the RTX 5060 Ti, so training will finish shortly, then exports + NPU INT8 evals + sample image follow). All mandatory artifacts are generated and syntax-checked:

- ✅ `pipeline.py` (compiles), launched in background (`session.log` filling)
- ✅ `setup.sh`, `run.sh` (`bash -n` OK), `verify.py` (compiles), `README.md`
- ✅ Spec + plan written and self-approved

The pipeline is running detached; I'll be re-invoked automatically when it exits, then I'll build `report.md` from `metrics.json`, run the `verify.py` gate, confirm `sample_detect.jpg` + both `.dxnn` dirs, and finalize. Pausing here rather than sleep-polling.
I'll await the background pipeline's completion notification before finalizing.

---

### Turn 6 [2026-06-11 01:32:56 UTC]

**User:**

> <task-notification>
<task-id>bd24t3vqe</task-id>
<tool-use-id>toolu_01Jd4pYmZ96rFPTAa6tNKRJq</tool-use-id>
<output-file>/tmp/claude-1000/claude-1000/-data-home-dhyang-github-dx-all-suite-ultralytics/821ce4fb-77f1-4d26-8ef5-cac0f2c14b9e/tasks/bd24t3vqe.output</output-file>
<status>completed</status>
<summary>Background command "Run the full train/eval/export pipeline (background)" completed (exit code 0)</summary>
</task-notification>

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > === metrics.json ===
{
  "meta": {
    "dataset": "brain-tumor.yaml",
    "classes": [
      "negative",
      "positive"
    ],
    "imgsz": 640,
    "epochs": 40,
    "batch": 16,
    "seed": 0,
  …

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > === deepx model dirs ===
/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/yolo26n_braintumor_deepx_model/:
total 6188
drwx…

✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude…`

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > verify image: /data/home/dhyang/github/datasets/brain-tumor/images/val/val_1 (1).jpg
fp32 PyTorch : 1 boxes, classes=[1]
WARNING ⚠️ Unable to automatically guess model task, assuming 'task=detect'. E…

✅ **Write** `/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude…`
  > File created successfully at: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/report.md (file state is current in your co…

✅ **Skill** `dx-agentic-verify`
  > Launching skill: dx-agentic-verify

**Claude:**

The pipeline completed with exit code 0 (all stages OK). Let me read the results:
All four points captured, all 8 stages OK (wall-clock ~5.8 min). Let me confirm the `.dxnn` dirs + sample image, then run the verify gate:
Both `.dxnn` files present (retrained 6.3 MB vs base 6.9 MB — smaller nc=2 head), sample image is a valid 512×512 JPEG with 1 detection. Let me view the sample and run the verify gate:
The sample image shows a brain MRI with a `positive 0.90` tumor detection box drawn by the retrained model — exactly the deliverable. Now the verify gate:
`verify.py` → **RESULT: PASS** (fp32 and INT8 both detect 1 `positive` box, count_diff=0). Now writing the comparison report:
`report.md` written. Now the final verification step (step 5):

---

### Turn 7 [2026-06-11 01:34:11 UTC]

**User:**

> Base directory for this skill: /data/home/dhyang/github/dx-all-suite-ultralytics/.claude/skills/dx-agentic-verify

<!-- Thin Claude Code wrapper — canonical skill doc lives in .deepx/ -->

Read and follow the complete skill documentation at `.deepx/skills/dx-agentic-verify/SKILL.md`.


✅ **Read** `/data/home/dhyang/github/dx-all-suite-ultralytics/.deepx/skills/dx-agentic-verify/SKILL.md`
  > 1	---
2	name: dx-agentic-verify
3	description: "DEEPX build verification checklists — dx_app, dx_stream, and cross-project."
4	---
5	
6	# Skill: DEEPX Build Verification Checklists
7	
8	> For the gen…

✅ **Bash** `SESS=/data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_c…`
  > === Mandatory deliverables presence ===
  OK   pipeline.py (9165 bytes)
  OK   setup.sh (2966 bytes)
  OK   run.sh (1125 bytes)
  OK   README.md (2757 bytes)
  OK   verify.py (3322 bytes)
  OK   sess…

✅ **Bash** `GENROOT="$(d="/data/home/dhyang/github/dx-all-suite-ultralytics"; while [ "$d" != / ]; do [ -f "$d/…`
  > jsonl: /data/home/dhyang/github/dx-all-suite-ultralytics/dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/claude-stream.jsonl
md: /data/home/dhyang/github/dx-all-suite-ultr…

**Claude:**

Running the final verification checklist — deliverable presence, session.log authenticity, and report/metrics consistency:
All verification gates pass:
- **All mandatory deliverables present** (pipeline.py, setup.sh, run.sh, README.md, verify.py, session.log, metrics.json, report.md, sample_detect.jpg, both `.dxnn` model dirs + config.json, retrained `.pt`)
- **session.log authentic** — 368 KB of real tee-captured output, 40 training-epoch lines, `PIPELINE DONE` + `ALL STAGES OK` markers
- **verify.py → RESULT: PASS** (fp32 vs INT8 agree)
- **report numbers match metrics.json**

## Summary

Fine-tuned `yolo26n` on the Ultralytics brain-tumor dataset (40 epochs, GPU) and measured all four points on real hardware:

| Model | Form | Device | mAP50-95 | mAP50 | FPS |
|-------|------|--------|----------|-------|-----|
| base | fp32 | RTX 5060 Ti | 0.0005 | 0.0010 | 529.3 |
| base | INT8 `.dxnn` | DX-M1 NPU | 0.0004 | 0.0011 | 59.0 |
| retrained | fp32 | RTX 5060 Ti | **0.4068** | 0.5589 | 582.2 |
| retrained | INT8 `.dxnn` | DX-M1 NPU | **0.3980** | 0.5441 | 83.4 |

- **Accuracy gain:** domain retraining lifts mAP50-95 from ~0.0005 → 0.4068 (+0.406, ~800×) — the COCO base never recognizes tumors; fine-tuning makes it viable.
- **INT8 quantization effect:** retrained INT8 keeps ~98 % of fp32 mAP50-95 (0.3980 vs 0.4068, −2.2 %).
- **Speed:** the retrained `nc=2` head runs **83 FPS on the NPU vs 59 FPS** for the `nc=80` base (~41 % faster, smaller `.dxnn`) — domain optimization improves both accuracy and edge throughput.
- `sample_detect.jpg`: retrained model marks a `positive` tumor box at 0.90 confidence on a val MRI.

Deployable artifact: `yolo26n_braintumor_deepx_model/yolo26n_braintumor.dxnn`.

```
 ███████████   █████████ ████████ ████████  ████      ████
 ███     █████ ███░░░░░░░███░░░░░░███   ███  ░████   ████░░
 ███        ██░███░      ██░░     ███   ███░   █████████░░
 ███        ████████████ ████████ ████████░░    ░█████░░░
 ███        ██░███░░░░░░░██░░░░░░░███░░░░░░  ██████████
 ███     █████░███░      ██░      ███░   ████████░░░░████
 ███████████░░░█████████ ████████ ██████████░░░░░░    ████
  ░░░░░░░░░░░   ░░░░░░░░░ ░░░░░░░░ ░░░░░░░░░░          ░░░░
        DX-AGENTIC-DEV · on-device NPU
```

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/)]

Now the final housekeeping step — rendering this session's transcript into the output dir:
Session transcript (md/html/jsonl) saved to: `dx-compiler/dx-agentic-dev/20260611-102324_claude_opus48_yolo26n_braintumor/claude-session.*`

---

## Summary

- **Turns:** 7
- **Tool calls:** 38
- **Raw messages:** 185