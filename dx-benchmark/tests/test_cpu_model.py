"""Host CPU model name from `lscpu`.

On big.LITTLE SoCs some lscpu builds print one ``Model name`` per cluster, and the first
one can be the placeholder ``-``. The recorded CPU must be the real core names, never ``-``.
"""
from benchmark import env_fingerprint as ef


def _cpu(monkeypatch, lscpu_out):
    monkeypatch.setattr(ef.shutil, "which", lambda _name: "/usr/bin/lscpu")
    monkeypatch.setattr(ef, "_run", lambda _cmd, *a, **kw: lscpu_out)
    return ef._get_cpu_model()


def test_single_model_name(monkeypatch):
    out = "Architecture: x86_64\nModel name:          AMD Ryzen 5 9600X 6-Core Processor\n"
    assert _cpu(monkeypatch, out) == "AMD Ryzen 5 9600X 6-Core Processor"


def test_placeholder_dash_is_skipped(monkeypatch):
    out = "Model name:          -\nModel name:          Cortex-A55\nModel name:          Cortex-A76\n"
    assert _cpu(monkeypatch, out) == "Cortex-A55 + Cortex-A76"


def test_big_little_names_are_joined_without_duplicates(monkeypatch):
    out = ("Model name:          Cortex-A55\nModel name:          Cortex-A76\n"
           "Model name:          Cortex-A76\n")
    assert _cpu(monkeypatch, out) == "Cortex-A55 + Cortex-A76"


def test_only_placeholder_never_returns_dash(monkeypatch):
    assert _cpu(monkeypatch, "Model name:          -\n") != "-"
