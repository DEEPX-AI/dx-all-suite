# `dx-showcase-gen` — Showcase 생성 자동화

> **dx-agent-dev showcase** 제작의 결정적(deterministic) 기계작업을 담당하는 도구로,
> RIGID skill [`dx-agent-showcase-build`](../../../skills/dx-agent-showcase-build/SKILL.md)와
> 짝을 이룹니다. 둘이 함께 "showcase 추가"를 **반복 가능·검증된 워크플로**로 만들고,
> 반복적으로 발생하던 실수를 (기억이 아니라) 코드+게이트로 차단합니다.

English: [`README.md`](./README.md).

## 왜 도구+skill로 나눴나

showcase = DEEPX 앱의 실제 agent-driven 빌드를 build GIF + complete transcript + 생성
산출물로 캡처한 뒤 README·docs에서 홍보하는 것입니다. 이 중 일부는 **비결정적/사람**
영역(agent-driven 빌드 자체, KB 기반 프롬프트, 녹화용 화면 비우기, 산문 작성)이고, 나머지는
**결정적이며 우리가 겪은 모든 반복 실수의 근원**이었습니다. 그래서:

- **도구(`dx-showcase-gen`, 이 패키지)** = 결정적 기계작업 — 테스트됨.
- **skill(`dx-agent-showcase-build`)** = 오케스트레이션 + 판단 + human-in-the-loop
  게이트, 그리고 DONE 선언 전 도구의 `verify` 실행.

## 이 도구가 막는 반복 실수

| 실수(실제 빌드에서 발생) | 차단 위치 |
|---|---|
| GIF가 실제 claude 화면이 아닌 합성 render였음 | skill이 실제 window 녹화, 도구가 crop |
| 터미널이 화면 밖으로 매핑돼 crop 실패 | `recorder`가 full-screen 캡처 후 window rect로 post-crop |
| GIF > 10MB (GitHub inline 불가) | `recorder.make_gif`가 자동 축소 |
| transcript에 **Wall-clock / Cost** 누락 | `transcript.render`가 `--stream-json`(=`result` 이벤트) 강제, 없으면 에러 |
| showcase의 tool/model이 틀림 | `verify`가 `tool=claude`, `model=claude-opus-4-8` 확인 |
| 생성 산출물 미복사/비포터블 | `artifacts.copy_session_artifacts` + `scan_nonportable` |
| README/docs 미보강(또는 중복 삽입) | `augment`가 idempotent + marker 앵커 |
| 깨진 채 DONE 선언 | skill Phase-8 `verify` 게이트 PASS 필수 |

## 설치 / 실행

```bash
pip install -e .deepx/tools          # `dx-showcase-gen` 등록
# 또는 설치 없이:
export PYTHONPATH=.deepx/tools/src
python3 -m dx_showcase_gen.cli --help
```

## 서브커맨드

| 커맨드 | 용도 |
|---|---|
| `transcript` | `--stream-json` 캡처에서 `claude-code-session.{md,html,jsonl}` 렌더(`result` 이벤트 없으면 실패 → Wall-clock/Cost 없음) |
| `verify` | showcase 검증 게이트 실행; 실패 시 exit 1 |
| `copy-artifacts` | 빌드 세션 파일을 showcase로 복사(venv/`*.pt`/`*.onnx`/`*.dxnn` 제외) + portability flag 출력 |
| `augment` | README/doc에 GIF 블록 upsert(idempotent, marker 앵커) |
| `gif` | 캡처 mp4 → timelapse GIF(target-secs 가속, <10MB) |
| `crop` | full-screen 캡처를 window rect로 post-crop(`--title` 또는 `--rect WxH+X+Y`) |
| `window-rect` | `xwininfo`로 window rect 출력 |
| `capture-start` / `capture-stop` | 백그라운드 x11grab full-screen 캡처 시작/정지 |
| `keepawake start|stop` | 긴 녹화 중 GNOME 화면 blank 방지 |

## 모듈

| 모듈 | 역할 |
|---|---|
| `recorder.py` | x11grab 캡처·window rect crop·timelapse GIF; 순수 helper(`clamp_crop`, `speedup_factor`, ffmpeg 인자)는 단위테스트됨 |
| `transcript.py` | COMPLETE transcript 렌더(`dx_transcripts` 재사용), `--stream-json` 강제 |
| `verify.py` | PASS/FAIL 게이트(`Report`/`Check`): transcript·model/tool·GIF·산출물·보강 |
| `artifacts.py` | session→showcase 복사 + 비포터블 경로 스캔 |
| `augment.py` | idempotent marker 앵커 블록 upsert |
| `constants.py` | 기본값(`model=claude-opus-4-8`, GIF 정책, 경로) |
| `cli.py` | argparse dispatch(실제 `__main__` 가드 포함 → `-m` 동작) |

## 테스트

```bash
PYTHONPATH=.deepx/tools/src python3 -m pytest .deepx/tools/tests/dx_showcase_gen/ -v
```

결정적 표면(crop 클램프, speedup, ffmpeg 인자, transcript 메트릭/완전성, idempotent
augment, verify 게이트의 누락 파일/잘못된 model 탐지)을 커버합니다. x11grab/ffmpeg
부수효과는 얇은 래퍼라 단위테스트하지 않습니다.

## 워크플로 (skill이 도구를 구동)

1. KB 기반 빌드 프롬프트(skill) → 2. 녹화 준비 게이트, 사람이 화면 영역 비움(skill) →
3. 실제 빌드 녹화 + `--output-format stream-json` 캡처(skill + 도구
`keepawake`/`capture`/`crop`/`gif`) → 4. `transcript`(complete) → 5. `copy-artifacts`
+ portability 수정 → 6. run GIF → 7. `augment` README/docs → 8. `verify` PASS.

skill 문서: [`dx-agent-showcase-build`](../../../skills/dx-agent-showcase-build/SKILL.md).
