from enum import IntEnum, auto

# Python 3.10 compatibility: StrEnum backport
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum
    class StrEnum(str, Enum):
        """StrEnum backport for Python < 3.11"""
        def __str__(self) -> str:
            return str(self.value)
        
        def _generate_next_value_(name, start, count, last_values):
            return name

class SessionType(StrEnum):
    onnxruntime = "OnnxRuntime"
    simulator = "Simulator"
    dxruntime = "DxRuntime"


class EvaluationType(StrEnum):
    image_classification = "ImageClassification"
    coco = "ObjectDection"
    segmentation = "ImageSegmentation"
    voc = "ObjectDetection"
    bsd68 = "ImageDenosing"
    widerface = "FaceDetection"
    omnidoc = "OmniDocBench"

    def metric(self) -> str:
        if self.value == EvaluationType.image_classification:
            return "TopK1, TopK5"
        elif self.value == EvaluationType.coco:
            return "mAP, mAP50"
        elif self.value == EvaluationType.voc:
            return "mAP50"
        elif self.value == EvaluationType.segmentation:
            return "mIoU"
        elif self.value == EvaluationType.widerface:
            return "AP"
        else:
            raise ValueError(f"Invalid Evaluation Type value. {self.value}")


class DatasetType(StrEnum):
    imagenet = "ImageNet"
    coco = "COCO"
    voc_seg = "VOCSegmentation"
    voc_od = "VOC2007Detection"
    bsd68 = "BSD68"
    city = "CitySpace"
    widerface = "WiderFace"
    omnidoc = "OmniDocBench"


class ResizeMode(StrEnum):
    torchvision = auto()
    default = auto()
    pad = auto()
    pycls = auto()
    ocr = auto()
    ppocr = auto()
    short = auto()  # resize_short mode (PaddleClas style)
    
    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


class ResizeArgEnum(StrEnum):
    size = auto()
    interpolation = auto()
    backend = auto()
    align_side = auto()
    scale_method = auto()
    pad_location = auto()
    pad_value = auto()
    normalize = auto()


class BackendEnum(StrEnum):
    cv2 = auto()
    pil = auto()


class AlignSideEnum(StrEnum):
    both = auto()
    long = auto()
    short = auto()


class ScaleMethodEnum(StrEnum):
    scale_up = auto()
    scale_down = auto()


class InterpolationEnum(StrEnum):
    BILINEAR = "BILINEAR"
    LINEAR = "LINEAR"
    NEAREST = "NEAREST"
    BICUBIC = "BICUBIC"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


class PILResizeInterpolationEnum(IntEnum):
    NEAREST = 0
    LANCZOS = 1
    BILINEAR = 2
    LINEAR = 2
    BICUBIC = 3
    BOX = 4
    HAMMING = 5

    def __repr__(self) -> str:
        return self.name


class CVResizeInterpolationEnum(IntEnum):
    NEAREST = 0
    LINEAR = 1
    BILINEAR = 1
    CUBIC = 2
    AREA = 3
    LANCZOS4 = 4
