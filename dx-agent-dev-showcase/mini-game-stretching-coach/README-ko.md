# Stretch Coach — 아케이드 스트레칭 미니게임 (yolo26n-pose · DX-M1 NPU)

> **스토리.** 단일 자연어 프롬프트로 dx-agent-dev가 온디바이스 **아케이드 스트레칭 게임**을
> 만듭니다: `yolo26n-pose` COCO-17 keypoint를 DEEPX **DX-M1 NPU**에서 실행해, **3가지 스트레칭**
> (머리 위로 뻗기 → 앞으로 굽히기 → 목 스트레칭)을 HOLD-투-어드밴스 루프 + GOOD!/CLEAR!
> 피드백으로 안내합니다.
>
> **이번 빌드의 변화:** 좌상단 "코치"가 이제 가는 stick-figure skeleton이 아니라 **채워진,
> 사람 같은 휴머노이드 아바타**(원형 머리, 채워진 몸통/골반, 음영 처리된 관절의 테이퍼드 limb
> capsule)로 렌더되어 실제 코치가 동작을 시연하는 것처럼 보입니다.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-stretch-gameplay.gif" width="460"><br><sub><b>게임플레이 — 채워진 휴머노이드 코치(좌상단) + 실시간 NPU pose 추적</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-stretch-build.gif" width="320"><br><sub><b>dx-agent-dev가 빌드하는 과정 (타임랩스)</b></sub></td>
</tr></table></div>

> **에이전트가 어떻게 만들었는지 보기:** [`claude-code-session.md`](./claude-code-session.md).

### Session 메트릭

| 항목 | 값 |
|--------|-------|
| Coding agent / model | **Claude Code** / **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율 |
| Skills | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| Wall-clock / turns / cost | ~17분 / 148 / ≈ $9.3 |

## 프롬프트

stick-figure 게임에서 바뀐 핵심은 아바타뿐 — 프롬프트가 pose keypoint로부터 **채워진 절차적
휴머노이드**를 그리도록 요구합니다:

```
Using the yolo26n-pose model on the DEEPX NPU, build a simple arcade-style stretching
mini-game ... For each stage, render a small "coach" avatar that demonstrates the current
target stretch. IMPORTANT — the coach must look like a REAL PERSON, not a stick figure:
draw it as a FILLED, PROCEDURAL HUMANOID built from the pose keypoints — a round head, a
filled torso/pelvis body, and tapered LIMB CAPSULES (filled rounded segments for
upper-arm/forearm and thigh/shin) with smooth filled joints ... Do NOT draw it as thin
stick-figure lines or a bare keypoint skeleton. Animate the coach ... Recognize each pose
from the player's keypoints ... HOLD to advance, CLEAR! when all three are done. Support
both --video <file> and --camera <id>; save an annotated output video.
```

## 게임

| Stage | 스트레칭 | keypoint 인식 |
|------:|---------|---------------------------|
| 1/3 | **OVERHEAD REACH** | 양 손목이 머리 위로 |
| 2/3 | **FORWARD FOLD** | 머리/어깨가 골반 쪽으로 내려감(상체 앞으로 굽힘) |
| 3/3 | **NECK STRETCH** | 한 손을 머리 옆으로 올리고 다른 팔은 아래 |

해당 pose를 ~1.2초 유지 → **GOOD!** + 다음 단계; 3개 모두 완료 → **CLEAR!**
화면: STAGE n/3, 애니메이션 **휴머노이드 코치**(좌상단), 스트레칭 이름 + 안내, HOLD 진행 바,
플레이어 실시간 skeleton, model · NPU · FPS 상태줄.

## 아키텍처

표준 dx_app pose 파이프라인 — `StretchPoseFactory`(`IPoseFactory`, Letterbox + YOLOv8Pose
post-process 재사용) + `SyncRunner`. 게임 코어(`game/stretch_game.py`)에 `PoseClassifier`,
`HumanoidCoach` 렌더러(`cv2.fillConvexPoly` 몸통 + 테이퍼드 limb capsule), `StretchGame` 상태머신
+ 아케이드 overlay 추가.

## 재현

```bash
bash setup.sh        # venv(dx-runtime) + GUI OpenCV + framework vendoring
bash run.sh          # 번들 데모 비디오 실행 → annotated output/<run>/output.mp4
bash run.sh --camera 0          # 라이브 카메라
bash run.sh --video clip.mp4    # 임의 비디오
```

> x86-64 Linux + DeepX DX-M1 runtime(`yolo26n-pose.dxnn`) 필요. self-contained: `common/`이
> vendoring되고 `sample/stretching_demo.mp4`가 번들 → suite 밖으로 옮겨도 실행됨.

## 파일

| 파일 | 용도 |
|------|---------|
| `yolo26n_pose_stretch_sync.py` | 엔트리 — `StretchPoseFactory` + `SyncRunner` |
| `factory/` | `IPoseFactory`(Letterbox + YOLOv8Pose) + 게임 visualizer |
| `game/stretch_game.py` | `PoseClassifier`, **`HumanoidCoach`**(채워진 휴머노이드 렌더러), `StretchGame` |
| `config.json` | pose 임계값 + hold 타이밍(데모에서 calibrate) |
| `calibrate.py` / `verify.py` | metric probe / headless 검증(CLEAR! 도달 + 비디오 저장 assert) |
| `setup.sh` / `run.sh` | relocatable 셋업 / 원커맨드 런처 |
| `sample/stretching_demo.mp4` | 번들 데모 입력 |
| `claude-code-session.md` | 전체 에이전트 빌드 transcript (Wall-clock + Cost) |

영어: [`README.md`](./README.md).
