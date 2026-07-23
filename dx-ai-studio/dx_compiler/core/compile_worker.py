#!/usr/bin/env python3
"""
venv Python으로 실행되는 독립 컴파일 워커.
stdin에서 JSON 파라미터를 읽고, event_queue 이벤트를 stdout JSON으로 출력한다.

사용법:
  echo '{"model":"/path/model.onnx","config":"/path/config.json",...}' | \
    /path/to/venv/bin/python3 compile_worker.py
"""
import json
import queue
import sys
import threading
import traceback

# compile_worker.py가 패키지 외부(venv Python)에서 실행될 때도
# dx_compiler.* import가 동작하도록 프로젝트 루트를 sys.path에 추가한다.
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

SENTINEL = "__COMPILE_DONE__"


def event_to_dict(event) -> dict:
    """PhaseEvent 객체를 JSON-serializable dict로 변환"""
    result = {"phase": str(getattr(event, "phase", "")),}
    meta = getattr(event, "metadata", None)
    if meta:
        safe_meta = {}
        for k, v in meta.items():
            try:
                json.dumps(v)
                safe_meta[k] = v
            except (TypeError, ValueError):
                safe_meta[k] = str(v)
        result["metadata"] = safe_meta
    # model 객체는 직렬화 불가 — 존재 여부만 표시
    if getattr(event, "model", None) is not None:
        result["has_model"] = True
    return result


def main():
    try:
        params = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        print(json.dumps({"type": "error", "message": f"Invalid JSON input: {e}"}), flush=True)
        sys.exit(1)

    event_q = queue.Queue()

    def compile_thread():
        try:
            from dx_compiler.core.compiler_bridge import run_compile
            run_compile(
                model=params.get("model"),
                config=params.get("config"),
                output_dir=params["output_dir"],
                opt_level=params.get("opt_level", 1),
                aggressive_partitioning=params.get("aggressive_partitioning", False),
                gen_log=params.get("gen_log", False),
                quant_debug=params.get("quant_debug", False),
                quant_diagnosis=params.get("quant_diagnosis", False),
                use_q_pro=params.get("use_q_pro", False),
                input_nodes=params.get("input_nodes"),
                output_nodes=params.get("output_nodes"),
                enhanced_scheme=params.get("enhanced_scheme"),
                event_queue=event_q,
                pause_for_selection=False,
                selection_done=None,
                selection_result=None,
            )
        except Exception as e:
            event_q.put({"type": "error", "message": str(e), "traceback": traceback.format_exc()})
        finally:
            event_q.put(SENTINEL)

    thread = threading.Thread(target=compile_thread, daemon=True)
    thread.start()

    while True:
        event = event_q.get()
        if event == SENTINEL:
            break
        if isinstance(event, dict):
            print(json.dumps(event), flush=True)
        else:
            print(json.dumps(event_to_dict(event)), flush=True)

    thread.join(timeout=5)
    print(json.dumps({"type": "done"}), flush=True)


if __name__ == "__main__":
    main()
