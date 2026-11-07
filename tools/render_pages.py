#!/usr/bin/env python3
"""Pre-render a magazine PDF into page images for the flipbook reader.

Usage:
    pip install pymupdf pillow
    python3 tools/render_pages.py "files/Uncle Magazine 2025.pdf" 2025

Writes pages/<slug>/1.webp, 2.webp, ... and pages/<slug>/info.json.
The issue is then readable at reader.html?issue=<slug>.
"""
import io
import json
import os
import shutil
import sys

import pymupdf
from PIL import Image

WIDTH = 1400     # pixels per page; plenty for a full-screen spread on most displays
QUALITY = 80     # WebP quality


def main(pdf_path, slug):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(root, "pages", slug)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    doc = pymupdf.open(pdf_path)
    first = doc[0].rect
    total = 0
    for i, page in enumerate(doc, start=1):
        zoom = WIDTH / page.rect.width
        pix = page.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        path = os.path.join(out, f"{i}.webp")
        img.save(path, "WEBP", quality=QUALITY, method=6)
        size = os.path.getsize(path)
        total += size
        print(f"  page {i}: {img.width}x{img.height}, {size // 1024} KB")

    info = {
        "title": os.path.splitext(os.path.basename(pdf_path))[0],
        "pdf": os.path.relpath(os.path.abspath(pdf_path), root).replace(os.sep, "/"),
        "pages": len(doc),
        "width": first.width,
        "height": first.height,
    }
    with open(os.path.join(out, "info.json"), "w") as f:
        json.dump(info, f, indent=2)
    print(f"{slug}: {len(doc)} pages, {total // 1024} KB total -> reader.html?issue={slug}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
