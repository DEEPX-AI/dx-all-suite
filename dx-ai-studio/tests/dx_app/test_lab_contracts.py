"""DX-APP Lab UI/session contracts — Phase 7 Release Hardening."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent.parent
INDEX = ROOT / "dx_app" / "templates" / "index.html"
DEV_JS = ROOT / "dx_app" / "static" / "js" / "developer.js"
UTILS_JS = ROOT / "dx_app" / "static" / "js" / "utils.js"
SERVER = ROOT / "dx_app" / "server.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_lab_nav_is_between_modelzoo_and_outputs():
    # The in-app DX-COM compiler nav was removed (dx-compiler is the single source);
    # Lab now sits between ModelZoo and Outputs.
    html = _read(INDEX)
    modelzoo = html.index('data-page="modelzoo"')
    lab = html.index('data-page="lab"')
    outputs = html.index('data-page="outputs"')
    assert modelzoo < lab < outputs
    assert 'data-page="compiler"' not in html
    assert '<span class="en">Lab</span>' in html
    assert '<span class="ko">실험실</span>' in html


def test_lab_has_no_password_gate_or_dev_auth_modal():
    html = _read(INDEX)
    js = _read(DEV_JS)
    assert 'id="dev-pw"' not in html
    assert "devAuth(" not in js
    assert "/api/dev/auth" not in js
    assert "openModal('modal-dev')" not in js


def test_lab_session_endpoint_and_token_header_exist():
    server = _read(SERVER)
    utils = _read(UTILS_JS)
    assert '"/api/lab/session"' in server
    # X-Lab-Token must be sent by postJ in utils.js (not just a comment in developer.js)
    assert "X-Lab-Token" in utils
    # Verify postJ function actually sends the header
    assert re.search(r"['\"]X-Lab-Token['\"]", utils), \
        "utils.js postJ must send X-Lab-Token header"


def test_lab_session_tokens_expire_after_ttl(monkeypatch):
    import developer

    developer._lab_sessions.clear()
    monkeypatch.setattr(developer, "_LAB_SESSION_TTL_SECONDS", 1, raising=False)
    monkeypatch.setattr(developer.time, "time", lambda: 100)
    tok = developer.lab_session()["token"]
    assert developer.lab_check(tok) is True

    monkeypatch.setattr(developer.time, "time", lambda: 102)
    assert developer.lab_check(tok) is False
    assert tok not in developer._lab_sessions


def test_no_nav_opendev_recursion():
    """nav('lab') → openDev() → nav('lab') 무한 재귀가 없어야 한다."""
    js = _read(DEV_JS)
    utils = _read(UTILS_JS)
    # openDev must NOT unconditionally call nav('lab')
    # Either openDev doesn't call nav('lab') at all, or nav('lab') doesn't call openDev()
    nav_calls_opendev = bool(re.search(r"if\s*\(\s*page\s*===?\s*['\"]lab['\"]\s*\)\s*openDev\s*\(", utils))
    opendev_calls_nav = bool(re.search(r"function\s+openDev\b[\s\S]*?nav\s*\(\s*['\"]lab['\"]\s*\)", js))
    assert not (nav_calls_opendev and opendev_calls_nav), \
        "nav('lab') calls openDev() and openDev() calls nav('lab') — infinite recursion"


def test_opendev_navigates_to_lab():
    """openDev() must navigate to lab page, not just init it."""
    js = _read(DEV_JS)
    # openDev should call nav('lab') to navigate to lab page
    # (nav('lab') internally calls initLabPage, so openDev should NOT also call initLabPage directly)
    has_nav_call = bool(re.search(r"nav\s*\(\s*['\"]lab['\"]\s*\)", js))
    has_only_init = bool(re.search(r"function\s+openDev\b[^}]*\binitLabPage\s*\(\s*\)", js))
    # openDev must either call nav('lab') or some other navigation mechanism
    assert has_nav_call or not has_only_init, \
        "openDev() must navigate to lab page, not just call initLabPage()"


def test_devAddModel_handles_overwrite_confirm():
    """devAddModel must detect overwrite error (existing array) and retry with confirm_overwrite."""
    js = _read(DEV_JS)
    # Must check for existing array in response
    assert "res.existing" in js, "devAddModel must check res.existing for overwrite prompt"
    assert "confirm_overwrite" in js, "devAddModel must send confirm_overwrite on retry"
    # Must call confirm() for user approval
    assert re.search(r"confirm\s*\(", js), "devAddModel must call confirm() before overwrite"


def test_devNewTask_handles_overwrite_confirm():
    """devNewTask must detect overwrite error (existing array) and retry with confirm_overwrite."""
    js = _read(DEV_JS)
    # Find devNewTask function and verify it handles overwrite
    idx = js.index("devNewTask")
    snippet = js[idx:idx+1500]
    assert "confirm_overwrite" in snippet, "devNewTask must send confirm_overwrite on retry"
    assert "existing" in snippet, "devNewTask must check for existing array"


def test_cors_preflight_uses_x_lab_token_not_x_dev_token():
    """CORS preflight must allow X-Lab-Token, not X-Dev-Token."""
    server_src = (ROOT / "shared" / "dx_server.py").read_text()
    assert "X-Lab-Token" in server_src, "CORS must allow X-Lab-Token"
    # X-Dev-Token should not appear in CORS allow-headers
    assert 'X-Dev-Token' not in server_src.split("Access-Control-Allow-Headers")[1].split("\n")[0], \
        "CORS preflight must not allow X-Dev-Token"
