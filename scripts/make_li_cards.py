#!/usr/bin/env python3
"""Generate attention-grabbing LinkedIn data cards (1200x1200 PNG) for the
grid-wire LinkedIn posts. Dark editorial style, one sharp claim + hero comps.
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1200
BG = (11, 18, 32)          # deep navy-slate
INK = (248, 250, 252)
MUTED = (148, 163, 184)
TEAL = (20, 184, 166)
AMBER = (245, 158, 11)
RULE = (30, 41, 59)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

def f(path, sz):
    return ImageFont.truetype(path, sz)

def wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_kicker(d, x, y, text):
    fk = f(FB, 26)
    d.text((x, y), text, font=fk, fill=TEAL)
    return y + 44

def card(path, kicker, claim, support, stats, footer, punch, accent=TEAL):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    M = 90
    # top accent bar
    d.rectangle([0, 0, W, 12], fill=accent)
    # subtle baseline grid ticks (right edge motif)
    for gy in range(120, H - 120, 60):
        d.line([(W - 40, gy), (W - 28, gy)], fill=RULE, width=2)

    y = 110
    y = draw_kicker(d, M, y, kicker)
    y += 18

    # claim (hero heading)
    fh = f(FB, 74)
    for ln in wrap(d, claim, fh, W - 2 * M):
        d.text((M, y), ln, font=fh, fill=INK)
        y += 86
    y += 14

    # support line
    fs = f(FR, 32)
    for ln in wrap(d, support, fs, W - 2 * M):
        d.text((M, y), ln, font=fs, fill=MUTED)
        y += 45
    y += 30

    # stat blocks
    for value, label, col in stats:
        fv = f(FB, 80)
        d.text((M, y), value, font=fv, fill=col)
        vw = d.textlength(value, font=fv)
        fl = f(FR, 28)
        lx = M + vw + 30
        ly = y + 16
        lab_lines = wrap(d, label, fl, W - M - lx)
        for ln in lab_lines:
            d.text((lx, ly), ln, font=fl, fill=INK)
            ly += 37
        y += max(100, (ly - y) + 18)
    y += 14

    # punch line (flows after stats), with a short accent tick above it
    d.rectangle([M, y, M + 70, y + 8], fill=accent)
    y += 30
    fp = f(FB, 40)
    for ln in wrap(d, punch, fp, W - 2 * M):
        d.text((M, y), ln, font=fp, fill=INK)
        y += 52

    # footer rule + caption
    d.line([(M, H - 95), (W - M, H - 95)], fill=RULE, width=2)
    ff = f(FB, 26)
    d.text((M, H - 70), "GRID WIRE", font=ff, fill=accent)
    fr2 = f(FR, 26)
    d.text((M + d.textlength("GRID WIRE", font=ff) + 18, H - 70),
           footer, font=fr2, fill=MUTED)
    img.save(path)
    print("wrote", path)

# ---- Card 1: fuel cells ----
card(
    "outputs/reports/li-fuelcells-2026-06-18.png",
    "POWER · THE OVERLOOKED AI-POWER TRADE",
    "A fuel cell skips the turbine and the flame.",
    "It doesn't burn gas — it pulls electrons off the same pipeline molecule by "
    "chemical reaction. So it dodges two bottlenecks at once. Time to first power:",
    [
        ("90 days", "on-site fuel cell — and ~60% efficient", TEAL),
        ("18–24 mo", "simple-cycle gas peaker — the fast workaround (burns ~55% more gas)", INK),
        ("5–7 yr", "combined-cycle turbine — the efficient one, backlogged", AMBER),
    ],
    "2026-06-18",
    "Bloom × Oracle 2.8 GW. Brookfield $5B. The capital already moved.",
    accent=TEAL,
)

# ---- Card 2: residual-value guarantee ----
card(
    "outputs/reports/li-rvg-2026-06-18.png",
    "AI INFRASTRUCTURE · CREDIT",
    "$29.5B financed. The risk is in the footnote.",
    "An A+ rating on an ~8–10% equity cushion required one thing — a guarantee "
    "that outlives the hardware it covers:",
    [
        ("16 yr", "Meta's residual-value guarantee on the Hyperion data center", AMBER),
        ("3–5 yr", "useful life of the GPUs inside it — the gap is the hidden leverage", TEAL),
    ],
    "2026-06-18",
    "The whole sector is copying the template. The guarantee is leverage no balance sheet shows.",
    accent=AMBER,
)
