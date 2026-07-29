"""DX-APP Setup & Installation steps."""

import os, sys, json, time, subprocess, threading, select, shutil, re, platform, tempfile, shlex
from pathlib import Path
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
    """release.ver 파일에서 버전 문자열 읽기."""
    try:
        p = Path(path) if not isinstance(path, Path) else path
        if not p.is_absolute():
            p = DX_APP_ROOT / path
        return p.read_text().strip().split('\n')[0]
    except Exception:
        return '--'

def _get_npu_driver_version():
    """dxrt-cli 또는 /dev/deepx* 기반 드라이버 버전."""
    try:
        r = subprocess.run(['dxrt-cli', '--version'], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            return r.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return '--'


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
        "args":["--target=dx_rt_npu_linux_driver"],"cwd":lambda:DX_RT_ROOT.parent,
        "desc":"Install DEEPX NPU kernel driver (requires sudo)",
        "needs_sudo":True,
    },
    "dx-app-build":{
        "label":"DX-APP Build","script":lambda:DX_APP_ROOT/"build.sh",
        "args":["--type","Release","--arch","x86_64"],"cwd":lambda:DX_APP_ROOT,
        "desc":"Compile C++ demo binaries (cmake build)",
        # build.sh installs the postprocess .so via `sudo cp ... /usr/local/lib` + `sudo ldconfig`.
        "needs_sudo":True,
    },
    "dx-app-setup":{
        "label":"Sample Assets Setup","script":lambda:DX_APP_ROOT/"setup.sh",
        "args":[],"cwd":lambda:DX_APP_ROOT,
        "desc":"Download sample models and videos for demos",
    },
    "inference-venv":{
        # Option 1: guarantee ONE interpreter with numpy+cv2+dx_engine for the python-variant
        # demos, without touching dx-runtime or the base interpreter. A no-op when an existing
        # interpreter already has all three (common on dx-all-suite boards); otherwise it builds
        # a studio-owned venv (--system-site-packages seed from a dx_engine-capable python) and
        # pip-installs opencv-python-headless + numpy into it only. dx_engine must already be
        # installed (it is not on PyPI) — run dx-rt-build first.
        "label":"Python Inference Deps",
        "cmd":lambda:[sys.executable,"-c",
            "from shared.runtime import ensure_inference_venv; "
            "print('OK' if ensure_inference_venv(log=print) else 'INCOMPLETE')"],
        "cwd":lambda:DX_APP_ROOT.parent,   # dx-ai-studio root so `import shared` resolves
        "desc":"Ensure numpy+cv2+dx_engine coexist for Python demos (studio venv; no dx-runtime changes)",
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


def setup_status():
    """Return dict of {step_id: {ok, detail}} for all setup steps."""
    r={}
    cmake_ok=bool(shutil.which("cmake"))
    gcc_ok=bool(shutil.which("gcc") or shutil.which("gcc-12") or shutil.which("g++"))
    ninja_ok=bool(shutil.which("ninja") or shutil.which("ninja-build"))
    r["dx-app-deps"]={"ok":cmake_ok and gcc_ok,
        "detail":"cmake "+("✅" if cmake_ok else "❌")+"  gcc "+("✅" if gcc_ok else "❌")+"  ninja "+("✅" if ninja_ok else "❌")}
    bdir=DX_APP_ROOT/"build_x86_64"
    bins=list(bdir.rglob("*_sync"))[:1] if bdir.exists() else []
    r["dx-app-build"]={"ok":bool(bins),
        "detail":f"build_x86_64/ {'✅ found' if bdir.exists() else '❌ not found'}"}
    mdir=ASSETS_DIR/"models";vdir=ASSETS_DIR/"videos"
    nm=len(list(mdir.glob("*.dxnn"))) if mdir.exists() else 0
    nv=len([f for f in vdir.iterdir() if f.is_file()]) if vdir.exists() else 0
    r["dx-app-setup"]={"ok":nm>0 and nv>0,
        "detail":f"{nm} model(s), {nv} video(s)"}
    rv=DX_RT_ROOT/"release.ver"
    rt_ver=rv.read_text().strip() if rv.exists() else None
    # release.ver may already start with "v" (e.g. "v3.4.1") → don't double it into "vv3.4.1".
    r["dx-rt-deps"]={"ok":rv.exists(),
        "detail":f"v{rt_ver.lstrip('v')}" if rt_ver else "release.ver not found"}
    # dx-rt-build — ok only when the dx_engine Python API is importable in venv-dx-runtime
    venv_ok,venv_detail=_probe_dx_engine_venv()
    r["dx-rt-build"]={"ok":venv_ok,"detail":venv_detail}
    # dx-driver — the loaded driver creates /dev/dxrt* (newer) or /dev/deepx* (legacy); accept both
    devs=(sorted(Path("/dev").glob("dxrt*"))+sorted(Path("/dev").glob("deepx*"))) if Path("/dev").exists() else []
    r["dx-driver"]={"ok":bool(devs),
        "detail":", ".join(d.name for d in devs) if devs else "/dev/dxrt* or /dev/deepx* not found"}
    dxcom=_find_dxcom();ver=_dxcom_version()
    r["dx-compiler"]={"ok":dxcom is not None,
        "detail":f"v{ver}" if ver else ("Install required" if not (DX_COMPILER_ROOT/"install.sh").exists() else "install.sh ✅"),
        "needs_credentials":True}
    # inference-venv (Option 1) — ok when the resolved inference interpreter has numpy+cv2+dx_engine.
    try:
        from shared.runtime import runtime_python, _has_numpy_cv2_dxengine
        _ip=runtime_python(); _iok=_has_numpy_cv2_dxengine(_ip)
        r["inference-venv"]={"ok":_iok,
            "detail":("numpy+cv2+dx_engine ✅ ("+Path(_ip).name+")") if _iok else "no interpreter has numpy+cv2+dx_engine yet"}
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
    return r


def deep_diagnostics():
    """Run 12 deep diagnostic checks (Python-native, no shell dependency)."""
    checks=[]

    # 1. PCIe Link — DeepX Vendor ID 1ff4
    try:
        out=subprocess.check_output(["lspci","-d","1ff4:"],text=True,timeout=5,stderr=subprocess.DEVNULL).strip()
        found=[l.strip() for l in out.splitlines() if l.strip()]
        checks.append({"id":"pcie_link","label":{"ko":"PCIe 링크 (DeepX)","en":"PCIe Link (DeepX)","ja":"PCIeリンク (DeepX)","zhCN":"PCIe链接 (DeepX)","zhTW":"PCIe連結 (DeepX)"},"ok":bool(found),
            "detail":", ".join(found) if found else "No DeepX device found on PCIe bus",
            "fix":{"ko":"NPU 보드가 올바르게 장착되었는지 확인. 실행: lspci -d 1ff4:","en":"Check NPU board is properly seated. Run: lspci -d 1ff4:","ja":"NPUボードが正しく装着されているか確認。実行: lspci -d 1ff4:","zhCN":"检查NPU板是否正确安装。执行: lspci -d 1ff4:","zhTW":"檢查NPU板是否正確安裝。執行: lspci -d 1ff4:"}})
    except FileNotFoundError:
        checks.append({"id":"pcie_link","label":{"ko":"PCIe 링크 (DeepX)","en":"PCIe Link (DeepX)","ja":"PCIeリンク (DeepX)","zhCN":"PCIe链接 (DeepX)","zhTW":"PCIe連結 (DeepX)"},"ok":False,
            "detail":"lspci not installed","fix":{"ko":"sudo apt install pciutils","en":"sudo apt install pciutils","ja":"sudo apt install pciutils","zhCN":"sudo apt install pciutils","zhTW":"sudo apt install pciutils"}})
    except Exception as e:
        checks.append({"id":"pcie_link","label":{"ko":"PCIe 링크 (DeepX)","en":"PCIe Link (DeepX)","ja":"PCIeリンク (DeepX)","zhCN":"PCIe链接 (DeepX)","zhTW":"PCIe連結 (DeepX)"},"ok":False,"detail":str(e)})

    # 2. Device Files — /dev/dxrt*
    devs=sorted(Path("/dev").glob("dxrt*")) if Path("/dev").exists() else []
    dxdevs=sorted(Path("/dev").glob("deepx*")) if Path("/dev").exists() else []
    all_devs=devs+dxdevs
    checks.append({"id":"dev_files","label":{"ko":"디바이스 파일 (/dev/dxrt*)","en":"Device Files (/dev/dxrt*)","ja":"デバイスファイル (/dev/dxrt*)","zhCN":"设备文件 (/dev/dxrt*)","zhTW":"裝置檔案 (/dev/dxrt*)"},"ok":bool(all_devs),
        "detail":", ".join(d.name for d in all_devs) if all_devs else "No /dev/dxrt* or /dev/deepx* found",
        "fix":{"ko":"NPU 드라이버 설치: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","en":"Install NPU driver: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","ja":"NPUドライバインストール: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zhCN":"安装NPU驱动: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zhTW":"安裝NPU驅動: cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver"}})

    # 3. Kernel Module — dxrt_driver
    try:
        lsmod=subprocess.check_output(["lsmod"],text=True,timeout=5).strip()
        has_dxrt="dxrt_driver" in lsmod
        checks.append({"id":"kmod_dxrt","label":{"ko":"커널 모듈 (dxrt_driver)","en":"Kernel Module (dxrt_driver)","ja":"カーネルモジュール (dxrt_driver)","zhCN":"内核模块 (dxrt_driver)","zhTW":"核心模組 (dxrt_driver)"},"ok":has_dxrt,
            "detail":"Loaded ✅" if has_dxrt else "Not loaded",
            "fix":{"ko":"sudo modprobe dxrt_driver 또는 드라이버 재설치","en":"sudo modprobe dxrt_driver  OR  reinstall driver","ja":"sudo modprobe dxrt_driver または ドライバ再インストール","zhCN":"sudo modprobe dxrt_driver 或 重新安装驱动","zhTW":"sudo modprobe dxrt_driver 或 重新安裝驅動"}})
    except Exception as e:
        checks.append({"id":"kmod_dxrt","label":{"ko":"커널 모듈 (dxrt_driver)","en":"Kernel Module (dxrt_driver)","ja":"カーネルモジュール (dxrt_driver)","zhCN":"内核模块 (dxrt_driver)","zhTW":"核心模組 (dxrt_driver)"},"ok":False,"detail":str(e)})

    # 4. DMA Module — dx_dma
    try:
        has_dma="dx_dma" in lsmod
        checks.append({"id":"kmod_dma","label":{"ko":"커널 모듈 (dx_dma)","en":"Kernel Module (dx_dma)","ja":"カーネルモジュール (dx_dma)","zhCN":"内核模块 (dx_dma)","zhTW":"核心模組 (dx_dma)"},"ok":has_dma,
            "detail":"Loaded ✅" if has_dma else "Not loaded",
            "fix":{"ko":"sudo modprobe dx_dma 또는 드라이버 재설치","en":"sudo modprobe dx_dma  OR  reinstall driver","ja":"sudo modprobe dx_dma または ドライバ再インストール","zhCN":"sudo modprobe dx_dma 或 重新安装驱动","zhTW":"sudo modprobe dx_dma 或 重新安裝驅動"}})
    except Exception:
        checks.append({"id":"kmod_dma","label":{"ko":"커널 모듈 (dx_dma)","en":"Kernel Module (dx_dma)","ja":"カーネルモジュール (dx_dma)","zhCN":"内核模块 (dx_dma)","zhTW":"核心模組 (dx_dma)"},"ok":False,"detail":"lsmod failed"})

    # 5. DKMS Status
    try:
        dkms_out=subprocess.check_output(["dkms","status"],text=True,timeout=10,stderr=subprocess.DEVNULL).strip()
        dxrt_dkms=[l for l in dkms_out.splitlines() if "dxrt" in l.lower() or "deepx" in l.lower()]
        installed_ok=any("installed" in l.lower() for l in dxrt_dkms)
        checks.append({"id":"dkms","label":{"ko":"DKMS 드라이버 상태","en":"DKMS Driver Status","ja":"DKMSドライバ状態","zhCN":"DKMS驱动状态","zhTW":"DKMS驅動狀態"},"ok":installed_ok,
            "detail":"; ".join(dxrt_dkms)[:200] if dxrt_dkms else "No DKMS entry for dxrt/deepx",
            "fix":{"ko":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","en":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","ja":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zhCN":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver","zhTW":"cd dx-runtime && sudo ./install.sh --target=dx_rt_npu_linux_driver"}})
    except FileNotFoundError:
        checks.append({"id":"dkms","label":{"ko":"DKMS 드라이버 상태","en":"DKMS Driver Status","ja":"DKMSドライバ状態","zhCN":"DKMS驱动状态","zhTW":"DKMS驅動狀態"},"ok":False,
            "detail":"dkms not installed","fix":{"ko":"sudo apt install dkms","en":"sudo apt install dkms","ja":"sudo apt install dkms","zhCN":"sudo apt install dkms","zhTW":"sudo apt install dkms"}})
    except Exception as e:
        checks.append({"id":"dkms","label":{"ko":"DKMS 드라이버 상태","en":"DKMS Driver Status","ja":"DKMSドライバ状態","zhCN":"DKMS驱动状态","zhTW":"DKMS驅動狀態"},"ok":False,"detail":str(e)})

    # 6. dxrt.service systemd
    try:
        r=subprocess.run(["systemctl","is-active","dxrt"],capture_output=True,text=True,timeout=5)
        active=r.stdout.strip()=="active"
        checks.append({"id":"dxrt_service","label":{"ko":"dxrt.service (systemd)","en":"dxrt.service (systemd)","ja":"dxrt.service (systemd)","zhCN":"dxrt.service (systemd)","zhTW":"dxrt.service (systemd)"},"ok":active,
            "detail":"active ✅" if active else r.stdout.strip(),
            "fix":{"ko":"sudo systemctl start dxrt && sudo systemctl enable dxrt","en":"sudo systemctl start dxrt && sudo systemctl enable dxrt","ja":"sudo systemctl start dxrt && sudo systemctl enable dxrt","zhCN":"sudo systemctl start dxrt && sudo systemctl enable dxrt","zhTW":"sudo systemctl start dxrt && sudo systemctl enable dxrt"}})
    except Exception:
        checks.append({"id":"dxrt_service","label":{"ko":"dxrt.service (systemd)","en":"dxrt.service (systemd)","ja":"dxrt.service (systemd)","zhCN":"dxrt.service (systemd)","zhTW":"dxrt.service (systemd)"},"ok":False,
            "detail":"systemctl not available","fix":{"ko":"서비스 확인 건너뜀 (비-systemd 환경)","en":"Service check skipped (non-systemd env)","ja":"サービスチェックスキップ (非systemd環境)","zhCN":"服务检查跳过 (非systemd环境)","zhTW":"服務檢查跳過 (非systemd環境)"}})

    # 7. CLI Tools — dxrt-cli, run_model, parse_model
    cli_bins=["dxrt-cli","run_model","parse_model","dxtop"]
    found_bins=[];missing_bins=[]
    for b in cli_bins:
        if shutil.which(b):found_bins.append(b)
        else:missing_bins.append(b)
    checks.append({"id":"cli_tools","label":{"ko":"CLI 도구","en":"CLI Tools","ja":"CLIツール","zhCN":"CLI工具","zhTW":"CLI工具"},"ok":len(missing_bins)==0,
        "detail":f"Found: {', '.join(found_bins)}" + (f" | Missing: {', '.join(missing_bins)}" if missing_bins else ""),
        "fix":{"ko":"dx_rt 빌드: cd dx_rt && ./build.sh","en":"Build dx_rt: cd dx_rt && ./build.sh","ja":"dx_rtビルド: cd dx_rt && ./build.sh","zhCN":"构建dx_rt: cd dx_rt && ./build.sh","zhTW":"建置dx_rt: cd dx_rt && ./build.sh"} if missing_bins else ""})

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
        checks.append({"id":"disk_space","label":{"ko":"디스크 공간 (≥5GB 여유)","en":"Disk Space (≥5GB free)","ja":"ディスク容量 (≥5GB空き)","zhCN":"磁盘空间 (≥5GB空闲)","zhTW":"磁碟空間 (≥5GB可用)"},"ok":free_gb>=5.0,
            "detail":f"{free_gb:.1f} GB free / {du.total/1e9:.0f} GB total",
            "fix":{"ko":"디스크 공간 확보 (빌드 산출물, 로그 등 정리)","en":"Free up disk space (clear build artifacts, logs, etc.)","ja":"ディスク容量を確保 (ビルド成果物、ログ等を削除)","zhCN":"释放磁盘空间 (清理构建产物、日志等)","zhTW":"釋放磁碟空間 (清理建置產物、日誌等)"}})
    except Exception as e:
        checks.append({"id":"disk_space","label":{"ko":"디스크 공간","en":"Disk Space","ja":"ディスク容量","zhCN":"磁盘空间","zhTW":"磁碟空間"},"ok":False,"detail":str(e)})

    # 10. Memory — at least 2GB available
    try:
        with open("/proc/meminfo") as _f:
            mi=_f.read()
        import re as _re
        avail=int(_re.search(r'MemAvailable:\s+(\d+)',mi).group(1))//1024  # MB
        total=int(_re.search(r'MemTotal:\s+(\d+)',mi).group(1))//1024
        checks.append({"id":"memory","label":{"ko":"메모리 (≥2GB 가용)","en":"Memory (≥2GB available)","ja":"メモリ (≥2GB使用可能)","zhCN":"内存 (≥2GB可用)","zhTW":"記憶體 (≥2GB可用)"},"ok":avail>=2048,
            "detail":f"{avail} MB available / {total} MB total",
            "fix":{"ko":"사용하지 않는 애플리케이션 종료하여 메모리 확보","en":"Close unused applications to free memory","ja":"未使用のアプリケーションを終了してメモリを解放","zhCN":"关闭未使用的应用程序以释放内存","zhTW":"關閉未使用的應用程式以釋放記憶體"}})
    except Exception as e:
        checks.append({"id":"memory","label":{"ko":"메모리","en":"Memory","ja":"メモリ","zhCN":"内存","zhTW":"記憶體"},"ok":False,"detail":str(e)})

    # 11. Model Files — check for zero-size .dxnn
    mdir=ASSETS_DIR/"models"
    if mdir.exists():
        all_dxnn=list(mdir.glob("*.dxnn"))
        zero_sz=[f.name for f in all_dxnn if f.stat().st_size==0]
        checks.append({"id":"model_integrity","label":{"ko":"모델 파일 무결성","en":"Model File Integrity","ja":"モデルファイル整合性","zhCN":"模型文件完整性","zhTW":"模型檔案完整性"},"ok":len(zero_sz)==0 and len(all_dxnn)>0,
            "detail":f"{len(all_dxnn)} model(s)" + (f", {len(zero_sz)} corrupted (0 bytes): {', '.join(zero_sz[:3])}" if zero_sz else " — all OK"),
            "fix":{"ko":"손상된 모델 재다운로드: ModelZoo 또는 setup.sh 실행","en":"Re-download corrupted models via ModelZoo or setup.sh","ja":"破損モデルの再ダウンロード: ModelZooまたはsetup.sh実行","zhCN":"重新下载损坏的模型: 通过ModelZoo或setup.sh","zhTW":"重新下載損壞的模型: 透過ModelZoo或setup.sh"}})
    else:
        checks.append({"id":"model_integrity","label":{"ko":"모델 파일 무결성","en":"Model File Integrity","ja":"モデルファイル整合性","zhCN":"模型文件完整性","zhTW":"模型檔案完整性"},"ok":False,
            "detail":"assets/models/ not found","fix":{"ko":"setup.sh 실행하여 모델 다운로드","en":"Run setup.sh to download models","ja":"setup.shを実行してモデルをダウンロード","zhCN":"运行setup.sh下载模型","zhTW":"執行setup.sh下載模型"}})

    # 12. OpenCV availability
    try:
        import cv2
        checks.append({"id":"opencv","label":{"ko":"OpenCV","en":"OpenCV","ja":"OpenCV","zhCN":"OpenCV","zhTW":"OpenCV"},"ok":True,"detail":f"v{cv2.__version__}"})
    except ImportError:
        checks.append({"id":"opencv","label":{"ko":"OpenCV","en":"OpenCV","ja":"OpenCV","zhCN":"OpenCV","zhTW":"OpenCV"},"ok":False,
            "detail":"Not installed","fix":{"ko":"pip install opencv-python-headless","en":"pip install opencv-python-headless","ja":"pip install opencv-python-headless","zhCN":"pip install opencv-python-headless","zhTW":"pip install opencv-python-headless"}})

    passed=sum(1 for c in checks if c["ok"])
    total=len(checks)
    return {"checks":checks,"passed":passed,"total":total,"all_ok":passed==total}

_QUICK_ORDER = ["dx-app-deps","dx-rt-deps","dx-rt-build","dx-driver","dx-app-build","dx-app-setup"]

def quick_start_plan():
    """Ordered setup step ids still needed for a demo-only setup (skip satisfied)."""
    st = setup_status()
    return [sid for sid in _QUICK_ORDER if not (st.get(sid) or {}).get("ok")]


def setup_run(step,params=None):
    """Start a setup step script in background (streams via config._comp_log)."""
    if params is None:params={}
    cfg=SETUP_STEPS.get(step)
    if not cfg:return{"ok":False,"error":f"Unknown step: {step}"}
    # A step is driven by either a shell "script" (bash <path> [args]) or a direct "cmd"
    # (argv list, for studio-native steps that must not add scripts to the dx-runtime tree).
    script=cfg["script"]() if cfg.get("script") else None
    if script is not None and not script.exists():return{"ok":False,"error":f"{script.name} not found"}
    with config._comp_lock:
        if config._comp_proc and config._comp_proc.poll() is None:
            return{"ok":False,"error":"Another process is already running"}
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
        if not u:return{"ok":False,"error":"Please enter your username (email)"}
        if not p:return{"ok":False,"error":"Please enter your password"}
        env["DX_USERNAME"]=u;env["DX_PASSWORD"]=p
    sudo_cleanup = lambda: None
    if cfg.get("needs_sudo"):
        sudo_cleanup = _configure_sudo_env(env, params.get("password",""))
        sudo_error = _preauthorize_sudo(params.get("password",""), env)
        if sudo_error:
            sudo_cleanup()
            # sudo_auth marker lets the client re-prompt for the password instead of failing.
            return{"ok":False,"error":sudo_error,"sudo_auth":True}
    cwd=cfg["cwd"]()
    args=cfg.get("args",[])
    # Demo Quick Start (frontend Task 10 passes {"demo_only": true} in the run params for the
    # dx-app-setup step only) — download demo sample assets instead of the full --all catalog.
    # Read from params (like username/password above) rather than adding a new function
    # parameter: the existing entrypoint signature/caller (server.py forwards the whole request
    # body as params) is left untouched, and no other step's args are affected.
    if step=="dx-app-setup" and params.get("demo_only"):
        args=["--demo-models"]
    with config._comp_log_lock:config._comp_log=""
    config._comp_done=False;config._comp_exit_code=-1
    def _run():
        import select as _select,os as _os
        buf=[]
        partial=""
        sudo_stop = threading.Event()
        try:
            if cfg.get("needs_sudo"):
                threading.Thread(target=_keep_sudo_alive,args=(sudo_stop,),daemon=True).start()
            run_argv=cfg["cmd"]() if cfg.get("cmd") else ["bash",str(script)]+args
            proc=subprocess.Popen(run_argv,
             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
             stdin=subprocess.PIPE,cwd=str(cwd),env=env,bufsize=0)
            config._comp_stdin_proc=proc
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
        finally:
            sudo_stop.set()
            sudo_cleanup()
            config._comp_stdin_proc=None
            with config._comp_log_lock:config._comp_log="".join(buf)
            config._comp_done=True
            print(f"[SETUP:{step}] Done. exit_code={config._comp_exit_code}")
    threading.Thread(target=_run,daemon=True).start()
    return{"ok":True,"started":True}

def setup_stop():
    """실행 중인 Setup 프로세스를 중단한다."""
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
