#!/usr/bin/env python3
"""Compile the Grid Wire operating docs into one branded PDF.

    python3 scripts/build_docs_pdf.py [-o OUT.pdf]

Reads the canonical docs in reading order, renders each as a section with a
page break, and styles them in the house green identity (Jost). This is an
internal documentation artifact, not a Grid Wire issue, so it is not ASCII-
or pdffonts-gated; fenced code falls back to a system monospace.
"""

import argparse
from datetime import date
from pathlib import Path

import markdown
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

REPO = Path(__file__).resolve().parent.parent
FONT_CONFIG = FontConfiguration()

DOCS = [
    ("CLAUDE.md", "Bootstrap (auto-loaded each session)"),
    ("Readme.md", "Operating rules"),
    ("STYLE.md", "Locked editorial spec"),
    ("OPERATING.md", "Pipeline reference"),
    ("WIP_OPEN.md", "Live state"),
    ("WIP_LOG.md", "Closed-issue ledger"),
]

CSS_TEXT = """
@font-face { font-family: "Jost"; src: url("FONTS/Jost-Regular.ttf");  font-weight: 400; font-style: normal; }
@font-face { font-family: "Jost"; src: url("FONTS/Jost-Medium.ttf");   font-weight: 500; font-style: normal; }
@font-face { font-family: "Jost"; src: url("FONTS/Jost-SemiBold.ttf"); font-weight: 600; font-style: normal; }
@font-face { font-family: "Jost"; src: url("FONTS/Jost-Bold.ttf");     font-weight: 700; font-style: normal; }
@font-face { font-family: "Jost"; src: url("FONTS/Jost-Italic.ttf");   font-weight: 400; font-style: italic; }

@page {
  size: letter; margin: 64pt 64pt 56pt 64pt;
  @top-left { content: "THE GRID WIRE  —  OPERATING DOCUMENTATION";
              font-family: "Jost"; font-size: 7.6pt; font-weight: 700;
              color: #1f4d3f; letter-spacing: 1pt; }
  @bottom-center { content: "Land Resource Partners  •  Page " counter(page) " of " counter(pages);
                   font-family: "Jost"; font-size: 7.6pt; color: #8a948f; padding-top: 12pt; }
}
@page :first { @top-left { content: none; } }

html, body { font-family: "Jost"; color: #1a2722; font-size: 9.8pt; line-height: 1.55; margin: 0; padding: 0; }

#cover { border-bottom: 1pt solid #1f4d3f; margin-bottom: 20pt; padding-bottom: 12pt; }
#cover h1 { font-size: 30pt; font-weight: 700; color: #1f4d3f; letter-spacing: 0.6pt; margin: 0 0 4pt 0; }
#cover .sub { font-size: 11pt; color: #1a2722; font-weight: 600; margin: 0 0 4pt 0; }
#cover .meta { font-size: 8.6pt; color: #5a6b63; margin: 0; }
#cover ol { font-size: 9.4pt; color: #1a2722; margin: 12pt 0 0 0; padding-left: 22pt; }
#cover li { line-height: 1.7; }

section.doc { page-break-before: always; }

h1 { font-size: 17pt; font-weight: 700; color: #1f4d3f; border-bottom: 1pt solid #c8d3cc;
     padding-bottom: 6pt; margin: 0 0 10pt 0; page-break-after: avoid; }
h2 { font-size: 12.5pt; font-weight: 700; color: #1f4d3f; margin: 16pt 0 7pt 0; page-break-after: avoid; }
h3 { font-size: 10.4pt; font-weight: 600; color: #2c5a4b; margin: 12pt 0 4pt 0; page-break-after: avoid; }
p { margin: 0 0 8pt 0; }
ul, ol { margin: 0 0 8pt 0; padding-left: 20pt; }
li { margin-bottom: 3pt; }
strong, b { font-weight: 600; color: #1a2722; }
hr { border: none; border-top: 0.6pt solid #c8d3cc; margin: 12pt 0; }

code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.4pt;
       background: #f1f5f3; padding: 0.5pt 2pt; border-radius: 2pt; }
pre { background: #f1f5f3; border-left: 3pt solid #1f4d3f; padding: 8pt 12pt;
      margin: 8pt 0; page-break-inside: avoid; overflow-wrap: anywhere; }
pre code { background: none; padding: 0; font-size: 8.2pt; line-height: 1.4; }

table { width: 100%; border-collapse: collapse; table-layout: fixed; margin: 8pt 0; font-size: 8.4pt; }
th { background: #1f4d3f; color: #fff; font-weight: 600; text-align: left; padding: 5pt 8pt; }
td { padding: 5pt 8pt; vertical-align: top; border-bottom: 0.6pt solid #d8e0db; overflow-wrap: anywhere; }
tbody tr:nth-child(even) { background: #f1f5f3; }
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default=str(REPO / "dist" / "Grid_Wire_Operating_Docs.pdf"))
    args = ap.parse_args()

    md = markdown.Markdown(extensions=["tables", "fenced_code", "attr_list", "sane_lists"])

    toc = "".join(f"<li>{name} — {desc}</li>" for name, desc in DOCS)
    parts = [
        '<div id="cover">',
        "<h1>THE GRID WIRE</h1>",
        '<p class="sub">Operating Documentation</p>',
        f'<p class="meta">Land Resource Partners  •  Andrea Himmel  •  compiled {date.today().isoformat()}</p>',
        f"<ol>{toc}</ol>",
        "</div>",
    ]
    for name, _ in DOCS:
        md.reset()
        body = md.convert((REPO / name).read_text(encoding="utf-8"))
        parts.append(f'<section class="doc">{body}</section>')
    html = "<!DOCTYPE html><html><head><meta charset='utf-8'></head><body>" + "".join(parts) + "</body></html>"

    css = CSS(string=CSS_TEXT.replace("FONTS", str(REPO / "fonts")), font_config=FONT_CONFIG)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(REPO)).write_pdf(str(out), stylesheets=[css], font_config=FONT_CONFIG)
    print(out)


if __name__ == "__main__":
    main()
