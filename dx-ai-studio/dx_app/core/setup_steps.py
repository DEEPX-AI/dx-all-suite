"""DX-APP Setup & Installation steps."""

import logging
import os, sys, json, time, subprocess, threading, select, shutil, re, platform, tempfile, shlex
from pathlib import Path
from shared.paths import host_arch
from dx_app.core import config
from dx_app.core.config import (SCRIPT_DIR, DX_APP_ROOT, SCRIPTS_DIR, BUILD_DIR,
                    DX_COMPILER_ROOT, DX_COMPILER_VENV,
                    DX_RT_ROOT, DX_DRIVER_ROOT, ASSETS_DIR)
from shared.runtime import runtime_venv_roots


def _find_dxcom():
    """Find dxcom binary, checking venv first, then PATH."""
    venv_dxcom=DX_COMPILER_VENV/"bin"/"dxcom"
    if venv_dxcom.exists():return str(venv_dxcom)
    venv_py=DX_COMPILER_VENV/"bin"/"python3"
    if venv_py.exists():
        try:
            r=subprocess.run([str(venv_py),"-c","import shutil; p=shutil.which('dxcom'); print(p or '')"],
             capture_output=True,text=True,timeout=5)
            p=r.stdout.strip()
            if p and os.path.exists(p):return p
        except Exception:pass
    p=shutil.which("dxcom")
    if p:return p
    return None

def _dxcom_version():
    """Get DX-COM version."""
    dxcom=_find_dxcom()
    if dxcom:
        try:
            r=subprocess.run([dxcom,"--version"],capture_output=True,text=True,timeout=10)
            out=(r.stdout+r.stderr).strip()
            m=re.search(r'(\d+\.\d+\.\d+)',out)
            if m:return m.group(1)
            return out[:50] if out else None
        except Exception:pass
    rv=DX_COMPILER_ROOT/"release.ver"
    if rv.exists():return rv.read_text().strip().lstrip("v")
    return None


def _read_release_ver(path):
    """Read the version string from a release.ver file."""
    try:
        p = Path(path) if not isinstance(path, Path) else path
        if not p.is_absolute():
            p = DX_APP_ROOT / path
        return p.read_text().strip().split('\n')[0]
    except Exception:
        return '--'

def _get_npu_driver_version():
    """dxrt_driver module version (shared.dxrt.npu_driver_version), '--' when no driver is installed."""
    from shared.dxrt import npu_driver_version
    return npu_driver_version() or '--'


SETUP_STEPS={
    # Order mirrors the Setup page cards / Run All sequence (setup.js STEPS): build toolchain →
    # runtime deps → runtime build → driver → app build → assets. DX-APP Build links dx_rt
    # (CMake reads ${DXRT_INSTALLED_DIR}/include/dxrt/gen.h), so it MUST run after DX-Runtime
    # Build + driver, not before. Assets download is independent and comes last.
    "dx-app-deps":{
        "label":"DX-APP Dependencies","script":lambda:DX_APP_ROOT/"install.sh",
        "args":["--all"],"cwd":lambda:DX_APP_ROOT,
        "desc":"System packages for C++ build (cmake, gcc, ninja, OpenCV, …)",
        "needs_sudo":True,
    },
    "dx-rt-deps":{
        "label":"DX-Runtime Dependencies","script":lambda:DX_RT_ROOT/"install.sh",
        "args":["--all"],"cwd":lambda:DX_RT_ROOT,
        "desc":"System packages for DX-RT runtime (cmake, ONNX Runtime, …)",
        "needs_sudo":True,
    },
    "dx-rt-build":{
        # dx-rt-deps only installs system packages; it never builds dx_rt nor installs the
        # dx_engine Python API into venv-dx-runtime. This step runs the runtime orchestrator's
        # dx_rt target, which builds dx_rt AND pip-installs the matching dx_engine wheel into
        # the (reused, never wiped) venv — the only thing that turns the "Python venv (dx_engine)"
        # diagnostic green. --skip-uninstall + --venv-reuse protect the shared venv.
        "label":"DX-Runtime Build","script":lambda:DX_RT_ROOT.parent/"install.sh",
        "args":["--target=dx_rt","--skip-uninstall","--venv-reuse"],"cwd":lambda:DX_RT_ROOT.parent,
        "desc":"Build DX-RT runtime and install the dx_engine Python API into venv-dx-runtime",
        "needs_sudo":True,
    },
    "dx-driver":{
        "label":"NPU Linux Driver","script":lambda:DX_RT_ROOT.parent/"install.sh",
        # --skip-uninstall/--venv-reuse: every runtime target recreates venv-dx-runtime unless told to reuse
        # it (default --venv-force-remove), which deleted the dx_engine DX-Runtime Build had just installed.
        "args":["--target=dx_rt_npu_linux_driver","--skip-uninstall","--venv-reuse"],"cwd":lambda:DX_RT_ROOT.parent,
        "desc":"Install DEEPX NPU kernel driver (requires sudo)",
        "needs_sudo":True,
    },
    "dx-app-build":{
        "label":"DX-APP Build","script":lambda:DX_APP_ROOT/"build.sh",
        # Native build for THIS machine. A fixed "x86_64" turned a Raspberry Pi build into a cross build:
        # dx_postprocess skipped (the *_cpp_postprocess paths fail) and nothing installed into bin/.
        "args":["--all","--type","Release","--arch",host_arch()],"cwd":lambda:DX_APP_ROOT,
        "desc":"Compile all C++ demo and Graph binaries (cmake build)",
        # build.sh installs the postprocess .so via `sudo cp ... /usr/local/lib` + `sudo ldconfig`.
        "needs_sudo":True,
    },
    "dx-app-setup":{
        "label":"Sample Assets Setup",
        "cmd":lambda:[sys.executable,"-m","shared.asset_setup","app"],
        "cwd":lambda:Path(__file__).resolve().parents[2],
        "desc":"Download sample models and videos for demos",
    },
    "inference-venv":{
        # Option 1: guarantee ONE interpreter with numpy+cv2+dx_engine for the python-variant
        # demos, without touching dx-runtime or the base interpreter. A no-op when an existing
        # interpreter already has all three (common on dx-all-suite boards); otherwise it builds
        # an ISOLATED studio-owned venv and installs a KNOWN-GOOD dx_engine into it — a matching
        # self-contained wheel (bundles libdxrt, so it survives a mismatched system libdxrt),
        # else a verbatim copy of a working install — plus numpy + opencv-python-headless.
        # dx_engine must already be installed (it is not on PyPI) — run dx-rt-build first.
        "label":"Python Inference Deps",
        "cmd":lambda:[sys.executable,"-c",
            "from shared.runtime import ensure_inference_venv; "
            "print('OK' if ensure_inference_venv(log=print) else 'INCOMPLETE')"],
        "cwd":lambda:DX_APP_ROOT.parent,   # dx-ai-studio root so `import shared` resolves
        "desc":"Ensure numpy+cv2+dx_engine coexist for Python demos (studio venv; no dx-runtime changes)",
    },
    "model-build":{
        # One model's C++ runners, started from Model Zoo (Build C++ runner). Targets come from
        # _model_build_targets (examples that have a C++ source) — never free argv. No sudo.
        "label":"C++ runner build","script":lambda:DX_APP_ROOT/"build.sh",
        "args":["--type","Release","--arch",host_arch()],"cwd":lambda:DX_APP_ROOT,
        "desc":"Build one model's C++ runners (build.sh --target); started from Model Zoo",
    },
    "clean-build":{
        "label":"Clean C++ build",
        "cmd":lambda:[sys.executable,"-m","dx_app.core.maintenance","clean-build"],
        "cwd":lambda:DX_APP_ROOT.parent,   # dx-ai-studio root so `import dx_app` resolves
        "desc":"Delete build_* and bin/, rebuild the demo runners for this machine",
        "needs_sudo":True,
    },
    "runtime-reset":{
        "label":"Reset runtime and reinstall",
        "cmd":lambda:[sys.executable,"-m","dx_app.core.maintenance","runtime-reset"],
        "cwd":lambda:DX_APP_ROOT.parent,
        "desc":"Uninstall DX-RT, NPU driver, venvs, C++ builds (downloaded models kept)",
        "needs_sudo":True,
        "confirm":"RESET",   # typed in the page; checked again in setup_run
    },
    "dx-compiler":{
        "label":"DX-COM Compiler","script":lambda:DX_COMPILER_ROOT/"install.sh",
        "args":[],"cwd":lambda:DX_COMPILER_ROOT,
        "desc":"ONNX→.dxnn converter. Requires DEEPX Portal account",
        # NOTE: install.sh may `sudo apt` for python3/venv, but this step is needs_credentials
        # and its "password" param is the DEEPX Portal password — reusing it as the sudo
        # password would misfire. Left non-sudo (deps are normally already present).
        "needs_credentials":True,
    },
}


def _configure_sudo_env(env, password):
    if not password:
        return lambda: None

    real_sudo = shutil.which("sudo", path=os.environ.get("PATH")) or "/usr/bin/sudo"
    temp_dir = tempfile.mkdtemp(prefix="dx-setup-sudo-")
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

    # apt in the runtime scripts runs as `sudo apt-get …`; sudo drops their `export DEBIAN_FRONTEND`, and a
    # debconf dialog then waits forever (dpkg runs in apt's pty — the Setup stdin box cannot reach it).
    keep_env = "DEBIAN_FRONTEND,NEEDRESTART_MODE"
    with open(sudo_wrapper_path, "w", encoding="utf-8") as f:
        f.write(f"#!/bin/sh\nexec {shlex.quote(real_sudo)} -A --preserve-env={keep_env} \"$@\"\n")
    os.chmod(sudo_wrapper_path, 0o700)

    env["SUDO_ASKPASS"] = askpass_path
    env["SUDO_REQUIRE_ASKPASS"] = "force"
    env["DX_REAL_SUDO"] = real_sudo
    env["DEBIAN_FRONTEND"] = "noninteractive"
    env["NEEDRESTART_MODE"] = "a"
    env["PATH"] = temp_dir + os.pathsep + env.get("PATH", "")

    def cleanup():
        shutil.rmtree(temp_dir, ignore_errors=True)
        for key in ("SUDO_ASKPASS", "SUDO_REQUIRE_ASKPASS", "DX_REAL_SUDO", "DEBIAN_FRONTEND", "NEEDRESTART_MODE"):
            env.pop(key, None)

    return cleanup


def _preauthorize_sudo(password, env=None):
    """Open a sudo timestamp so nested sudo calls in setup scripts do not need a TTY."""
    try:
        if password and env and env.get("SUDO_ASKPASS"):
            result = subprocess.run(
                [env.get("DX_REAL_SUDO", "sudo"), "-A", "-v"],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
        elif password:
            result = subprocess.run(
                ["sudo", "-S", "-v"],
                input=password + "\n",
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
        else:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
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


def _keep_sudo_alive(stop_event):
    while not stop_event.wait(60):
        subprocess.run(
            ["sudo", "-n", "-v"],
            capture_output=True,
            text=True,
            timeout=10,
        )


def _probe_dx_engine_venv():
    """Probe venv-dx-runtime roots for an importable dx_engine.
    Returns (ok: bool, detail: str). Shared by setup_status() and deep_diagnostics()."""
    for vp in runtime_venv_roots():
        py=vp/"bin"/"python3"
        if py.exists():
            try:
                r=subprocess.run([str(py),"-c","import dx_engine; print(dx_engine.__version__)"],
                    capture_output=True,text=True,timeout=10)
                if r.returncode==0:return True,f"dx_engine v{r.stdout.strip()} ({vp.name})"
                return False,f"{vp.name} exists but dx_engine import failed"
            except Exception:
                return False,f"{vp.name} python3 error"
    return False,"venv-dx-runtime not found"


def _demo_targets(targets):
    """The run_demo C++ targets (build.sh --minimal: each DEMO_MODEL stem, sync + async) that this
    tree declares. Without a readable demo list every declared target counts as a demo one."""
    from shared.asset_setup import demo_model_files
    try:
        stems = [Path(name).stem for name in demo_model_files(DX_APP_ROOT)]
    except ValueError:
        return set(targets)
    wanted = {f"{stem}_{variant}" for stem in stems for variant in ("sync", "async")}
    return wanted & set(targets)


def _app_build_status():
    """Check the demo runners and Graph through the same resolvers as Studio execution.

    ``ok`` — what Run All needs: the run_demo C++ runners and both Graph binaries. Every other
    per-model target is reported (``complete``, "all C++ n/m") but does not gate readiness: one
    target that does not build on a board must not make Run All rebuild forever.
    ``demo_ok`` — what Quick Start needs (build.sh --minimal): the run_demo runners.
    """
    from dx_app.core import graph_cli
    from dx_app.core.inference_exec import _is_executable_file
    from shared import dx_app_layout

    targets = {}
    for example in dx_app_layout.examples(DX_APP_ROOT):
        if example.cpp_dir is None:
            continue
        for variant in ("sync", "async"):
            if dx_app_layout.cpp_source(DX_APP_ROOT, example.task, example.name, variant).is_file():
                name = f"{example.name}_{variant}"
                targets[name] = _is_executable_file(dx_app_layout.cpp_binary(BUILD_DIR, example.name, variant))
    graphs = {name: graph_cli.binary(variant) is not None for variant, name in graph_cli.NAMES.items()}
    demo = {name: targets[name] for name in sorted(_demo_targets(targets))}
    demo_ok = bool(demo) and all(demo.values())
    ok = demo_ok and all(graphs.values())
    missing = [name for name, ready in {**graphs, **demo}.items() if not ready]
    detail = (f"demo C++ {sum(demo.values())}/{len(demo)} · Graph {sum(graphs.values())}/{len(graphs)}"
              f" · all C++ {sum(targets.values())}/{len(targets)}")
    if missing:
        detail += " · missing: " + ", ".join(missing[:4])
        if len(missing) > 4:
            detail += f" (+{len(missing) - 4})"
    return {"ok": ok, "demo_ok": demo_ok, "complete": ok and all(targets.values()), "detail": detail}


LIVE_DISPLAY_HINT = "sudo apt install xvfb"


def live_display_status():
    """Optional: Live / graph Live display capture draws on an Xvfb virtual display.

    Not part of any installer step — dx_app install.sh --all never installs Xvfb, so it must not
    gate DX-APP Dependencies (Run All / Quick Start would re-run sudo install.sh forever).
    Live start fails with this hint when it is missing (dx_app/core/live.py, graph_live.py).
    """
    ok = bool(shutil.which("Xvfb"))
    return {"ok": ok, "optional": True, "hint": LIVE_DISPLAY_HINT,
            "detail": "Xvfb found" if ok else f"Xvfb not installed · {LIVE_DISPLAY_HINT}"}


def _dx_device_nodes():
    """Device nodes the loaded driver creates: /dev/dxrt* (newer) or /dev/deepx* (legacy)."""
    dev=Path("/dev")
    return [d.name for d in sorted(dev.glob("dxrt*"))+sorted(dev.glob("deepx*"))] if dev.exists() else []


def _driver_installed():
    """The module is on disk for the next boot. Runtime reset removes the DKMS package while the module stays
    loaded (in use) until reboot, so the device node alone would say the driver is fine."""
    try:
        return subprocess.run(["modinfo","-n","dxrt_driver"],capture_output=True,text=True,timeout=10).returncode==0
    except (OSError,subprocess.SubprocessError):
        return True     # cannot tell — do not force a driver reinstall


def _driver_status():
    devs=_dx_device_nodes()
    if not devs:
        return {"ok":False,"detail":"/dev/dxrt* or /dev/deepx* not found"}
    if any(d.startswith("dxrt") for d in devs) and not _driver_installed():
        return {"ok":False,"detail":"Loaded, but not installed for the next boot"}
    return {"ok":True,"detail":", ".join(devs)}


def setup_status():
    """Return dict of {step_id: {ok, detail}} for all setup steps."""
    r={}
    cmake_ok=bool(shutil.which("cmake"))
    gcc_ok=bool(shutil.which("gcc") or shutil.which("gcc-12") or shutil.which("g++"))
    ninja_ok=bool(shutil.which("ninja") or shutil.which("ninja-build"))
    deps=(("cmake", cmake_ok), ("gcc", gcc_ok), ("ninja", ninja_ok))
    r["dx-app-deps"]={"ok":cmake_ok and gcc_ok,
        # The screen (shared step list) splits on " · " into short facts on one line; show words, no emoji.
        "detail":" · ".join([n for n, ok in deps if ok]
                            + (["missing: " + ", ".join(n for n, ok in deps if not ok)]
                               if not all(ok for _, ok in deps) else []))}
    r["dx-app-build"]=_app_build_status()
    from shared.asset_setup import sample_assets_status
    r["dx-app-setup"]=sample_assets_status("app",sdk_root=DX_APP_ROOT)
    r["live-display"]=live_display_status()
    rv=DX_RT_ROOT/"release.ver"
    rt_ver=rv.read_text().strip() if rv.exists() else None
    # release.ver may already start with "v" (e.g. "v3.4.1") → don't double it into "vv3.4.1".
    r["dx-rt-deps"]={"ok":rv.exists(),
        "detail":f"v{rt_ver.lstrip('v')}" if rt_ver else "release.ver not found"}
    # dx-rt-build — ok only when the dx_engine Python API is importable in venv-dx-runtime
    venv_ok,venv_detail=_probe_dx_engine_venv()
    r["dx-rt-build"]={"ok":venv_ok,"detail":venv_detail}
    r["dx-driver"]=_driver_status()
    dxcom=_find_dxcom();ver=_dxcom_version()
    r["dx-compiler"]={"ok":dxcom is not None,
        "detail":f"v{ver}" if ver else ("Install required" if not (DX_COMPILER_ROOT/"install.sh").exists() else "install.sh found"),
        "needs_credentials":True}
    # inference-venv (Option 1) — ok when the resolved inference interpreter has numpy+cv2+dx_engine.
    try:
        from shared.runtime import runtime_python, _has_numpy_cv2_dxengine
        _ip=runtime_python(); _iok=_has_numpy_cv2_dxengine(_ip)
        r["inference-venv"]={"ok":_iok,
            "detail":("numpy · cv2 · dx_engine ("+Path(_ip).name+")") if _iok else "no interpreter has numpy+cv2+dx_engine yet"}
    except Exception as _e:
        r["inference-venv"]={"ok":False,"detail":f"probe failed: {_e}"}
    r["versions"] = {
        "dx_app": _read_release_ver("release.ver"),
        "dx_runtime": _read_release_ver(str(DX_RT_ROOT.parent / "release.ver")),
        "npu_driver": _get_npu_driver_version(),
        "compiler": _dxcom_version() or '--',
        "kernel": platform.release(),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    # The command each SDK card shows (rendered by setup.js) and the word the reset dialog asks for.
    r["commands"] = {sid: " ".join(_display_argv(sid)) for sid in
                     ("dx-app-deps","dx-rt-deps","dx-rt-build","dx-driver","dx-app-build","dx-app-setup")}
    r["runtime-reset"] = {"confirm": RESET_CONFIRM}
    _du = shutil.disk_usage(str(DX_APP_ROOT if DX_APP_ROOT.exists() else Path.home()))
    r["disk"] = {"free_gb": round(_du.free / 1e9, 1), "min_gb": MIN_FREE_GB}
    return r



def _dkms_check():
    """Deep Diagnostics row for the driver's DKMS entry (shared.dxrt.dkms_dxrt_status asks for the module only)."""
    from shared import dxrt
    label={"ko":"DKMS 드라이버 상태","en":"DKMS Driver Status","ja":"DKMSドライバ状態","zh-CN":"DKMS驱动状态","zh-TW":"DKMS驅動狀態","es":"Estado del driver DKMS"}
    rc,out=dxrt.dkms_dxrt_status()
    if rc==-1:
        return {"id":"dkms","label":label,"ok":False,"detail":"dkms not installed","fix":{"ko":"sudo apt install dkms","en":"sudo apt install dkms","ja":"sudo apt install dkms","zh-CN":"sudo apt install dkms","zh-TW":"sudo apt install dkms","es":"sudo apt install dkms"}}
    if rc==-2:
        return {"id":"dkms","label":label,"ok":False,"detail":"dkms status timed out"}
    dxrt_dkms=[l for l in out.splitlines() if "dxrt" in l.lower() or "deepx" in l.lower()]
    installed_ok=any("installed" in l.lower() for l in dxrt_dkms)
    return {"id":"dkms","label":label,"ok":installed_ok,
        "detail":"; ".join(dxrt_dkms)[:200] if dxrt_dkms else "No DKMS entry for dxrt/deepx",
        "fix":{"ko":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","en":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","ja":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zh-CN":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zh-TW":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","es":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver"}}

def deep_diagnostics():
    """Run deep diagnostic checks without importing native media libraries into Studio."""
    checks=[]

    # 1. PCIe Link — DeepX Vendor ID 1ff4
    try:
        out=subprocess.check_output(["lspci","-d","1ff4:"],text=True,timeout=5,stderr=subprocess.DEVNULL).strip()
        found=[l.strip() for l in out.splitlines() if l.strip()]
        checks.append({"id":"pcie_link","label":{"ko":"PCIe 링크 (DeepX)","en":"PCIe Link (DeepX)","ja":"PCIeリンク (DeepX)","zhCN":"PCIe链接 (DeepX)","zhTW":"PCIe連結 (DeepX)","es":"Enlace PCIe (DeepX)"},"ok":bool(found),
            "detail":", ".join(found) if found else "No DeepX device found on PCIe bus",
            "fix":{"ko":"NPU 보드가 올바르게 장착되었는지 확인. 실행: lspci -d 1ff4:","en":"Check NPU board is properly seated. Run: lspci -d 1ff4:","ja":"NPUボードが正しく装着されているか確認。実行: lspci -d 1ff4:","zhCN":"检查NPU板是否正确安装。执行: lspci -d 1ff4:","zhTW":"檢查NPU板是否正確安裝。執行: lspci -d 1ff4:","es":"Compruebe que la placa NPU esté bien insertada. Ejecute: lspci -d 1ff4:"}})
    except FileNotFoundError:
        checks.append({"id":"pcie_link","label":{"ko":"PCIe 링크 (DeepX)","en":"PCIe Link (DeepX)","ja":"PCIeリンク (DeepX)","zhCN":"PCIe链接 (DeepX)","zhTW":"PCIe連結 (DeepX)","es":"Enlace PCIe (DeepX)"},"ok":False,
            "detail":"lspci not installed","fix":{"ko":"sudo apt install pciutils","en":"sudo apt install pciutils","ja":"sudo apt install pciutils","zhCN":"sudo apt install pciutils","zhTW":"sudo apt install pciutils","es":"sudo apt install pciutils"}})
    except Exception as e:
        checks.append({"id":"pcie_link","label":{"ko":"PCIe 링크 (DeepX)","en":"PCIe Link (DeepX)","ja":"PCIeリンク (DeepX)","zhCN":"PCIe链接 (DeepX)","zhTW":"PCIe連結 (DeepX)","es":"Enlace PCIe (DeepX)"},"ok":False,"detail":str(e)})

    # 2. Device Files — /dev/dxrt*
    devs=sorted(Path("/dev").glob("dxrt*")) if Path("/dev").exists() else []
    dxdevs=sorted(Path("/dev").glob("deepx*")) if Path("/dev").exists() else []
    all_devs=devs+dxdevs
    checks.append({"id":"dev_files","label":{"ko":"디바이스 파일 (/dev/dxrt*)","en":"Device Files (/dev/dxrt*)","ja":"デバイスファイル (/dev/dxrt*)","zhCN":"设备文件 (/dev/dxrt*)","zhTW":"裝置檔案 (/dev/dxrt*)","es":"Archivos de dispositivo (/dev/dxrt*)"},"ok":bool(all_devs),
        "detail":", ".join(d.name for d in all_devs) if all_devs else "No /dev/dxrt* or /dev/deepx* found",
        "fix":{"ko":"NPU 드라이버 설치: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","en":"Install NPU driver: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","ja":"NPUドライバインストール: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zhCN":"安装NPU驱动: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zhTW":"安裝NPU驅動: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","es":"Instale el driver de la NPU: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver"}})

    # 3. Kernel Module — dxrt_driver
    try:
        lsmod=subprocess.check_output(["lsmod"],text=True,timeout=5).strip()
        has_dxrt="dxrt_driver" in lsmod
        checks.append({"id":"kmod_dxrt","label":{"ko":"커널 모듈 (dxrt_driver)","en":"Kernel Module (dxrt_driver)","ja":"カーネルモジュール (dxrt_driver)","zhCN":"内核模块 (dxrt_driver)","zhTW":"核心模組 (dxrt_driver)","es":"Módulo del kernel (dxrt_driver)"},"ok":has_dxrt,
            "detail":"Loaded" if has_dxrt else "Not loaded",
            "fix":{"ko":"sudo modprobe dxrt_driver 또는 드라이버 재설치","en":"sudo modprobe dxrt_driver  OR  reinstall driver","ja":"sudo modprobe dxrt_driver または ドライバ再インストール","zhCN":"sudo modprobe dxrt_driver 或 重新安装驱动","zhTW":"sudo modprobe dxrt_driver 或 重新安裝驅動","es":"sudo modprobe dxrt_driver  O  reinstale el driver"}})
    except Exception as e:
        checks.append({"id":"kmod_dxrt","label":{"ko":"커널 모듈 (dxrt_driver)","en":"Kernel Module (dxrt_driver)","ja":"カーネルモジュール (dxrt_driver)","zhCN":"内核模块 (dxrt_driver)","zhTW":"核心模組 (dxrt_driver)","es":"Módulo del kernel (dxrt_driver)"},"ok":False,"detail":str(e)})

    # 4. DMA Module — dx_dma
    try:
        has_dma="dx_dma" in lsmod
        checks.append({"id":"kmod_dma","label":{"ko":"커널 모듈 (dx_dma)","en":"Kernel Module (dx_dma)","ja":"カーネルモジュール (dx_dma)","zhCN":"内核模块 (dx_dma)","zhTW":"核心模組 (dx_dma)","es":"Módulo del kernel (dx_dma)"},"ok":has_dma,
            "detail":"Loaded" if has_dma else "Not loaded",
            "fix":{"ko":"sudo modprobe dx_dma 또는 드라이버 재설치","en":"sudo modprobe dx_dma  OR  reinstall driver","ja":"sudo modprobe dx_dma または ドライバ再インストール","zhCN":"sudo modprobe dx_dma 或 重新安装驱动","zhTW":"sudo modprobe dx_dma 或 重新安裝驅動","es":"sudo modprobe dx_dma  O  reinstale el driver"}})
    except Exception:
        checks.append({"id":"kmod_dma","label":{"ko":"커널 모듈 (dx_dma)","en":"Kernel Module (dx_dma)","ja":"カーネルモジュール (dx_dma)","zhCN":"内核模块 (dx_dma)","zhTW":"核心模組 (dx_dma)","es":"Módulo del kernel (dx_dma)"},"ok":False,"detail":"lsmod failed"})

    # 5. DKMS Status
    checks.append(_dkms_check())

    # 6. dxrt.service systemd
    try:
        r=subprocess.run(["systemctl","is-active","dxrt"],capture_output=True,text=True,timeout=5)
        active=r.stdout.strip()=="active"
        checks.append({"id":"dxrt_service","label":{"ko":"dxrt.service (systemd)","en":"dxrt.service (systemd)","ja":"dxrt.service (systemd)","zhCN":"dxrt.service (systemd)","zhTW":"dxrt.service (systemd)","es":"dxrt.service (systemd)"},"ok":active,
            "detail":"active" if active else r.stdout.strip(),
            "fix":{"ko":"sudo systemctl start dxrt && sudo systemctl enable dxrt","en":"sudo systemctl start dxrt && sudo systemctl enable dxrt","ja":"sudo systemctl start dxrt && sudo systemctl enable dxrt","zhCN":"sudo systemctl start dxrt && sudo systemctl enable dxrt","zhTW":"sudo systemctl start dxrt && sudo systemctl enable dxrt","es":"sudo systemctl start dxrt && sudo systemctl enable dxrt"}})
    except Exception:
        checks.append({"id":"dxrt_service","label":{"ko":"dxrt.service (systemd)","en":"dxrt.service (systemd)","ja":"dxrt.service (systemd)","zhCN":"dxrt.service (systemd)","zhTW":"dxrt.service (systemd)","es":"dxrt.service (systemd)"},"ok":False,
            "detail":"systemctl not available","fix":{"ko":"서비스 확인 건너뜀 (비-systemd 환경)","en":"Service check skipped (non-systemd env)","ja":"サービスチェックスキップ (非systemd環境)","zhCN":"服务检查跳过 (非systemd环境)","zhTW":"服務檢查跳過 (非systemd環境)","es":"Comprobación del servicio omitida (entorno sin systemd)"}})

    # 7. CLI Tools — dxrt-cli, run_model, parse_model
    cli_bins=["dxrt-cli","run_model","parse_model","dxtop"]
    found_bins=[];missing_bins=[]
    for b in cli_bins:
        if shutil.which(b):found_bins.append(b)
        else:missing_bins.append(b)
    checks.append({"id":"cli_tools","label":{"ko":"CLI 도구","en":"CLI Tools","ja":"CLIツール","zhCN":"CLI工具","zhTW":"CLI工具","es":"Herramientas CLI"},"ok":len(missing_bins)==0,
        "detail":f"Found: {', '.join(found_bins)}" + (f" | Missing: {', '.join(missing_bins)}" if missing_bins else ""),
        "fix":{"ko":"dx_rt 빌드: cd dx_rt && ./build.sh","en":"Build dx_rt: cd dx_rt && ./build.sh","ja":"dx_rtビルド: cd dx_rt && ./build.sh","zhCN":"构建dx_rt: cd dx_rt && ./build.sh","zhTW":"建置dx_rt: cd dx_rt && ./build.sh","es":"Compile dx_rt: cd dx_rt && ./build.sh"} if missing_bins else ""})

    # 8. Python venv — dx_engine importable (shares the probe with setup_status's dx-rt-build)
    venv_ok,venv_detail=_probe_dx_engine_venv()
    # dx_engine is NOT on PyPI — `pip install dx_engine` fails. The API is built + installed
    # into venv-dx-runtime by the runtime's dx_rt target (build.sh + the shipped wheel), which
    # the Setup page now exposes as the "DX-Runtime Build" step.
    _venv_fix="cd dx-runtime && ./install.sh --target=dx_rt --skip-uninstall --venv-reuse"
    checks.append({"id":"python_venv","label":{"ko":"Python venv (dx_engine)","en":"Python venv (dx_engine)","ja":"Python venv (dx_engine)","zhCN":"Python venv (dx_engine)","zhTW":"Python venv (dx_engine)","es":"Python venv (dx_engine)"},"ok":venv_ok,
        "detail":venv_detail,"fix":{
            "ko":f"Setup 페이지의 'DX-Runtime Build' 단계를 실행하세요 (또는 터미널: {_venv_fix})",
            "en":f"Run the 'DX-Runtime Build' step on the Setup page (or a terminal: {_venv_fix})",
            "ja":f"Setup ページの「DX-Runtime Build」ステップを実行してください（またはターミナル: {_venv_fix}）",
            "zhCN":f"运行 Setup 页面的「DX-Runtime Build」步骤（或在终端中: {_venv_fix}）",
            "zhTW":f"執行 Setup 頁面的「DX-Runtime Build」步驟（或在終端機中: {_venv_fix}）",
            "es":f"Ejecute el paso «DX-Runtime Build» en la página de configuración (o en una terminal: {_venv_fix})"}})

    # 9. Disk Space — at least 5GB free
    try:
        du=shutil.disk_usage("/")
        free_gb=du.free/1e9
        checks.append({"id":"disk_space","label":{"ko":"디스크 공간 (≥5GB 여유)","en":"Disk Space (≥5GB free)","ja":"ディスク容量 (≥5GB空き)","zhCN":"磁盘空间 (≥5GB空闲)","zhTW":"磁碟空間 (≥5GB可用)","es":"Espacio en disco (≥5 GB libres)"},"ok":free_gb>=5.0,
            "detail":f"{free_gb:.1f} GB free / {du.total/1e9:.0f} GB total",
            "fix":{"ko":"디스크 공간 확보 (빌드 산출물, 로그 등 정리)","en":"Free up disk space (clear build artifacts, logs, etc.)","ja":"ディスク容量を確保 (ビルド成果物、ログ等を削除)","zhCN":"释放磁盘空间 (清理构建产物、日志等)","zhTW":"釋放磁碟空間 (清理建置產物、日誌等)","es":"Libere espacio en disco (artefactos de compilación, registros, etc.)"}})
    except Exception as e:
        checks.append({"id":"disk_space","label":{"ko":"디스크 공간","en":"Disk Space","ja":"ディスク容量","zhCN":"磁盘空间","zhTW":"磁碟空間","es":"Espacio en disco"},"ok":False,"detail":str(e)})

    # 10. Memory — at least 2GB available
    try:
        with open("/proc/meminfo") as _f:
            mi=_f.read()
        import re as _re
        avail=int(_re.search(r'MemAvailable:\s+(\d+)',mi).group(1))//1024  # MB
        total=int(_re.search(r'MemTotal:\s+(\d+)',mi).group(1))//1024
        checks.append({"id":"memory","label":{"ko":"메모리 (≥2GB 가용)","en":"Memory (≥2GB available)","ja":"メモリ (≥2GB使用可能)","zhCN":"内存 (≥2GB可用)","zhTW":"記憶體 (≥2GB可用)","es":"Memoria (≥2 GB disponibles)"},"ok":avail>=2048,
            "detail":f"{avail} MB available / {total} MB total",
            "fix":{"ko":"사용하지 않는 애플리케이션 종료하여 메모리 확보","en":"Close unused applications to free memory","ja":"未使用のアプリケーションを終了してメモリを解放","zhCN":"关闭未使用的应用程序以释放内存","zhTW":"關閉未使用的應用程式以釋放記憶體","es":"Cierre las aplicaciones que no use para liberar memoria"}})
    except Exception as e:
        checks.append({"id":"memory","label":{"ko":"메모리","en":"Memory","ja":"メモリ","zhCN":"内存","zhTW":"記憶體","es":"Memoria"},"ok":False,"detail":str(e)})

    # 11. Model Files — check for zero-size .dxnn
    mdir=ASSETS_DIR/"models"
    if mdir.exists():
        all_dxnn=list(mdir.glob("*.dxnn"))
        zero_sz=[f.name for f in all_dxnn if f.stat().st_size==0]
        checks.append({"id":"model_integrity","label":{"ko":"모델 파일 무결성","en":"Model File Integrity","ja":"モデルファイル整合性","zhCN":"模型文件完整性","zhTW":"模型檔案完整性","es":"Integridad de los archivos de modelo"},"ok":len(zero_sz)==0 and len(all_dxnn)>0,
            "detail":f"{len(all_dxnn)} model(s)" + (f", {len(zero_sz)} corrupted (0 bytes): {', '.join(zero_sz[:3])}" if zero_sz else " — all OK"),
            "fix":{"ko":"손상된 모델 재다운로드: ModelZoo 또는 setup.sh 실행","en":"Re-download corrupted models via ModelZoo or setup.sh","ja":"破損モデルの再ダウンロード: ModelZooまたはsetup.sh実行","zhCN":"重新下载损坏的模型: 通过ModelZoo或setup.sh","zhTW":"重新下載損壞的模型: 透過ModelZoo或setup.sh","es":"Vuelva a descargar los modelos dañados con ModelZoo o setup.sh"}})
    else:
        checks.append({"id":"model_integrity","label":{"ko":"모델 파일 무결성","en":"Model File Integrity","ja":"モデルファイル整合性","zhCN":"模型文件完整性","zhTW":"模型檔案完整性","es":"Integridad de los archivos de modelo"},"ok":False,
            "detail":"assets/models/ not found","fix":{"ko":"setup.sh 실행하여 모델 다운로드","en":"Run setup.sh to download models","ja":"setup.shを実行してモデルをダウンロード","zhCN":"运行setup.sh下载模型","zhTW":"執行setup.sh下載模型","es":"Ejecute setup.sh para descargar los modelos"}})

    xvfb_ok=bool(shutil.which("Xvfb"))
    checks.append({"id":"live_display","optional":True,
        "label":{"ko":"Live 화면 캡처 (Xvfb, 선택)","en":"Live display capture (Xvfb, optional)",
                 "ja":"ライブ画面キャプチャ (Xvfb、任意)","zhCN":"实时画面捕获 (Xvfb，可选)",
                 "zhTW":"即時畫面擷取 (Xvfb，選用)","es":"Captura de pantalla en vivo (Xvfb, opcional)"},
        "ok":xvfb_ok,"detail":"Xvfb found" if xvfb_ok else "Xvfb not installed",
        "fix":{lang:LIVE_DISPLAY_HINT for lang in ("ko","en","ja","zhCN","zhTW","es")}})

    # OpenCV is probed in a compatible child; importing it here can abort the server on a NumPy ABI mismatch.
    from shared.media import run_media, MediaError
    try:
        versions=run_media("probe")
        checks.append({"id":"opencv","label":{"ko":"OpenCV","en":"OpenCV","ja":"OpenCV","zhCN":"OpenCV","zhTW":"OpenCV","es":"OpenCV"},"ok":True,"detail":f"v{versions['opencv']}"})
    except MediaError as exc:
        checks.append({"id":"opencv","label":{"ko":"OpenCV","en":"OpenCV","ja":"OpenCV","zhCN":"OpenCV","zhTW":"OpenCV","es":"OpenCV"},"ok":False,
            "detail":str(exc),"fix":{"ko":"Setup에서 Demo Quick Start(또는 Set up the rest)를 다시 실행","en":"Run Demo Quick Start (or Set up the rest) in Setup again",
            "ja":"Setup で Demo Quick Start（または Set up the rest）をもう一度実行","zhCN":"在 Setup 中再次运行 Demo Quick Start（或 Set up the rest）",
            "zhTW":"在 Setup 中再次執行 Demo Quick Start（或 Set up the rest）","es":"Vuelva a ejecutar Demo Quick Start (o Set up the rest) en Setup"}})

    s=npu_sanity()
    checks.append({"id":"npu_sanity","label":{lang:"NPU sanity check" for lang in ("ko","en","ja","zh-CN","zh-TW","es")},
        "ok":s["state"]=="passed","pending":s["state"]=="needs_password",
        "detail":{"passed":"Sanity check PASSED","needs_password":"Needs administrator password"}.get(
            s["state"], s.get("detail") or "Sanity check FAILED"),
        **({"fix":s["fix"]} if s["state"]=="failed" else {})})

    # A pending row (no sudo yet) is neither a pass nor a failure.
    counted=[c for c in checks if not c.get("pending")]
    passed=sum(1 for c in counted if c["ok"])
    total=len(counted)
    return {"checks":checks,"passed":passed,"total":total,"all_ok":passed==total}


SANITY_SCRIPT = DX_RT_ROOT.parent / "scripts" / "sanity_check.sh"
_ANSI = re.compile(r"\x1b\[[0-9;]*m")
_COLD_BOOT = {"ko":"NPU 초기화 실패 — 전원을 완전히 끄고(cold boot) 10~30초 뒤 다시 켠 다음 다시 확인하세요",
  "en":"NPU initialization failed — power the system fully off (cold boot), wait 10–30 s, power on, check again",
  "ja":"NPU の初期化に失敗 — 電源を完全に切り（コールドブート）、10〜30 秒後に入れ直してから再確認してください",
  "zh-CN":"NPU 初始化失败 — 完全断电（冷启动），等待 10–30 秒后开机再检查",
  "zh-TW":"NPU 初始化失敗 — 完全斷電（冷開機），等待 10–30 秒後開機再檢查",
  "es":"Falló la inicialización de la NPU: apague el equipo por completo (arranque en frío), espere 10–30 s, enciéndalo y vuelva a comprobar"}
_REINSTALL = {"ko":"Setup 4단계 NPU Linux Driver를 다시 실행하거나 실행 로그를 확인하세요",
  "en":"Run Setup step 4 (NPU Linux Driver) again, or read the execution log",
  "ja":"Setup のステップ 4（NPU Linux Driver）を再実行するか、実行ログを確認してください",
  "zh-CN":"重新运行 Setup 第 4 步（NPU Linux Driver），或查看执行日志",
  "zh-TW":"重新執行 Setup 第 4 步（NPU Linux Driver），或查看執行日誌",
  "es":"Vuelva a ejecutar el paso 4 de Setup (NPU Linux Driver) o revise el registro de ejecución"}


def npu_sanity(password=None):
    """dx-runtime/scripts/sanity_check.sh --dx_rt (it runs `sudo ./SanityCheck.sh`), judged by its TEXT, never
    the exit code. Without a cached sudo session and no password → pending, so Deep Diagnostics stays
    password-free; POST /api/setup/sanity runs it with the password."""
    env=os.environ.copy(); cleanup=lambda: None
    if password:
        cleanup=_configure_sudo_env(env,password)
        err=_preauthorize_sudo(password,env)
        if err:
            cleanup(); return {"state":"auth_failed","error":err}
    else:
        try:
            if subprocess.run(["sudo","-n","true"],capture_output=True,text=True,timeout=10).returncode!=0:
                return {"state":"needs_password"}
        except (OSError,subprocess.SubprocessError):
            return {"state":"needs_password"}
    try:
        r=subprocess.run(["bash",str(SANITY_SCRIPT),"--dx_rt"],env=env,stdin=subprocess.DEVNULL,
                         capture_output=True,text=True,timeout=180)
        out=_ANSI.sub("",(r.stdout or "")+(r.stderr or ""))
    except (OSError,subprocess.SubprocessError) as exc:
        out=f"[ERROR] {exc}"
    finally:
        cleanup()
    ok="Sanity check PASSED" in out and "[ERROR]" not in out
    first=next((l.strip() for l in out.splitlines() if "[ERROR]" in l or "FAILED" in l),"")
    fix=_COLD_BOOT if re.search(r"initiali[sz]",out,re.I) else _REINSTALL
    return {"state":"passed" if ok else "failed","detail":first,"fix":None if ok else fix,"log":out[-6000:]}

# inference-venv last: the only step that yields a numpy+cv2+dx_engine interpreter (it seeds from the dx_engine
# DX-Runtime Build installs). Without it a "done" Quick Start crashed every Python-path Use Default.
# DX-APP Dependencies runs the runtime's `apt-get upgrade` (whole system), then the build and the samples follow:
# a fresh Raspberry Pi setup took a 29 GB card to 97 %. The Setup page confirms below this (setup.js _setupDiskOk).
MIN_FREE_GB = 5.0

_QUICK_ORDER = ["dx-app-deps","dx-rt-deps","dx-rt-build","dx-driver","dx-app-build","dx-app-setup","inference-venv"]
# Steps Quick Start runs in their demo form (demo_only): build.sh --minimal, asset_setup --demo.
_DEMO_FORM_STEPS = ("dx-app-build", "dx-app-setup")

def quick_start_plan():
    """Ordered setup step ids still needed for a demo-only setup (skip satisfied).

    The build and asset steps are judged by their demo form (``demo_ok``) — what Quick Start
    runs for them — not by the full step's promise."""
    st = setup_status()
    def ready(sid):
        s = st.get(sid) or {}
        return s.get("demo_ok", s.get("ok")) if sid in _DEMO_FORM_STEPS else s.get("ok")
    return [sid for sid in _QUICK_ORDER if not ready(sid)]


_SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
RESET_CONFIRM = SETUP_STEPS["runtime-reset"]["confirm"]


def _model_build_targets(params):
    """`<example>_sync/_async` that have a C++ source — the whitelist for build.sh --target (no free argv)."""
    name, cat = str(params.get("model_name") or ""), str(params.get("category") or "")
    mf = str(params.get("model_file") or "")
    if not (_SAFE_NAME.match(name) and _SAFE_NAME.match(cat)) or ".." in name or ".." in mf:
        return []
    from shared import dx_app_layout as layout
    ex = layout.example_name(DX_APP_ROOT, cat, name, mf)
    if not _SAFE_NAME.match(ex or ""):
        return []
    return [f"{ex}_{v}" for v in ("sync", "async") if layout.cpp_source(DX_APP_ROOT, cat, ex, v).is_file()]


def _display_argv(step):
    """The command a step runs, as shown on its Setup card (paths relative to the suite)."""
    argv, _ = step_argv(step, {})
    suite = str(DX_RT_ROOT.parent.parent)
    shown = []
    for a in argv:
        if a == "bash":
            continue
        if a == sys.executable:
            shown.append("python")
        elif str(a).startswith(suite + os.sep):
            shown.append(str(a)[len(suite) + 1:])   # e.g. dx-runtime/dx_app/build.sh
        else:
            shown.append(str(a))
    return shown


def step_argv(step, params=None):
    """(argv, cwd) a setup step runs. ``demo_only`` (Quick Start) selects the demo form of the
    build (build.sh --minimal) and asset (asset_setup --demo) steps."""
    params = params or {}
    cfg = SETUP_STEPS[step]
    args = list(cfg.get("args", []))
    demo = bool(params.get("demo_only")) and step in _DEMO_FORM_STEPS
    if demo and step == "dx-app-build":
        args = ["--minimal" if a == "--all" else a for a in args]
    if demo and step == "dx-app-setup":
        args = args + ["--demo"]
    if step == "model-build":
        args = ["--target", *_model_build_targets(params)] + args
    argv = cfg["cmd"]() + args if cfg.get("cmd") else ["bash", str(cfg["script"]())] + args
    return argv, cfg["cwd"]()


class _Starting:
    """Placeholder in config._comp_proc between the busy check and Popen (keeps the check atomic)."""
    def poll(self):
        return None


def setup_run(step,params=None):
    """Start a setup step script in background (streams via config._comp_log)."""
    if params is None:params={}
    cfg=SETUP_STEPS.get(step)
    if not cfg:return{"ok":False,"error":f"Unknown step: {step}"}
    # A step is driven by either a shell "script" (bash <path> [args]) or a direct "cmd"
    # (argv list, for studio-native steps that must not add scripts to the dx-runtime tree).
    if cfg.get("confirm") and params.get("confirm") != cfg["confirm"]:
        return{"ok":False,"code":"confirm_required","error":f"Type {cfg['confirm']} to confirm"}
    if step=="model-build" and not _model_build_targets(params):
        return{"ok":False,"code":"no_cpp_source","error":"This model has no C++ example to build"}
    script=cfg["script"]() if cfg.get("script") else None
    if script is not None and not script.exists():return{"ok":False,"error":f"{script.name} not found"}
    # One Setup job at a time, server-side: Model Zoo starts model-build from another page, so the page's
    # own SETUP.running guard is not enough. (config._comp_proc was never assigned before, so this never fired.)
    with config._comp_lock:
        if config._comp_proc and config._comp_proc.poll() is None:
            return{"ok":False,"error":"Another process is already running"}
        config._comp_proc=_Starting()
    try:
        return _setup_start(step,cfg,params)
    except BaseException:
        config._comp_proc=None
        raise


def _setup_start(step,cfg,params):
    env=os.environ.copy()
    # Real-time log/progress: force Python children (e.g. download_models.py progress bar)
    # to flush stdout immediately instead of block-buffering when piped — otherwise progress
    # arrives in big chunks ("suddenly 24%") instead of streaming.
    env["PYTHONUNBUFFERED"]="1"
    # PEP 668 (Ubuntu 24.04+): system pip refuses `pip install` outside a venv. The dx_app
    # install.sh/build.sh pip steps run as our children, so allow it via the env var (equivalent
    # to --break-system-packages) — installs land in the same system python the module runs with.
    env.setdefault("PIP_BREAK_SYSTEM_PACKAGES", "1")
    if cfg.get("needs_credentials"):
        u=params.get("username","");p=params.get("password","")
        if not u:config._comp_proc=None;return{"ok":False,"error":"Please enter your username (email)"}
        if not p:config._comp_proc=None;return{"ok":False,"error":"Please enter your password"}
        env["DX_USERNAME"]=u;env["DX_PASSWORD"]=p
    sudo_cleanup = lambda: None
    if cfg.get("needs_sudo"):
        sudo_cleanup = _configure_sudo_env(env, params.get("password",""))
        sudo_error = _preauthorize_sudo(params.get("password",""), env)
        if sudo_error:
            sudo_cleanup()
            config._comp_proc=None
            # sudo_auth marker lets the client re-prompt for the password instead of failing.
            return{"ok":False,"error":sudo_error,"sudo_auth":True}
    # Demo Quick Start passes {"demo_only": true} for the build and asset steps (step_argv).
    run_argv,cwd=step_argv(step,params)
    with config._comp_log_lock:config._comp_log=""
    config._comp_done=False;config._comp_exit_code=-1;config._comp_step=step
    if step=="runtime-reset":
        # The NPU driver is about to be removed: stop any run that holds the device.
        try:
            from dx_app.core.inference import stop_inference, shutdown_live_processes
            stop_inference(); shutdown_live_processes()
        except Exception:
            logging.exception("could not stop running inference before runtime-reset")
    def _run():
        import select as _select,os as _os
        buf=[]
        partial=""
        sudo_stop = threading.Event()
        try:
            if cfg.get("needs_sudo"):
                threading.Thread(target=_keep_sudo_alive,args=(sudo_stop,),daemon=True).start()
            proc=subprocess.Popen(run_argv,
             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
             stdin=subprocess.PIPE,cwd=str(cwd),env=env,bufsize=0)
            config._comp_stdin_proc=proc
            config._comp_proc=proc
            fd=proc.stdout.fileno()
            while True:
                rlist,_,_=_select.select([fd],[],[],0.1)
                if rlist:
                    chunk=_os.read(fd,4096)
                    if not chunk:break
                    text=chunk.decode("utf-8","replace")
                    partial+=text
                    # split on newlines but keep trailing partial line
                    lines=partial.split("\n")
                    partial=lines.pop()  # last element: incomplete line (may be prompt)
                    for l in lines:
                        buf.append(l+"\n")
                        print(f"[SETUP:{step}] {l}")
                    # always expose current state including partial (prompt without \n)
                    with config._comp_log_lock:
                        config._comp_log="".join(buf)+(partial if partial else "")
                else:
                    # no data: flush partial so prompt shows up in log
                    if partial:
                        with config._comp_log_lock:
                            config._comp_log="".join(buf)+partial
                    if proc.poll() is not None:
                        break
            if partial:
                buf.append(partial)
                print(f"[SETUP:{step}] {partial}")
            proc.wait();config._comp_exit_code=proc.returncode
        except Exception as e:
            buf.append(f"\n[ERROR] {e}\n")
            config._comp_exit_code=1
            if isinstance(config._comp_proc,_Starting):config._comp_proc=None
        finally:
            sudo_stop.set()
            sudo_cleanup()
            config._comp_stdin_proc=None
            with config._comp_log_lock:config._comp_log="".join(buf)
            config._comp_done=True
            # A step may have installed or repaired OpenCV / the runtime: probe media again.
            try:
                from shared.media import media_python
                media_python.cache_clear()
            except (ImportError, AttributeError):
                logging.exception("Media cache reset failed after Setup step %s", step)
            # …and the inference interpreter: Python Inference Deps / runtime steps change which one works.
            try:
                config.refresh_runtime_python()
            except Exception:
                logging.exception("runtime python refresh failed after Setup step %s", step)
            # DX-APP Build (re)installs dx_postprocess into the system python; bring it into the Studio
            # inference venv when that venv already exists (Python Inference Deps is then skipped as done).
            if step == "dx-app-build" and config._comp_exit_code == 0:
                try:
                    from shared.runtime import STUDIO_INFER_VENV, sync_dx_postprocess
                    _venv_py = STUDIO_INFER_VENV / "bin" / "python3"
                    if _venv_py.is_file():
                        sync_dx_postprocess(str(_venv_py))
                except Exception:
                    logging.exception("dx_postprocess sync failed after Setup step %s", step)
            print(f"[SETUP:{step}] Done. exit_code={config._comp_exit_code}")
    threading.Thread(target=_run,daemon=True).start()
    return{"ok":True,"started":True}

def model_build_log():
    """Log of the model-build job only — Model Zoo must not read other Setup jobs."""
    if config._comp_step != "model-build":
        return {"log":"","done":True,"exit_code":None,"busy":bool(config._comp_proc and config._comp_proc.poll() is None),
                "step":config._comp_step}
    out = setup_log()
    out["busy"] = False
    return out


def model_build_stop():
    """Stop only a running model-build (Model Zoo must not stop a driver install, …)."""
    if config._comp_step != "model-build" or config._comp_done:
        return {"ok":False,"error":"No C++ runner build is running"}
    return setup_stop()


def setup_stop():
    """Stop the running Setup process."""
    with config._comp_lock:
        proc = config._comp_stdin_proc
        if proc and proc.poll() is None:
            proc.terminate()
            config._comp_exit_code = 130
            config._comp_done = True
            return {"ok": True}
    return {"ok": False, "error": "No running process"}


def setup_log():
    """Current setup-step log + completion state (polled by the Setup page)."""
    with config._comp_log_lock:
        log = config._comp_log
    return {"log": log, "done": config._comp_done, "exit_code": config._comp_exit_code}


def setup_input(text):
    """Send a line to the running setup-step process's stdin (interactive prompts)."""
    proc = config._comp_stdin_proc
    if not proc or proc.poll() is not None:
        return {"ok": False, "error": "no active process"}
    try:
        proc.stdin.write(((text or "") + "\n").encode("utf-8"))
        proc.stdin.flush()
        return {"ok": True}
    except Exception as e:  # noqa: BLE001 — surface any write failure to the UI
        return {"ok": False, "error": str(e)}
