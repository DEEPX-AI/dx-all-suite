"""Phase F (F20): ONNX input-shape surgery on real models."""
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import onnx
from onnx import helper, TensorProto

from dx_compiler.core.onnx_surgery import fix_input_batch_to_one, set_static_input_shapes


def _make(path, name, shape):
    x = helper.make_tensor_value_info(name, TensorProto.FLOAT, shape)
    y = helper.make_tensor_value_info("out", TensorProto.FLOAT, shape)
    g = helper.make_graph([helper.make_node("Identity", [name], ["out"])], "g", [x], [y])
    onnx.save(helper.make_model(g, opset_imports=[helper.make_opsetid("", 13)]), str(path))


def _input_shape(path, name="x"):
    m = onnx.load(str(path))
    inp = next(i for i in m.graph.input if i.name == name)
    return [d.dim_value if d.HasField("dim_value") else None for d in inp.type.tensor_type.shape.dim]


class TestOnnxSurgery(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        self.m = self.d / "m.onnx"

    def tearDown(self):
        self.tmp.cleanup()

    def test_dynamic_batch_to_one(self):
        _make(self.m, "x", [None, 3, 224, 224])
        res = fix_input_batch_to_one(str(self.m), str(self.d / "out.onnx"))
        self.assertEqual(res["status"], "changed")
        self.assertEqual(_input_shape(self.d / "out.onnx")[0], 1)

    def test_batch_gt1_to_one(self):
        _make(self.m, "x", [8, 3, 224, 224])
        res = fix_input_batch_to_one(str(self.m), str(self.d / "out.onnx"))
        self.assertEqual(res["status"], "changed")
        self.assertEqual(_input_shape(self.d / "out.onnx")[0], 1)

    def test_batch_already_one_unchanged(self):
        _make(self.m, "x", [1, 3, 224, 224])
        res = fix_input_batch_to_one(str(self.m))
        self.assertEqual(res["status"], "unchanged")

    def test_set_static_shapes(self):
        _make(self.m, "x", [1, 3, None, None])
        res = set_static_input_shapes(str(self.m), {"x": [1, 3, 512, 512]}, str(self.d / "out.onnx"))
        self.assertEqual(res["status"], "changed")
        self.assertEqual(_input_shape(self.d / "out.onnx", "x"), [1, 3, 512, 512])

    def test_set_static_ignores_unknown_and_dynamic(self):
        _make(self.m, "x", [1, 3, 224, 224])
        res = set_static_input_shapes(str(self.m), {"nope": [1, 1], "x": [1, 3, -1, -1]})
        self.assertEqual(res["status"], "unchanged")  # unknown name + non-positive dim skipped

    def test_error_on_missing_file(self):
        res = fix_input_batch_to_one(str(self.d / "nope.onnx"))
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
