#!/usr/bin/env python3
"""Annotate the Section 7 exhibit to spotlight the Amazon / GW Ranch news.

Amazon disclosed ownership of the GW Ranch site (Aug 2026) — previously
tracked in data/datacenters/dc_anchors.json as a Pacifico Energy project.
This script crops the existing exhibit_7_1 raster (no live map capture in
this sandbox — see scripts/capture_om_exhibits.py notes) to the GW Ranch /
Caramba North area and draws:
  - a highlight ring around the GW Ranch label
  - an "AMAZON — ACQUIRED" callout
  - a dashed line to the Caramba North site marker, labeled with the
    straight-line distance pulled from caramba_om_data's derived model
    (tract centroid -> GW Ranch anchor point, same method as Section 7).

Label pixel positions were located by visual inspection of the source
raster (a rendered map screenshot, not a GIS layer) and are declared as
constants below — re-locate them if exhibit_7_1 is ever recaptured at a
different zoom/pan.

    python3 scripts/build_amz_gwranch_exhibit.py
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
OUT = REPO / "outputs" / "reports" / "om_exhibits" / "exhibit_amz_gwranch.jpg"

# Pixel positions in the SOURCE raster (2400x1374), located by inspection.
# Widened vs. the initial cut to keep the GW Ranch / Chevron / Longfellow
# label boxes fully inside the frame (no mid-word clipping at the edges).
CROP_BOX = (330, 330, 1740, 870)
GW_LABEL_BOX = (895, 553, 1405, 600)     # "GW Ranch — Pacifico Energy · 7.65 GW permitted"
CARAMBA_MARKER = (1202, 772)              # Caramba North site-boundary marker

# This crop also catches the base map's Longfellow label lower in frame,
# which names a tenant (CoreWeave) that has since exited — mask + relabel
# it the same way build_longfellow_exhibit.py does, so every deck/doc that
# uses this shared exhibit stays compliant without a per-build workaround.
LF_LABEL_MASK_BOX = (963, 793, 1736, 838)
LF_LABEL_TEXT = "Longfellow — Project Horizon · Gas Generation Site · 2 GW"

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
    miles = ins["distances_edge_to_edge"]["gw_ranch_mi"]  # edge-to-edge: tract boundary -> site

    im = Image.open(SRC).convert("RGB")
    crop = im.crop(CROP_BOX).convert("RGBA")
    ox, oy = CROP_BOX[0], CROP_BOX[1]

    def to_crop(x, y):
        return (x - ox, y - oy)

    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    f_tag, f_dist = font(27), font(23)

    # --- mask the baked-in Longfellow label (names an exited tenant) that --
    # --- falls inside this crop, and redraw it tenant-neutral --------------
    lf_x0, lf_y0 = to_crop(LF_LABEL_MASK_BOX[0], LF_LABEL_MASK_BOX[1])
    lf_x1, lf_y1 = to_crop(LF_LABEL_MASK_BOX[2], LF_LABEL_MASK_BOX[3])
    if lf_x1 > 0 and lf_y1 > 0 and lf_x0 < crop.width and lf_y0 < crop.height:
        draw.rounded_rectangle([lf_x0, lf_y0, lf_x1, lf_y1], radius=9, fill=WHITE,
                                outline=LABEL_BORDER, width=2)
        f_label = font(20)
        lbbox = draw.textbbox((0, 0), LF_LABEL_TEXT, font=f_label)
        lw, lh = lbbox[2] - lbbox[0], lbbox[3] - lbbox[1]
        lcx, lcy = (lf_x0 + lf_x1) / 2, (lf_y0 + lf_y1) / 2
        draw.text((lcx - lw / 2 - lbbox[0], lcy - lh / 2 - lbbox[1]), LF_LABEL_TEXT, font=f_label, fill=BLACK)

    gx0, gy0 = to_crop(GW_LABEL_BOX[0], GW_LABEL_BOX[1])
    gx1, gy1 = to_crop(GW_LABEL_BOX[2], GW_LABEL_BOX[3])
    gx1 = min(gx1, crop.width - 4)
    pad = 9

    for i in range(5, 0, -1):
        alpha = max(55 - i * 8, 0)
        draw.rounded_rectangle(
            [gx0 - pad - i * 3, gy0 - pad - i * 3, gx1 + pad + i * 3, gy1 + pad + i * 3],
            radius=14, outline=(RED[0], RED[1], RED[2], alpha), width=3)
    draw.rounded_rectangle([gx0 - pad, gy0 - pad, gx1 + pad, gy1 + pad], radius=12, outline=RED, width=4)

    text = "AMAZON — ACQUIRED AUG 2026"
    bbox = draw.textbbox((0, 0), text, font=f_tag)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 20, 13
    badge_w, badge_h = tw + pad_x * 2, th + pad_y * 2
    badge_cx = (gx0 + gx1) / 2 - 60
    badge_bottom = gy0 - 50
    bx0 = badge_cx - badge_w / 2
    by0 = badge_bottom - badge_h
    draw.rounded_rectangle([bx0, by0, bx0 + badge_w, by0 + badge_h], radius=10, fill=RED)
    draw.text((bx0 + pad_x - bbox[0], by0 + pad_y - bbox[1]), text, font=f_tag, fill=WHITE)
    draw.line([(badge_cx, by0 + badge_h), (badge_cx, gy0 - pad)], fill=RED, width=3)
    draw.polygon([(badge_cx - 6, gy0 - pad - 10), (badge_cx + 6, gy0 - pad - 10), (badge_cx, gy0 - pad)], fill=RED)

    p1 = (badge_cx + 90, gy1 + pad)
    p2 = to_crop(*CARAMBA_MARKER)
    dashed_line(draw, p1, p2, NAVY)
    draw.ellipse([p2[0] - 9, p2[1] - 9, p2[0] + 9, p2[1] + 9], outline=NAVY, width=4)
    draw.ellipse([p1[0] - 7, p1[1] - 7, p1[0] + 7, p1[1] + 7], fill=RED)

    label = f"≈ {miles} MI"
    lb = draw.textbbox((0, 0), label, font=f_dist)
    ltw, lth = lb[2] - lb[0], lb[3] - lb[1]
    mx, my = (p1[0] + p2[0]) / 2 + 45, (p1[1] + p2[1]) / 2 - 6
    draw.rounded_rectangle([mx - 12, my - 10, mx + ltw + 12, my + lth + 14], radius=8,
                            fill=(255, 255, 255, 240), outline=NAVY, width=2)
    draw.text((mx - lb[0], my - lb[1]), label, font=f_dist, fill=NAVY)
    draw.line([(mx - 12, my + lth / 2 + 2), ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)], fill=NAVY, width=2)

    out = Image.alpha_composite(crop, overlay).convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, quality=92)
    print(f"exhibit -> {OUT.relative_to(REPO)}  ({out.size[0]}x{out.size[1]})  distance={miles} mi")


if __name__ == "__main__":
    main()
