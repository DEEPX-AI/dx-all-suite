"""ModelInfo-format fixture for the parse_modelzoo_model_file tests."""
# Written in the same pattern as a real dx-modelzoo model file
# (it is parsed as text, so only the structure matters; nothing is imported)

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
