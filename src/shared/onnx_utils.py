"""Shared ONNX export + PyTorch-vs-ORT parity + latency benchmark (used by every task)."""
import time
from pathlib import Path

import numpy as np
import onnx
import onnxruntime as ort
import torch

OPSET = 17


def export_and_verify(model: torch.nn.Module, example_inputs: tuple, input_names: list[str], output_names: list[str],
                      path: Path, atol: float = 1e-4, batches: tuple = (1, 4, 8), bench: bool = True) -> dict:
    """Export on CPU with dynamic batch, check graph, compare outputs for several batch sizes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    model = model.cpu().eval()
    axes = {n: {0: "batch_size"} for n in input_names + output_names}
    torch.onnx.export(model, example_inputs, str(path), input_names=input_names, output_names=output_names,
                      dynamic_axes=axes, opset_version=OPSET, do_constant_folding=True, dynamo=False)
    onnx.checker.check_model(onnx.load(str(path)))
    sess = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
    res = {"path": str(path), "opset": OPSET, "size_mb": round(path.stat().st_size / 1e6, 2), "max_abs_err": {}}
    for b in batches:
        ins = tuple(_resize(e, b) for e in example_inputs)
        with torch.no_grad():
            ref = model(*ins)
        ref = ref if isinstance(ref, (tuple, list)) else (ref,)
        out = sess.run(None, {n: t.numpy() for n, t in zip(input_names, ins)})
        err = max(float(np.abs(r.numpy() - o).max()) for r, o in zip(ref, out))
        res["max_abs_err"][b] = err
        assert all(np.allclose(r.numpy(), o, atol=atol) for r, o in zip(ref, out)), f"parity failed b={b}: {err}"
    if bench:
        one = tuple(_resize(e, 1) for e in example_inputs)
        feed = {n: t.numpy() for n, t in zip(input_names, one)}
        for name, f in (("pytorch", lambda: model(*one)), ("onnxruntime", lambda: sess.run(None, feed))):
            with torch.no_grad():
                for _ in range(20):
                    f()
                t0 = time.perf_counter()
                for _ in range(50):
                    f()
            res[f"{name}_ms"] = round(1000 * (time.perf_counter() - t0) / 50, 3)
    return res


def _resize(t: torch.Tensor, b: int) -> torch.Tensor:
    n = t.shape[0]
    return t[:b] if b <= n else t.repeat(-(-b // n), *([1] * (t.ndim - 1)))[:b]
