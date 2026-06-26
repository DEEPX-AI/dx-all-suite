## Self-Contained & Portable (HARD GATE — 모든 생성 산출물)

생성된 모든 session/app 디렉터리는 **suite 밖으로 복사해도** 실행되어야 합니다 — 유일한 외부
전제는 DEEPX 런타임(`dx_engine`)뿐입니다. 모든 산출물에 적용: dx_app app, dx_stream pipeline,
fork 기반 app(PaddleOCR / RapidDoc), compile/retrain session.

- **필요한 코드는 session 안으로 vendoring** — `./common`, fork의 importable package
  (`engine/`, `rapid_doc/`) 등. 다른 showcase/source 디렉터리를 in-place로 import하지 말고,
  source 디렉터리를 session에 symlink하지 말고, 런타임에 fork를 다시 clone하지 마세요.
- **모든 code/model 경로는 session 상대경로**(`$SCRIPT_DIR` / `APP_DIR`)로. model은 session
  로컬 디렉터리에 download하고, model/output 디렉터리를 `dx-agent-dev-showcase/...`나 commit된
  source로 향하게 하지 마세요. (프롬프트가 지정한 **입력** 미디어를 `*/sample/` 경로에서 읽는
  것은 허용 — 이는 code/model 의존성이 아니라 런타임 입력입니다.)
- **검증(copy-out gate):** done 선언 전, app 디렉터리를 suite 밖 temp로 복사해 entry를
  import/run 하세요. 실패하면 — vendoring 누락(`ModuleNotFoundError: engine`/`common`), app
  디렉터리를 벗어나는 symlink, 또는 suite/showcase의 code-or-model 참조 — self-contained가
  아니므로 **FAIL**. 정확한 절차는 `dx-agent-verify`(Step 6) 참조.
