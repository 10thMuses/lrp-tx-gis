#!/usr/bin/env python3
"""Build a NEW annotated variant of the Section 7 regional pipeline exhibit
that numbers and highlights ALL FIVE labeled projects on the base map
(exhibit_7_1_datacenter-pipeline.jpg), not just the two feature anchors
(GW Ranch, Longfellow) that exhibit_amz_gwranch.jpg / exhibit_longfellow.jpg
already cover individually.

This does NOT touch exhibit_7_1 or the two existing feature exhibits — it
crops from exhibit_7_1 (read-only) and writes a new file. No capacity
figures are invented: every number placed on the image is copied from the
label text already printed on the exhibit_7_1 base map (built from the GIS
point/boundary layers). Label pixel positions were located by visual
inspection of the source raster, same method as build_amz_gwranch_exhibit.py
— re-locate them if exhibit_7_1 is ever recaptured at a different zoom/pan.

    python3 scripts/build_pipeline5_annotated_exhibit.py
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "outputs" / "reports" / "om_exhibits" / "exhibit_7_1_datacenter-pipeline.jpg"
OUT = REPO / "outputs" / "reports" / "om_exhibits" / "exhibit_pipeline5_mapled.jpg"

# Pixel positions in the SOURCE raster (2400x1374). Located by scanning for
# the dark navy label-box border strokes (thin rounded-rect outlines around
# each callout on the base map) rather than eyeballing a downsampled
# preview — see git history for the detection script if these ever need
# re-deriving after exhibit_7_1 is recaptured at a different zoom/pan.
CROP_BOX = (250, 320, 1820, 1090)

CHEVRON_BOX = (364, 366, 1408, 404)
GWRANCH_BOX = (985, 554, 1576, 593)
ALPHA_BOX = (721, 606, 1536, 646)
CARAMBA_BOX = (1085, 713, 1321, 752)
CARAMBA_MARKER = (1205, 773)
LONGFELLOW_BOX = (967, 795, 1732, 835)
HORIZON_ANCHOR_MARKER = (1178, 956)
LAESCALERA_BOX = (942, 1008, 1587, 1048)

# Longfellow's base-map label names a tenant (CoreWeave) that has since
# exited; mask + relabel it tenant-neutral before ringing/numbering it,
# same fix applied to build_amz_gwranch_exhibit.py / build_longfellow_exhibit.py.
LF_LABEL_TEXT = "Longfellow — Project Horizon · Gas Generation Site · 2 GW"

RED = (185, 28, 28, 255)
COPPER = (176, 98, 32, 255)
NAVY = (15, 27, 45, 255)
WHITE = (255, 255, 255, 255)
LABEL_BORDER = (150, 152, 156, 255)
BLACK = (20, 20, 22, 255)

# (box, badge_color, badge_number, badge_offset_x)
PROJECTS = [
    (CHEVRON_BOX, COPPER, "1", -50),
    (GWRANCH_BOX, RED, "2", -50),
    (ALPHA_BOX, COPPER, "3", -50),
    (LONGFELLOW_BOX, RED, "4", -50),
    (LAESCALERA_BOX, COPPER, "5", -50),
]

FONT_PATHS_BOLD = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def font(size):
    for p in FONT_PATHS_BOLD:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def main():
    im = Image.open(SRC).convert("RGB")
    crop = im.crop(CROP_BOX).convert("RGBA")
    ox, oy = CROP_BOX[0], CROP_BOX[1]

    def to_crop(x, y):
        return (x - ox, y - oy)

    overlay = Image.new("RGBA", crop.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    f_num = font(26)

    # Mask + redraw the Longfellow label before anything rings/numbers it
    lx0, ly0 = to_crop(LONGFELLOW_BOX[0] - 3, LONGFELLOW_BOX[1] - 3)
    lx1, ly1 = to_crop(LONGFELLOW_BOX[2] + 3, LONGFELLOW_BOX[3] + 3)
    draw.rounded_rectangle([lx0, ly0, lx1, ly1], radius=9, fill=WHITE, outline=LABEL_BORDER, width=2)
    f_label = font(20)
    lbbox = draw.textbbox((0, 0), LF_LABEL_TEXT, font=f_label)
    lw, lh = lbbox[2] - lbbox[0], lbbox[3] - lbbox[1]
    lcx, lcy = (lx0 + lx1) / 2, (ly0 + ly1) / 2
    draw.text((lcx - lw / 2 - lbbox[0], lcy - lh / 2 - lbbox[1]), LF_LABEL_TEXT, font=f_label, fill=BLACK)

    # Highlight the Caramba North label + marker (subject site — navy, not numbered)
    cx0, cy0 = to_crop(CARAMBA_BOX[0], CARAMBA_BOX[1])
    cx1, cy1 = to_crop(CARAMBA_BOX[2], CARAMBA_BOX[3])
    draw.rounded_rectangle([cx0 - 6, cy0 - 6, cx1 + 6, cy1 + 6], radius=10, outline=NAVY, width=4)
    mx, my = to_crop(*CARAMBA_MARKER)
    draw.ellipse([mx - 16, my - 16, mx + 16, my + 16], outline=NAVY, width=4)

    # Ring the Project Horizon anchor point (belongs to Longfellow / #4)
    hx, hy = to_crop(*HORIZON_ANCHOR_MARKER)
    draw.ellipse([hx - 15, hy - 15, hx + 15, hy + 15], outline=RED, width=4)

    for box, color, num, off in PROJECTS:
        bx0, by0 = to_crop(box[0], box[1])
        bx1, by1 = to_crop(box[2], box[3])
        # outline around the label box
        draw.rounded_rectangle([bx0 - 5, by0 - 5, bx1 + 5, by1 + 5], radius=8, outline=color, width=4)
        # numbered badge to the left of the box
        bcx = bx0 + off
        bcy = (by0 + by1) / 2
        r = 22
        draw.ellipse([bcx - r, bcy - r, bcx + r, bcy + r], fill=color, outline=WHITE, width=3)
        tb = draw.textbbox((0, 0), num, font=f_num)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        draw.text((bcx - tw / 2 - tb[0], bcy - th / 2 - tb[1]), num, font=f_num, fill=WHITE)
        # short tick connecting badge to box
        draw.line([(bcx + r, bcy), (bx0 - 5, bcy)], fill=color, width=3)

    out = Image.alpha_composite(crop, overlay).convert("RGB")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT, quality=92)
    print(f"exhibit -> {OUT.relative_to(REPO)}  ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    main()
