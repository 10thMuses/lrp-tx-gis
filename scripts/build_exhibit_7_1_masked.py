#!/usr/bin/env python3
"""Produce a tenant-neutral copy of the full Section 7 base map.

exhibit_7_1_datacenter-pipeline.jpg carries a baked-in label reading
"Longfellow — Project Horizon · Poolside / CoreWeave · 2 GW U/C" — CoreWeave
has since exited as anchor tenant, and OM/marketing materials are not to
surface tenant identity or tenant-change history for this site (framing is
on existing/planned power infrastructure instead, see
docs/redesign_content_brief.md §0 rule 3).

The two feature-anchor exhibits (build_amz_gwranch_exhibit.py,
build_longfellow_exhibit.py) and the map-led 5-project exhibit
(build_pipeline5_annotated_exhibit.py) already crop this label out of their
own frame and redraw it. This script does the same mask-and-relabel for
decks that embed the FULL, uncropped exhibit_7_1 raster directly (e.g. the
Institutional deck's Exhibit 7.1 slide) — it does NOT modify
exhibit_7_1_datacenter-pipeline.jpg itself (the pre-existing
Caramba-North-OM-PostNDA.* deck references that file directly and is left
as-is); it writes a separate exhibit_7_1_masked.jpg for new builds to use
in its place wherever the full map is shown uncropped.

    python3 scripts/build_exhibit_7_1_masked.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "outputs" / "reports" / "om_exhibits" / "exhibit_7_1_datacenter-pipeline.jpg"
OUT = REPO / "outputs" / "reports" / "om_exhibits" / "exhibit_7_1_masked.jpg"

LF_LABEL_MASK_BOX = (963, 793, 1736, 838)  # same box used by the feature/map-led exhibit scripts
LF_LABEL_TEXT = "Longfellow — Project Horizon · Gas Generation Site · 2 GW"

WHITE = (255, 255, 255, 255)
LABEL_BORDER = (150, 152, 156, 255)
BLACK = (20, 20, 22, 255)

FONT_PATHS_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def font(size):
    for p in FONT_PATHS_BOLD:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def main():
    im = Image.open(SRC).convert("RGBA")
    draw = ImageDraw.Draw(im)
    x0, y0, x1, y1 = LF_LABEL_MASK_BOX
    draw.rounded_rectangle([x0, y0, x1, y1], radius=9, fill=WHITE, outline=LABEL_BORDER, width=2)
    f = font(20)
    bbox = draw.textbbox((0, 0), LF_LABEL_TEXT, font=f)
    lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    draw.text((cx - lw / 2 - bbox[0], cy - lh / 2 - bbox[1]), LF_LABEL_TEXT, font=f, fill=BLACK)
    im.convert("RGB").save(OUT, quality=92)
    print(f"exhibit -> {OUT.relative_to(REPO)}  ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    main()
