"""REPORT.md throughput section shows the buffer-count winner + sweep curve."""
from benchmark.reporter import _add_model_throughput_section


def _row(**kw):
    base = {"model": "yolo26-n_640x640.dxnn", "task": "object_detection", "size": "n",
            "use_ort": False, "family": "throughput", "fps": 322.0, "fps_std": 1.0,
            "cpu_pct": 180.0, "status": "ok"}
    base.update(kw)
    return base


def test_throughput_table_has_bc_column_with_winner():
    rows = [_row(buffer_count=5, buffer_count_curve="3:215.0 4:282.0 5:322.0 6:302.0 7:298.0 8:297.0")]
    lines = []
    _add_model_throughput_section(lines, rows)
    out = "\n".join(lines)
    assert "BC" in out                      # BC column header
    # the winner value appears in the throughput row (…| 322.0 ±1.0 | 5 | 180 |…)
    assert "| 5 |" in out


def test_throughput_section_has_sweep_curve_with_bolded_winner():
    rows = [_row(buffer_count=5, buffer_count_curve="3:215.0 4:282.0 5:322.0 6:302.0 7:298.0 8:297.0")]
    lines = []
    _add_model_throughput_section(lines, rows)
    out = "\n".join(lines)
    assert "Buffer-count sweep" in out       # dedicated sub-table below throughput
    assert "[3]:215" in out and "[8]:297" in out  # curve endpoints, bracketed bc
    assert " · " in out                       # pairs clearly separated
    assert "**[5]:322" in out                 # winner bolded
    assert "★" in out                         # winner marked


def test_bc_columns_absent_for_legacy_rows_without_buffer_count():
    rows = [_row()]   # no buffer_count / buffer_count_curve (old data)
    lines = []
    _add_model_throughput_section(lines, rows)
    out = "\n".join(lines)
    assert "Buffer-count sweep" not in out    # no empty sweep table for legacy runs


def test_sweep_curve_shows_one_decimal_not_integer_rounded():
    # Stored curve keeps 1 decimal; the table must display that decimal so the
    # winner's margin is visible instead of being hidden by integer rounding.
    rows = [_row(buffer_count=5,
                 buffer_count_curve="3:215.3 4:282.6 5:322.1 6:302.9 7:298.0 8:297.4")]
    lines = []
    _add_model_throughput_section(lines, rows)
    out = "\n".join(lines)
    assert "[3]:215.3" in out
    assert "[4]:282.6" in out                  # would be 283 if integer-rounded
    assert "**[5]:322.1 ★**" in out            # winner bolded, 1 decimal
    assert "[8]:297.4" in out
    assert "[4]:283" not in out                # no integer-rounded form


def test_sweep_subtable_has_winner_policy_footnote():
    rows = [_row(buffer_count=5,
                 buffer_count_curve="3:215.0 4:282.0 5:322.0 6:302.0 7:298.0 8:297.0")]
    lines = []
    _add_model_throughput_section(lines, rows)
    out = "\n".join(lines)
    # footnote clarifies that ★ is decided on full precision and shown rounded
    assert "highest measured throughput" in out
    assert "1 decimal" in out
