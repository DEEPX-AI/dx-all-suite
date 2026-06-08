# 스트레칭 아케이드 미니게임 — dx-agentic-dev로 제작

> **단일 자연어 프롬프트로 [dx-agentic-dev](../../docs/source/agentic_development-KO.md)가
> end-to-end로 생성** — 손으로 작성한 코드 없음. 이 폴더는 **self-contained & portable**입니다
> (vendored `./common`): dx-all-suite 밖으로 복사해도 동작합니다(DEEPX 런타임이 있는 임의 머신).

<div align="center">
<table>
<tr>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-build.gif" width="470"><br><sub><b>dx-agentic-dev가 앱을 빌드하는 모습 (timelapse)</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agentic-dev-stretch-gameplay.gif" width="300"><br><sub><b>생성된 앱이 DX-M1 NPU에서 실행되는 모습</b></sub></td>
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
| 빌드 wall-clock | **≈ 21분** (1,257,117 ms) |
| Agent turn 수 | **75** |
| 확인 질문 | 1회 (`AskUserQuestion`, knowledge base 기본값으로 자동 해결) |
| 사용 도구 | `Bash` ×30, `Write` ×16, `Read` ×10, `Edit` ×7, `Skill` ×5, `AskUserQuestion` ×1 |
| 호출한 skill (순서) | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |
| Output 토큰 | **≈ 84.6K** (input 5.7K; cached-context read ≈ 11.8M) |
| 대략 비용 | **≈ $9.4** |

brainstorm → plan → TDD → verify 전체 skill 시퀀스가 앱 완료 선언 전에 end-to-end로
실행됐습니다 — 샘플 클립에서 coach 포즈를 도출하는 과정 포함.

DEEPX NPU에서 `yolo26n-pose`를 실행하는 아케이드 스타일 스트레칭 미니게임. 애니메이션 스틱피겨
**coach**가 각 목표 포즈를 시연하며, **세 가지 스트레칭을 한 단계씩** 안내합니다:

| 단계 | 스트레칭 | 인식 방식 (COCO-17, leg-normalized) |
|------|----------|--------------------------------------|
| 1/3 | **머리 위로 뻗기** | 양 손목이 코 **및** 어깨보다 위 |
| 2/3 | **허리 굽히기(forward fold)** | 어깨가 엉덩이 쪽으로 내려가고 **및** 손이 엉덩이 높이 이하로 닿음 |
| 3/3 | **목 스트레칭** | 정확히 **한** 손이 머리 옆으로 올라감(머리 높이 근처 + 귀에 가까움) |

해당 포즈를 잠깐 유지하면(frame 기반 HOLD 바가 채워짐) → **GOOD!**, 다음 단계로 진행.
세 가지 모두 완료 → **CLEAR!**

## 아케이드 UI (매 프레임 오버레이)
- 상단 배너: 타이틀 + `STAGE n/3` (→ `COMPLETE`).
- 좌상단 **coach 패널**: 중립 서있는 자세와 목표 스트레칭을 번갈아 보여주는 애니메이션 스틱피겨
  (둘 다 `calibrate_coach_poses.py` → `pose_templates.json`로 **샘플 클립에서 도출**), 스트레칭
  **이름**과 짧은 **안내**, **HOLD %** 진행바.
- 중앙 **GOOD! / CLEAR!** 피드백 텍스트.
- 플레이어의 라이브 skeleton을 영상 위에 그림.

## 아키텍처 (framework-compliant)
- **IFactory** `StretchGameFactory`: `LetterboxPreprocessor` + `YOLOv8PosePostprocessor`
  + custom `StretchGameVisualizer`.
- **SyncRunner** (AsyncRunner 아님): 게임이 stateful이고 엄격히 순서가 보장된 프레임이 필요.
  visualizer 인스턴스가 프레임 간 유지되며 게임 상태를 보관.
- 인식 + state machine은 `pose_logic.py`에 있음(순수, NPU-free, unit-tested).

## 빠른 시작
```bash
./setup.sh                                   # dx_engine venv 해결 + ./common vendoring
./run.sh --video sample/stretching_demo.mp4  # 비디오 파일 → annotated output/ 저장
./run.sh --camera 0                          # 라이브 카메라 input
# 명시적 모델: MODEL=/path/yolo26n-pose.dxnn ./run.sh --camera 0
```
`run.sh`는 **relocatable**입니다: venv fallback 체인, 다운로드 안내가 있는 모델 존재 가드,
bundled-sample-first input, 앱 자체 `output/`에 저장 — 그래서 dx-all-suite 밖으로 복사해도
동작합니다(vendored `./common`을 들고 다님; `dx_engine`이 유일한 외부 전제).

## 파일
| 파일 | 역할 |
|------|------|
| `stretch_game_sync.py` | 진입점 (SyncRunner + factory; portable `common` walker). |
| `factory/stretch_game_factory.py`, `factory/__init__.py` | IFactory (5 메서드). |
| `stretch_game_visualizer.py` | stateful 게임 + 아케이드 UI 오버레이. |
| `coach.py` | 애니메이션 스틱피겨 coach 아바타. |
| `pose_logic.py` | NPU-free recognizer + `StretchGame` state machine. |
| `config.json` | threshold + 게임 파라미터(hold, grace). |
| `pose_templates.json` | 클립에서 baked된 coach skeleton. |
| `calibrate_coach_poses.py` | OFFLINE 개발 도구: 클립 측정 → threshold + template. |
| `verify.py` | end-to-end 검증(클립별 clear + demo CLEAR), 영상 저장. |
| `game_eval.py` | 개발 헬퍼: 실제 SyncRunner 파이프라인을 영상에 구동. |
| `test_pose_logic.py` | recognizer + state machine unit test (7개). |
| `setup.sh`, `run.sh` | 환경 셋업(`common` vendoring) + relocatable 런처. |
| `sample/stretching_demo.mp4` | 동봉 데모 input(3개 스트레칭 concat). |
| `claude-code-session.md` / `.html` | 이 앱을 만든 전체 agent 세션. |

## 검증 근거 (`session.log` 참조)
- Unit test: **7 passed**.
- Fresh clip 측정 — 자기 클립에서의 pose separation: **overhead 47.9% / fold 40.8% / neck 50.8%**, cross-talk ~0.
- `verify.py`: **RESULT: PASS** — 각 클립이 목표 단계를 clear; `stretching_demo.mp4`가 전체 **CLEAR (3/3)** 도달.
- 런타임: NPU에서 **~35 FPS**. 비디오 input은 annotated `output.mp4` 저장.
- Portability: vendored `./common`으로 suite 밖에서도 동작.
