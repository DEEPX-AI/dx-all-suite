"""dx_stream Deep Diagnostics: 11 system checks for GStreamer/NPU environment."""
import glob as _glob
import shutil
import subprocess

from shared.runtime_context import RuntimeContextError, resolve_active_runtime_context
from shared.runtime_environment import RuntimeEnvironmentError, build_child_environment
from shared.runtime_validation import validate_stream_pipeline


_DXINFER_PARSE_PROBE = "videotestsrc num-buffers=1 ! dxinfer ! fakesink"


_DIAGNOSTIC_CHECK_SPECS = (
    {
        "checker": "_check_pcie",
        "id": "pcie_link",
        "severity": "blocker",
        "label": {"ko": "PCIe 링크 (DeepX)", "en": "PCIe Link (DeepX)", "ja": "PCIeリンク(DeepX)", "zhCN": "PCIe链接(DeepX)", "zhTW": "PCIe連結(DeepX)", "es": "Enlace PCIe (DeepX)"},
        "fix": {"ko": "PCIe 장치 확인: sudo lspci -d 1ff4:", "en": "Check PCIe: sudo lspci -d 1ff4:", "ja": "PCIe確認: sudo lspci -d 1ff4:", "zhCN": "检查PCIe: sudo lspci -d 1ff4:", "zhTW": "檢查PCIe: sudo lspci -d 1ff4:", "es": "Comprobar PCIe: sudo lspci -d 1ff4:"},
    },
    {
        "checker": "_check_dev_files",
        "id": "dev_files",
        "severity": "blocker",
        "label": {"ko": "디바이스 파일", "en": "Device Files", "ja": "デバイスファイル", "zhCN": "设备文件", "zhTW": "裝置檔案", "es": "Archivos de dispositivo"},
        "fix": {"ko": "드라이버 재설치 필요", "en": "Reinstall driver", "ja": "ドライバ再インストール", "zhCN": "重新安装驱动", "zhTW": "重新安裝驅動", "es": "Reinstalar el controlador"},
    },
    {
        "checker": "_check_kmod",
        "id": "kmod",
        "severity": "blocker",
        "label": {"ko": "커널 모듈", "en": "Kernel Modules", "ja": "カーネルモジュール", "zhCN": "内核模块", "zhTW": "核心模組", "es": "Módulos del kernel"},
        "fix": {"ko": "실행: sudo modprobe dxrt_driver", "en": "Run: sudo modprobe dxrt_driver", "ja": "実行: sudo modprobe dxrt_driver", "zhCN": "执行: sudo modprobe dxrt_driver", "zhTW": "執行: sudo modprobe dxrt_driver", "es": "Ejecutar: sudo modprobe dxrt_driver"},
    },
    {
        "checker": "_check_dkms",
        "id": "dkms",
        "severity": "blocker",
        "label": {"ko": "DKMS 상태", "en": "DKMS Status", "ja": "DKMSステータス", "zhCN": "DKMS状态", "zhTW": "DKMS狀態", "es": "Estado de DKMS"},
        "fix": {"ko": "DKMS 재빌드: sudo dkms autoinstall", "en": "Rebuild DKMS: sudo dkms autoinstall", "ja": "DKMS再ビルド: sudo dkms autoinstall", "zhCN": "重建DKMS: sudo dkms autoinstall", "zhTW": "重建DKMS: sudo dkms autoinstall", "es": "Reconstruir DKMS: sudo dkms autoinstall"},
    },
    {
        "checker": "_check_dxrt_service",
        "id": "dxrt_service",
        "severity": "blocker",
        "label": {"ko": "dxrt 서비스", "en": "dxrt Service", "ja": "dxrtサービス", "zhCN": "dxrt服务", "zhTW": "dxrt服務", "es": "Servicio dxrt"},
        "fix": {"ko": "실행: sudo systemctl restart dxrt", "en": "Run: sudo systemctl restart dxrt", "ja": "実行: sudo systemctl restart dxrt", "zhCN": "执行: sudo systemctl restart dxrt", "zhTW": "執行: sudo systemctl restart dxrt", "es": "Ejecutar: sudo systemctl restart dxrt"},
    },
    {
        "checker": "_check_gst_install",
        "id": "gst_install",
        "severity": "blocker",
        "label": {"ko": "GStreamer 설치", "en": "GStreamer Install", "ja": "GStreamerインストール", "zhCN": "GStreamer安装", "zhTW": "GStreamer安裝", "es": "Instalación de GStreamer"},
        "fix": {"ko": "Runtime Deps 단계 실행", "en": "Run Runtime Deps step", "ja": "Runtime Depsステップ実行", "zhCN": "运行Runtime Deps步骤", "zhTW": "執行Runtime Deps步驟", "es": "Ejecutar el paso Runtime Deps"},
    },
    {
        "checker": "_check_gst_plugin",
        "id": "gst_plugin",
        "severity": "blocker",
        "label": {"ko": "DX Stream 플러그인 factory", "en": "DX Stream Plugin Factory", "ja": "DX Streamプラグイン factory", "zhCN": "DX Stream插件 factory", "zhTW": "DX Stream外掛 factory", "es": "Factory del complemento DX Stream"},
        "fix": {"ko": "Build 단계 실행", "en": "Run Build step", "ja": "Buildステップ実行", "zhCN": "运行Build步骤", "zhTW": "執行Build步驟", "es": "Ejecutar el paso Build"},
    },
    {
        "checker": "_check_gst_pipeline",
        "id": "gst_pipeline_test",
        "severity": "blocker",
        "label": {"ko": "DeepX 파이프라인 구성", "en": "DeepX Pipeline Construction", "ja": "DeepXパイプライン構成", "zhCN": "DeepX管道构建", "zhTW": "DeepX管線建構", "es": "Construcción de pipeline DeepX"},
        "fix": {"ko": "활성 Runtime profile 및 DX Stream 플러그인을 복구한 후 다시 시도", "en": "Repair the active runtime profile and DX Stream plugin, then retry", "ja": "有効なRuntime profileとDX Streamプラグインを修復して再試行", "zhCN": "修复活动Runtime profile和DX Stream插件后重试", "zhTW": "修復使用中的Runtime profile和DX Stream外掛後重試", "es": "Repare el perfil de runtime activo y el complemento DX Stream, y vuelva a intentarlo"},
    },
    {
        "checker": "_check_webrtc",
        "id": "webrtc_elements",
        "severity": "advisory",
        "label": {"ko": "WebRTC 요소", "en": "WebRTC Elements", "ja": "WebRTC要素", "zhCN": "WebRTC元素", "zhTW": "WebRTC元素", "es": "Elementos WebRTC"},
        "fix": {"ko": "WebRTC Deps 단계 실행", "en": "Run WebRTC Deps step", "ja": "WebRTC Depsステップ実行", "zhCN": "运行WebRTC Deps步骤", "zhTW": "執行WebRTC Deps步驟", "es": "Ejecutar el paso WebRTC Deps"},
    },
    {
        "checker": "_check_disk",
        "id": "disk_space",
        "severity": "advisory",
        "label": {"ko": "디스크 공간", "en": "Disk Space", "ja": "ディスク容量", "zhCN": "磁盘空间", "zhTW": "磁碟空間", "es": "Espacio en disco"},
        "fix": {"ko": "최소 5GB 여유 공간 필요", "en": "Need >=5GB free space", "ja": "5GB以上の空き容量が必要", "zhCN": "需要>=5GB可用空间", "zhTW": "需要>=5GB可用空間", "es": "Se necesitan >=5GB de espacio libre"},
    },
    {
        "checker": "_check_memory",
        "id": "memory",
        "severity": "advisory",
        "label": {"ko": "가용 메모리", "en": "Available Memory", "ja": "利用可能メモリ", "zhCN": "可用内存", "zhTW": "可用記憶體", "es": "Memoria disponible"},
        "fix": {"ko": "최소 2GB 메모리 필요", "en": "Need >=2GB available memory", "ja": "2GB以上のメモリが必要", "zhCN": "需要>=2GB可用内存", "zhTW": "需要>=2GB可用記憶體", "es": "Se necesitan >=2GB de memoria disponible"},
    },
)


def _run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timeout"


def _check_pcie():
    rc, out, _ = _run(["lspci", "-d", "1ff4:"])
    ok = rc == 0 and len(out) > 0
    return {
        "id": "pcie_link",
        "label": {"ko": "PCIe 링크 (DeepX)", "en": "PCIe Link (DeepX)", "ja": "PCIeリンク(DeepX)", "zhCN": "PCIe链接(DeepX)", "zhTW": "PCIe連結(DeepX)", "es": "Enlace PCIe (DeepX)"},
        "ok": ok,
        "detail": out or "no DeepX device found",
        "fix": {"ko": "PCIe 장치 확인: sudo lspci -d 1ff4:", "en": "Check PCIe: sudo lspci -d 1ff4:", "ja": "PCIe確認: sudo lspci -d 1ff4:", "zhCN": "检查PCIe: sudo lspci -d 1ff4:", "zhTW": "檢查PCIe: sudo lspci -d 1ff4:", "es": "Comprobar PCIe: sudo lspci -d 1ff4:"},
    }


def _check_dev_files():
    devs = _glob.glob("/dev/dxrt*") + _glob.glob("/dev/deepx*")
    ok = len(devs) > 0
    return {
        "id": "dev_files",
        "label": {"ko": "디바이스 파일", "en": "Device Files", "ja": "デバイスファイル", "zhCN": "设备文件", "zhTW": "裝置檔案", "es": "Archivos de dispositivo"},
        "ok": ok,
        "detail": ", ".join(devs) if devs else "no /dev/dxrt* or /dev/deepx* found",
        "fix": {"ko": "드라이버 재설치 필요", "en": "Reinstall driver", "ja": "ドライバ再インストール", "zhCN": "重新安装驱动", "zhTW": "重新安裝驅動", "es": "Reinstalar el controlador"},
    }


def _check_kmod():
    rc, out, _ = _run(["lsmod"])
    modules = out if rc == 0 else ""
    has_dxrt = "dxrt_driver" in modules
    has_dma = "dx_dma" in modules
    ok = has_dxrt and has_dma
    detail = f"dxrt_driver={'OK' if has_dxrt else 'missing'} dx_dma={'OK' if has_dma else 'missing'}"
    return {
        "id": "kmod",
        "label": {"ko": "커널 모듈", "en": "Kernel Modules", "ja": "カーネルモジュール", "zhCN": "内核模块", "zhTW": "核心模組", "es": "Módulos del kernel"},
        "ok": ok,
        "detail": detail,
        "fix": {"ko": "실행: sudo modprobe dxrt_driver", "en": "Run: sudo modprobe dxrt_driver", "ja": "実行: sudo modprobe dxrt_driver", "zhCN": "执行: sudo modprobe dxrt_driver", "zhTW": "執行: sudo modprobe dxrt_driver", "es": "Ejecutar: sudo modprobe dxrt_driver"},
    }


def _check_dkms():
    rc, out, _ = _run(["dkms", "status"])
    ok = rc == 0 and "dxrt" in out.lower()
    return {
        "id": "dkms",
        "label": {"ko": "DKMS 상태", "en": "DKMS Status", "ja": "DKMSステータス", "zhCN": "DKMS状态", "zhTW": "DKMS狀態", "es": "Estado de DKMS"},
        "ok": ok,
        "detail": out[:200] if out else "dkms not found or no dxrt module",
        "fix": {"ko": "DKMS 재빌드: sudo dkms autoinstall", "en": "Rebuild DKMS: sudo dkms autoinstall", "ja": "DKMS再ビルド: sudo dkms autoinstall", "zhCN": "重建DKMS: sudo dkms autoinstall", "zhTW": "重建DKMS: sudo dkms autoinstall", "es": "Reconstruir DKMS: sudo dkms autoinstall"},
    }


def _check_dxrt_service():
    rc, out, _ = _run(["systemctl", "is-active", "dxrt"])
    ok = rc == 0 and out.strip() == "active"
    return {
        "id": "dxrt_service",
        "label": {"ko": "dxrt 서비스", "en": "dxrt Service", "ja": "dxrtサービス", "zhCN": "dxrt服务", "zhTW": "dxrt服務", "es": "Servicio dxrt"},
        "ok": ok,
        "detail": out or "inactive",
        "fix": {"ko": "실행: sudo systemctl restart dxrt", "en": "Run: sudo systemctl restart dxrt", "ja": "実行: sudo systemctl restart dxrt", "zhCN": "执行: sudo systemctl restart dxrt", "zhTW": "執行: sudo systemctl restart dxrt", "es": "Ejecutar: sudo systemctl restart dxrt"},
    }


def _check_gst_install():
    rc, out, _ = _run(["gst-inspect-1.0", "--version"])
    ok = rc == 0
    return {
        "id": "gst_install",
        "label": {"ko": "GStreamer 설치", "en": "GStreamer Install", "ja": "GStreamerインストール", "zhCN": "GStreamer安装", "zhTW": "GStreamer安裝", "es": "Instalación de GStreamer"},
        "ok": ok,
        "detail": out.split("\n")[0] if out else "not installed",
        "fix": {"ko": "Runtime Deps 단계 실행", "en": "Run Runtime Deps step", "ja": "Runtime Depsステップ実行", "zhCN": "运行Runtime Deps步骤", "zhTW": "執行Runtime Deps步驟", "es": "Ejecutar el paso Runtime Deps"},
    }


def _check_gst_plugin():
    rc, _, _ = _run(["gst-inspect-1.0", "--exists", "dxinfer"])
    ok = rc == 0
    return {
        "id": "gst_plugin",
        "label": {"ko": "DX Stream 플러그인 factory", "en": "DX Stream Plugin Factory", "ja": "DX Streamプラグイン factory", "zhCN": "DX Stream插件 factory", "zhTW": "DX Stream外掛 factory", "es": "Factory del complemento DX Stream"},
        "ok": ok,
        "detail": "dxinfer factory found" if ok else "dxinfer factory not found",
        "fix": {"ko": "Build 단계 실행", "en": "Run Build step", "ja": "Buildステップ実行", "zhCN": "运行Build步骤", "zhTW": "執行Build步驟", "es": "Ejecutar el paso Build"},
    }


def _check_gst_pipeline():
    try:
        context = resolve_active_runtime_context()
        result = validate_stream_pipeline(
            _DXINFER_PARSE_PROBE,
            python_executable=context.python_executable,
            environment=build_child_environment(context),
        )
        ok = result.passed
        failure = result.first_failure
        detail = "parsed" if ok else (failure.observed if failure else "parse failed")
    except (RuntimeContextError, RuntimeEnvironmentError) as exc:
        ok = False
        detail = str(exc) or exc.__class__.__name__
    return {
        "id": "gst_pipeline_test",
        "label": {"ko": "DeepX 파이프라인 구성", "en": "DeepX Pipeline Construction", "ja": "DeepXパイプライン構成", "zhCN": "DeepX管道构建", "zhTW": "DeepX管線建構", "es": "Construcción de pipeline DeepX"},
        "ok": ok,
        "detail": detail,
        "fix": {"ko": "활성 Runtime profile 및 DX Stream 플러그인을 복구한 후 다시 시도", "en": "Repair the active runtime profile and DX Stream plugin, then retry", "ja": "有効なRuntime profileとDX Streamプラグインを修復して再試行", "zhCN": "修复活动Runtime profile和DX Stream插件后重试", "zhTW": "修復使用中的Runtime profile和DX Stream外掛後重試", "es": "Repare el perfil de runtime activo y el complemento DX Stream, y vuelva a intentarlo"},
    }


def _check_webrtc():
    rc, _, _ = _run(["gst-inspect-1.0", "nicesrc"])
    ok = rc == 0
    return {
        "id": "webrtc_elements",
        "label": {"ko": "WebRTC 요소", "en": "WebRTC Elements", "ja": "WebRTC要素", "zhCN": "WebRTC元素", "zhTW": "WebRTC元素", "es": "Elementos WebRTC"},
        "ok": ok,
        "detail": "nicesrc found" if ok else "nicesrc not found",
        "fix": {"ko": "WebRTC Deps 단계 실행", "en": "Run WebRTC Deps step", "ja": "WebRTC Depsステップ実行", "zhCN": "运行WebRTC Deps步骤", "zhTW": "執行WebRTC Deps步驟", "es": "Ejecutar el paso WebRTC Deps"},
    }


def _check_disk():
    usage = shutil.disk_usage("/")
    free_gb = usage.free / (1024**3)
    ok = free_gb >= 5.0
    return {
        "id": "disk_space",
        "label": {"ko": "디스크 공간", "en": "Disk Space", "ja": "ディスク容量", "zhCN": "磁盘空间", "zhTW": "磁碟空間", "es": "Espacio en disco"},
        "ok": ok,
        "detail": f"{free_gb:.1f} GB free",
        "fix": {"ko": "최소 5GB 여유 공간 필요", "en": "Need >=5GB free space", "ja": "5GB以上の空き容量が必要", "zhCN": "需要>=5GB可用空间", "zhTW": "需要>=5GB可用空間", "es": "Se necesitan >=5GB de espacio libre"},
    }


def _check_memory():
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    kb = int(line.split()[1])
                    gb = kb / (1024 * 1024)
                    ok = gb >= 2.0
                    return {
                        "id": "memory",
                        "label": {"ko": "가용 메모리", "en": "Available Memory", "ja": "利用可能メモリ", "zhCN": "可用内存", "zhTW": "可用記憶體", "es": "Memoria disponible"},
                        "ok": ok,
                        "detail": f"{gb:.1f} GB available",
                        "fix": {"ko": "최소 2GB 메모리 필요", "en": "Need >=2GB available memory", "ja": "2GB以上のメモリが必要", "zhCN": "需要>=2GB可用内存", "zhTW": "需要>=2GB可用記憶體", "es": "Se necesitan >=2GB de memoria disponible"},
                    }
    except Exception:
        pass
    return {
        "id": "memory",
        "label": {"ko": "가용 메모리", "en": "Available Memory", "ja": "利用可能メモリ", "zhCN": "可用内存", "zhTW": "可用記憶體", "es": "Memoria disponible"},
        "ok": False,
        "detail": "cannot read /proc/meminfo",
        "fix": {"ko": "/proc/meminfo 확인", "en": "Check /proc/meminfo", "ja": "/proc/meminfo確認", "zhCN": "检查/proc/meminfo", "zhTW": "檢查/proc/meminfo", "es": "Comprobar /proc/meminfo"},
    }


def deep_diagnostics():
    """Run all 11 diagnostic checks and return structured results."""
    # Build this registry per invocation so patched checker symbols are honored.
    check_specs = (
        (_check_pcie, "pcie_link", "blocker", _DIAGNOSTIC_CHECK_SPECS[0]),
        (_check_dev_files, "dev_files", "blocker", _DIAGNOSTIC_CHECK_SPECS[1]),
        (_check_kmod, "kmod", "blocker", _DIAGNOSTIC_CHECK_SPECS[2]),
        (_check_dkms, "dkms", "blocker", _DIAGNOSTIC_CHECK_SPECS[3]),
        (_check_dxrt_service, "dxrt_service", "blocker", _DIAGNOSTIC_CHECK_SPECS[4]),
        (_check_gst_install, "gst_install", "blocker", _DIAGNOSTIC_CHECK_SPECS[5]),
        (_check_gst_plugin, "gst_plugin", "blocker", _DIAGNOSTIC_CHECK_SPECS[6]),
        (_check_gst_pipeline, "gst_pipeline_test", "blocker", _DIAGNOSTIC_CHECK_SPECS[7]),
        (_check_webrtc, "webrtc_elements", "advisory", _DIAGNOSTIC_CHECK_SPECS[8]),
        (_check_disk, "disk_space", "advisory", _DIAGNOSTIC_CHECK_SPECS[9]),
        (_check_memory, "memory", "advisory", _DIAGNOSTIC_CHECK_SPECS[10]),
    )
    checks = []
    for checker, check_id, severity, presentation in check_specs:
        try:
            result = checker()
            if not isinstance(result, dict):
                raise TypeError("checker returned an invalid result")
            check = dict(result)
            check["id"] = check_id
            check["ok"] = bool(check.get("ok", False))
            check["detail"] = str(check.get("detail", ""))
            check["severity"] = severity
            if "label" not in check:
                check["label"] = presentation["label"]
            if "fix" not in check:
                check["fix"] = presentation["fix"]
        except Exception as exc:
            message = str(exc) or exc.__class__.__name__
            check = {
                "id": check_id,
                "label": presentation["label"],
                "ok": False,
                "detail": "Diagnostic check failed: {}".format(message),
                "fix": presentation["fix"],
                "severity": severity,
            }
        checks.append(check)

    passed = sum(1 for c in checks if c["ok"])
    blockers = sum(1 for c in checks if not c["ok"] and c["severity"] == "blocker")
    advisories = sum(1 for c in checks if not c["ok"] and c["severity"] == "advisory")
    return {
        "all_ok": passed == len(checks),
        "runtime_ready": blockers == 0,
        "severity_summary": {"blockers": blockers, "advisories": advisories},
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }
