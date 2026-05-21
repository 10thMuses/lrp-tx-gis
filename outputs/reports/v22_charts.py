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

# ---------- Chart 1: Wellbore-record new-drill vs recompletion (Pecos since 2020) ----------
fig, ax = plt.subplots(figsize=(7.5, 2.2))
new_drill = 117
recomp    = 1001
total = new_drill + recomp
nd_pct = 100 * new_drill / total
rc_pct = 100 * recomp / total

ax.barh([0], [nd_pct], color=NEW, label=f"New drilling: {new_drill} ({nd_pct:.0f}%)")
ax.barh([0], [rc_pct], left=[nd_pct], color=RECOMP, label=f"Recompletion / workover: {recomp:,} ({rc_pct:.0f}%)")
ax.text(nd_pct / 2, 0, f"{new_drill}\n({nd_pct:.0f}%)", ha="center", va="center",
        color="white", fontsize=11, fontweight="bold")
ax.text(nd_pct + rc_pct / 2, 0, f"{recomp:,}\n({rc_pct:.0f}%)", ha="center", va="center",
        color="white", fontsize=11, fontweight="bold")

ax.set_xlim(0, 100); ax.set_xticks([])
ax.set_yticks([]); ax.set_yticklabels([])
ax.set_title("Pecos County since 2020 — wellbore-record activity\n"
             f"({total:,} wellbore records with new drilling, completion, or workover events)",
             fontsize=11, color="#1F3864", fontweight="bold", pad=12)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.55), ncol=2, frameon=False, fontsize=10)
for spine in ax.spines.values():
    spine.set_visible(False)
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

# ---------- Chart 4: FracFocus disclosures by ring band around Caramba ----------
labels4 = ["0–2 mi", "2–5 mi", "5–10 mi", "10–20 mi"]
vals4 = [0, 9, 20, 464]         # ring-band counts (not cumulative)
recents = ["—", "2015", "2025", "2026"]
colors4 = ["#A6A6A6"] + [NEW] * 3

fig, ax = plt.subplots(figsize=(7.5, 3.4))
bars = ax.barh(labels4, vals4, color=colors4)
for b, v, rec in zip(bars, vals4, recents):
    lbl = f"  {v}  (most recent: {rec})" if v > 0 else "  0  (none, ever)"
    ax.text(v + 6 if v > 0 else 4, b.get_y() + b.get_height() / 2, lbl,
            va="center", ha="left", fontsize=10, color="#1F3864", fontweight="bold")
ax.set_xlabel("FracFocus disclosures (2011 – present)", fontsize=10)
ax.set_xlim(0, max(vals4) * 1.25)
ax.invert_yaxis()
ax.set_title("Hydraulic-fracturing disclosures by distance from Caramba North\n"
             "(Pecos County, all years on FracFocus)",
             fontsize=11, color="#1F3864", fontweight="bold", pad=12)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_axisbelow(True)
ax.grid(axis="x", linestyle=":", color="#cccccc", linewidth=0.6)
plt.tight_layout()
plt.savefig(OUT / "ch_fracfocus_rings.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print(f"wrote {OUT/'ch_fracfocus_rings.png'}")
