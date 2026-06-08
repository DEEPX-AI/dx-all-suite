"""
TFLite Detection Postprocessor

Handles TFLite-style detection models where NMS is built-in to the model.
Output format (4 tensors):
  - output[0]: [1, N, 4]  bounding boxes (ymin, xmin, ymax, xmax) normalized [0,1]
  - output[1]: [1, N]     class IDs (float → int)
  - output[2]: [1, N]     confidence scores
  - output[3]: [1]        number of valid detections

Examples: MobileDetV1, EfficientDet-Lite, SSD MobileNet TFLite exports.
"""

import numpy as np
from typing import List

from ..base import IPostprocessor, DetectionResult, PreprocessContext


class TFLiteDetectionPostprocessor(IPostprocessor):
    """
    Postprocessor for TFLite models with built-in NMS.

    No additional NMS needed — the model already outputs filtered detections.
    """

    def __init__(self, input_width: int, input_height: int, config: dict = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}

        self.conf_threshold = self.config.get('conf_threshold',
                              self.config.get('score_threshold', 0.3))

    def process(self, outputs: List[np.ndarray], ctx: PreprocessContext) -> List[DetectionResult]:
        """
        Process TFLite detection outputs.

        Args:
            outputs: [boxes, class_ids, scores, num_detections]
            ctx: Preprocessing context

        Returns:
            List of DetectionResult
        """
        boxes_raw = np.squeeze(outputs[0])    # [N, 4]  (ymin, xmin, ymax, xmax) normalized
        class_ids = np.squeeze(outputs[1])    # [N]
        scores = np.squeeze(outputs[2])       # [N]
        num_dets = int(np.squeeze(outputs[3]))  # scalar

        # Ensure 2D for single-detection edge case
        if boxes_raw.ndim == 1:
            boxes_raw = boxes_raw.reshape(1, -1)
            class_ids = np.array([class_ids])
            scores = np.array([scores])

        results = []
        for i in range(min(num_dets, len(scores))):
            if scores[i] < self.conf_threshold:
                continue

            # TFLite box format: [ymin, xmin, ymax, xmax] normalized
            ymin, xmin, ymax, xmax = boxes_raw[i]

            # Scale to original image coordinates
            # TFLite models typically use simple_resize (no letterbox)
            if hasattr(ctx, 'pad_x') and ctx.pad_x == 0 and ctx.pad_y == 0:
                # simple_resize: scale directly to original dimensions
                x1 = xmin * ctx.original_width
                y1 = ymin * ctx.original_height
                x2 = xmax * ctx.original_width
                y2 = ymax * ctx.original_height
            else:
                # letterbox: scale to input, undo pad/scale
                x1_inp = xmin * self.input_width
                y1_inp = ymin * self.input_height
                x2_inp = xmax * self.input_width
                y2_inp = ymax * self.input_height
                gain = max(ctx.scale, 1e-6)
                x1 = (x1_inp - ctx.pad_x) / gain
                y1 = (y1_inp - ctx.pad_y) / gain
                x2 = (x2_inp - ctx.pad_x) / gain
                y2 = (y2_inp - ctx.pad_y) / gain

            x1 = np.clip(x1, 0, ctx.original_width - 1)
            y1 = np.clip(y1, 0, ctx.original_height - 1)
            x2 = np.clip(x2, 0, ctx.original_width - 1)
            y2 = np.clip(y2, 0, ctx.original_height - 1)

            results.append(DetectionResult(
                box=[float(x1), float(y1), float(x2), float(y2)],
                confidence=float(scores[i]),
                class_id=int(class_ids[i]),
            ))

        return results

    def get_model_name(self) -> str:
        return "tflite_detection"
