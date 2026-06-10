# 스쿼트 피트니스 미니게임 — dx-agentic-dev로 제작

> **단일 자연어 프롬프트로 [dx-agentic-dev](../../docs/source/00_Agentic_Development_kor.md)가
> end-to-end로 생성** — 손으로 작성한 코드 없음. 이 폴더는 **self-contained & portable**입니다:
> 프레임워크를 `./common`으로 vendoring하므로 dx-all-suite 밖으로 복사해도 동작합니다
> (DEEPX 런타임이 있는 임의 머신).

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-build.gif" width="470"><br><sub><b>dx-agentic-dev가 앱을 빌드하는 모습 (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-squat-gameplay.gif" width="188"><br><sub><b>생성된 앱이 DX-M1 NPU에서 실행되는 모습</b></sub></td>
</tr>
</table>
</div>

> **agent가 어떻게 만들었는지 보기:** [`claude-code-session.md`](./claude-code-session.md)
> (GitHub에서 렌더링됨; `claude-code-session.html`은 로컬 브라우저에서 열기).

### 이 앱이 만들어진 과정 — 세션 메트릭

빌드 세션 transcript(`claude-code-session.*`)에서 발췌:

| 항목 | 값 |
|------|-----|
| 코딩 에이전트 | **Claude Code** (`claude` CLI, headless `-p`) |
| 모델 | **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율, 손으로 작성한 코드 없음 |
| 빌드 wall-clock | **≈ 20분** (1,188,799 ms) |
| Agent turn 수 | **81** |
| 확인 질문 | 1회 (`AskUserQuestion`, knowledge base 기본값으로 자동 해결) |
| 사용 도구 | `Bash` ×33, `Write` ×17, `Read` ×15, `Skill` ×5, `Edit` ×3, `TaskCreate` ×1, `AskUserQuestion` ×1 |
| 호출한 skill (순서) | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |
| Output 토큰 | **≈ 85.3K** (input 7.9K; cached-context read ≈ 12.5M) |
| 대략 비용 | **≈ $9.9** |

brainstorm → plan → TDD → verify 전체 skill 시퀀스가 앱 완료 선언 전에 end-to-end로
실행됐습니다 — transcript에 각 단계가 실제 tool call로 기록돼 있습니다.

아케이드 스타일 스쿼트 카운터. DEEPX NPU에서 **yolo26n-pose**를 실행해 신체 keypoint(무릎+엉덩이
각도)로 스쿼트 횟수를 검출하고, 실시간으로 횟수를 세며, 게임 HUD(횟수, 목표, 점수,
**DOWN / UP / GOOD!** 피드백, 진행바)를 오버레이합니다. **비디오 파일** 또는 **라이브 카메라**에서
동작하며 런타임에 선택 가능합니다. 비디오 파일로 실행하면 **주석이 표시된 출력 영상**을 저장합니다.

## 프롬프트

> 에이전트에게 준 실제 자연어 프롬프트 (verbatim):

```
Build a squat-counting fitness mini-game using yolo26n-pose on DEEPX NPU, validate with sample/squat_demo.mp4
```

## 빠른 시작

```bash
./setup.sh                 # 프레임워크를 ./common으로 vendoring, 모델+샘플 준비
./run.sh                   # 동봉 데모 영상으로 플레이 (annotated output.mp4 저장)
./run.sh --camera 0        # 라이브 카메라
./run.sh --video my.mp4 --save
./run.sh --target-reps 15 --camera 0
```

직접 실행 (동등):

```bash
python yolo26n_pose_squat_sync.py -m yolo26n-pose.dxnn --video sample/squat_demo.mp4 --save
python yolo26n_pose_squat_sync.py -m yolo26n-pose.dxnn --camera 0
```

## 런타임 옵션

| 옵션 | 의미 |
|------|------|
| `--video, -v <file>` | 비디오 파일을 input으로 사용 |
| `--camera, -c <id>` | 라이브 카메라 사용 (예: `0`) |
| `--image, -i <path>` | 단일 이미지 / 이미지 디렉토리 |
| `--save, -s` | 주석 출력 영상 저장 (video/camera) |
| `--no-display` | headless 실행(창 없음); `--save`로 여전히 저장 |
| `--target-reps <N>` | 게임 목표 (기본값은 `config.json`, 10) |
| `--config <path>` | config.json 재정의 |

display 창에서 **q** 또는 **ESC**로 종료.

## 스쿼트 검출 방식

- **무릎 각도** = 무릎에서 hip→knee와 ankle→knee 사이 각도(COCO-17 인덱스: hip 11/12,
  knee 13/14, ankle 15/16). 양 다리가 보이면 좌+우 평균.
- **엉덩이 각도** = hip에서의 각도(shoulder 5/6 → hip → knee). 보강 게이트로 사용.
- 2-state FSM(UP↔DOWN) + **hysteresis**로 DOWN→UP 한 사이클당 1회 카운트. threshold는
  `sample/squat_demo.mp4`에서 **자동 calibration**됨(2D 무릎 각도는 교과서적 90°가 아니라
  ~135°에서 바닥을 치므로 고정 컷오프는 오카운트 — `calibrate.py` 참조).

## threshold 재calibration

```bash
python calibrate.py --video sample/squat_demo.mp4   # config.json 갱신
```

## 검증

```bash
python verify.py        # NPU E2E: 17-keypoint pose + 횟수 카운트 -> RESULT: PASS
```

## 아키텍처 (IFactory + SyncRunner, skeleton-first)

| 구성요소 | 구현 |
|----------|------|
| Preprocessor | `LetterboxPreprocessor` (framework) |
| Postprocessor | `YOLOv8PosePostprocessor` (framework) → COCO-17 포함 `PoseResult` |
| Visualizer | **`SquatGameVisualizer`** — stateful rep FSM + 아케이드 HUD |
| Factory | **`SquatGameFactory`** (`IPoseFactory`, 5 메서드 + `get_num_keypoints`) |
| Runner | `SyncRunner` (단일 모델, frame-ordered) |

게임 로직은 전부 visualizer의 `visualize(frame, results)` hook 안에 있습니다 — 직접적인
`InferenceEngine` 호출 없이 프레임워크 패턴을 완전히 따릅니다.

## 파일

| 파일 | 용도 |
|------|------|
| `yolo26n_pose_squat_sync.py` | 진입점 — factory 생성, `SyncRunner` 실행 |
| `factory/squat_game_factory.py` | `SquatGameFactory` (IFactory) |
| `factory/squat_game_visualizer.py` | `SquatGameVisualizer` (게임 hook + HUD) |
| `factory/squat_logic.py` | 순수 `angle_3pt` + `SquatCounter` FSM |
| `factory/__init__.py` | factory export |
| `config.json` | threshold(calibrated) + target_reps |
| `calibrate.py` | 샘플 영상에서 threshold 도출 |
| `verify.py` | NPU end-to-end 검증 |
| `test_squat_logic.py` | angle 수학 + FSM unit test (10개) |
| `setup.sh` / `run.sh` | self-contained 셋업 + relocatable 런처 |
| `session.json` / `session.log` | 세션 메타데이터 + 명령 로그 |

## Self-contained / portable

`setup.sh`가 공용 프레임워크를 `./common`으로 vendoring하고, entry walker가 그 vendored
`./common`을 우선 사용합니다(`PYTHONPATH` 불필요). 모델+샘플 동봉으로, 폴더를 dx-all-suite
밖으로 복사해도 동작합니다 — `dx_engine`(DEEPX 런타임)이 유일한 외부 전제입니다.
