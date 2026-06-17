#!/usr/bin/env python3
"""Render the grid wire markdown into a styled PDF using reportlab.

Lightweight, purpose-built markdown subset matching the wire's structure:
H1/H2/H3 headings, bullet lists (with nested source lines), bold (**...**),
and horizontal rules. Not a general markdown engine.
"""
import re
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, HRFlowable,
)

SRC = sys.argv[1]
OUT = sys.argv[2]

INK = colors.HexColor("#1a1a1a")
MUTED = colors.HexColor("#5b6470")
ACCENT = colors.HexColor("#0f4c5c")
RULE = colors.HexColor("#c9d2d9")

styles = getSampleStyleSheet()

def mk(name, **kw):
    kw.setdefault("parent", styles["Normal"])
    return ParagraphStyle(name, **kw)

s_title = mk("wTitle", fontName="Helvetica-Bold", fontSize=22, leading=26,
             textColor=ACCENT, spaceAfter=2)
s_sub = mk("wSub", fontName="Helvetica", fontSize=9.5, leading=13,
           textColor=MUTED, spaceAfter=6)
s_h2 = mk("wH2", fontName="Helvetica-Bold", fontSize=14, leading=18,
          textColor=ACCENT, spaceBefore=14, spaceAfter=4)
s_h3 = mk("wH3", fontName="Helvetica-Bold", fontSize=10.5, leading=14,
          textColor=INK, spaceBefore=8, spaceAfter=2)
s_body = mk("wBody", fontName="Helvetica", fontSize=9.5, leading=13.5,
            textColor=INK, spaceAfter=5, alignment=TA_LEFT)
s_bullet = mk("wBullet", parent=s_body, leftIndent=12, bulletIndent=2,
              spaceAfter=5)
s_src = mk("wSrc", fontName="Helvetica-Oblique", fontSize=8, leading=10.5,
           textColor=MUTED, leftIndent=12)
s_quote = mk("wQuote", fontName="Helvetica-Oblique", fontSize=8, leading=11,
             textColor=MUTED, leftIndent=10, spaceBefore=2, spaceAfter=6,
             borderColor=RULE, borderWidth=0, leftPadding=6)

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(t):
    t = esc(t)
    # bold
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    # bare URLs -> muted (no scheme in source, so just style domain-y tokens lightly)
    return t

def split_source(text):
    """Split a bullet on the em-dash source attribution."""
    if " — " in text:
        idx = text.rindex(" — ")
        return text[:idx].strip(), text[idx + 3:].strip()
    return text, None

# Page furniture
def on_page(canvas, doc):
    canvas.saveState()
    w, h = letter
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(0.75 * inch, 0.62 * inch, w - 0.75 * inch, 0.62 * inch)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.46 * inch, "Grid Wire — 2026-06-17")
    canvas.drawRightString(w - 0.75 * inch, 0.46 * inch, "Page %d" % doc.page)
    canvas.restoreState()

doc = BaseDocTemplate(
    OUT, pagesize=letter,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.7 * inch, bottomMargin=0.8 * inch,
    title="Grid Wire 2026-06-17",
)
frame = Frame(doc.leftMargin, doc.bottomMargin,
              doc.width, doc.height, id="main")
doc.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=on_page)])

flow = []
with open(SRC) as f:
    lines = f.read().split("\n")

# Buffer paragraph continuation for wrapped bullet lines in the source
i = 0
n = len(lines)
def coalesce(start):
    """Join a logical block that may wrap across source lines until blank,
    heading, list marker, or hr."""
    buf = [lines[start].rstrip()]
    j = start + 1
    while j < n:
        nxt = lines[j]
        if (nxt.strip() == "" or nxt.startswith("#") or nxt.startswith("- ")
                or nxt.startswith("---") or nxt.startswith(">")):
            break
        buf.append(nxt.strip())
        j += 1
    return " ".join(buf), j

first_h1_done = False
while i < n:
    line = lines[i]
    stripped = line.strip()
    if stripped == "":
        i += 1
        continue
    if stripped.startswith("# "):
        flow.append(Paragraph(inline(stripped[2:]), s_title))
        i += 1
        continue
    if stripped.startswith("### "):
        flow.append(Paragraph(inline(stripped[4:]), s_h3))
        i += 1
        continue
    if stripped.startswith("## "):
        flow.append(Spacer(1, 2))
        flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE,
                               spaceBefore=2, spaceAfter=4))
        flow.append(Paragraph(inline(stripped[3:]), s_h2))
        i += 1
        continue
    if stripped.startswith("---"):
        flow.append(HRFlowable(width="100%", thickness=0.6, color=RULE,
                               spaceBefore=4, spaceAfter=4))
        i += 1
        continue
    if stripped.startswith(">"):
        # blockquote: coalesce consecutive ">" lines
        buf = [stripped.lstrip(">").strip()]
        j = i + 1
        while j < n and lines[j].strip().startswith(">"):
            buf.append(lines[j].strip().lstrip(">").strip())
            j += 1
        flow.append(Paragraph(inline(" ".join(buf)), s_quote))
        i = j
        continue
    if stripped.startswith("- "):
        block, j = coalesce(i)
        block = block[2:].strip()  # drop "- "
        body, src = split_source(block)
        flow.append(Paragraph("• " + inline(body), s_bullet))
        if src:
            flow.append(Paragraph("— " + inline(src), s_src))
        i = j
        continue
    # plain paragraph (subtitle under title, or numbered through-lines)
    block, j = coalesce(i)
    style = s_sub if not first_h1_done else s_body
    flow.append(Paragraph(inline(block), style))
    first_h1_done = True
    i = j

doc.build(flow)
print("wrote", OUT)
