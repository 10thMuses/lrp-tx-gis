"""Transform the OXY intelligence report HTML into a clean, editable Word (.docx).

The report HTML (scripts/build_oxy_report_v3.py) is print-CSS heavy: label/value
flex rows, shaded "Key findings" boxes, status chips, a styled cover and a TOC with
page numbers. pandoc ignores CSS, so we first rewrite those constructs into plain
semantic HTML (paragraphs, bold runs, lists) and then let pandoc emit a Word file
that is genuinely editable rather than a wall of unstyled spans.

pandoc runs from outputs/reports/ so the relative oxy_permian_map.png embeds.

Usage: python3 scripts/build_oxy_docx.py
"""
import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RDIR = os.path.join(ROOT, "outputs", "reports")
SRC = os.path.join(RDIR, "oxy-intelligence-report.html")
TMP = os.path.join(RDIR, "_oxy_docx_src.html")
OUT = "OXY-Intelligence-Report.docx"  # written into RDIR by pandoc

h = open(SRC, encoding="utf-8").read()

# 1) shaded "Key findings" boxes -> bold heading + bullet list
h = re.sub(r'<div class="keyfind"[^>]*>\s*<div class="kh">(.*?)</div>\s*<ul>(.*?)</ul>\s*</div>',
           r'<p><strong>\1</strong></p><ul>\2</ul>', h, flags=re.S)
# any stray kh wrapper
h = re.sub(r'<div class="kh">(.*?)</div>', r'<p><strong>\1</strong></p>', h, flags=re.S)

# 2) label/value flex rows -> "Label: value" paragraphs
h = re.sub(r'<div class="f"><span class="fl">(.*?)</span><span class="fv">(.*?)</span></div>',
           r'<p><strong>\1:</strong> \2</p>', h, flags=re.S)

# 3) status chips -> bracketed text next to the heading
h = re.sub(r'<span class="tag [^"]*">(.*?)</span>', r' [\1]', h, flags=re.S)

# 4) TOC page-number spans are meaningless once Word reflows -> drop
h = re.sub(r'<span class="s">.*?</span>', '', h, flags=re.S)

# 5) section eyebrow ("SECTION 4") -> keep as small bold lead-in
h = re.sub(r'<span class="secnum">(.*?)</span>', r'<strong>\1</strong><br>', h, flags=re.S)

open(TMP, "w", encoding="utf-8").write(h)

cmd = ["pandoc", os.path.basename(TMP), "-f", "html", "-t", "docx",
       "--metadata", "title=OXY — Permian Infrastructure, Water, Power & Financial Profile",
       "-o", OUT]
r = subprocess.run(cmd, cwd=RDIR, capture_output=True, text=True)
if r.returncode != 0:
    sys.stderr.write(r.stderr)
    sys.exit(r.returncode)
os.remove(TMP)
p = os.path.join(RDIR, OUT)
print("wrote", p, "·", os.path.getsize(p), "bytes")
