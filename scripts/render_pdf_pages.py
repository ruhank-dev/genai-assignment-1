"""Render PDF pages to PNG for visual inspection: python scripts/render_pdf_pages.py report/main.pdf OUT_PREFIX [dpi]"""
import sys

import pymupdf

d = pymupdf.open(sys.argv[1])
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 75
for i, p in enumerate(d):
    p.get_pixmap(dpi=dpi).save(f"{sys.argv[2]}{i + 1}.png")
print("pages", len(d))
