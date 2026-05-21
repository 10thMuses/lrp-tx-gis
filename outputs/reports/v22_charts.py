#!/usr/bin/env python3
"""Generate charts for v22 memo restructure."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pathlib import Path

OUT = Path("/home/andreahimmel/lrp-tx-gis/outputs/reports/charts")
OUT.mkdir(parents=True, exist_ok=True)

# Color palette to match Word/PDF: navy + blue + green + light-green
NEW = "#2E74B5"     # blue
RECOMP = "#548235"  # green
GREY = "#A6A6A6"

# ---------- Chart 1: Permit vs Wellbore ratio of new-drill vs recompletion ----------
fig, ax = plt.subplots(figsize=(7.5, 3.6))
labels = ["W-1 permits filed\n(intent)", "Wellbore records updated\n(actual activity)"]
new_drill = [478, 117]
recomp    = [405, 1001]
totals    = [a + b for a, b in zip(new_drill, recomp)]
nd_pct = [100 * a / t for a, t in zip(new_drill, totals)]
rc_pct = [100 * a / t for a, t in zip(recomp,    totals)]

import numpy as np
x = np.arange(len(labels))
ax.bar(x, nd_pct, color=NEW, label=f"New drilling")
ax.bar(x, rc_pct, bottom=nd_pct, color=RECOMP, label=f"Recompletion / workover")

# value labels
for i, (n, r, t) in enumerate(zip(new_drill, recomp, totals)):
    ax.text(i, nd_pct[i] / 2, f"{n}\n({nd_pct[i]:.0f}%)", ha="center", va="center",
            color="white", fontsize=10, fontweight="bold")
    ax.text(i, nd_pct[i] + rc_pct[i] / 2, f"{r}\n({rc_pct[i]:.0f}%)", ha="center", va="center",
            color="white", fontsize=10, fontweight="bold")
    ax.text(i, 102, f"n = {t}", ha="center", va="bottom", fontsize=9, color="#404040")

ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
ax.set_ylabel("Share of activity (%)", fontsize=10)
ax.set_ylim(0, 110)
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_title("Pecos County since 2020: permit intent vs. actual wellbore activity",
             fontsize=11, color="#1F3864", fontweight="bold", pad=14)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.30), ncol=2, frameon=False, fontsize=10)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis="y", linestyle=":", color="#cccccc", linewidth=0.6)
plt.tight_layout()
plt.savefig(OUT / "ch_recomp_ratio.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print(f"wrote {OUT/'ch_recomp_ratio.png'}")

# ---------- Chart 2: Spud-decade distribution of 291 within-10-mi wellbores ----------
decades = ["1960s", "1970s", "1980s", "1990s", "2000s", "2010s", "2020s"]
counts  = [29, 57, 122, 20, 42, 18, 3]

fig, ax = plt.subplots(figsize=(7.5, 3.6))
colors = [GREY if d != "1980s" else NEW for d in decades]
bars = ax.bar(decades, counts, color=colors)
for b, c in zip(bars, counts):
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, str(c),
            ha="center", va="bottom", fontsize=10, color="#1F3864", fontweight="bold")

ax.set_ylabel("Wellbores", fontsize=10)
ax.set_xlabel("Spud decade", fontsize=10)
ax.set_ylim(0, max(counts) * 1.18)
ax.set_title("291 non-plugged wellbores within 10 mi of Caramba North — spud decade",
             fontsize=11, color="#1F3864", fontweight="bold", pad=14)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis="y", linestyle=":", color="#cccccc", linewidth=0.6)
plt.tight_layout()
plt.savefig(OUT / "ch_spud_decade.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print(f"wrote {OUT/'ch_spud_decade.png'}")

# ---------- Chart 3: Production status of 291 within-10-mi wellbores ----------
labels3 = ["Marginal or\nend-of-life", "Still producing\nabove threshold"]
vals3   = [241, 50]
colors3 = ["#A6A6A6", NEW]
fig, ax = plt.subplots(figsize=(5.6, 3.2))
bars = ax.barh(labels3, vals3, color=colors3)
for b, v in zip(bars, vals3):
    pct = 100 * v / sum(vals3)
    ax.text(v + 4, b.get_y() + b.get_height() / 2, f"{v}  ({pct:.0f}%)",
            va="center", fontsize=10, color="#1F3864", fontweight="bold")
ax.set_xlim(0, max(vals3) * 1.25)
ax.set_xlabel("Wellbores", fontsize=10)
ax.set_title("Production status of 291 non-plugged wellbores within 10 mi",
             fontsize=11, color="#1F3864", fontweight="bold", pad=14)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis="x", linestyle=":", color="#cccccc", linewidth=0.6)
plt.tight_layout()
plt.savefig(OUT / "ch_status_mix.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print(f"wrote {OUT/'ch_status_mix.png'}")
