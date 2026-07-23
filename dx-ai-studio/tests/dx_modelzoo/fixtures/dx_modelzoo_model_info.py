"""ModelInfo 형식 fixture – parse_modelzoo_model_file 테스트용."""
# 실제 dx-modelzoo 모델 파일과 동일한 패턴으로 작성
# (텍스트 파싱 대상이므로 실제 import 없이 구조만 유지)

from dx_modelzoo.models import ModelInfo
from dx_modelzoo.enums import DatasetType, EvaluationType


class AlexNet:
    info = ModelInfo(
        name="AlexNet",
        dataset=DatasetType.imagenet,
        evaluation=EvaluationType.image_classification,
        raw_performance="56.54 79.09",
        q_lite_performance="56.10 78.80",
        q_pro_performance=None,
    )
