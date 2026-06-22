"""Transform the OXY dossier HTML into a clean, editable Word (.docx).

The report HTML (build_oxy_report.py) is print-CSS heavy: shaded section intros,
structured asset cards (label/value rows + a "JV relevance" callout), status
chips, map-key lists, bios and a footnotes appendix. pandoc ignores CSS, so we
first rewrite those constructs into plain semantic HTML (headings, bold runs,
blockquotes, paragraphs) and then let pandoc emit a genuinely editable Word file.

pandoc runs from outputs/reports/ so the relative map PNGs embed.

Run: python3 scripts/build_oxy_docx.py
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RDIR = os.path.join(ROOT, "outputs", "reports")
SRC = os.path.join(RDIR, "oxy-intelligence-report.html")
TMP = os.path.join(RDIR, "_oxy_docx_src.html")
OUT = "OXY-Intelligence-Report.docx"

h = open(SRC, encoding="utf-8").read()
S = re.S

# section eyebrow ("Section 2", "Appendix B") -> bold lead-in
h = re.sub(r'<span class="snum">(.*?)</span>', r'<p><strong>\1</strong></p>', h, flags=S)

# asset card header: name (+ footnote sup) + status chip -> H3 with [status]
h = re.sub(r'<div class="ah"><span class="an">(.*?)</span><span class="chip[^"]*">(.*?)</span></div>',
           r'<h3>\1 [\2]</h3>', h, flags=S)
# one-liner -> italic paragraph
h = re.sub(r'<div class="one">(.*?)</div>', r'<p><em>\1</em></p>', h, flags=S)
# label/value rows -> "Label: value"
h = re.sub(r'<div class="arow"><span class="al">(.*?)</span><span class="av">(.*?)</span></div>',
           r'<p><strong>\1:</strong> \2</p>', h, flags=S)
# JV callout -> bold-labelled paragraph
h = re.sub(r'<div class="jv"><span class="jvl">(.*?)</span>(.*?)</div>',
           r'<p><strong>\1:</strong> \2</p>', h, flags=S)
# section intro / lead -> blockquote
h = re.sub(r'<div class="lead">(.*?)</div>', r'<blockquote>\1</blockquote>', h, flags=S)
# kbox heading -> bold paragraph
h = re.sub(r'<div class="h">(.*?)</div>', r'<p><strong>\1</strong></p>', h, flags=S)
# key-table heading + rows -> simple list
h = re.sub(r'<div class="keyh">(.*?)</div>', r'<p><strong>\1</strong></p>', h, flags=S)
h = re.sub(r'<div class="kr"><span class="kn">(.*?)</span><span class="kt">(.*?)</span></div>',
           r'<p>\1 — \2</p>', h, flags=S)
h = re.sub(r'<span class="kk">(.*?)</span>', r'\1', h, flags=S)
# bios
h = re.sub(r'<span class="bn">(.*?)</span>', r'<strong>\1</strong>', h, flags=S)
h = re.sub(r'<span class="br">(.*?)</span>', r' — <em>\1</em>', h, flags=S)
# TOC arrows -> drop
h = re.sub(r'<span class="tn">.*?</span>', '', h, flags=S)
h = re.sub(r'<span class="tt">(.*?)</span>', r'\1', h, flags=S)
# any stray chips -> bracketed
h = re.sub(r'<span class="chip[^"]*">(.*?)</span>', r' [\1]', h, flags=S)

open(TMP, "w", encoding="utf-8").write(h)

cmd = ["pandoc", os.path.basename(TMP), "-f", "html", "-t", "docx",
       "--metadata", "title=Occidental Petroleum — Infrastructure for a Hyperscale Data-Center JV",
       "-o", OUT]
r = subprocess.run(cmd, cwd=RDIR, capture_output=True, text=True)
if r.returncode != 0:
    sys.stderr.write(r.stderr); sys.exit(r.returncode)
os.remove(TMP)
p = os.path.join(RDIR, OUT)
print("wrote", p, "·", os.path.getsize(p), "bytes")
