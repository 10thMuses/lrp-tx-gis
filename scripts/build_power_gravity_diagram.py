#!/usr/bin/env python3
"""Build the "power gravity" ring diagram — a schematic (not a literal map)
showing cumulative operating + ERCOT-queue capacity at 15/30/60/100-mile
rings from Caramba North, with GW Ranch and Longfellow/Project Horizon
plotted at their true bearing and distance. Values come from
build_insight_pack.py's ring_analysis, which is computed from the same
sourced EIA-860 / ERCOT-queue point layers used throughout the OM.

Produces a light and a dark variant (for light/dark deck backgrounds).

    python3 scripts/build_power_gravity_diagram.py
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
import caramba_om_data as D  # noqa: E402

OUT_DIR = REPO / "outputs" / "reports" / "om_exhibits"

RED = "#B91C1C"
NAVY = "#0F1B2D"
SLATE = "#475569"
MUTED = "#94A3B8"
LIGHT_LINE = "#CBD5E1"
DARK_LINE = "#2A3A52"


def bearing_and_distance(lon, lat):
    cx, cy = D.CX, D.CY
    dx = (lon - cx) * math.cos(math.radians((lat + cy) / 2))
    dy = (lat - cy)
    ang = math.degrees(math.atan2(dx, dy)) % 360
    dist = D.miles(lon, lat)
    return ang, dist


def draw(dark: bool, out_path: Path):
    import build_insight_pack as IP
    ins = IP.build()

    model = D.build()
    s7 = model["section7"]
    gw = next(a for a in s7["anchors"] if a["id"] == "gw-ranch-pacifico-pecos")
    lf = next(a for a in s7["anchors"] if a["id"] == "project-horizon-poolside-coreweave")
    gw_bearing, gw_dist = bearing_and_distance(gw["lon"], gw["lat"])
    lf_bearing, lf_dist = bearing_and_distance(lf["lon"], lf["lat"])
    gw_edge = ins["distances_edge_to_edge"]["gw_ranch_mi"]
    lf_edge = ins["distances_edge_to_edge"]["longfellow_mi"]

    bg = NAVY if dark else "#FFFFFF"
    fg = "#E7ECF5" if dark else NAVY
    ring_line = DARK_LINE if dark else LIGHT_LINE
    ring_label_bg = "#16202E" if dark else "#F8FAFC"

    fig, ax = plt.subplots(figsize=(7.4, 7.4), dpi=200)
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)

    max_r = 100
    ax.set_xlim(-max_r * 1.08, max_r * 1.08)
    ax.set_ylim(-max_r * 1.08, max_r * 1.08)
    ax.set_aspect("equal")
    ax.axis("off")

    rings = ins["ring_analysis"]
    for row in rings:
        r = row["radius_mi"]
        circ = plt.Circle((0, 0), r, fill=False, edgecolor=ring_line, linewidth=1.3, zorder=1)
        ax.add_patch(circ)

    # legend box, lower-left corner (clear of both site markers and the center)
    legend_x0, legend_y0 = -max_r * 1.05, -max_r * 1.05
    legend_lines = [f"≤ {row['radius_mi']} mi   {row['total_gw']:.1f} GW combined" for row in rings]
    legend_text = "REGIONAL POWER — OPERATING + ERCOT QUEUE\n" + "\n".join(legend_lines)
    ax.text(legend_x0, legend_y0, legend_text, color=fg, fontsize=10.5, fontweight="bold",
            ha="left", va="bottom", zorder=5, linespacing=1.9,
            bbox=dict(boxstyle="round,pad=0.55", fc=ring_label_bg, ec=ring_line, lw=0.9))

    # center marker — Caramba North
    ax.scatter([0], [0], s=170, color=RED, zorder=6, edgecolor=bg, linewidth=1.5)
    ax.text(0, -6.5, "CARAMBA NORTH", color=fg, fontsize=10.5, fontweight="bold",
            ha="center", va="top", zorder=6)

    def plot_site(bearing_deg, dist_mi, label, edge_mi):
        theta = math.radians(bearing_deg)
        x, y = dist_mi * math.sin(theta), dist_mi * math.cos(theta)
        ax.scatter([x], [y], s=110, color=fg, zorder=6, edgecolor=RED, linewidth=2)
        dy = 6 if y >= 0 else -6
        va = "bottom" if y >= 0 else "top"
        ax.text(x, y + dy, f"{label}\n≈{edge_mi} mi", color=fg, fontsize=10.5, fontweight="bold",
                ha="center", va=va, zorder=6, linespacing=1.3)

    plot_site(gw_bearing, gw_dist, "GW RANCH", gw_edge)
    plot_site(lf_bearing, lf_dist, "LONGFELLOW", lf_edge)

    # north arrow
    ax.annotate("", xy=(max_r * 0.98, max_r * 0.98), xytext=(max_r * 0.98, max_r * 0.82),
                arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.6))
    ax.text(max_r * 0.98, max_r * 1.01, "N", color=MUTED, fontsize=10, ha="center", fontweight="bold")

    plt.tight_layout(pad=0.4)
    fig.savefig(out_path, facecolor=bg, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print(f"gravity diagram -> {out_path.relative_to(REPO)}")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    draw(False, OUT_DIR / "exhibit_power_gravity_light.png")
    draw(True, OUT_DIR / "exhibit_power_gravity_dark.png")
