"""dx_stream Deep Diagnostics: 11 system checks for GStreamer/NPU environment."""
import glob as _glob
import shutil
import subprocess


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
    rc, out, _ = _run(["gst-inspect-1.0", "dxstream"])
    ok = rc == 0 and "dxstream" in out.lower()
    return {
        "id": "gst_plugin",
        "label": {"ko": "dxstream 플러그인", "en": "dxstream Plugin", "ja": "dxstreamプラグイン", "zhCN": "dxstream插件", "zhTW": "dxstream外掛", "es": "Complemento dxstream"},
        "ok": ok,
        "detail": "found" if ok else "not found",
        "fix": {"ko": "Build 단계 실행", "en": "Run Build step", "ja": "Buildステップ実行", "zhCN": "运行Build步骤", "zhTW": "執行Build步驟", "es": "Ejecutar el paso Build"},
    }


def _check_gst_pipeline():
    rc, _, err = _run(["gst-launch-1.0", "videotestsrc", "num-buffers=1", "!", "dxstream", "!", "fakesink"], timeout=15)
    ok = rc == 0
    return {
        "id": "gst_pipeline_test",
        "label": {"ko": "파이프라인 테스트", "en": "Pipeline Test", "ja": "パイプラインテスト", "zhCN": "管道测试", "zhTW": "管線測試", "es": "Prueba de pipeline"},
        "ok": ok,
        "detail": "passed" if ok else (err[:200] if err else "failed"),
        "fix": {"ko": "파이프라인 디버그: GST_DEBUG=3 gst-launch-1.0 ...", "en": "Debug pipeline: GST_DEBUG=3 gst-launch-1.0 ...", "ja": "パイプラインデバッグ: GST_DEBUG=3 gst-launch-1.0 ...", "zhCN": "调试管道: GST_DEBUG=3 gst-launch-1.0 ...", "zhTW": "除錯管線: GST_DEBUG=3 gst-launch-1.0 ...", "es": "Depurar pipeline: GST_DEBUG=3 gst-launch-1.0 ..."},
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
    checks = [
        _check_pcie(),
        _check_dev_files(),
        _check_kmod(),
        _check_dkms(),
        _check_dxrt_service(),
        _check_gst_install(),
        _check_gst_plugin(),
        _check_gst_pipeline(),
        _check_webrtc(),
        _check_disk(),
        _check_memory(),
    ]
    passed = sum(1 for c in checks if c["ok"])
    return {"all_ok": passed == len(checks), "passed": passed, "total": len(checks), "checks": checks}
