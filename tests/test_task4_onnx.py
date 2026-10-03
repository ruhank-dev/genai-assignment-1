"""ONNX parity for the generator (random weights, so this runs without a trained checkpoint)."""
import numpy as np
import onnxruntime as ort
import torch

from src.shared.onnx_utils import export_and_verify
from src.task4.generator import UNetGenerator


def test_generator_onnx_parity_and_dynamic_batch(tmp_path):
    torch.manual_seed(0)
    g = UNetGenerator(base=16, emb_dim=8).eval()
    x = torch.rand(8, 3, 128, 128) * 2 - 1
    s = torch.tensor([0, 1, 2, 0, 1, 2, 0, 1], dtype=torch.int64)
    r = export_and_verify(g, (x, s), ["photo", "style_index"], ["sketch"], tmp_path / "g.onnx", atol=1e-4, bench=False)
    assert max(r["max_abs_err"].values()) < 1e-4
    sess = ort.InferenceSession(str(tmp_path / "g.onnx"), providers=["CPUExecutionProvider"])
    out = sess.run(None, {"photo": x[:3].numpy(), "style_index": s[:3].numpy()})[0]  # batch 3 (not exported with 3)
    ref = g(x[:3], s[:3]).detach().numpy()
    assert out.shape == (3, 3, 128, 128) and np.allclose(out, ref, atol=1e-4)
