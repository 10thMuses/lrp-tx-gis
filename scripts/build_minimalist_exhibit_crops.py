#!/usr/bin/env python3
"""Derive two deck-specific crops from the shared, do-not-regenerate exhibit
rasters (exhibit_amz_gwranch.jpg, exhibit_longfellow.jpg) for the Minimalist
Executive deck ONLY. This does not touch or regenerate the canonical exhibit
files or the map/distance logic that produced them (brief §5/§7a) — it just
derives a crop, because both source rasters carry an incidental
"Longfellow ... Poolside / CoreWeave ... 2 GW U/C" label that conflicts with
brief Rule 3 (Longfellow must be infrastructure-first, no tenant mention, no
stated current MW target). Output goes to a build-specific subfolder so
concurrent builds of the other five decks are untouched.

    python3 scripts/build_minimalist_exhibit_crops.py
"""
import os
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "outputs", "reports", "om_exhibits")
OUT_DIR = os.path.join(SRC, "_minimalist")
os.makedirs(OUT_DIR, exist_ok=True)


def crop_gwranch():
    """The GW Ranch exhibit's bottom edge carries an incidental Longfellow/
    CoreWeave label unrelated to the GW Ranch story on this slide. Crop it
    off; everything else (Amazon callout, ring highlight, distance line,
    Caramba North label) sits well above the cut line."""
    im = Image.open(os.path.join(SRC, "exhibit_amz_gwranch.jpg"))
    w, h = im.size  # 1410 x 540
    cropped = im.crop((0, 0, w, int(h * 450 / 540)))
    out = os.path.join(OUT_DIR, "exhibit_amz_gwranch_crop.jpg")
    cropped.save(out, quality=92)
    print(f"wrote {out} {cropped.size}")


def redact_longfellow():
    """The Longfellow exhibit's highlighted map-label callout reads
    'Longfellow — Project Horizon · Poolside / CoreWeave · 2 GW U/C' baked
    into the base map raster, inside the ring highlight itself (not
    croppable without losing the highlight/badge/distance-line). Paint over
    the tenant clause and the stated MW figure, in white, flush inside the
    label box border, leaving 'Longfellow — Project Horizon' and every other
    element (ring, badge, ≈19.3 MI distance line) untouched."""
    im = Image.open(os.path.join(SRC, "exhibit_longfellow.jpg")).convert("RGB")
    draw = ImageDraw.Draw(im)
    # Interior of the white label box, right of "...Horizon", left of the box's
    # right border — measured directly off the 880x315 source raster.
    draw.rectangle((393, 101, 833, 139), fill=(255, 255, 255))
    out = os.path.join(OUT_DIR, "exhibit_longfellow_notenant.jpg")
    im.save(out, quality=92)
    print(f"wrote {out} {im.size}")


if __name__ == "__main__":
    crop_gwranch()
    redact_longfellow()
