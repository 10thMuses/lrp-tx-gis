#!/usr/bin/env python3
"""Grid Wire PDF renderer: draft.md -> Grid_Wire_Vol{N}_{YYYYMMDD}_{cut}_ET.pdf

Usage:
    python3 scripts/render_pdf.py issues/vol16/600pm/draft.md [-o OUT.pdf]
                                  [--html-out OUT.html] [--no-font-check]

Draft format: front matter block delimited by '---' lines, then markdown.
Required front-matter keys: vol, date_long, date_compact, cut_slug, cut_label,
edition_note, coverage, runhead_date.

Markup extensions handled here (before python-markdown):
  ::: angle ... :::   ANGLE callout box (red label injected automatically)
  ^[12,13]            superscript footnote refs -> <sup>12,13</sup>
  ==text==            crimson bold inline emphasis -> <b class="hot">text</b>

Tables are authored as markdown tables inside a raw wrapper, e.g.
  <div class="tbl t-deals" markdown="1"> ... </div>
The header row is demoted into tbody (styled tr.th) so it does NOT repeat
when a table breaks across pages, matching the Vol 16 reference.

WeasyPrint requirement (locked): a single FontConfiguration instance is
passed to BOTH CSS() and write_pdf(). Omitting either silently falls back
to system fonts. Post-render, pdffonts must report Jost subsets only; any
other font hard-fails the build (override with --no-font-check).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

import markdown
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

REPO = Path(__file__).resolve().parent.parent
TEMPLATE_HTML = REPO / "templates" / "gridwire.html"
TEMPLATE_CSS = REPO / "templates" / "gridwire.css"
EDITION_HTML = REPO / "templates" / "gridwire-edition.html"
EDITION_CSS = REPO / "templates" / "gridwire-edition.css"

# single module-level instance, used for CSS() and write_pdf() identically
FONT_CONFIG = FontConfiguration()

# format: "daily" (navy/crimson cut, gridwire.css) or "edition" (green
# comprehensive long-form: Weekend/Close/Special/sweep, gridwire-edition.css)
DAILY_KEYS = (
    "vol", "date_long", "date_compact", "cut_slug", "cut_label",
    "edition_note", "coverage", "runhead_date",
)
EDITION_KEYS = (
    "vol", "date_compact", "edition_slug", "edition_label", "byline",
    "timestamp",
)


def parse_front_matter(text):
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        sys.exit("render_pdf: draft has no front matter block (--- ... ---)")
    meta = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    fmt = meta.get("format", "daily")
    required = EDITION_KEYS if fmt == "edition" else DAILY_KEYS
    missing = [k for k in required if not meta.get(k)]
    if missing:
        sys.exit(f"render_pdf: front matter ({fmt}) missing keys: "
                 f"{', '.join(missing)}")
    return meta, text[m.end():]


def preprocess(md_text):
    # fenced callouts: "::: <name>" ... ":::"
    #   angle -> ANGLE box with injected red label (daily format)
    #   box   -> shaded callout; author supplies the bold lead-in
    #            ("**Practitioner read.** ...") per the edition references
    #   quote -> italic pull-quote box for on-record statements
    def fence(m):
        name = m.group(1)
        inner = m.group(2).strip()
        if name == "angle":
            return ('<div class="angle" markdown="1">\n'
                    '<p class="angle-label">ANGLE</p>\n'
                    f"{inner}\n</div>\n")
        return f'<div class="{name}" markdown="1">\n{inner}\n</div>\n'
    md_text = re.sub(r"^::: *(angle|box|quote) *\n(.*?)\n^::: *$", fence,
                     md_text, flags=re.S | re.M)
    # superscript footnote refs
    md_text = re.sub(r"\^\[([0-9, ]+)\]", r"<sup>\1</sup>", md_text)
    # accent bold (crimson in daily, green in edition)
    md_text = re.sub(r"==(.+?)==", r'<b class="hot">\1</b>', md_text)
    return md_text


def postprocess(html):
    # red roman numeral on section headings
    html = re.sub(
        r"<h2>([IVXLCDM]+\.)\s*",
        r'<h2><span class="n">\1</span> ',
        html,
    )
    # demote table headers inside .tbl wrappers so they do not repeat
    # across page breaks (reference behavior)
    def demote(m):
        head = re.sub(r"</?th(?=[ >])", lambda t: t.group(0).replace("th", "td"),
                      m.group(1))
        return f'<tbody><tr class="th">{head}</tr>'
    html = re.sub(
        r"<thead>\s*<tr>(.*?)</tr>\s*</thead>\s*<tbody>",
        demote, html, flags=re.S,
    )
    return html


def _md_inline(s):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def build_html(meta, body_md):
    body_html = postprocess(markdown.markdown(
        preprocess(body_md),
        extensions=["tables", "md_in_html", "attr_list"],
    ))
    if meta.get("format", "daily") == "edition":
        return build_edition(meta, body_md, body_html)

    meta_line = (
        f"Vol {meta['vol']} &nbsp;|&nbsp; {meta['date_long']} &nbsp;|&nbsp; "
        f"{meta['cut_label']} cut, {meta['edition_note']} &nbsp;|&nbsp; "
        f"{meta['coverage']}"
    )
    tpl = TEMPLATE_HTML.read_text(encoding="utf-8")
    return (
        tpl.replace("{{DOC_TITLE}}",
                    f"Grid Wire Vol {meta['vol']} - {meta['cut_label']}")
           .replace("{{RUNLEFT}}", f"THE GRID WIRE | Vol {meta['vol']}")
           .replace("{{RUNRIGHT}}", meta["runhead_date"])
           .replace("{{META_LINE}}", meta_line)
           .replace("{{CONTENT}}", body_html)
    )


def build_edition(meta, body_md, body_html):
    # auto-build the TOC from the section headings (## ...), one ordinal each
    heads = re.findall(r"^## +(.+?) *$", body_md, flags=re.M)
    toc = "<ol>" + "".join(f"<li>{h}</li>" for h in heads) + "</ol>"
    foot = f"{meta['edition_label']}  •  Vol. {meta['vol']}"
    tpl = EDITION_HTML.read_text(encoding="utf-8")
    return (
        tpl.replace("{{DOC_TITLE}}",
                    f"Grid Wire Vol {meta['vol']} - {meta['edition_label']}")
           .replace("{{BYLINE}}", meta["byline"])
           .replace("{{TIMESTAMP}}", _md_inline(meta["timestamp"]))
           .replace("{{FOOTEDITION}}", foot)
           .replace("{{TOC}}", toc)
           .replace("{{CONTENT}}", body_html)
    )


def check_fonts(pdf_path):
    try:
        out = subprocess.run(["pdffonts", str(pdf_path)],
                             capture_output=True, text=True, check=True).stdout
    except FileNotFoundError:
        sys.exit("render_pdf: pdffonts not found (install poppler-utils); "
                 "font check is mandatory, or pass --no-font-check")
    fonts = [ln.split()[0] for ln in out.splitlines()[2:] if ln.strip()]
    bad = [f for f in fonts if "Jost" not in f]
    if not fonts:
        sys.exit("render_pdf: pdffonts reports no embedded fonts; "
                 "WeasyPrint fell back to system fonts")
    if bad:
        sys.exit(f"render_pdf: non-Jost fonts embedded: {', '.join(bad)}; "
                 "check @font-face paths and FontConfiguration usage")
    return fonts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("draft")
    ap.add_argument("-o", "--out")
    ap.add_argument("--html-out", help="also write the assembled HTML")
    ap.add_argument("--no-font-check", action="store_true")
    args = ap.parse_args()

    draft = Path(args.draft)
    meta, body_md = parse_front_matter(draft.read_text(encoding="utf-8"))
    html = build_html(meta, body_md)

    if args.html_out:
        Path(args.html_out).write_text(html, encoding="utf-8")

    if meta.get("format", "daily") == "edition":
        slug = meta["edition_slug"]
        css_path = EDITION_CSS
    else:
        slug = meta["cut_slug"]
        css_path = TEMPLATE_CSS
    out = Path(args.out) if args.out else draft.parent / (
        f"Grid_Wire_Vol{meta['vol']}_{meta['date_compact']}_{slug}_ET.pdf"
    )
    css = CSS(filename=str(css_path), font_config=FONT_CONFIG)
    HTML(string=html, base_url=str(REPO)).write_pdf(
        str(out), stylesheets=[css], font_config=FONT_CONFIG,
    )
    if not args.no_font_check:
        fonts = check_fonts(out)
        print(f"fonts ok: {', '.join(sorted(set(fonts)))}")
    print(out)


if __name__ == "__main__":
    main()
