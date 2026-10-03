"""Browser end-to-end test of the running app (needs: pip install playwright && playwright install chromium).
Drives all four workspaces like an evaluator and stores screenshots in results/app/. Usage: python scripts/ui_test.py [url]"""
import sys
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
OUT = Path("results/app")
OUT.mkdir(parents=True, exist_ok=True)
FACE = Path("src/app/frontend/public/samples/pet_3.jpg")  # any JPEG works for the face workspace smoke test
results: list[tuple[str, bool]] = []


def step(name: str, fn) -> None:
    try:
        fn()
        results.append((name, True))
        print("PASS", name)
    except Exception as e:  # noqa: BLE001
        results.append((name, False))
        print("FAIL", name, str(e)[:400])


with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1440, "height": 1000})
    errors: list[str] = []
    pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    pg.goto(URL)
    sample = lambda n: pg.locator("button[aria-label='clean sample']").nth(n)  # noqa: E731
    def bottom(name):  # scroll the workspace to its end so the error / stroke heat map card is captured
        pg.evaluate("document.querySelector('main').scrollTo(0, 99999)")
        pg.wait_for_timeout(400)
        pg.screenshot(path=str(OUT / name))
        pg.evaluate("document.querySelector('main').scrollTo(0, 0)")

    heat = lambda alt: pg.get_by_alt_text(alt)  # noqa: E731

    def shell():
        expect(pg.get_by_text("Welcome, Ruhan!")).to_be_visible()
        expect(pg.get_by_text("Models ready 7/7").first).to_be_visible(timeout=10000)
        assert pg.url.rstrip("/").endswith("/universal")

    step("Stitch shell: header, status card with live health, redirect to /universal", shell)

    def universal():
        sample(0).click()
        pg.get_by_role("button", name="Gaussian blur").click()
        pg.get_by_role("button", name="Medium").click()
        pg.get_by_role("button", name="Restore Image").click()
        expect(pg.get_by_alt_text("Restored Output")).to_be_visible(timeout=15000)
        expect(heat("absolute error heat map")).to_be_visible()
        expect(pg.get_by_text("k=5, σ=1.5").first).to_be_visible()
        pg.get_by_role("button", name="Compare before / after").click()
        expect(pg.get_by_label("before / after position")).to_be_visible()
        pg.get_by_role("button", name="Compare before / after").click()
        pg.screenshot(path=str(OUT / "1_universal.png"))
        bottom("1_universal_bottom.png")

    step("universal: sample + blur + restore, split view, compare slider, error heat map", universal)

    def hard():
        pg.get_by_role("link", name="Hard-Routed Restoration").first.click()
        sample(1).click()
        pg.get_by_role("button", name="Salt & Pepper").click()
        pg.get_by_role("button", name="High").click()
        pg.get_by_role("button", name="Analyze & Restore").first.click()
        expect(pg.get_by_text("Routed to: task2_specialist_salt.onnx")).to_be_visible(timeout=15000)
        expect(pg.get_by_text("Elected")).to_be_visible()
        expect(heat("absolute error heat map")).to_be_visible()
        pg.get_by_role("button", name="A/B Diff Overlay").click()
        expect(pg.get_by_alt_text("difference overlay")).to_be_visible()
        pg.screenshot(path=str(OUT / "2_hard_routed.png"))
        bottom("2_hard_routed_bottom.png")

    step("hard-routed: salt specialist chosen, probabilities, diff overlay, error heat map", hard)

    def bypass():
        pg.get_by_role("switch", name="Force identity bypass").click()
        pg.get_by_role("button", name="Analyze & Restore").first.click()
        expect(pg.get_by_text("Routed to: Identity Bypass")).to_be_visible(timeout=15000)

    step("hard-routed: forced identity bypass", bypass)

    def soft():
        pg.get_by_role("link", name="Soft Mixture-of-Experts Restoration").first.click()
        sample(2).click()
        pg.get_by_role("button", name="Occlusion").click()
        pg.get_by_role("button", name="High").click()
        pg.get_by_role("button", name="Run Soft MoE Restoration").click()
        expect(pg.get_by_text("DOMINANT EXPERT")).to_be_visible(timeout=15000)
        expect(heat("absolute error heat map")).to_be_visible()
        expect(pg.get_by_alt_text("blended output")).to_be_visible()
        pg.screenshot(path=str(OUT / "3_soft_moe.png"))
        bottom("3_soft_moe_bottom.png")

    step("soft MoE: four weights, dominant expert, blend, error heat map", soft)

    def sketch():
        pg.get_by_role("link", name="Face-to-Sketch Generator").first.click()
        pg.set_input_files("input[type=file]", str(FACE))
        pg.get_by_role("radio", name="Style 2 Heavy Hatching").click()
        pg.get_by_role("button", name="Generate Sketch").click()
        expect(pg.get_by_alt_text("generated sketch")).to_be_visible(timeout=15000)
        expect(heat("stroke intensity heat map")).to_be_visible()
        with pg.expect_download() as d:
            pg.get_by_role("button", name="Download PNG").click()
        name = d.value.suggested_filename
        assert name.startswith("sketch_style_2_") and name.endswith(".png"), name
        pg.get_by_role("radio", name="Style 3 Medium Dynamic").click()  # switching style regenerates
        expect(pg.get_by_text("Style 3", exact=True).first).to_be_visible(timeout=15000)
        pg.screenshot(path=str(OUT / "4_face_to_sketch.png"))
        bottom("4_face_to_sketch_bottom.png")

    step("face-to-sketch: upload, style 2, download, switch to style 3, stroke heat map", sketch)

    def bad_file():
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
        pg.unroute("**/api/**")

    step("backend 503 shown as error banner", offline)

    def theme_and_search():
        pg.get_by_role("button", name="Dark theme").click()
        assert "dark" in (pg.evaluate("document.documentElement.className") or "")
        pg.get_by_role("button", name="Light theme").click()
        pg.get_by_label("Search workspaces").fill("mixture")
        pg.get_by_role("button", name="Soft Mixture-of-Experts Restoration").first.click()
        expect(pg.get_by_text("Soft Gating Distribution")).to_be_visible()
        pg.get_by_role("button", name="System status").click()
        expect(pg.get_by_text("System status")).to_be_visible()

    step("theme toggle, workspace search, status bell", theme_and_search)
    b.close()
    step("no console errors", lambda: (_ for _ in ()).throw(AssertionError(errors[:3])) if [e for e in errors if "503" not in e] else None)

failed = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(failed)}/{len(results)} UI steps passed", failed or "")
sys.exit(1 if failed else 0)
