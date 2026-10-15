"""graph_events: [EVENT] lines and --events files (the event object of the spec, section 6)."""
from __future__ import annotations

from dx_app.core import graph_events
from tests.dx_app import graph_fakes


def test_an_event_line_becomes_a_typed_event():
    ev = graph_events.parse_event_line('[EVENT] {"frame": 12, "time": 0.48, "stream": "cam", "node": "zone", '
                                       '"event": "enter", "track_id": 3, "data": {"zone": 0}}')
    assert ev == {"frame": 12, "time": 0.48, "stream": "cam", "node": "zone", "event": "enter", "track_id": 3,
                  "data": {"zone": 0}}


def test_lines_that_are_not_events_are_skipped():
    for line in ("[PROGRESS] frames=1", "[EVENT] not json", '[EVENT] {"node": "zone"}', '[EVENT] ["a"]',
                 '[EVENT] {"node": "", "event": "x"}', ""):
        assert graph_events.parse_event_line(line) is None, line


def test_odd_field_types_do_not_break_an_event():
    ev = graph_events.parse_event_line('[EVENT] {"node": "a", "event": "b", "frame": "7", "time": true, '
                                       '"track_id": 1e400, "stream": 5, "data": [1]}')
    assert ev == {"frame": None, "time": None, "stream": None, "node": "a", "event": "b", "track_id": None,
                  "data": {}}


def test_the_log_numbers_events_and_hands_out_only_new_ones():
    """run_events.log is a real 2-frame run of zone_intrusion.json: five people enter the zone on frame 0, then the
    alarm fires once (track_id -1: more than one track)."""
    log = graph_events.EventLog(keep=6)
    assert log.feed(graph_fakes.fixture("run_events.log") + "[EVENT] not json\n") == 6
    assert [e["seq"] for e in log.since(0)] == [1, 2, 3, 4, 5, 6]
    assert [e["seq"] for e in log.since(4)] == [5, 6]
    assert log.since(5)[0]["track_id"] == -1 and log.since(5)[0]["data"]["track_ids"] == "0,3,4,5,7"
    assert log.snapshot() == {"event_total": 6, "event_counts": {"zone": {"enter": 5}, "alarm": {"intrusion": 1}}}
    for _ in range(5):
        log.add({"node": "zone", "event": "exit", "frame": None, "time": None, "stream": None, "track_id": 1,
                 "data": {}})
    assert [e["seq"] for e in log.since(0)] == [6, 7, 8, 9, 10, 11], "only the last `keep` are kept"
    assert log.snapshot()["event_total"] == 11, "counts cover every event"
    assert log.listing()["truncated"] is True
    assert len(log.since(0, limit=2)) == 2


def test_a_jsonl_file_is_read_with_totals_and_skips_bad_lines(tmp_path):
    f = tmp_path / "events.jsonl"
    f.write_text(graph_fakes.fixture("events.jsonl") + '\n{"frame": 1, "node": "zone"}\nnot json\n', encoding="utf-8")
    r = graph_events.read_jsonl(f)
    assert r["total"] == 6 and r["truncated"] is False
    assert r["counts"] == {"zone": {"enter": 5}, "alarm": {"intrusion": 1}}
    assert [e["seq"] for e in r["events"]] == [1, 2, 3, 4, 5, 6] and r["events"][1]["track_id"] == 3
    capped = graph_events.read_jsonl(f, limit=1)
    assert len(capped["events"]) == 1 and capped["total"] == 6 and capped["truncated"] is True
    assert graph_events.read_jsonl(tmp_path / "none.jsonl") == {"events": [], "total": 0, "counts": {},
                                                                "truncated": False}
