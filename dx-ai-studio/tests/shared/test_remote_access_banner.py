"""The console banner that shows the remote access code is English only."""
import re

from shared.remote_access import _announce_to_console


def test_banner_has_no_hangul(capsys):
    _announce_to_console("280988")
    out = capsys.readouterr().out
    assert "280988" in out
    assert not re.search(r"[가-힣]", out)
