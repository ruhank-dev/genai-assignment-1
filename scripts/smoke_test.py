"""End-to-end smoke test of the running stack (default: the nginx front door of docker compose).
Usage: python -m scripts.smoke_test [http://localhost]"""
import base64
import io
import sys

import httpx
from PIL import Image

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
SAMPLE = "src/app/frontend/public/samples/pet_1.jpg"
checks: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, info: str = "") -> None:
    checks.append((name, ok, info))
    print(("PASS" if ok else "FAIL"), name, info)


def png(url: str) -> bytes:
    return base64.b64decode(url.split(",", 1)[1])


def main() -> int:
    c = httpx.Client(base_url=BASE, timeout=60)
    img = open(SAMPLE, "rb").read()
    h = c.get("/health").json()
    check("health", h["status"] == "ok" and all(h["models_loaded"].values()), str(h["models_loaded"]))
    check("frontend index", "<div id=\"root\">" in c.get("/").text)
    check("spa route fallback", "<div id=\"root\">" in c.get("/soft-moe").text)

    def post(path, files=None, **data):
        return c.post(path, files=files or {"image": ("a.jpg", img, "image/jpeg")}, data=data)

    r = post("/api/v1/restore/universal", apply_corruption="true", corruption_type="gaussian_blur", severity="2").json()
    check("universal", r["corruption_applied"]["kernel"] == 5 and r["inference_time_ms"] > 0, f"{r['inference_time_ms']:.1f} ms")
    corrupted = png(r["corrupted_image"])
    for kind in ("salt_and_pepper", "gaussian_blur", "rectangular_occlusion"):
        cr = post("/api/v1/restore/universal", apply_corruption="true", corruption_type=kind, severity="3").json()
        f = {"image": ("c.png", png(cr["corrupted_image"]), "image/png")}
        hr = post("/api/v1/restore/hard-routed", files=f).json()
        check(f"hard-routed {kind}", hr["predicted_class"] == {"salt_and_pepper": "salt_and_pepper", "gaussian_blur": "gaussian_blur",
              "rectangular_occlusion": "rectangular_occlusion"}[kind], f"{hr['predicted_class']} -> {hr['selected_expert']}")
    hr = post("/api/v1/restore/hard-routed").json()
    check("hard-routed clean bypass", hr["selected_expert"] == "Identity Bypass" and hr["inference_time"]["specialist_ms"] == 0.0)
    sm = post("/api/v1/restore/soft-moe", files={"image": ("c.png", corrupted, "image/png")}).json()
    w = sm["routing_weights"]
    check("soft-moe weights", abs(sum(w.values()) - 1) < 1e-5 and sm["dominant_expert"] == max(w, key=w.get), str({k: round(v, 3) for k, v in w.items()}))
    outs = [post("/api/v1/sketch/generate", style=str(s)).json() for s in (1, 2, 3)]
    check("sketch 3 styles", len({o["sketch_image"] for o in outs}) == 3, f"{outs[0]['inference_time_ms']:.1f} ms")
    check("heat maps on all four endpoints", all(k["error_map"].startswith("data:image/png") for k in (r, hr, sm, outs[0])) and "stats" in outs[0])
    check("sketch image decodes", Image.open(io.BytesIO(png(outs[0]["sketch_image"]))).size == (128, 128))
    check("non-image -> 400", c.post("/api/v1/restore/soft-moe", files={"image": ("a.txt", b"hi", "text/plain")}).status_code == 400)
    big = io.BytesIO()
    Image.effect_noise((2400, 2400), 100).convert("RGB").save(big, format="PNG")
    check("oversized -> 413", c.post("/api/v1/restore/soft-moe", files={"image": ("b.png", big.getvalue(), "image/png")}).status_code == 413,
          f"{len(big.getvalue()) / 1e6:.1f} MB")
    bad = c.post("/api/v1/sketch/generate", files={"image": ("a.jpg", img, "image/jpeg")}, data={"style": "9"})
    check("bad style -> 422", bad.status_code == 422)
    failed = [n for n, ok, _ in checks if not ok]
    print(f"\n{len(checks) - len(failed)}/{len(checks)} checks passed", "" if not failed else f"FAILED: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
