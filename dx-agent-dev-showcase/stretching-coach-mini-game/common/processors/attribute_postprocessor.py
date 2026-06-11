"""
Attribute Recognition Postprocessor

For person attribute recognition models like DeepMAR, face_attr, etc.
Uses sigmoid activation (multi-label) instead of softmax (single-label).

DeepMAR output: [1, 35] logits → sigmoid → threshold per attribute
CelebA output:  [1, 40, 2] logits → softmax per attribute → argmax
"""

import numpy as np
from typing import List

from ..base import IPostprocessor, PreprocessContext, ClassificationResult


# PETA dataset 35 person attributes (used by DeepMAR models)
PETA_35_LABELS = [
    "Hat",                    #  0
    "Muffler",                #  1
    "Nothing on head",        #  2
    "Sunglasses",             #  3
    "Long Hair",              #  4
    "Casual Upper",           #  5
    "Formal Upper",           #  6
    "Jacket",                 #  7
    "Logo on Upper",          #  8
    "Plaid on Upper",         #  9
    "Short Sleeve",           # 10
    "Thin Stripes on Upper",  # 11
    "T-shirt",                # 12
    "Other Upper",            # 13
    "V-Neck",                 # 14
    "Casual Lower",           # 15
    "Formal Lower",           # 16
    "Jeans",                  # 17
    "Shorts",                 # 18
    "Long Lower",             # 19
    "Skirt",                  # 20
    "Thin Stripes on Lower",  # 21
    "Female",                 # 22
    "Age 17-30",              # 23
    "Age 31-45",              # 24
    "Age 46-60",              # 25
    "Age Over 60",            # 26
    "Body Fat",               # 27
    "Body Normal",            # 28
    "Body Thin",              # 29
    "Customer",               # 30
    "Employee",               # 31
    "Backpack",               # 32
    "Carrying Other",         # 33
    "Messenger Bag",          # 34
]

# CelebA 40 face attributes (used by face_attr models)
CELEBA_40_LABELS = [
    "5 o'Clock Shadow",       #  0
    "Arched Eyebrows",        #  1
    "Attractive",             #  2
    "Bags Under Eyes",        #  3
    "Bald",                   #  4
    "Bangs",                  #  5
    "Big Lips",               #  6
    "Big Nose",               #  7
    "Black Hair",             #  8
    "Blond Hair",             #  9
    "Blurry",                 # 10
    "Brown Hair",             # 11
    "Bushy Eyebrows",         # 12
    "Chubby",                 # 13
    "Double Chin",            # 14
    "Eyeglasses",             # 15
    "Goatee",                 # 16
    "Gray Hair",              # 17
    "Heavy Makeup",           # 18
    "High Cheekbones",        # 19
    "Male",                   # 20
    "Mouth Slightly Open",    # 21
    "Mustache",               # 22
    "Narrow Eyes",            # 23
    "No Beard",               # 24
    "Oval Face",              # 25
    "Pale Skin",              # 26
    "Pointy Nose",            # 27
    "Receding Hairline",      # 28
    "Rosy Cheeks",            # 29
    "Sideburns",              # 30
    "Smiling",                # 31
    "Straight Hair",          # 32
    "Wavy Hair",              # 33
    "Wearing Earrings",       # 34
    "Wearing Hat",            # 35
    "Wearing Lipstick",       # 36
    "Wearing Necklace",       # 37
    "Wearing Necktie",        # 38
    "Young",                  # 39
]


class AttributePostprocessor(IPostprocessor):
    """
    Postprocessor for person/face attribute recognition models.

    Applies sigmoid (multi-label) and returns attributes above threshold.
    Supports:
      - DeepMAR: [1, 35] logits → sigmoid → threshold
      - CelebA:  [1, 40, 2] logits → softmax per attr → positive class prob
    """

    def __init__(self, input_width: int = 224, input_height: int = 224,
                 config: dict = None, labels: List[str] = None):
        self.input_width = input_width
        self.input_height = input_height
        self.config = config or {}
        self.threshold = self.config.get('threshold', 0.5)
        self._labels = labels  # Auto-detected if None

    def process(self, outputs: List[np.ndarray],
                ctx: PreprocessContext) -> List[ClassificationResult]:
        output = outputs[0]

        # Detect model type by output shape
        if output.ndim == 3 and output.shape[-1] == 2:
            # CelebA style: [1, N, 2] → softmax per attribute
            logits = output.reshape(-1, 2)
            exp = np.exp(logits - logits.max(axis=1, keepdims=True))
            probs = exp[:, 1] / exp.sum(axis=1)
            labels = self._labels or CELEBA_40_LABELS
        else:
            # DeepMAR style: [1, N] → sigmoid
            logits = output.flatten()
            probs = 1.0 / (1.0 + np.exp(-logits))
            labels = self._labels or PETA_35_LABELS

        # Build results for activated attributes
        results = []
        for i, prob in enumerate(probs):
            if prob > self.threshold:
                name = labels[i] if i < len(labels) else f"attr_{i}"
                results.append(ClassificationResult(
                    class_id=int(i),
                    confidence=float(prob),
                    class_name=name,
                ))

        # Sort by confidence descending
        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    def get_model_name(self) -> str:
        return "attribute_recognition"
