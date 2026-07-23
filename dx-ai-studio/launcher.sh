#!/bin/bash
# ─── DeepX AI Studio Launcher ───
# Usage: ./launcher.sh [--port PORT] [--no-kill]
#
# Starts the unified launcher (default 8890) which boots all module servers and
# reverse-proxies them. Designed to "just work" on shared hosts:
#   • Kills only OUR own stale studio servers (never other services e.g. nginx/argus).
#   • If a default port is held by a foreign service, auto-picks the next free port
#     and passes it via DX_*_PORT env → launcher.py propagates it to the proxy map,
#     health checks, and the printed URL (no manual --port juggling).

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SUITE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DX_APP_ROOT="${DX_APP_ROOT:-$SUITE_ROOT/dx-runtime/dx_app}"

PORT=8890
NO_KILL=0
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --port|-p) PORT="$2"; shift 2 ;;
    --no-kill) NO_KILL=1; shift ;;
    --fast) export DX_LAUNCHER_FAST=1; shift ;;
    --verbose|-v) DX_LAUNCHER_VERBOSE=1; shift ;;
    --no-browser) export DX_NO_BROWSER=1; shift ;;
    --help|-h)
      echo "Usage: $0 [--port PORT] [--no-kill] [--fast] [--verbose] [--no-browser]"
      echo "  --port, -p    Launcher port (default: 8890; auto-bumps if busy)"
      echo "  --no-kill     Do not kill stale studio servers before starting"
      echo "  --fast        Skip the cosmetic boot animation"
      echo "  --verbose, -v Print port-fallback notices when a default port is busy"
      echo "  --no-browser  Do not auto-open the browser"
      exit 0 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

export DX_APP_ROOT
cd "$SCRIPT_DIR"

# ── 1) Kill our own stale studio instances (never other users' — pkill only signals
#       processes owned by us, and patterns are scoped to this project) ──
# Kill the launcher/watchdog FIRST (so it can't respawn sub-servers), then the detached
# sub-servers. Match BOTH absolute paths and hand-run relative invocations
# (`python3 launcher/launcher.py`) — the old $SCRIPT_DIR-anchored pattern missed the
# relative form, so zombies from manual runs piled up and forced port bumping.
if [[ "$NO_KILL" -eq 0 ]]; then
  pkill -f "launcher/launcher\.py"            2>/dev/null   # abs + relative launcher
  pkill -f "dx-ai-studio/dx_[a-z_]*/server\.py" 2>/dev/null # all sub-servers (this project)
  sleep 1
  # hard-kill any stragglers, then let the OS release the ports
  pkill -9 -f "launcher/launcher\.py"            2>/dev/null
  pkill -9 -f "dx-ai-studio/dx_[a-z_]*/server\.py" 2>/dev/null
  sleep 0.5
fi

# ── helpers ──
port_busy() {  # 0 if something is LISTENING on $1
  ss -ltnH 2>/dev/null | awk '{n=split($4,a,":"); print a[n]}' | grep -qx "$1"
}
USED=" "      # ports already claimed in this run
RESULT=""     # set by claim_port (avoids $() subshell so USED accumulates)
claim_port() { # find first free port >= $1, skipping already-claimed; sets RESULT
  local p="$1"
  while port_busy "$p" || [[ "$USED" == *" $p "* ]]; do p=$((p+1)); done
  USED="$USED$p "
  RESULT="$p"
}

# ── 2) Launcher port — STICKY so the URL stays stable across runs. The launcher port is
#       the ONLY TCP port the user touches; the 8 module servers self-assign OS ephemeral
#       ports (--port 0, zero collision), so there's no module-port juggling here anymore. ──
REQUESTED_PORT="$PORT"
STICKY_FILE="$SCRIPT_DIR/.launcher-port"
# Honor the remembered port only when the caller didn't pin one (default 8890).
# Never reuse legacy 8888 (often MediaMTX / other services on shared hosts).
if [[ "$PORT" == "8890" && -f "$STICKY_FILE" ]]; then
  STICKY_PORT="$(cat "$STICKY_FILE" 2>/dev/null)"
  if [[ "$STICKY_PORT" == "8888" ]]; then
    STICKY_PORT=""
  fi
  if [[ "$STICKY_PORT" =~ ^[0-9]+$ ]] && ! port_busy "$STICKY_PORT"; then
    PORT="$STICKY_PORT"
  fi
fi
claim_port "$PORT"
PORT="$RESULT"
echo "$PORT" > "$STICKY_FILE"   # remember → same URL next run while it stays free
if [[ "$PORT" != "$REQUESTED_PORT" ]]; then
  echo "  [launcher.sh] Port $REQUESTED_PORT is held by another service → using $PORT"
fi

# ── 3) Persist the URL for discovery, but do NOT print a clickable URL here. An editor
#       that auto-links terminal URLs (VS Code remote) forwards the instant the link
#       appears — if that happens before the launcher binds the port, the tunnel is cached
#       broken and the page "won't open". launcher.py prints the loud, now-LIVE banner
#       itself, immediately after it binds the port (so the link is only ever surfaced
#       once the port is actually accepting connections). File write only — no stdout URL. ──
STUDIO_URL="http://localhost:$PORT"
echo "$STUDIO_URL" > "$SCRIPT_DIR/.launcher-url"   # discoverable: cat dx-ai-studio/.launcher-url
echo "  Starting DeepX AI Studio on port $PORT  (the clickable URL appears once it's ready)"

# Interpreter selection. The launcher spawns each module server with this interpreter,
# so the choice propagates to every module.
#
# We need a venv (not bare system python) because:
#   1. the studio is installed editable (`pip install -e`), which fails on a modern
#      externally-managed system Python (PEP 668);
#   2. it MUST be created with --system-site-packages so it inherits the platform's
#      DEEPX runtime (`dx_engine`, from the dx-runtime install) and GStreamer Python
#      bindings (`gi`/PyGObject). Without them DX Monitor falls back to mock and DX
#      Stream cannot run pipelines. These are platform deps (like the NPU driver), not
#      pip third-party — the studio's own code stays stdlib-only (pyproject deps == []).
if [[ ! -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
  echo "  [launcher.sh] Creating .venv (--system-site-packages) ..."
  python3 -m venv --system-site-packages "$SCRIPT_DIR/.venv" 2>/dev/null || true
fi
if [[ -x "$SCRIPT_DIR/.venv/bin/python" ]]; then
  DX_PY="$SCRIPT_DIR/.venv/bin/python"
else
  DX_PY="python3"   # last-resort fallback (mock mode); editable install may be unavailable
fi
# Ensure the studio package is importable so module servers resolve `import dx_app.core...`
# etc. The studio has zero third-party deps (stdlib only), so put the repo root on PYTHONPATH —
# this alone makes `import shared, dx_app` work on a fresh `git clone` with NO install. The
# editable install below is now just an optimization (kept for parity); it's no longer required,
# and its silent failure ("No module named 'shared'") can't break startup anymore.
export PYTHONPATH="$SCRIPT_DIR${PYTHONPATH:+:$PYTHONPATH}"
"$DX_PY" -c "import shared, dx_app" 2>/dev/null || "$DX_PY" -m pip install -e "$SCRIPT_DIR" >/dev/null 2>&1 || true
"$DX_PY" "$SCRIPT_DIR/launcher/launcher.py" --port "$PORT"
