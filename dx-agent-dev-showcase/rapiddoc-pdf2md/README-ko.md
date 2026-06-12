# DEEPX DX-M1 NPU에서 PDF → Markdown 변환 (RapidDoc / PP-StructureV3)

> **스토리.** 사용자가 **짧고 목표만 담은 프롬프트** — "DEEPX NPU에서 동작하는 PDF→Markdown
> 앱을 만들어줘" — 를 입력합니다. **toolset도, 파일도, repo 브랜치도, env script도 적지
> 않습니다.** 그것만으로 dx-agent-dev는 알맞은 knowledge base로 routing해 **standalone·
> self-contained 앱**을 생성합니다: RapidAI **RapidDoc** 파이프라인 패키지(`rapid_doc`,
> PP-StructureV3)를 앱에 **vendoring**하고, 이를 import하는 **자체 entry**(`pdf_to_markdown.py`)
> 를 작성해, **layout 분석·OCR·표 인식을 DX-M1 NPU에서** 실행(수식 인식은 ONNX Runtime).
> PDF(디지털/스캔)를 구조화된 **Markdown + JSON**으로 변환하며, 런타임에 포크를 clone하지 않습니다.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-rapiddoc-pdf2md-build.gif" width="470"><br><sub><b>dx-agent-dev가 이 showcase를 빌드하는 과정 (타임랩스)</b></sub></td>
<td align="center"><img src="./images/sample_before_after.png" width="470"><br><sub><b>PDF 페이지 → Markdown, DX-M1 NPU에서 파싱</b></sub></td>
</tr></table></div>

> **에이전트가 어떻게 만들었는지 보기:** [`claude-code-session.md`](./claude-code-session.md).

### Session 메트릭

| 항목 | 값 |
|--------|-------|
| Coding agent / model | **Claude Code** / **Claude Opus 4.8** (`claude-opus-4-8`) |
| 사람 입력 | **짧은 자연어 프롬프트 1개** — 완전 자율 |
| 읽은 KB toolset | `paddleocr-rapiddoc-app` — 프롬프트에 적지 않았으나 **routing으로 스스로 찾음** |
| Skills | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| Wall-clock / turns / cost | ~12분 / 61 / ≈ $6.2 |

## 프롬프트

이 showcase의 핵심: 프롬프트는 **간결**하며 toolset 경로·파일·브랜치·env script를 적지
않습니다 — 그 부분(그리고 **포크 demo를 래핑하지 않고 standalone 앱을 생성**한다는 결정까지)은
skill + KB routing이 채웁니다.

```
Build a PDF-to-Markdown app whose document-parsing pipeline (layout analysis + OCR +
table/formula recognition) runs on the DEEPX DX-M1 NPU. Input a PDF (digital or scanned),
output structured Markdown (+ JSON) preserving headings and tables. Support
--parse-method auto|txt|ocr. Provide setup.sh, run.sh, a sample input PDF + its rendered
Markdown output (sample_output.md), and a README reporting NPU stage timings.
```

> **아키텍처 노트.** RapidDoc는 *자체* NPU 파이프라인(DX-M1 위 PP-StructureV3)을 제공하므로
> dx_app IFactory / SyncRunner 패턴의 문서화된 **예외**입니다. 산출물은 **vendored** `rapid_doc`
> 패키지를 구동하는 **자체 entry**(`pdf_to_markdown.py`)이며, 포크의 `demo/demo_offline.py`
> 래퍼가 **아닙니다**.

## 빠른 시작

```bash
./setup.sh                       # venv + deps + dx_engine bridge + NPU 모델 다운로드
./run.sh                         # 번들된 sample_input.pdf 파싱 (auto)
./run.sh mydoc.pdf auto          # 디지털 PDF (text layer 우선, OCR fallback)
./run.sh scan.pdf  ocr           # 스캔 PDF (전체 페이지 NPU OCR 강제)
./run.sh doc.pdf   txt           # text layer만 추출 (OCR 없음)
```

런타임에 포크를 clone하지 않습니다 — `rapid_doc/`가 이 폴더에 vendoring되어 있고, `setup.sh`는
pip 의존성 설치 + **NPU 모델 다운로드**(16 `.dxnn` + 8 `.onnx`, 커밋 안 함)만 수행합니다.

## `--parse-method`

| Method | 동작 | 용도 |
|---|---|---|
| `auto` *(기본)* | 페이지별 text layer 사용, 없으면 OCR fallback | 디지털/혼합 PDF |
| `txt`  | text layer만, OCR 없음 | 디지털 PDF (가장 빠름) |
| `ocr`  | 모든 페이지 NPU OCR(det+rec) 강제 | 스캔/이미지 PDF |

## 측정된 NPU 성능

`sample_input.pdf` = `physics0409110_origin.pdf` (영문 물리 논문, *"High-precision Absolute
Distance and Vibration Measurement using Frequency Scanned Interferometry"*, **16페이지**,
수식 위주), **이 앱의 `pdf_to_markdown.py`** 가 DX-M1에서 직접 생성(`DXNN_DEVICES=0`, runtime
3.3.2 / FW v2.5.6). `auto` end-to-end **41.3 s** (2.58 s/page):

| Stage | Count | 평균 latency | Throughput | Engine | 비중 |
|---|---:|---:|---:|---|---:|
| Formula recognition | 164 | 213.82 ms | 4.7 FPS | ONNX/CPU | 85.0% |
| Layout analysis | 16 | 317.42 ms | 3.2 FPS | **NPU** | 12.3% |
| Table recognition | 1 | 848.05 ms | 1.2 FPS | **NPU** | 2.1% |
| OCR det / PDF text-det | 100 | ~2–108 ms | — | **NPU** | 0.7% |

이 논문은 **수식이 많아**(수식 region 164개 → 85%) formula recognition + NPU layout/OCR/table을
함께 보여줍니다. 모델 load 1.75 s.

## 샘플 출력 (`sample_output.md` 발췌)

제목·저자·abstract·섹션 제목이 보존되며, 수식은 formula region으로 인식됩니다(Markdown에서는
잘린 이미지로 렌더):

```markdown
# High-precision Absolute Distance and Vibration Measurement using Frequency Scanned Interferometry

Hai-Jun Yang, Jason Deibel, Sven Nyberg, Keith Riles
Department of Physics, University of Michigan, Ann Arbor, MI 48109-1120, USA

In this paper, we report high-precision absolute distance and vibration measurements
performed with frequency scanned interferometry using a pair of single-mode optical fibers...

# 1. Introduction
# 2. Principles
# 3. Demonstration System of FSI
```

## 동작 방식 (standalone)

1. `pdf_to_markdown.py`가 **vendored `./rapid_doc`** 를 `sys.path`에 추가(설치·런타임 clone 없음)하고
   DX-RT threading env를 확인.
2. per-model engine config 구성(layout `PP-DocLayout-L`, OCR `PP-OCRv5` det+rec, table `UNET`,
   formula `PP-FormulaNet+`), layout/OCR/table은 로컬 `dxnn_models/`(NPU)를 가리킴.
3. `rapid_doc.backend.pipeline.pipeline_analyze.doc_analyze(...)`를 NPU에서 실행.
4. `FileBasedDataWriter`로 Markdown(`MakeMode.MM_MD`) + JSON content list 렌더.

## 재현

```bash
bash setup.sh        # venv + deps + dx_engine bridge + NPU 모델 다운로드 (foreground)
bash run.sh          # sample_input.pdf를 NPU에서 파싱 → output/<stem>/<method>/<stem>.md
```

> x86-64 Linux + DeepX runtime 필요; `dx_engine` 없으면: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.
> 모델은 `setup_sample_models.sh`(prebuilt onnx+dxnn)로 받으며 `dxcom`으로 직접 컴파일하지 않습니다.

## 파일

| 파일 | 역할 |
|---|---|
| `pdf_to_markdown.py` | vendored NPU 파이프라인을 구동하는 **자체** entry |
| `rapid_doc/` | **vendored** RapidDoc 파이프라인 패키지 (순수 Python, ~2.5 MB) |
| `deepx_scripts/`, `setup_sample_models.sh` | DX env 설정 + NPU/ONNX 모델 다운로더 |
| `setup.sh` | venv + `requirements.deepx.txt` + dx_engine `.pth` bridge + 모델 다운로드 |
| `run.sh` | 런처: `set_env.sh` source, `DXNN_DEVICES=0`, `pdf_to_markdown.py` 실행 |
| `sample_input.pdf` / `sample_output.md` | 영문 물리 논문 + 렌더된 Markdown |
| `images/sample_before_after.png` | before/after: PDF 페이지 → 파싱된 Markdown |
| `timings.md` | per-stage NPU 처리시간 리포트 (실제 run) |
| `session.log` | 추론 run의 실제 캡처 출력 |
| `claude-code-session.md` | 전체 에이전트 빌드 transcript (Wall-clock + Cost) |

영어: [`README.md`](./README.md).
