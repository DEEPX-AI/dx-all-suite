import subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]  # dx-ai-studio/


def test_launcher_sh_sets_debug_env_and_help():
    src = (ROOT / "launcher.sh").read_text(encoding="utf-8")
    assert "--debug)" in src and 'export DX_STUDIO_DEBUG=1' in src
    assert "--debug=" in src
    assert "--debug" in src.split("Usage:", 1)[-1][:400]


def test_gitignore_excludes_debug_log_dir():
    gi = (ROOT / ".gitignore")
    assert gi.exists(), ".gitignore must exist"
    assert "var/log/" in gi.read_text(encoding="utf-8")


def _extract_argparse_block(src):
    # Pull the real `while [[ "$#" ... ]]; do ... done` arg-parse loop out of launcher.sh
    # so the test drives the ACTUAL case arms, not a hand-copied duplicate.
    lines = src.splitlines()
    start = next(i for i, l in enumerate(lines) if l.lstrip().startswith('while [[ "$#"'))
    end = next(j for j in range(start + 1, len(lines)) if lines[j].strip() == "done")
    return "\n".join(lines[start:end + 1])


def test_debug_flag_actually_exports(tmp_path):
    src = (ROOT / "launcher.sh").read_text(encoding="utf-8")
    block = _extract_argparse_block(src)
    # Prove we captured the real debug arms (guards against silent extraction drift).
    assert "--debug=*)" in block and "--debug)" in block
    driver = block + '\necho "$DX_STUDIO_DEBUG:$DX_STUDIO_DEBUG_LOG"'
    out = subprocess.run(["bash", "-c", driver, "_", "--debug=/tmp/x.log"],
                         capture_output=True, text=True).stdout.strip()
    assert out == "1:/tmp/x.log", out
    out2 = subprocess.run(["bash", "-c", driver, "_", "--debug"],
                          capture_output=True, text=True).stdout.strip()
    assert out2 == "1:", out2
