import os
import sys
from dx_engine import InferenceEngine as IE

engine_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(engine_path)


# Import Node base class from paddleocr
