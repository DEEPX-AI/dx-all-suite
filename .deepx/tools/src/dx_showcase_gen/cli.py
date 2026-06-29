"""dx-showcase-gen CLI.

Subcommands (deterministic mechanics; the skill orchestrates them):
  transcript      render a COMPLETE transcript from a stream-json capture
  verify          run the showcase verification gate (exit 1 on any failure)
  copy-artifacts  copy a build session's files into the showcase dir (+portability scan)
  augment         upsert a GIF block into a README/doc (idempotent, marker-anchored)
  regen-docs      regenerate the card grid / catalog / 00-docs table from showcases.json
  gif             encode a timelapse GIF from a captured mp4
  crop            post-crop a full-screen capture to a window rect
  window-rect     print a window's rect (xwininfo) as WxH+X+Y
  capture-start   start an x11grab full-screen capture (backgrounded; writes pidfile)
  capture-stop    stop a capture started with capture-start (clean SIGINT)
  keepawake       start/stop the screensaver-blank keep-awake loop
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

from . import constants as C
from . import artifacts, augment, recorder, transcript, verify


def _cmd_transcript(a) -> int:
    try:
        out = transcript.render(a.out_dir, stream_json=a.stream_json,
                                session_id=a.session_id, project=a.project,
                                tool=a.tool, prefix=a.prefix,
                                require_complete=not a.allow_incomplete)
    except transcript.IncompleteTranscript as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    for k, v in out.items():
        print(f"{k}: {v}")
    return 0


def _cmd_verify(a) -> int:
    rep = verify.verify_showcase(
        a.showcase_dir, stream_json=a.stream_json,
        expected_tool=a.tool, expected_model=a.model,
        gifs=a.gif, require_files=a.require_file, augment_targets=a.augment_target,
        showcase_name=a.name)
    print(rep.render())
    return 0 if rep.passed else 1


def _cmd_copy_artifacts(a) -> int:
    res = artifacts.copy_session_artifacts(a.session_dir, a.showcase_dir, include=a.include)
    print(f"copied: {res['copied']}")
    print(f"skipped: {res['skipped']}")
    flags = artifacts.scan_nonportable(a.showcase_dir)
    if flags:
        print("\nPORTABILITY — fix these absolute/session-specific refs:")
        for f in flags:
            print(f"  {f['file']}:{f['line']}: {f['text']}")
    return 0


def _cmd_augment(a) -> int:
    changed = augment.augment_readme_gif(a.readme, name=a.name, anchor=a.anchor,
                                         gif_rel=a.gif, caption=a.caption, width=a.width,
                                         sample_rel=a.sample or "",
                                         sample_caption=a.sample_caption or "")
    print(f"{'updated' if changed else 'unchanged'}: {a.readme}")
    return 0


def _cmd_regen_docs(a) -> int:
    from . import manifest as M
    root = Path(a.repo_root).resolve()
    man = M.load_manifest(str(root))
    surfaces = [
        ("README.md", "cardgrid", augment.cardgrid_region(man, lang="en"), "dx-agent-dev (Beta)"),
        ("README-KO.md", "cardgrid", augment.cardgrid_region(man, lang="ko"), "dx-agent-dev (Beta)"),
        ("dx-agent-dev-showcase/README.md", "catalog",
         augment.catalog_region(man, lang="en"), "<!-- catalog -->"),
        ("dx-agent-dev-showcase/README-ko.md", "catalog",
         augment.catalog_region(man, lang="ko"), "<!-- catalog -->"),
        ("docs/source/00_Agent_Driven_Development.md", "intro",
         augment.intro_region(man, lang="en"), "<!-- intro -->"),
        ("docs/source/00_Agent_Driven_Development_kor.md", "intro",
         augment.intro_region(man, lang="ko"), "<!-- intro -->"),
        ("docs/source/00_Agent_Driven_Development.md", "table",
         augment.categorized_table(man, lang="en"), "<!-- showcase-table -->"),
        ("docs/source/00_Agent_Driven_Development_kor.md", "table",
         augment.categorized_table(man, lang="ko"), "<!-- showcase-table -->"),
    ]
    changed = []
    for relpath, kind, block, anchor in surfaces:
        mk = f"dx-showcase:docs:{kind}"
        if augment.upsert_block(str(root / relpath), anchor=anchor, block=block, mk=mk):
            changed.append(relpath)
    missing = M.missing_from_manifest(str(root))
    if missing:
        print("WARNING: showcase dirs missing from manifest:", ", ".join(missing))
    for c in changed:
        print(f"updated: {c}")
    if not changed:
        print("unchanged (idempotent)")
    return 0


def _cmd_gif(a) -> int:
    size = recorder.make_gif(a.input, a.output, duration_secs=a.duration,
                             target_secs=a.target_secs, width=a.width)
    print(f"gif: {a.output} ({size // 1024}KB)")
    return 0 if size else 1


def _cmd_crop(a) -> int:
    if a.rect:
        w, rest = a.rect.split("x"); h, xy = rest.split("+", 1); x, y = xy.split("+")
        rect = recorder.clamp_crop(int(w), int(h), int(x), int(y))
    else:
        rect = recorder.window_rect(a.title)
        if not rect:
            print("ERROR: could not resolve window rect", file=sys.stderr)
            return 1
    ok = recorder.crop_capture(a.input, a.output, rect)
    print(f"crop {rect.w}x{rect.h}+{rect.x}+{rect.y} -> {a.output}: {'ok' if ok else 'FAIL'}")
    return 0 if ok else 1


def _cmd_window_rect(a) -> int:
    r = recorder.window_rect(a.title)
    if not r:
        print("ERROR: window not found", file=sys.stderr)
        return 1
    print(f"{r.w}x{r.h}+{r.x}+{r.y}")
    return 0


def _cmd_capture_start(a) -> int:
    log = open(a.output + ".fflog", "w")
    proc = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "x11grab",
         "-framerate", str(a.framerate), "-video_size", f"{C.SCREEN_W}x{C.SCREEN_H}",
         "-i", f"{a.display}.0", "-c:v", "libx264", "-preset", "ultrafast",
         "-pix_fmt", "yuv420p", a.output],
        stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    Path(a.pidfile).write_text(str(proc.pid))
    print(f"capture pid {proc.pid} -> {a.output}")
    return 0


def _cmd_capture_stop(a) -> int:
    pid = int(Path(a.pidfile).read_text().strip())
    try:
        os.kill(pid, signal.SIGINT)
    except ProcessLookupError:
        pass
    print(f"stopped capture pid {pid}")
    return 0


def _cmd_keepawake(a) -> int:
    if a.action == "start":
        script = (
            'while true; do '
            'dbus-send --session --type=method_call --dest=org.gnome.ScreenSaver '
            '/org/gnome/ScreenSaver org.gnome.ScreenSaver.SetActive boolean:false 2>/dev/null; '
            'xset s reset 2>/dev/null; xset s off 2>/dev/null; xset -dpms 2>/dev/null; '
            'sleep 25; done')
        env = dict(os.environ, DISPLAY=a.display)
        proc = subprocess.Popen(["bash", "-c", script], env=env, start_new_session=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        Path(a.pidfile).write_text(str(proc.pid))
        print(f"keepawake pid {proc.pid}")
    else:
        try:
            os.kill(int(Path(a.pidfile).read_text().strip()), signal.SIGTERM)
        except (ProcessLookupError, FileNotFoundError):
            pass
        print("keepawake stopped")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="dx-showcase-gen",
                                 description="Deterministic mechanics for dx-agent-dev showcases.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("transcript"); t.set_defaults(fn=_cmd_transcript)
    t.add_argument("--stream-json", required=True)
    t.add_argument("--out-dir", required=True)
    t.add_argument("--session-id"); t.add_argument("--project")
    t.add_argument("--tool", default=C.DEFAULT_TOOL)
    t.add_argument("--prefix", default=C.TRANSCRIPT_PREFIX)
    t.add_argument("--allow-incomplete", action="store_true")

    v = sub.add_parser("verify"); v.set_defaults(fn=_cmd_verify)
    v.add_argument("--showcase-dir", required=True)
    v.add_argument("--name")
    v.add_argument("--stream-json")
    v.add_argument("--tool", default=C.DEFAULT_TOOL)
    v.add_argument("--model", default=C.DEFAULT_MODEL)
    v.add_argument("--gif", action="append", default=[])
    v.add_argument("--require-file", action="append", default=[])
    v.add_argument("--augment-target", action="append", default=[])

    c = sub.add_parser("copy-artifacts"); c.set_defaults(fn=_cmd_copy_artifacts)
    c.add_argument("--session-dir", required=True)
    c.add_argument("--showcase-dir", required=True)
    c.add_argument("--include", action="append")

    g = sub.add_parser("augment"); g.set_defaults(fn=_cmd_augment)
    g.add_argument("--readme", required=True)
    g.add_argument("--name", required=True)
    g.add_argument("--anchor", required=True)
    g.add_argument("--gif", required=True)
    g.add_argument("--caption", required=True)
    g.add_argument("--width", type=int, default=760)
    g.add_argument("--sample", help="optional 2nd image (result sample) → 2-column block")
    g.add_argument("--sample-caption", default="")

    rd = sub.add_parser("regen-docs"); rd.set_defaults(fn=_cmd_regen_docs)
    rd.add_argument("--repo-root", default=".",
                    help="suite root containing dx-agent-dev-showcase/showcases.json")

    gi = sub.add_parser("gif"); gi.set_defaults(fn=_cmd_gif)
    gi.add_argument("--input", required=True); gi.add_argument("--output", required=True)
    gi.add_argument("--duration", type=float, required=True)
    gi.add_argument("--target-secs", type=int, default=C.GIF_TARGET_SECS)
    gi.add_argument("--width", type=int, default=C.GIF_WIDTH)

    cr = sub.add_parser("crop"); cr.set_defaults(fn=_cmd_crop)
    cr.add_argument("--input", required=True); cr.add_argument("--output", required=True)
    cr.add_argument("--title"); cr.add_argument("--rect", help="WxH+X+Y")

    wr = sub.add_parser("window-rect"); wr.set_defaults(fn=_cmd_window_rect)
    wr.add_argument("--title", required=True)

    cs = sub.add_parser("capture-start"); cs.set_defaults(fn=_cmd_capture_start)
    cs.add_argument("--output", required=True); cs.add_argument("--pidfile", required=True)
    cs.add_argument("--framerate", type=int, default=15); cs.add_argument("--display", default=":1")

    cst = sub.add_parser("capture-stop"); cst.set_defaults(fn=_cmd_capture_stop)
    cst.add_argument("--pidfile", required=True)

    ka = sub.add_parser("keepawake"); ka.set_defaults(fn=_cmd_keepawake)
    ka.add_argument("action", choices=["start", "stop"])
    ka.add_argument("--pidfile", required=True); ka.add_argument("--display", default=":1")

    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
