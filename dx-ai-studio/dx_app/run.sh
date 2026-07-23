#!/bin/bash
# ─── DX-APP Launcher ───
# Usage: ./run.sh [--port PORT]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SUITE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DX_APP_ROOT="${DX_APP_ROOT:-$SUITE_ROOT/dx-runtime/dx_app}"

PORT=8080
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --port|-p) PORT="$2"; shift 2 ;;
    --help|-h)
      echo "Usage: $0 [--port PORT]"
      echo "  --port, -p   Server port (default: 8080)"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

export DX_APP_ROOT
cd "$SCRIPT_DIR"

echo "═══════════════════════════════════════════"
echo "  DX-APP"
echo "  Root: $DX_APP_ROOT"
echo "  URL:  http://localhost:$PORT"
echo "═══════════════════════════════════════════"
echo ""

# Prefer the studio venv (Python 3.12) over system python3 (may be 3.10) — some
# studio modules use 3.12-only syntax. Fall back to python3 if the venv is absent.
PY="$SCRIPT_DIR/../.venv/bin/python"
[ -x "$PY" ] || PY="python3"
# Ensure the studio package is importable (so server.py resolves `import dx_app.core...`
# without sys.path hacks). Editable install is idempotent; `|| true` keeps it bootable offline.
"$PY" -c "import shared, dx_app" 2>/dev/null || "$PY" -m pip install -e "$SCRIPT_DIR/.." >/dev/null 2>&1 || true
"$PY" "$SCRIPT_DIR/server.py" --port "$PORT"
