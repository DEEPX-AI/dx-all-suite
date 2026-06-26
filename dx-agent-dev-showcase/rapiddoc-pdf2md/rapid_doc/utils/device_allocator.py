# rapid_doc/utils/device_allocator.py
"""모델별 NPU 디바이스 할당기.

hybrid 모드에서 각 모델에 전용 NPU 디바이스를 할당하여
어셈블리 라인의 스테이지가 물리적으로 동시에 추론할 수 있게 한다.
"""
import os
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 모델 이름 상수
MODEL_LAYOUT = "layout"
MODEL_OCR_DET = "ocr_det"
MODEL_OCR_REC = "ocr_rec"
MODEL_TABLE = "table"
ALL_MODELS = [MODEL_LAYOUT, MODEL_OCR_DET, MODEL_OCR_REC, MODEL_TABLE]
# OCR det/rec은 파이프라인 상 순차 실행 — 같은 디바이스 공유 시 lock 불필요
OCR_GROUP = {MODEL_OCR_DET, MODEL_OCR_REC}

DXNN_DEVICES_ENV = "DXNN_DEVICES"


class DeviceAllocator:
    """모델별 NPU 디바이스 할당기.

    Args:
        hybrid: True이면 모델별 전용 디바이스 할당 모드.
        device_ids: 사용할 디바이스 ID 목록. None이면 자동 감지.
    """

    def __init__(self, hybrid: bool = False, device_ids: Optional[list] = None):
        self.hybrid = hybrid
        self._all_devices = device_ids if device_ids is not None else self._detect_devices()
        self._allocation = self._compute_allocation()
        self._device_locks: dict = {
            dev: threading.Lock() for dev in self._all_devices
        }

    @property
    def all_devices(self) -> list:
        return list(self._all_devices)

    def _detect_devices(self) -> list:
        """NPU 디바이스 목록 감지. 우선순위: 환경변수 > DX-RT API > /dev 스캔."""
        env = os.environ.get(DXNN_DEVICES_ENV)
        if env:
            try:
                devices = [int(d.strip()) for d in env.split(",") if d.strip()]
                if devices:
                    logger.info("DXNN_DEVICES로부터 디바이스 감지: %s", devices)
                    return devices
            except ValueError:
                logger.warning("DXNN_DEVICES 파싱 실패: '%s'", env)

        try:
            from dx_engine import get_device_count
            n = get_device_count()
            logger.info("DX-RT API로 %d개 디바이스 감지", n)
            return list(range(n))
        except (ImportError, AttributeError, Exception):
            pass

        import glob as glob_mod
        devs = sorted(glob_mod.glob("/dev/dxrt*"))
        if devs:
            logger.info("/dev/dxrt* 스캔으로 %d개 디바이스 감지", len(devs))
            return list(range(len(devs)))

        logger.warning("NPU 디바이스를 감지하지 못했습니다. 기본값 [0] 사용")
        return [0]

    def _compute_allocation(self) -> dict:
        """디바이스 수에 따라 모델별 할당 계산."""
        n = len(self._all_devices)

        if not self.hybrid:
            return {model: list(self._all_devices) for model in ALL_MODELS}

        if n < 2:
            raise RuntimeError(
                f"--hybrid 모드는 NPU 2대 이상 필요합니다 (감지된 디바이스: {n}대)"
            )

        devs = self._all_devices

        if n == 2:
            return {
                MODEL_LAYOUT: [devs[0]],
                MODEL_OCR_DET: [devs[1]],
                MODEL_OCR_REC: [devs[1]],
                MODEL_TABLE: [devs[0]],
            }
        elif n == 3:
            return {
                MODEL_LAYOUT: [devs[0]],
                MODEL_OCR_DET: [devs[1]],
                MODEL_OCR_REC: [devs[1]],
                MODEL_TABLE: [devs[2]],
            }
        elif n == 4:
            return {
                MODEL_LAYOUT: [devs[0]],
                MODEL_OCR_DET: [devs[1]],
                MODEL_OCR_REC: [devs[2]],
                MODEL_TABLE: [devs[3]],
            }
        else:  # 5+
            return {
                MODEL_LAYOUT: [devs[0]],
                MODEL_OCR_DET: [devs[1]],
                MODEL_OCR_REC: devs[2:-1],
                MODEL_TABLE: [devs[-1]],
            }

    def get_devices(self, model_name: str) -> list:
        """특정 모델의 할당된 디바이스 목록 반환."""
        return list(self._allocation[model_name])

    def get_lock(self, model_name: str) -> Optional[threading.Lock]:
        """이 모델의 디바이스 lock 반환. exclusive면 None."""
        if not self.hybrid:
            return None
        if self.is_exclusive(model_name):
            return None
        devices = self.get_devices(model_name)
        return self._device_locks[devices[0]]

    def is_exclusive(self, model_name: str) -> bool:
        """이 모델이 전용 디바이스를 갖는지 (다른 모델과 공유하지 않는지).

        OCR det/rec은 순차 실행이므로 서로 간의 디바이스 공유는 충돌로 보지 않는다.
        """
        my_devices = set(self._allocation[model_name])
        for other_model, other_devices in self._allocation.items():
            if other_model == model_name:
                continue
            # OCR det↔rec 공유는 순차 실행이므로 exclusive로 취급
            if {model_name, other_model} <= OCR_GROUP:
                continue
            if my_devices & set(other_devices):
                return False
        return True
