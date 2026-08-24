#!/usr/bin/env python3
"""Annotate the Section 7 exhibit to spotlight the Longfellow / Project Horizon news.

Project Horizon (announced Oct 2025) is tracked in
data/datacenters/dc_anchors.json as project-horizon-poolside-coreweave.
Per instruction, OM/marketing materials do not surface tenant identity or
tenant-change history for this site — the narrative is framed entirely
around existing and planned power infrastructure (on-site gas generation,
ERCOT/TCEQ filings). This script crops the existing exhibit_7_1 raster (no
live map capture in this sandbox — see scripts/capture_om_exhibits.py
notes) to the Longfellow / Caramba North area and draws:
  - a solid mask over the base map's baked-in "Longfellow — Project
    Horizon · Poolside / CoreWeave · 2 GW U/C" label (which names a
    tenant that has since exited) and a redrawn, tenant-neutral label in
    the same visual style
  - a highlight ring around that redrawn label
  - an "ON-SITE GAS GENERATION PLANNED" callout badge
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
LF_LABEL_BOX = (966, 796, 1733, 835)      # visible white label pill (interior)
LF_LABEL_MASK_BOX = (963, 793, 1736, 838)  # full label pill incl. border — masked + relabeled
LF_LABEL_TEXT = "Longfellow — Project Horizon · Gas Generation Site · 2 GW"
CARAMBA_MARKER = (1202, 771)               # Caramba North site-boundary marker
ANCHOR_DOT = (1193, 946)                   # actual Project Horizon anchor point (mapped dot)
BADGE_CENTER_X = 1540                      # clear desert area right of the CARAMBA NORTH label box

NAVY = (15, 27, 45, 255)
RED = (185, 28, 28, 255)
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
    import build_insight_pack as IP
    ins = IP.build()
    miles = ins["distances_edge_to_edge"]["longfellow_mi"]  # edge-to-edge: tract boundary -> site

    im = Image.open(SRC).convert("RGB")
    crop = im.crop(CROP_BOX).convert("RGBA")
    ox, oy = CROP_BOX[0], CROP_BOX[1]

    def to_crop(x, y):
        return (x - ox, y - oy)

    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    f_tag, f_dist = font(23), font(21)

    # --- mask the baked-in base-map label (names an exited tenant) and ------
    # --- redraw it tenant-neutral, matching the original pill style ---------
    mx0, my0 = to_crop(LF_LABEL_MASK_BOX[0], LF_LABEL_MASK_BOX[1])
    mx1, my1 = to_crop(LF_LABEL_MASK_BOX[2], LF_LABEL_MASK_BOX[3])
    draw.rounded_rectangle([mx0, my0, mx1, my1], radius=9, fill=WHITE, outline=LABEL_BORDER, width=2)
    f_label = font(20)
    lbbox = draw.textbbox((0, 0), LF_LABEL_TEXT, font=f_label)
    lw, lh = lbbox[2] - lbbox[0], lbbox[3] - lbbox[1]
    lcx, lcy = (mx0 + mx1) / 2, (my0 + my1) / 2
    draw.text((lcx - lw / 2 - lbbox[0], lcy - lh / 2 - lbbox[1]), LF_LABEL_TEXT, font=f_label, fill=BLACK)

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

    # --- "ON-SITE GAS GENERATION" badge, offset right of the ring's top edge --
    text = "ON-SITE GAS GENERATION PLANNED"
    bbox = draw.textbbox((0, 0), text, font=f_tag)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 16, 11
    badge_w, badge_h = tw + pad_x * 2, th + pad_y * 2
    badge_cx, _ = to_crop(BADGE_CENTER_X, 0)
    badge_bottom = (gy0 - pad) - 12
    bx0 = badge_cx - badge_w / 2
    by0 = badge_bottom - badge_h
    draw.rounded_rectangle([bx0, by0, bx0 + badge_w, by0 + badge_h], radius=10, fill=NAVY)
    draw.text((bx0 + pad_x - bbox[0], by0 + pad_y - bbox[1]), text, font=f_tag, fill=WHITE)
    draw.line([(badge_cx, by0 + badge_h), (badge_cx, gy0 - pad)], fill=NAVY, width=3)
    draw.polygon([(badge_cx - 6, gy0 - pad - 10), (badge_cx + 6, gy0 - pad - 10), (badge_cx, gy0 - pad)], fill=NAVY)

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
