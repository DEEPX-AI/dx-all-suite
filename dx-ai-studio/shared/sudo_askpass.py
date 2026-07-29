"""Shared sudo-over-web helpers.

Lets a studio module run an installer/build script that makes internal ``sudo`` calls,
feeding the password the user typed into a web dialog — without a TTY. It works by
prepending a temp dir to ``PATH`` that holds a ``sudo`` wrapper (``sudo -A "$@"``) plus a
``SUDO_ASKPASS`` script that echoes the password, so **every** ``sudo`` inside the script
authenticates non-interactively. Originally in ``dx_stream.core.setup``; promoted here so
``dx_compiler`` (SDK install) can reuse the exact same, proven mechanism.
"""
from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tempfile
import threading


def configure_sudo_env(env: dict, password: str = None):
    """Wire SUDO_ASKPASS + a PATH-shadowing ``sudo`` wrapper into *env* so nested sudo calls
    authenticate with *password*. Returns a cleanup callable (removes the temp dir + env keys).
    No-op (returns a no-op cleanup) when *password* is falsy."""
    if not password:
        return lambda: None

    real_sudo = shutil.which("sudo", path=os.environ.get("PATH")) or "/usr/bin/sudo"
    temp_dir = tempfile.mkdtemp(prefix="dx-sudo-")
    os.chmod(temp_dir, 0o700)
    pass_path = os.path.join(temp_dir, "password")
    askpass_path = os.path.join(temp_dir, "askpass.sh")
    sudo_wrapper_path = os.path.join(temp_dir, "sudo")

    fd = os.open(pass_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(password)

    with open(askpass_path, "w", encoding="utf-8") as f:
        f.write(f"#!/bin/sh\nexec /bin/cat {shlex.quote(pass_path)}\n")
    os.chmod(askpass_path, 0o700)

    with open(sudo_wrapper_path, "w", encoding="utf-8") as f:
        f.write(f"#!/bin/sh\nexec {shlex.quote(real_sudo)} -A \"$@\"\n")
    os.chmod(sudo_wrapper_path, 0o700)

    env["SUDO_ASKPASS"] = askpass_path
    env["SUDO_REQUIRE_ASKPASS"] = "force"
    env["DX_REAL_SUDO"] = real_sudo
    env["PATH"] = temp_dir + os.pathsep + env.get("PATH", "")

    def cleanup():
        shutil.rmtree(temp_dir, ignore_errors=True)
        for key in ("SUDO_ASKPASS", "SUDO_REQUIRE_ASKPASS", "DX_REAL_SUDO"):
            env.pop(key, None)

    return cleanup


def preauthorize_sudo(password: str = None, env: dict = None):
    """Open a sudo timestamp so nested sudo calls in scripts do not need a TTY.
    Returns None on success, or a short error string (wrong/expired/missing password)."""
    try:
        if password and env and env.get("SUDO_ASKPASS"):
            result = subprocess.run(
                [env.get("DX_REAL_SUDO", "sudo"), "-A", "-v"],
                capture_output=True, text=True, timeout=30, env=env,
            )
        elif password:
            result = subprocess.run(
                ["sudo", "-S", "-v"],
                input=password + "\n",
                capture_output=True, text=True, timeout=30, env=env,
            )
        else:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True, text=True, timeout=10, env=env,
            )
    except FileNotFoundError:
        return "sudo not found"
    except subprocess.TimeoutExpired:
        return "sudo authentication timed out"

    if result.returncode == 0:
        return None
    output = (result.stderr or result.stdout or "sudo authentication failed").strip()
    if not password:
        return "sudo password is required"
    return output.splitlines()[-1] if output else "sudo authentication failed"


def keep_sudo_alive(stop_event: threading.Event):
    """Refresh the sudo timestamp every 60s until *stop_event* is set (for long installs)."""
    while not stop_event.wait(60):
        subprocess.run(["sudo", "-n", "-v"], capture_output=True, text=True, timeout=10)
