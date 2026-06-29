import os
import glob as glob_mod
import logging

logger = logging.getLogger(__name__)

DXNN_DEVICES_ENV = "DXNN_DEVICES"


def _detect_device_count() -> int:
    """시스템에 설치된 NPU 디바이스 수를 자동 감지한다.
    우선순위: DX-RT API > /dev/dxrt* 스캔 > 기본값 1
    """
    try:
        from dx_engine import get_device_count
        n = get_device_count()
        if n > 0:
            return n
    except (ImportError, AttributeError, Exception):
        pass

    devs = sorted(glob_mod.glob("/dev/dxrt*"))
    if devs:
        return len(devs)

    return 1


def get_dxnn_devices() -> list[int]:
    """환경변수 DXNN_DEVICES에서 디바이스 목록을 읽어 반환한다.

    환경변수 형식: 쉼표로 구분된 정수 (예: "0" 또는 "0,1,2,3")
    환경변수가 설정되지 않으면 시스템의 NPU 디바이스 수를 자동 감지한다.
    """
    env_value = os.environ.get(DXNN_DEVICES_ENV)
    if env_value is None:
        n = _detect_device_count()
        devices = list(range(n))
        logger.info("DXNN_DEVICES 미설정 — 자동 감지: %d개 디바이스 %s", n, devices)
        return devices

    try:
        devices = [int(d.strip()) for d in env_value.split(",") if d.strip()]
        if not devices:
            n = _detect_device_count()
            devices = list(range(n))
            logger.warning("DXNN_DEVICES 환경변수가 비어 있습니다. 자동 감지: %s", devices)
            return devices
        logger.info("DXNN_DEVICES 환경변수로부터 디바이스 설정: %s", devices)
        return devices
    except ValueError:
        n = _detect_device_count()
        devices = list(range(n))
        logger.warning("DXNN_DEVICES 환경변수 파싱 실패 ('%s'). 자동 감지: %s", env_value, devices)
        return devices
