"""Setup's WebRTC check needs both packages (2026-10-11 real-use audit).

With gstreamer1.0-nice installed Setup showed "gstreamer1.0-nice OK" and marked step 6 done, but Local (WebRTC)
still fell back to MJPEG every time: the server also needs the GstWebRTC bindings (gir1.2-gst-plugins-bad-1.0), which
step 6 installs but nothing checked.
"""
from dx_stream.core import status


def test_webrtc_is_ok_only_with_nice_and_the_gstwebrtc_bindings(monkeypatch):
    monkeypatch.setattr(status, "_nice_plugin_ok", lambda: True)
    monkeypatch.setattr(status, "_gi_webrtc_ok", lambda: False)
    r = status._check_webrtc()
    assert r["ok"] is False and r["nice_plugin"] is True and r["gi_webrtc"] is False
    assert r["missing"] == ["gir1.2-gst-plugins-bad-1.0"]
    monkeypatch.setattr(status, "_gi_webrtc_ok", lambda: True)
    assert status._check_webrtc() == {"ok": True, "nice_plugin": True, "gi_webrtc": True, "missing": []}


def test_setup_names_what_is_missing():
    from pathlib import Path
    js = (Path(__file__).resolve().parents[2] / "dx_stream/static/js/stream-setup.js").read_text(encoding="utf-8")
    assert "status.webrtc.missing" in js and "sysStatus.webrtc.ok" in js
