import time

import torch
import torch.nn as nn

from src.task2.classifier import CLS_NAMES

EXPERTS = ["identity_bypass", "specialist_salt", "specialist_blur", "specialist_occlusion"]


class HardRouter(nn.Module):
    """r = argmax C(x); r=0 -> identity bypass, r=1..3 -> specialist r. Batched: group by r, run each expert once."""

    def __init__(self, classifier: nn.Module, specialists: list[nn.Module]):
        super().__init__()
        self.classifier = classifier
        self.specialists = nn.ModuleList(specialists)  # order: salt, blur, occlusion

    @staticmethod
    def _sync(x):
        if x.is_cuda:
            torch.cuda.synchronize()

    @torch.no_grad()
    def forward(self, x: torch.Tensor, oracle_labels: torch.Tensor | None = None) -> dict:
        self._sync(x)
        t0 = time.perf_counter()
        probs = self.classifier(x).softmax(1)
        self._sync(x)
        t1 = time.perf_counter()
        r = probs.argmax(1) if oracle_labels is None else oracle_labels  # oracle mode bypasses the classifier decision
        out = x.clone()  # identity bypass is an exact copy (MSE = 0)
        for k, spec in enumerate(self.specialists, start=1):
            m = r == k
            if m.any():
                out[m] = spec(x[m])
        self._sync(x)
        t2 = time.perf_counter()
        res = {"reconstructed": out, "routing_decision": r, "probabilities": probs,
               "classifier_latency_ms": 1000 * (t1 - t0), "restoration_latency_ms": 1000 * (t2 - t1),
               "total_latency_ms": 1000 * (t2 - t0)}
        if x.shape[0] == 1:  # single image: human-readable fields used by the API
            k = int(r[0])
            res["predicted_class"] = CLS_NAMES[int(probs[0].argmax())]
            res["selected_expert"] = EXPERTS[k]
            res["probabilities"] = {n: float(probs[0, i]) for i, n in enumerate(CLS_NAMES)}
        return res
