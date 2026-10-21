#!/usr/bin/env python3
"""Chart generator for the Energy + AI Infrastructure Deal-Terms Compendium.

Palette: NAVY #16213e, GOLD #b08d57, TEAL #2f6f6f. DejaVu Sans.
Outputs PNGs into ./assets/ for embedding in deals3.html.

All figures are disclosed or derived-from-disclosed (per deals3.html sources);
no estimates. "Derived" series are flagged in the document captions.
"""
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY = "#16213e"
GOLD = "#b08d57"
TEAL = "#2f6f6f"
INK = "#1b1b1b"
MUTE = "#6b6b6b"
GRID = "#d9d9d9"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "text.parse_math": False,
    "axes.edgecolor": MUTE,
    "axes.linewidth": 0.8,
    "savefig.dpi": 200,
    "figure.dpi": 200,
})

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(exist_ok=True)


def _style(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(length=0)
    ax.set_axisbelow(True)


def _save(fig, name):
    fig.tight_layout()
    out = ASSETS / name
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# DATA  (see deals3.html source notes)
# ---------------------------------------------------------------------------

# c2 — annual rent per MW-year ($M/MW-yr); IT basis unless marked gross
C2 = [
    ("Galaxy–CoreWeave (IT)", 2.26),
    ("TeraWulf Abernathy (IT)", 2.26),
    ("Cipher BL exp. (IT)", 2.13),
    ("Applied Digital (IT)", 1.87),
    ("Hut 8 Beacon Pt (IT)", 1.86),
    ("TeraWulf Mariner (IT)", 1.85),
    ("Cipher Barber Lake (IT)", 1.79),
    ("Cipher–AWS (gross)", 1.22),
]

# c5 — landlord contracted-revenue backlog ($B), Q1-Q2 2026
C5 = [
    ("Applied Digital", 36.0),
    ("Hut 8", 16.8),
    ("Galaxy", 15.0),
    ("TeraWulf", 12.8),
    ("Cipher", 11.4),
    ("Core Scientific", 10.2),
]

# c1 — capacity cost per kW across the stack ($/kW)
C1 = [
    ("Gas fleet — NRG/LS Power", 923),
    ("Gas CCGT — Talen", 1319),
    ("Nuclear restart — Palisades", 1900),
    ("Geothermal — Fervo Ph2", 5500),
    ("SMR FOAK — TerraPower", 11600),
    ("Nuclear new-build — Vogtle", 16500),
]


def c2():
    labels = [d[0] for d in C2]
    vals = [d[1] for d in C2]
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    bars = ax.barh(labels, vals, color=TEAL, height=0.66)
    bars[-1].set_color(GOLD)  # gross outlier highlighted
    hi = max(vals)
    for b, v in zip(bars, vals):
        ax.text(v + hi * 0.012, b.get_y() + b.get_height() / 2,
                f"${v:.2f}M", va="center", ha="left", fontsize=9.5, color=INK)
    ax.invert_yaxis()
    ax.axvspan(1.22, 2.26, color=GOLD, alpha=0.08)
    ax.set_xlabel("Annual rent per MW-year ($M / MW-yr)", color=MUTE, fontsize=10)
    ax.set_xlim(0, hi * 1.16)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    _style(ax)
    _save(fig, "c2_per_mw_yr.png")


def c5():
    labels = [d[0] for d in C5]
    vals = [d[1] for d in C5]
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    bars = ax.bar(labels, vals, color=NAVY, width=0.64)
    bars[0].set_color(GOLD)
    hi = max(vals)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + hi * 0.012,
                f"${v:.1f}B", ha="center", va="bottom", fontsize=9.3, color=INK)
    ax.set_ylabel("Contracted-revenue backlog ($B)", color=MUTE, fontsize=10)
    ax.set_ylim(0, hi * 1.16)
    ax.tick_params(axis="x", labelsize=8.5)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    _style(ax)
    _save(fig, "c5_backlog.png")


def c1():
    labels = [d[0] for d in C1]
    vals = [d[1] for d in C1]
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    bars = ax.barh(labels, vals, color=NAVY, height=0.64)
    bars[-1].set_color(GOLD)   # new-build
    bars[0].set_color(TEAL)    # cheapest
    bars[1].set_color(TEAL)
    hi = max(vals)
    for b, v in zip(bars, vals):
        ax.text(v + hi * 0.012, b.get_y() + b.get_height() / 2,
                f"${v:,.0f}/kW", va="center", ha="left", fontsize=9.3, color=INK)
    ax.invert_yaxis()
    ax.set_xlabel("Capacity cost per kW installed ($/kW)", color=MUTE, fontsize=10)
    ax.set_xlim(0, hi * 1.20)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    _style(ax)
    _save(fig, "c1_per_mw.png")


if __name__ == "__main__":
    c2()
    c5()
    c1()
    print("charts done")
