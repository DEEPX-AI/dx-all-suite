"""_cleanup_old_pids() must kill only the sub-servers the launcher itself started.

The pidfile numbers were left by a previous launcher, but after a reboot or an early server exit an unrelated
process can receive the same number. Signalling a process group by number alone would hit it.

Sub-servers are started with setsid as `python <studio>/<module>/server.py --port 0 --no-browser`
(start_sub_server). Only a process of that shape is terminated.
"""
import json
import os
import signal
import subprocess
import sys
import time

import pytest

pytestmark = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="/proc 기반")


def _spawn(argv, setsid=True):
    return subprocess.Popen(argv, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            preexec_fn=os.setsid if setsid else None)


def _alive(proc):
    return proc.poll() is None


@pytest.fixture
def launcher_mod(tmp_path, monkeypatch):
    from launcher import launcher as L
    studio = tmp_path / "studio"
    (studio / "dx_fake").mkdir(parents=True)
    (studio / "dx_fake" / "server.py").write_text("import time\ntime.sleep(60)\n")
    monkeypatch.setattr(L, "STUDIO_DIR", studio)
    monkeypatch.setattr(L, "_PIDFILE", tmp_path / ".launcher_pids")
    return L


@pytest.fixture
def procs():
    started = []
    yield started
    for p in started:
        if _alive(p):
            p.kill()
        p.wait(timeout=5)


def _write_pids(L, mapping):
    L._PIDFILE.write_text(json.dumps({k: p.pid for k, p in mapping.items()}))


def test_unrelated_process_with_a_recorded_pid_survives(launcher_mod, procs):
    L = launcher_mod
    stranger = _spawn([sys.executable, "-c", "import time; time.sleep(60)"])
    procs.append(stranger)
    _write_pids(L, {"DX Stream": stranger})
    L._cleanup_old_pids()
    time.sleep(0.2)
    assert _alive(stranger), "번호만 같은 무관한 프로세스를 죽였다"
    assert not L._PIDFILE.exists()


def test_server_py_outside_the_studio_survives(launcher_mod, procs, tmp_path):
    L = launcher_mod
    other = tmp_path / "elsewhere" / "server.py"
    other.parent.mkdir()
    other.write_text("import time\ntime.sleep(60)\n")
    p = _spawn([sys.executable, str(other), "--port", "0", "--no-browser"])
    procs.append(p)
    _write_pids(L, {"DX Stream": p})
    L._cleanup_old_pids()
    time.sleep(0.2)
    assert _alive(p), "studio 밖의 server.py 까지 죽였다"


def test_our_orphaned_sub_server_is_killed(launcher_mod, procs):
    L = launcher_mod
    server_py = L.STUDIO_DIR / "dx_fake" / "server.py"
    ours = _spawn([sys.executable, str(server_py), "--port", "0", "--no-browser"])
    procs.append(ours)
    _write_pids(L, {"DX Fake": ours})
    L._cleanup_old_pids()
    ours.wait(timeout=5)
    assert not _alive(ours)


@pytest.mark.parametrize("legacy_popen", [False, True])
def test_group_kill_only_when_the_pid_leads_its_own_group(launcher_mod, procs, monkeypatch, legacy_popen):
    """Even our own server is not signalled as a group unless it leads its group: one started without setsid
    shares the group of the shell that started the launcher."""
    L = launcher_mod
    server_py = L.STUDIO_DIR / "dx_fake" / "server.py"
    if legacy_popen:
        popen = subprocess.Popen
        def pre311_popen(*args, **kwargs):
            if "process_group" in kwargs:
                raise TypeError("Popen.__init__() got an unexpected keyword argument 'process_group'")
            return popen(*args, **kwargs)
        monkeypatch.setattr(subprocess, "Popen", pre311_popen)
    # A separate group in the same session: a setsid child is in another session and cannot join via setpgid.
    leader = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setpgrp)
    procs.append(leader)
    # Put our server.py into the leader's group, without setsid.
    member = subprocess.Popen([sys.executable, str(server_py), "--port", "0", "--no-browser"],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              preexec_fn=lambda: os.setpgid(0, leader.pid))
    procs.append(member)
    assert os.getpgid(member.pid) == leader.pid
    _write_pids(L, {"DX Fake": member})
    L._cleanup_old_pids()
    member.wait(timeout=5)
    time.sleep(0.2)
    assert not _alive(member)
    assert _alive(leader), "group 째 보내 같은 group 의 다른 프로세스까지 죽였다"


def test_unreadable_pidfile_is_removed_without_killing(launcher_mod):
    L = launcher_mod
    L._PIDFILE.write_text("{not json")
    L._cleanup_old_pids()
    assert not L._PIDFILE.exists()


@pytest.mark.parametrize("payload", ["[1, 2]", '"x"', "null", '{"DX Stream": "123"}'])
def test_wrong_shape_pidfile_does_not_crash_startup(launcher_mod, payload):
    L = launcher_mod
    L._PIDFILE.write_text(payload)
    L._cleanup_old_pids()
    assert not L._PIDFILE.exists()


def test_sigkill_rechecks_identity(launcher_mod, monkeypatch):
    """The number can be reused in the 0.3 s after SIGTERM, so identity is checked again before SIGKILL."""
    L = launcher_mod
    L._PIDFILE.write_text(json.dumps({"DX Fake": 424242}))
    answers = iter([True, False])
    monkeypatch.setattr(L, "_is_our_sub_server", lambda pid: next(answers))
    sent = []
    monkeypatch.setattr(L.os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(L.os, "killpg", lambda pid, sig: sent.append(("pg", sig)))
    monkeypatch.setattr(L.os, "kill", lambda pid, sig: sent.append(("p", sig)))
    monkeypatch.setattr(L.time, "sleep", lambda s: None)
    L._cleanup_old_pids()
    assert ("pg", signal.SIGTERM) in sent
    assert all(sig != signal.SIGKILL for _, sig in sent), sent
