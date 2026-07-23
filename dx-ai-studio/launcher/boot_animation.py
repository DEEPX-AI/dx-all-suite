"""Terminal boot animation for DX AI Studio launcher.

Provides ASCII art logo display and module boot progress bar.
Uses only Python stdlib (sys, time, shutil, socket).
"""
import shutil
import socket
import sys
import time

_BLUE = '\033[38;5;69m'
_BRIGHT_BLUE = '\033[38;5;111m'
_CYAN = '\033[38;5;45m'
_GREEN = '\033[38;5;77m'
_RED = '\033[38;5;203m'
_DIM = '\033[2m'
_RESET = '\033[0m'

# ANSI 256-color gradient: deep blue → cyan
_LOGO_COLORS = [
    '\033[38;5;27m',   # 진파랑
    '\033[38;5;27m',
    '\033[38;5;33m',   # 파랑
    '\033[38;5;33m',
    '\033[38;5;39m',   # 시안블루
    '\033[38;5;39m',
]


_LOGO_LINES = [
    "  ██████╗ ███████╗███████╗██████╗ ██╗  ██╗",
    "  ██╔══██╗██╔════╝██╔════╝██╔══██╗╚██╗██╔╝",
    "  ██║  ██║█████╗  █████╗  ██████╔╝ ╚███╔╝ ",
    "  ██║  ██║██╔══╝  ██╔══╝  ██╔═══╝  ██╔██╗ ",
    "  ██████╔╝███████╗███████╗██║     ██╔╝ ██╗",
    "  ╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝  ╚═╝",
]
_SUBTITLE = "═══ AI Studio ═══"


def show_logo(*, file=None, animate=True, term_width=None):
    """Print the DEEPX ASCII art logo with ANSI colors.

    Args:
        file: Output stream (default: sys.stdout).
        animate: If True, print line-by-line with delay.
        term_width: Override terminal width (for testing).
    """
    out = file or sys.stdout
    if term_width is None:
        term_width = shutil.get_terminal_size((80, 24)).columns

    out.write('\n')
    for i, line in enumerate(_LOGO_LINES):
        if len(line) > term_width:
            color = _LOGO_COLORS[0]
            out.write(f"{color}  DEEPX{_RESET}\n")
            out.write(f"  {_CYAN}{_SUBTITLE}{_RESET}\n\n")
            out.flush()
            return
        color = _LOGO_COLORS[i % len(_LOGO_COLORS)]
        out.write(f"{color}{line}{_RESET}\n")
        out.flush()
        if animate:
            time.sleep(0.04)

    logo_width = max(len(line) for line in _LOGO_LINES)
    padding = (logo_width - len(_SUBTITLE)) // 2
    out.write(f"{_CYAN}{' ' * padding}{_SUBTITLE}{_RESET}\n\n")
    out.flush()
    if animate:
        time.sleep(0.15)


_BAR_WIDTH = 20


def _format_bar(filled, total, state='progress'):
    """Format a progress bar string with ANSI colors."""
    color = {
        'progress': _BLUE,
        'done': _GREEN,
        'fail': _RED,
    }.get(state, _BLUE)

    bar = '█' * filled + '░' * (total - filled)
    return f"{color}[{bar}]{_RESET}"


def _check_port(port):
    """Check if a TCP port is accepting connections."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)
        result = s.connect_ex(('127.0.0.1', port))
        s.close()
        return result == 0
    except Exception:
        return False


def _module_visual_progress(index, tick, min_ticks, module_count):
    """Return staggered visual progress for a module."""
    if min_ticks <= 1:
        return _BAR_WIDTH
    delay = index
    effective_tick = max(0, tick - 1 - delay)
    spread = max(1, min_ticks - 1 + max(0, module_count - 1))
    return min(int(effective_tick / spread * _BAR_WIDTH), _BAR_WIDTH)


def show_boot_progress(modules, *, file=None, poll_interval=0.2, timeout=30,
                       min_ticks=9):
    """Show boot progress bars for each module.

    Args:
        modules: Dict of {name: port} for each module.
        file: Output stream (default: sys.stdout).
        poll_interval: Seconds between polls.
        timeout: Max seconds to wait before giving up.
        min_ticks: Minimum redraw count before completing ready modules.
    """
    out = file or sys.stdout
    names = list(modules.keys())
    ports = list(modules.values())
    ready = [False] * len(names)
    max_name_len = max(len(n) for n in names)
    min_ticks = max(1, int(min_ticks))

    out.write(f"  {_DIM}Booting modules...{_RESET}\n")
    out.flush()

    start = time.time()
    first_draw = True
    tick = 0
    while (time.time() - start) < timeout:
        for i, (name, port) in enumerate(zip(names, ports)):
            if not ready[i]:
                ready[i] = _check_port(port)

        if not first_draw:
            out.write(f"\033[{len(names)}A")
        first_draw = False
        tick += 1
        for i, (name, port) in enumerate(zip(names, ports)):
            padded = name.ljust(max_name_len)
            visual_progress = _module_visual_progress(i, tick, min_ticks, len(names))
            if ready[i] and visual_progress >= _BAR_WIDTH:
                bar = _format_bar(_BAR_WIDTH, _BAR_WIDTH, 'done')
                status = f"{_GREEN}✓{_RESET}"
            else:
                elapsed = time.time() - start
                timeout_progress = min(int(elapsed / timeout * _BAR_WIDTH), _BAR_WIDTH - 1)
                progress = max(visual_progress, timeout_progress)
                if ready[i]:
                    progress = min(progress, _BAR_WIDTH - 1)
                bar = _format_bar(progress, _BAR_WIDTH, 'progress')
                status = f"{_DIM}⟳{_RESET}"
            out.write(f"\r  ✦ {padded} {bar} {status} :{port}\n")
        out.flush()

        if all(ready) and all(
                _module_visual_progress(i, tick, min_ticks, len(names)) >= _BAR_WIDTH
                for i in range(len(names))):
            break
        time.sleep(poll_interval)

    if not all(ready):
        out.write(f"\033[{len(names)}A")
        for i, (name, port) in enumerate(zip(names, ports)):
            padded = name.ljust(max_name_len)
            if ready[i]:
                bar = _format_bar(_BAR_WIDTH, _BAR_WIDTH, 'done')
                status = f"{_GREEN}✓{_RESET}"
            else:
                bar = _format_bar(0, _BAR_WIDTH, 'fail')
                status = f"{_RED}✗{_RESET}"
            out.write(f"\r  ✦ {padded} {bar} {status} :{port}\n")
        out.write(f"\n  {_RED}⚠ Some modules failed to start (timeout: {timeout}s){_RESET}\n")
    else:
        out.write(f"\n  {_GREEN}✅ All systems ready{_RESET}\n")
    out.flush()


_YELLOW = '\033[33m'
_CHECK_GREEN = '\033[32m'  # standard green (spec requires distinct from 256-color _GREEN)
_CHECK_LABEL_WIDTH = 30

_CHECK_ITEMS = [
    ('[BOOT]', 'Initializing DeepX NPU Runtime...', None, None),
    ('[CHECK]', 'Python Environment', '✓', 'OK'),
    ('[CHECK]', 'NPU SDK Path', '✓', 'Found'),
    ('[CHECK]', 'Network Ports', '✓', 'Clear'),
]


def _build_check_items(module_count=None):
    items = list(_CHECK_ITEMS)
    registry_count = module_count if module_count is not None else 8
    items.append(('[CHECK]', 'Module Registry', '✓', f'{registry_count}/{registry_count}'))
    return items


def show_system_check(*, file=None, animate=True, term_width=None, module_count=None):
    """Display system preflight check sequence (cosmetic only)."""
    out = file or sys.stdout
    if term_width is None:
        term_width = shutil.get_terminal_size((80, 24)).columns

    if term_width < 50:
        out.write(f"  {_CYAN}[SYS]  Preflight OK{_RESET}\n\n")
        out.flush()
        return

    out.write('\n')

    for tag, label, mark, result in _build_check_items(module_count):
        out.write(f"  {_YELLOW}{tag}{_RESET} {label}")
        out.flush()

        if mark is None:
            out.write('\n')
            out.flush()
            if animate:
                time.sleep(0.15)
            continue

        dots = '.' * max(0, _CHECK_LABEL_WIDTH - len(label))
        if animate:
            for dot in dots:
                out.write(dot)
                out.flush()
                time.sleep(0.008)
        else:
            out.write(dots)

        out.write(f" {_CHECK_GREEN}{mark} {result}{_RESET}\n")
        out.flush()
        if animate:
            time.sleep(0.1)

    out.write(f"  {_CYAN}[SYS]  All preflight checks passed{_RESET}\n\n")
    out.flush()
    if animate:
        time.sleep(0.15)


def show_completion_banner(port, *, file=None, term_width=None):
    """Display completion banner with box-drawing border."""
    out = file or sys.stdout
    if term_width is None:
        term_width = shutil.get_terminal_size((80, 24)).columns

    msg = f"All Systems Online — http://localhost:{port}"
    inner = f"  ✓ {msg}  "
    width = len(inner)

    if width + 2 > term_width:
        out.write(f"\n  {_GREEN}✓ Online — :{port}{_RESET}\n\n")
        out.flush()
        return

    out.write(f"\n  {_GREEN}╔{'═' * width}╗{_RESET}\n")
    out.write(f"  {_GREEN}║{inner}║{_RESET}\n")
    out.write(f"  {_GREEN}╚{'═' * width}╝{_RESET}\n\n")
    out.flush()


if __name__ == '__main__':
    show_logo()
    show_system_check()
    show_completion_banner(8890)
