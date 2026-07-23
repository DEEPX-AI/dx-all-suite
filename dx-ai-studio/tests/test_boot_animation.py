"""Tests for launcher/boot_animation.py."""
import io
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_show_logo_contains_deepx():
    """show_logo()가 DEEPX ASCII 아트를 출력하는지 확인."""
    from launcher.boot_animation import show_logo
    buf = io.StringIO()
    show_logo(file=buf, animate=False)
    output = buf.getvalue()
    assert '██' in output, "ASCII art should contain block characters"
    assert 'AI Studio' in output, "Should contain 'AI Studio' subtitle"


def test_show_logo_has_ansi_colors():
    """show_logo()가 ANSI 색상 코드를 포함하는지 확인."""
    from launcher.boot_animation import show_logo
    buf = io.StringIO()
    show_logo(file=buf, animate=False)
    output = buf.getvalue()
    assert '\033[' in output, "Should contain ANSI escape codes"


def test_show_logo_narrow_terminal():
    """좁은 터미널(40컬럼)에서도 에러 없이 출력되는지 확인."""
    from launcher.boot_animation import show_logo
    buf = io.StringIO()
    show_logo(file=buf, animate=False, term_width=40)


import socket
import threading


def test_show_boot_progress_all_ready(tmp_path):
    """모든 포트가 열려있을 때 프로그레스 바가 완료 상태로 끝나는지."""
    from launcher.boot_animation import show_boot_progress

    servers = []
    ports = {}
    for name in ["DX App", "DX Stream"]:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind(('127.0.0.1', 0))
        srv.listen(1)
        ports[name] = srv.getsockname()[1]
        servers.append(srv)

    buf = io.StringIO()
    try:
        show_boot_progress(ports, file=buf, poll_interval=0.05, timeout=2)
    finally:
        for srv in servers:
            srv.close()

    output = buf.getvalue()
    assert '✓' in output, "Should show checkmark for ready modules"
    assert 'All systems ready' in output


def test_show_boot_progress_animates_ready_ports():
    """이미 열린 포트도 최소 게이지 애니메이션을 거치는지 확인."""
    from launcher.boot_animation import show_boot_progress

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(('127.0.0.1', 0))
    srv.listen(1)
    ports = {"DX App": srv.getsockname()[1]}
    buf = io.StringIO()
    try:
        show_boot_progress(ports, file=buf, poll_interval=0, timeout=2, min_ticks=3)
    finally:
        srv.close()

    output = buf.getvalue()
    assert '[░░░░░░░░░░░░░░░░░░░░]' in output
    assert '[██████' in output
    assert '[████████████████████]' in output


def test_module_visual_progress_is_staggered():
    """모듈별 게이지가 완전히 같은 속도로 차지 않도록 stagger를 둔다."""
    from launcher.boot_animation import _module_visual_progress

    values = [
        _module_visual_progress(i, tick=6, min_ticks=9, module_count=8)
        for i in range(8)
    ]

    assert len(set(values)) >= 6
    assert values[0] > values[-1]


def test_show_boot_progress_timeout():
    """포트가 열리지 않을 때 타임아웃 처리."""
    from launcher.boot_animation import show_boot_progress

    ports = {"DX Test": 59999}
    buf = io.StringIO()
    show_boot_progress(ports, file=buf, poll_interval=0.05, timeout=0.3)
    output = buf.getvalue()
    assert '✗' in output or 'timeout' in output.lower(), "Should indicate timeout"


def test_show_logo_gradient_colors():
    """show_logo()가 행별 그라데이션 ANSI 256색 코드를 사용하는지 확인."""
    from launcher.boot_animation import show_logo
    buf = io.StringIO()
    show_logo(file=buf, animate=False)
    output = buf.getvalue()
    # 파랑→시안 그라데이션: 27/33/39 코드 모두 존재해야 함
    color_codes = set(re.findall(r'\033\[38;5;(\d+)m', output))
    assert {'27', '33', '39'}.issubset(color_codes), \
        f"Logo gradient codes 27/33/39 must all be present, got: {color_codes}"


def test_progress_bar_ansi_colors():
    """프로그레스 바가 상태별 ANSI 색상을 사용하는지."""
    from launcher.boot_animation import _format_bar
    bar = _format_bar(20, 20, 'done')
    assert '\033[38;5;77m' in bar, "Done state should use green"
    bar = _format_bar(10, 20, 'progress')
    assert '\033[38;5;69m' in bar, "Progress state should use blue"
    bar = _format_bar(0, 20, 'fail')
    assert '\033[38;5;203m' in bar, "Fail state should use red"


def test_show_system_check_output():
    """show_system_check()가 5개 점검 항목을 출력하는지 확인."""
    from launcher.boot_animation import show_system_check
    buf = io.StringIO()
    show_system_check(file=buf, animate=False)
    output = buf.getvalue()
    assert '[BOOT]' in output, "Should contain [BOOT] tag"
    assert '[CHECK]' in output, "Should contain [CHECK] tags"
    assert '✓' in output, "Should contain checkmarks"
    assert 'All preflight checks passed' in output


def test_show_system_check_uses_current_module_count():
    """show_system_check()가 현재 launcher 모듈 개수를 표시하는지 확인."""
    from launcher.boot_animation import show_system_check
    buf = io.StringIO()
    show_system_check(file=buf, animate=False, module_count=8)
    output = buf.getvalue()
    assert '8/8' in output
    assert '7/7' not in output


def test_show_system_check_has_colors():
    """show_system_check()가 ANSI 색상(노랑, 초록)을 사용하는지."""
    from launcher.boot_animation import show_system_check
    buf = io.StringIO()
    show_system_check(file=buf, animate=False)
    output = buf.getvalue()
    assert '\033[33m' in output, "Should use yellow for tags"
    assert '\033[32m' in output, "Should use green for checkmarks"


def test_show_completion_banner():
    """show_completion_banner()가 박스 테두리 배너를 출력하는지."""
    from launcher.boot_animation import show_completion_banner
    buf = io.StringIO()
    show_completion_banner(8890, file=buf)
    output = buf.getvalue()
    assert '╔' in output and '╗' in output, "Should have box border"
    assert '8890' in output, "Should contain port number"
    assert 'Online' in output


def test_show_completion_banner_narrow():
    """좁은 터미널에서 배너가 에러 없이 출력되는지."""
    from launcher.boot_animation import show_completion_banner
    buf = io.StringIO()
    show_completion_banner(8890, file=buf, term_width=40)
    output = buf.getvalue()
    assert '8890' in output
    assert '╔' not in output, "Narrow mode should not render box border"


def test_show_system_check_narrow():
    """좁은 터미널(< 50컬럼)에서 컴팩트 단일 라인을 출력하는지."""
    from launcher.boot_animation import show_system_check
    buf = io.StringIO()
    show_system_check(file=buf, animate=False, term_width=40)
    output = buf.getvalue()
    assert 'Preflight OK' in output
    assert '[CHECK]' not in output, "Narrow mode should not show individual items"
