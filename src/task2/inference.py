"""Load the trained classifier + specialists into a HardRouter; small CLI benchmark."""
import torch

from src.shared.config import get_device, settings
from src.task1.autoencoder import UniversalAutoencoder
from src.task2.classifier import CHANNELS, CorruptionClassifier
from src.task2.router import HardRouter
from src.task2.specialist import SPEC_FILES, SPEC_TYPES


def load_classifier(path, dev):
    ck = torch.load(path, map_location=dev)
    c = ck["config"]
    m = CorruptionClassifier(CHANNELS[c["channel_config"]], c["dropout"]).to(dev)
    m.load_state_dict(ck["model_state_dict"], strict=True)
    return m.eval()


def load_specialist(path, dev):
    ck = torch.load(path, map_location=dev)
    c = ck["config"]
    m = UniversalAutoencoder(c["channels"], c["bottleneck_dim"], c["dropout"]).to(dev)
    m.load_state_dict(ck["model_state_dict"], strict=True)
    return m.eval()


def load_router(dev=None) -> HardRouter:
    dev = dev or get_device()
    d = settings.checkpoint_dir / "task2"
    cls = load_classifier(d / "classifier_best.pt", dev)
    specs = [load_specialist(d / SPEC_FILES[t], dev) for t in SPEC_TYPES]
    return HardRouter(cls, specs).to(dev).eval()


if __name__ == "__main__":
    dev = get_device()
    router = load_router(dev)
    from src.shared.datasets.corrupted import CorruptedPets
    ds = CorruptedPets("val")
    x = torch.stack([ds[i][0] for i in range(8)]).to(dev)
    r = router(x)
    print({k: v for k, v in r.items() if k.endswith("_ms")}, r["routing_decision"].tolist())
    one = router(x[:1])
    print(one["predicted_class"], one["selected_expert"], one["probabilities"])
