#!/usr/bin/env python3
"""Render a Grid Wire markdown issue to branded HTML + PDF.

Grid Wire is LRP's weekly Texas energy-intelligence product. This renderer is
deliberately self-contained and reusable across issues:

    python3 outputs/grid-wire/render_grid_wire.py outputs/grid-wire/2026-06-15-grid-wire.md

It converts the markdown (tables, footnotes, attr_list, toc) to a print-ready,
LRP-styled HTML, then renders a PDF via WeasyPrint. Fonts (Jost masthead / Inter
body) are provisioned to ~/.fonts on demand — never committed to the repo, per
the bootstrap convention. Font download and PDF render are both non-fatal: the
HTML always lands, and CSS falls back to a clean system stack if Jost/Inter are
unavailable.

Atomic in-place writes (os.replace) per OPERATING.md §3 rule 4.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import urllib.request

import markdown

# Variable TTFs from Google Fonts' GitHub mirror (OFL). Mirrors the bootstrap
# "fonts for Grid Wire PDFs" step — installed to ~/.fonts, not the repo. Saved
# under bracket-free names so the file:// URLs in @font-face stay clean.
FONT_BASE = "https://raw.githubusercontent.com/google/fonts/main/ofl"
FONT_FILES = {
    "GW-Jost.ttf":  f"{FONT_BASE}/jost/Jost%5Bwght%5D.ttf",
    "GW-Inter.ttf": f"{FONT_BASE}/inter/Inter%5Bopsz%2Cwght%5D.ttf",
}

CSS = """
@page {
  size: Letter;
  margin: 18mm 16mm 16mm 16mm;
  @bottom-left  { content: "Grid Wire · Land Resource Partners"; font-family: 'Inter', sans-serif; font-size: 7.5pt; color: #94a3b8; }
  @bottom-right { content: "p. " counter(page) " / " counter(pages); font-family: 'Inter', sans-serif; font-size: 7.5pt; color: #94a3b8; }
}
* { box-sizing: border-box; }
html { -weasy-hyphens: none; }
body {
  font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 9.6pt; line-height: 1.46; color: #0f172a; margin: 0;
}
.masthead { border-bottom: 2.5px solid #0f172a; padding-bottom: 8px; margin-bottom: 14px; }
.masthead .brand {
  font-family: 'Jost', sans-serif; font-weight: 700; letter-spacing: 0.16em;
  text-transform: uppercase; font-size: 15pt; color: #0f172a; margin: 0;
}
.masthead .sub {
  font-family: 'Jost', sans-serif; font-weight: 500; letter-spacing: 0.05em;
  font-size: 8pt; text-transform: uppercase; color: #64748b; margin: 3px 0 0 0;
}
h1 {
  font-family: 'Jost', sans-serif; font-weight: 700; font-size: 17pt;
  line-height: 1.12; color: #0f172a; margin: 2px 0 2px 0;
}
h2 {
  font-family: 'Jost', sans-serif; font-weight: 600; font-size: 12.5pt;
  color: #0f172a; margin: 17px 0 5px 0; padding-bottom: 3px;
  border-bottom: 1px solid #cbd5e1; -weasy-bookmark-level: 1;
}
h3 {
  font-family: 'Jost', sans-serif; font-weight: 600; font-size: 10.4pt;
  color: #1e293b; margin: 11px 0 3px 0;
}
p { margin: 4px 0; }
a { color: #1d4ed8; text-decoration: none; }
strong { font-weight: 600; color: #0f172a; }
em { color: #334155; }
ul, ol { margin: 4px 0 4px 0; padding-left: 17px; }
li { margin: 2px 0; }
hr { border: none; border-top: 1px solid #e2e8f0; margin: 12px 0; }
blockquote {
  margin: 8px 0; padding: 6px 12px; border-left: 3px solid #0f172a;
  background: #f8fafc; color: #1e293b; font-size: 9.4pt;
}
table {
  border-collapse: collapse; width: 100%; margin: 7px 0; font-size: 8.4pt;
  -weasy-table-layout: fixed;
}
th {
  background: #0f172a; color: #fff; text-align: left; padding: 4px 7px;
  font-family: 'Jost', sans-serif; font-weight: 500; font-size: 8pt;
  letter-spacing: 0.02em; vertical-align: top;
}
td { padding: 4px 7px; border-bottom: 1px solid #e2e8f0; vertical-align: top; }
tr:nth-child(even) td { background: #f8fafc; }
code {
  font-family: 'SFMono-Regular', Consolas, monospace; font-size: 8pt;
  background: #f1f5f9; padding: 0.5px 3px; border-radius: 2px;
}
.dek { font-size: 10pt; color: #475569; margin: 4px 0 2px 0; }
h2, h3 { -weasy-bookmark-state: open; }
table, blockquote, h2 { page-break-inside: avoid; }
h2, h3 { page-break-after: avoid; }
"""

FONTFACE_TMPL = """
@font-face {{ font-family: 'Jost';  src: url('file://{d}/GW-Jost.ttf');  font-weight: 100 900; }}
@font-face {{ font-family: 'Inter'; src: url('file://{d}/GW-Inter.ttf'); font-weight: 100 900; }}
"""


def ensure_fonts():
    """Download Jost/Inter to ~/.fonts if missing. Returns dir or None."""
    fdir = os.path.expanduser("~/.fonts")
    os.makedirs(fdir, exist_ok=True)
    ok = True
    for name, url in FONT_FILES.items():
        dest = os.path.join(fdir, name)
        if os.path.exists(dest) and os.path.getsize(dest) > 1000:
            continue
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "lrp-grid-wire"})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = r.read()
            tmp = dest + ".tmp"
            with open(tmp, "wb") as f:
                f.write(data)
            os.replace(tmp, dest)
        except Exception as e:  # noqa: BLE001 — non-fatal, fall back to system fonts
            print(f"  font fetch failed ({name}): {e}", file=sys.stderr)
            ok = False
    if shutil.which("fc-cache"):
        subprocess.run(["fc-cache", "-f", fdir], capture_output=True)
    return fdir if ok else None


def atomic_write(path, text):
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    md_path = sys.argv[1]
    stem = os.path.splitext(md_path)[0]
    html_path = sys.argv[2] if len(sys.argv) > 2 else stem + ".html"
    pdf_path = stem + ".pdf"

    with open(md_path, encoding="utf-8") as f:
        md_text = f.read()

    # Strip an optional leading YAML-ish front matter line set if present.
    body_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "attr_list", "sane_lists",
                    "footnotes", "toc", "md_in_html"],
        output_format="html5",
    )

    fdir = ensure_fonts()
    fontface = FONTFACE_TMPL.format(d=fdir) if fdir else ""

    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Grid Wire</title>
<style>{fontface}{CSS}</style></head>
<body>
<div class="masthead">
  <p class="brand">Grid&nbsp;Wire</p>
  <p class="sub">Land Resource Partners · Texas Energy &amp; AI-Infrastructure Intelligence</p>
</div>
{body_html}
</body></html>"""

    atomic_write(html_path, doc)
    print(f"wrote {html_path}  ({len(doc):,} bytes)")

    try:
        from weasyprint import HTML
        d = os.path.dirname(os.path.abspath(pdf_path))
        fd, tmp = tempfile.mkstemp(dir=d, suffix=".pdf.tmp")
        os.close(fd)
        HTML(string=doc, base_url=".").write_pdf(tmp)
        os.replace(tmp, pdf_path)
        print(f"wrote {pdf_path}  ({os.path.getsize(pdf_path):,} bytes)")
    except Exception as e:  # noqa: BLE001 — HTML already written; PDF best-effort
        print(f"PDF render skipped: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
