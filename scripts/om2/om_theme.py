#!/usr/bin/env python3
"""Design systems + page shell + PDF renderer for the Caramba North OM set.

Four deck systems (A-D) and two document systems, each with its own type
pairing and palette, sharing one page shell and one PDF pipeline.

Why HTML -> Chromium -> PDF rather than pptx/docx: the whole point of this
pass is typographic control, and Office substitutes fonts silently. Here the
faces are embedded as base64 @font-face, so the PDF is byte-identical
wherever it is opened. The HTML sources ship alongside as the editable form.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO = Path(os.environ.get("LRP_PROJECT_DIR", Path(__file__).resolve().parent.parent.parent))
FONT_DIR = REPO / "scripts" / "om2" / "fonts"
VEC = REPO / "outputs" / "reports" / "om_exhibits" / "vector"

# Page geometry at 96 css px/inch
SLIDE_W, SLIDE_H = 1280, 720          # 13.333 x 7.5 in, 16:9
PAGE_W, PAGE_H = 816, 1056            # 8.5 x 11 in, US Letter portrait


# The shared vector exhibits set their own type in IBM Plex Sans / Mono, so
# EVERY document that inlines one must embed those faces regardless of its own
# pairing — otherwise the exhibit labels silently fall back to Liberation Sans
# and the document ships mixed type.
EXHIBIT_FONTS = ("plexsans", "plexmono")


def font_css(*families):
    """Inline the faces a document uses, plus the ones its exhibits need."""
    out, seen = [], set()
    for fam in tuple(families) + EXHIBIT_FONTS:
        if fam in seen:
            continue
        seen.add(fam)
        p = FONT_DIR / f"{fam}.css"
        if p.exists():
            out.append(p.read_text(encoding="utf-8"))
    return "\n".join(out)


def svg(name, fill_parent=True):
    """Inline a vector exhibit, stripped of fixed width/height so it scales."""
    import re
    p = VEC / f"{name}.svg"
    if not p.exists():
        raise FileNotFoundError(f"exhibit not built: {p}")
    s = p.read_text(encoding="utf-8")
    s = re.sub(r'\s(width|height)="[\d.]+"', "", s, count=2)
    style = "width:100%;height:100%;display:block" if fill_parent else "width:100%;height:auto;display:block"
    return s.replace("<svg ", f'<svg preserveAspectRatio="xMidYMid meet" style="{style}" ', 1)


# ---------------------------------------------------------------------------
# The four deck systems + two document systems.
# Each: fonts (families to embed), display/body/mono stacks, palette.
# ---------------------------------------------------------------------------
INK = dict(ink="#12181F", ink70="#4A545F", ink45="#8A939D",
           ink25="#C5CBD1", ink12="#E7E9EC")
# validated categorical triple (dataviz six checks, light + dark surfaces)
RED, GOLD, BLUE = "#B03A2E", "#C08A10", "#0E6E9C"

SYSTEMS = {
    "institutional": dict(
        label="Institutional",
        fonts=["newsreader", "publicsans", "plexmono"],
        display="Newsreader, Georgia, 'Times New Roman', serif",
        body="'Public Sans', 'Helvetica Neue', Arial, sans-serif",
        mono="'IBM Plex Mono', SFMono-Regular, Consolas, monospace",
        paper="#FBFAF7", rule="#D9D4CB", panel="#F2EEE6",
        accent=RED, second=GOLD, third=BLUE, **INK,
    ),
    "editorial": dict(
        label="Editorial",
        fonts=["instrumentserif", "plexsans", "plexmono"],
        display="'Instrument Serif', Georgia, serif",
        body="'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif",
        mono="'IBM Plex Mono', SFMono-Regular, Consolas, monospace",
        paper="#0E141A", rule="#223040", panel="#16202B",
        ink="#E8EDF2", ink70="#9BA8B6", ink45="#6B7885",
        ink25="#333F4B", ink12="#1C252E",
        accent=RED, second=GOLD, third=BLUE,
    ),
    "technical": dict(
        label="Technical",
        fonts=["plexsans", "plexmono"],
        display="'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif",
        body="'IBM Plex Sans', 'Helvetica Neue', Arial, sans-serif",
        mono="'IBM Plex Mono', SFMono-Regular, Consolas, monospace",
        paper="#F4F6F7", rule="#C9D3D9", panel="#FBFCFC",
        accent=BLUE, second=RED, third=GOLD,
        ink="#12181F", ink70="#4A545F", ink45="#5A6B78",
        ink25="#C9D3D9", ink12="#E2E8EB",
    ),
    "minimal": dict(
        label="Minimal",
        fonts=["archivo", "plexmono"],
        display="Archivo, 'Helvetica Neue', Arial, sans-serif",
        body="Archivo, 'Helvetica Neue', Arial, sans-serif",
        mono="'IBM Plex Mono', SFMono-Regular, Consolas, monospace",
        paper="#FFFFFF", rule="#E3E5E8", panel="#F7F8F9",
        accent=RED, second=GOLD, third=BLUE,
        ink="#0B0D0F", ink70="#5C666F", ink45="#9AA0A6",
        ink25="#D6D9DC", ink12="#EDEFF1",
    ),
}
SYSTEMS["brief_exec"] = dict(SYSTEMS["institutional"], label="Executive Brief")
SYSTEMS["brief_tech"] = dict(SYSTEMS["technical"], label="Technical Snapshot")


BASE_CSS = """
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
a { color: inherit; text-decoration: none; }
h1, h2, h3, p, ul, ol { margin: 0; }
ul { padding-left: 1.1em; }
.page { position: relative; overflow: hidden; page-break-after: always;
        break-after: page; }
.page:last-child { page-break-after: auto; break-after: auto; }
.mono { font-variant-numeric: tabular-nums; }
table { border-collapse: collapse; width: 100%; }
"""


def document(system, pages_html, orientation="landscape", title="Caramba North"):
    """Wrap page divs in a print-ready HTML document."""
    S = SYSTEMS[system]
    w, h = (SLIDE_W, SLIDE_H) if orientation == "landscape" else (PAGE_W, PAGE_H)
    size = "13.333in 7.5in" if orientation == "landscape" else "8.5in 11in"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
{font_css(*S["fonts"])}
{BASE_CSS}
@page {{ size: {size}; margin: 0; }}
body {{ background: {S['paper']}; color: {S['ink']}; font-family: {S['body']};
        font-size: 14px; line-height: 1.5; }}
.page {{ width: {w}px; height: {h}px; background: {S['paper']}; }}
.d {{ font-family: {S['display']}; }}
.m {{ font-family: {S['mono']}; font-variant-numeric: tabular-nums; }}
</style>
</head>
<body>
{pages_html}
</body>
</html>
"""


def render_pdf(html_path, pdf_path, orientation="landscape"):
    """Chromium print-to-PDF with CSS page size honoured."""
    script = REPO / "scripts" / "om2" / "_print.mjs"
    subprocess.run(["node", str(script), str(html_path), str(pdf_path)],
                   check=True, cwd=str(REPO / "scripts" / "om2"))
    return pdf_path
