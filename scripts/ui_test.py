"""Browser end-to-end test of the running app (needs: pip install playwright && playwright install chromium).
Drives all four workspaces like an evaluator and stores screenshots in results/app/. Usage: python scripts/ui_test.py [url]"""
import sys
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
OUT = Path("results/app")
OUT.mkdir(parents=True, exist_ok=True)
SAMPLE = Path("src/app/frontend/public/samples/pet_2.jpg")
FACE = Path("src/app/frontend/public/samples/pet_3.jpg")  # any JPEG works for the face workspace smoke test
results: list[tuple[str, bool]] = []


def step(name: str, fn) -> None:
    try:
        fn()
        results.append((name, True))
        print("PASS", name)
    except Exception as e:  # noqa: BLE001
        results.append((name, False))
        print("FAIL", name, str(e)[:300])


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1400, "height": 1000})
    errors: list[str] = []
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(URL)

    def shell():
        expect(pg.get_by_text("GenAI Studio")).to_be_visible()
        expect(pg.get_by_text("models ready")).to_be_visible(timeout=10000)
        assert pg.url.endswith("/universal")

    step("shell + health badge + redirect to /universal", shell)

    def universal():
        pg.locator("button:has(img[alt='clean sample'])").first.click()
        pg.get_by_role("button", name="Gaussian blur").click()
        pg.get_by_role("button", name="Medium").click()
        pg.get_by_role("button", name="Restore Image").click()
        expect(pg.get_by_text("Inference")).to_be_visible(timeout=15000)
        expect(pg.get_by_alt_text("Restored")).to_be_visible()
        expect(pg.get_by_alt_text("absolute error map")).to_be_visible()
        expect(pg.get_by_text("gaussian blur · k=5, σ=1.5")).to_be_visible()
        pg.screenshot(path=str(OUT / "1_universal.png"), full_page=True)

    pg.get_by_role("button", name="Salt-and-pepper").first.click()
    step("universal restoration (studio mode, blur medium)", universal)

    def hard():
        pg.get_by_role("link", name="Hard-Routed Restoration").click()
        pg.locator("button:has(img[alt='clean sample'])").nth(1).click()
        pg.get_by_role("button", name="Salt-and-pepper").click()
        pg.get_by_role("button", name="High").click()
        pg.get_by_role("button", name="Apply corruption → use as input").click()
        expect(pg.get_by_alt_text("selected upload")).to_be_visible(timeout=15000)
        pg.get_by_role("button", name="Analyze & Restore").click()
        expect(pg.get_by_text("Routing decision (argmax)")).to_be_visible(timeout=15000)
        expect(pg.get_by_text("task2_specialist_salt.onnx")).to_be_visible()
        pg.screenshot(path=str(OUT / "2_hard_routed.png"), full_page=True)

    step("hard-routed: corrupted sample routed to salt specialist", hard)

    def soft():
        pg.get_by_role("link", name="Soft Mixture-of-Experts").click()
        pg.locator("button:has(img[alt='clean sample'])").nth(2).click()
        pg.get_by_role("button", name="Rectangular occlusion").click()
        pg.get_by_role("button", name="High").click()
        pg.get_by_role("button", name="Apply corruption → use as input").click()
        expect(pg.get_by_alt_text("selected upload")).to_be_visible(timeout=15000)
        pg.get_by_role("button", name="Run Soft MoE Restoration").click()
        expect(pg.get_by_text("Gating weights")).to_be_visible(timeout=15000)
        expect(pg.get_by_text("DOMINANT")).to_be_visible()
        pg.screenshot(path=str(OUT / "3_soft_moe.png"), full_page=True)

    step("soft MoE: weights + dominant expert shown", soft)

    def sketch():
        pg.get_by_role("link", name="Face-to-Sketch Generator").click()
        pg.set_input_files("input[type=file]", str(FACE))
        pg.get_by_role("radio", name="Style 2 Heavy dark hatching").click()
        pg.get_by_role("button", name="Generate Sketch").click()
        expect(pg.get_by_alt_text("Generated sketch")).to_be_visible(timeout=15000)
        with pg.expect_download() as d:
            pg.get_by_role("link", name="Download PNG").click()
        name = d.value.suggested_filename
        assert name.startswith("sketch_style_2_") and name.endswith(".png"), name
        pg.get_by_role("radio", name="Style 3 Medium-weight contours").click()  # switching style regenerates
        expect(pg.get_by_text("FS2K Style 3")).to_be_visible(timeout=15000)
        pg.screenshot(path=str(OUT / "4_face_to_sketch.png"), full_page=True)

    step("face-to-sketch: upload, style 2, download, switch to style 3", sketch)

    def bad_file():
        pg.get_by_role("button", name="clear selection").click()
        pg.set_input_files("input[type=file]", {"name": "x.txt", "mimeType": "text/plain", "buffer": b"hello"})
        expect(pg.get_by_text("Only JPEG and PNG images are supported.")).to_be_visible()

    step("client-side validation rejects non-image", bad_file)

    def offline():
        pg.route("**/api/**", lambda r: r.fulfill(status=503, content_type="application/json",
                                                  body='{"detail":"Model task4_generator.onnx is not loaded."}'))
        pg.set_input_files("input[type=file]", str(FACE))
        pg.get_by_role("button", name="Generate Sketch").click()
        expect(pg.get_by_role("alert")).to_contain_text("not loaded")
        pg.screenshot(path=str(OUT / "5_error_state.png"))

    step("backend 503 shown as error alert", offline)
    b.close()
    step("no console errors", lambda: (_ for _ in ()).throw(AssertionError(errors[:3])) if [e for e in errors if "503" not in e] else None)

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} UI steps passed", failed or "")
sys.exit(1 if failed else 0)
