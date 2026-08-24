#!/usr/bin/env python3
"""Annotate the Section 7 exhibit to spotlight the Longfellow / Project Horizon news.

Project Horizon (Poolside + CoreWeave, announced Oct 2025) is tracked in
data/datacenters/dc_anchors.json as project-horizon-poolside-coreweave.
CoreWeave terminated its anchor-tenant lease in Apr 2026; the site is now
being developed by the spun-off Poolside Infrastructure Company, which is
seeking a new anchor tenant. This script crops the existing exhibit_7_1
raster (no live map capture in this sandbox — see
scripts/capture_om_exhibits.py notes) to the Longfellow / Caramba North
area and draws:
  - a highlight ring around the "Longfellow — Project Horizon" map label
  - a "COREWEAVE EXITED — APR 2026" callout badge
  - a dashed line from the Caramba North site marker down to the actual
    Project Horizon anchor point (the mapped dot, not the label — the
    label is offset for legibility), labeled with the straight-line
    distance pulled from caramba_om_data's derived model (tract centroid
    -> anchor point, same method as Section 7 and the GW Ranch / Amazon
    exhibit).

Label and marker pixel positions were located by visual/color inspection
of the source raster (a rendered map screenshot, not a GIS layer) and are
declared as constants below — re-locate them if exhibit_7_1 is ever
recaptured at a different zoom/pan.

    python3 scripts/build_longfellow_exhibit.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import caramba_om_data as D  # noqa: E402

SRC = REPO / "outputs" / "reports" / "om_exhibits" / "exhibit_7_1_datacenter-pipeline.jpg"
OUT = REPO / "outputs" / "reports" / "om_exhibits" / "exhibit_longfellow.jpg"

# Pixel positions in the SOURCE raster (2400x1374), located by inspection.
CROP_BOX = (930, 695, 1810, 1010)
LF_LABEL_BOX = (966, 796, 1733, 835)      # "Longfellow — Project Horizon · Poolside / CoreWeave · 2 GW U/C"
CARAMBA_MARKER = (1202, 771)               # Caramba North site-boundary marker
ANCHOR_DOT = (1193, 946)                   # actual Project Horizon anchor point (mapped dot)
BADGE_CENTER_X = 1540                      # clear desert area right of the CARAMBA NORTH label box

NAVY = (15, 27, 45, 255)
RED = (185, 28, 28, 255)
WHITE = (255, 255, 255, 255)

FONT_PATHS_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def font(size):
    for p in FONT_PATHS_BOLD:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def dashed_line(draw, p1, p2, color, width=5, dash=13, gap=9):
    x1, y1 = p1
    x2, y2 = p2
    dist = math.hypot(x2 - x1, y2 - y1)
    n = int(dist // (dash + gap)) + 1
    for i in range(n):
        s = i * (dash + gap)
        e = min(s + dash, dist)
        if s >= dist:
            break
        t0, t1 = s / dist, e / dist
        draw.line([(x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0),
                   (x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1)], fill=color, width=width)


def main():
    model = D.build()
    anchor = next(a for a in model["section7"]["anchors"] if a["id"] == "project-horizon-poolside-coreweave")
    miles = anchor["miles"]

    im = Image.open(SRC).convert("RGB")
    crop = im.crop(CROP_BOX).convert("RGBA")
    ox, oy = CROP_BOX[0], CROP_BOX[1]

    def to_crop(x, y):
        return (x - ox, y - oy)

    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    f_tag, f_dist = font(23), font(21)

    # --- highlight ring around the Longfellow map label ---------------------
    gx0, gy0 = to_crop(LF_LABEL_BOX[0], LF_LABEL_BOX[1])
    gx1, gy1 = to_crop(LF_LABEL_BOX[2], LF_LABEL_BOX[3])
    gx1 = min(gx1, crop.width - 4)
    pad = 9
    for i in range(5, 0, -1):
        alpha = max(55 - i * 8, 0)
        draw.rounded_rectangle(
            [gx0 - pad - i * 3, gy0 - pad - i * 3, gx1 + pad + i * 3, gy1 + pad + i * 3],
            radius=14, outline=(RED[0], RED[1], RED[2], alpha), width=3)
    draw.rounded_rectangle([gx0 - pad, gy0 - pad, gx1 + pad, gy1 + pad], radius=12, outline=RED, width=4)

    # --- "COREWEAVE EXITED" badge, offset right of the ring's top edge ------
    text = "COREWEAVE EXITED — APR 2026"
    bbox = draw.textbbox((0, 0), text, font=f_tag)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 16, 11
    badge_w, badge_h = tw + pad_x * 2, th + pad_y * 2
    badge_cx, _ = to_crop(BADGE_CENTER_X, 0)
    badge_bottom = (gy0 - pad) - 12
    bx0 = badge_cx - badge_w / 2
    by0 = badge_bottom - badge_h
    draw.rounded_rectangle([bx0, by0, bx0 + badge_w, by0 + badge_h], radius=10, fill=RED)
    draw.text((bx0 + pad_x - bbox[0], by0 + pad_y - bbox[1]), text, font=f_tag, fill=WHITE)
    draw.line([(badge_cx, by0 + badge_h), (badge_cx, gy0 - pad)], fill=RED, width=3)
    draw.polygon([(badge_cx - 6, gy0 - pad - 10), (badge_cx + 6, gy0 - pad - 10), (badge_cx, gy0 - pad)], fill=RED)

    # --- distance line: Caramba marker -> actual Project Horizon anchor -----
    p1 = to_crop(*CARAMBA_MARKER)
    p2 = to_crop(*ANCHOR_DOT)
    dashed_line(draw, p1, p2, NAVY)
    draw.ellipse([p1[0] - 7, p1[1] - 7, p1[0] + 7, p1[1] + 7], fill=NAVY)
    draw.ellipse([p2[0] - 8, p2[1] - 8, p2[0] + 8, p2[1] + 8], outline=RED, width=4)

    label = f"≈ {miles} MI"
    lb = draw.textbbox((0, 0), label, font=f_dist)
    ltw, lth = lb[2] - lb[0], lb[3] - lb[1]
    mid_x, mid_y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    mx, my = mid_x + 38, mid_y - lth / 2 - 7
    draw.rounded_rectangle([mx - 12, my - 7, mx + ltw + 12, my + lth + 11], radius=8,
                            fill=(255, 255, 255, 240), outline=NAVY, width=2)
    draw.text((mx - lb[0], my - lb[1]), label, font=f_dist, fill=NAVY)
    draw.line([(mx - 12, my + lth / 2 + 2), (mid_x, mid_y)], fill=NAVY, width=2)

    out = Image.alpha_composite(crop, overlay).convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, quality=92)
    print(f"exhibit -> {OUT.relative_to(REPO)}  ({out.size[0]}x{out.size[1]})  distance={miles} mi")


if __name__ == "__main__":
    main()
