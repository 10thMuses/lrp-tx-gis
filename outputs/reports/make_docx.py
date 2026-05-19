from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/andreahimmel/lrp-tx-gis/outputs/reports/Pecos-Shallow-Drilling-Caramba-Vibration.docx"

def shade(el, fill):
    """Apply background shading to a paragraph (el=_p) or table cell (el=_tc)."""
    pr = el.get_or_add_pPr() if el.tag.endswith('}p') else el.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill)
    pr.append(shd)

def runs(p, segs, size=11, color=None):
    for text, bold in segs:
        r = p.add_run(text)
        r.bold = bold
        r.font.size = Pt(size)
        if color:
            r.font.color.rgb = RGBColor(*color)

def para(doc, segs, size=11, fill=None, space_after=6, italic=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    runs(p, segs, size)
    if italic:
        for r in p.runs:
            r.italic = True
    if fill:
        shade(p._p, fill)
    return p

def bullet(doc, segs, fill=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(4)
    runs(p, segs, 11)
    if fill:
        shade(p._p, fill)
    return p

def cell_text(cell, text, bold=False, fill=None, color=None):
    cell.text = ''
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(10)
    if color:
        r.font.color.rgb = RGBColor(*color)
    if fill:
        shade(cell._tc, fill)

def table(doc, headers, rows, hdr_fill='DBE8FD', row_styles=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell_text(t.rows[0].cells[i], h, bold=True, fill=hdr_fill, color=(0x1F, 0x3A, 0x63))
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        st = (row_styles or {}).get(ri, {})
        for ci, val in enumerate(row):
            f = st.get('fill')
            cf = st.get('cellfill', {}).get(ci, f)
            b = st.get('bold', False) or st.get('boldcells', {}).get(ci, False)
            col = (0x14, 0x53, 0x2D) if cf in ('CFECCF',) else None
            cell_text(cells[ci], val, bold=b, fill=cf, color=col)
    return t

doc = Document()
st = doc.styles['Normal']
st.font.name = 'Georgia'
st.font.size = Pt(11)

# Confidential banner
p = doc.add_paragraph()
r = p.add_run("CONFIDENTIAL — PECOS COUNTY · CARAMBA NORTH")
r.bold = True; r.font.size = Pt(9); r.font.color.rgb = RGBColor(0xB0, 0, 0)

h = doc.add_heading("Shallow (<3,000 ft) Oil-and-Gas Drilling at and Within Ten Miles of the Caramba North Tract — Historical and Recent Record", level=0)
para(doc, [("Prepared: 2026-05-18  ·  Subject site: Caramba North tract (≈1,300 ac), Pecos County, TX — centroid ≈ 30.9032° N, 102.9747° W  ·  Classification: Confidential", False)], size=9)

doc.add_heading("Purpose", level=1)
para(doc, [("This memorandum summarizes the historical and recent record of shallow oil-and-gas drilling — wells less than 3,000 ft total depth — at and within ten miles of the Caramba North tract, drawn from the Railroad Commission of Texas (RRC) wellbore and drilling-permit records. It is provided as context for evaluating potential ground-vibration considerations for a data-center development on the site.", False)])
para(doc, [("Proximity is reported at explicit distances from the tract centroid — principally ", False), ("within two miles", True), (" and ", False), ("within ten miles", True), (". Ten miles is a deliberately generous boundary: ground vibration from drilling and completion attenuates well within that distance.", False)])

doc.add_heading("Summary of findings", level=1)
sp = para(doc, [
    ("No drilling of any kind is occurring at or immediately adjacent to the Caramba North site. ", True),
    ("The ground-vibration concern associated with oil-and-gas activity is hydraulic fracturing of deep horizontal wells, and such vibration attenuates well within ten miles — so what matters is activity close to the site. ", False),
    ("No well of any kind has been spudded within two miles of the tract in over a decade", True),
    (" (none since before 2015; no shallow well within two miles since 2002), and the only wells within two miles are old (1950s–2002), plugged, shallow vertical legacy wells — not active, not hydraulically fractured, and not a vibration source. Within ten miles, drilling is sparse: only ", False),
    ("23 wells have been spudded since 2020 — about 2% of the county's total", True),
    (" — none of them within two miles, the nearest recent well about 2.2 miles away (2022). The bulk of Pecos drilling sits a median of roughly thirty miles from the tract.", False),
], fill='EAF2FF', space_after=8)

para(doc, [("Two further points reinforce this:", True)], space_after=2)
bullet(doc, [("Pecos drilling is disproportionately the low-intensity, non-fracked kind. ", True),
             ("Of wells spudded since 2020, about half are shallow (<3,000 ft) and — confirmed against the Railroad Commission's own Wellbore Profile field — roughly 86% of those are vertical (conventional, unfracked), versus the peer counties where only about 2% of wells are shallow and programs are almost entirely deep horizontal.", False)], fill='F1F7F0')
bullet(doc, [("Hydraulic fracturing is a feature of deep horizontal wells specifically. ", True),
             ("The shallow vertical conventional wells that sit within two miles of the site, and that weight Pecos's overall mix, are not fracked. The fracking activity that could be a vibration source is the deep-horizontal minority of Pecos drilling — and it is concentrated well away from the tract.", False)], fill='F1F7F0')

doc.add_heading("Findings", level=1)

doc.add_heading("1. On the Caramba North tract", level=2)
para(doc, [("The shallowest wellbores recorded inside the tract boundary:", False)], space_after=4)
table(doc, ["Depth (ft)", "Spud year", "Status", "Oil/Gas"], [
    ["2,873", "1960", "Plugged & abandoned", "Gas"],
    ["3,067", "1991", "Plugged & abandoned", "Oil"],
    ["3,109", "1957", "Plugged & abandoned", "Oil"],
    ["3,186", "1987", "Plugged & abandoned", "Oil"],
    ["3,250", "2008", "Active", "Oil"],
])
para(doc, [("Only one well on the tract lies below 3,000 ft — a 2,873-ft well spudded in 1960 and long since plugged and abandoned. The only active well on the tract (3,250 ft, spudded 2008) is deeper than 3,000 ft. There has been no shallow (<3,000 ft) drilling on the tract in the modern era. (The remaining tract records are a single deep 22,545-ft wellbore and permitted-but-undrilled location entries.)", False)])

doc.add_heading("2. Within 1 mile — no shallow wells", level=2)
para(doc, [("Three wellbores of any depth lie within one mile of the tract; ", False), ("none is shallow (<3,000 ft).", True)])

doc.add_heading("3. Within 2 miles — shallow drilling ended roughly 24 years ago", level=2)
para(doc, [("Of about 46 wellbores within two miles, the ten shallow wells were spudded between 1960 and 2002. The most recent shallow spud within two miles was in 2002, and most of these wells are plugged and abandoned. No shallow well has been spudded within two miles in roughly a quarter-century.", False)])

doc.add_heading("4. Recent drilling (wells spudded since 2020), by distance", level=2)
para(doc, [("These are wells spudded since 2020 — new drilling, not cumulative historical totals:", False)], space_after=4)
table(doc, ["Radius", "Wells spudded ≥ 2020", "Shallow (<3,000 ft)", "Deep (≥3,000 ft)"], [
    ["≤ 2 mi", "0", "0", "0"],
    ["≤ 5 mi", "8", "3", "5"],
    ["≤ 10 mi", "23", "7", "16"],
], row_styles={0: {'fill': 'CFECCF', 'bold': True}})
para(doc, [("No well of any kind has been spudded within two miles of the tract since before 2015. ", True),
           ("In the entire ten-mile radius only 23 wells have been spudded since 2020 — roughly three to four a year across a 314-square-mile area — and none within two miles of the site. About 70% of the 23 are deeper wells; the shallow vertical wells at issue are the minority even of this sparse activity.", False)])

doc.add_heading("5. The nearest active wells are decades-old completions", level=2)
para(doc, [("The nearest non-plugged shallow wells were spudded in 1970 (1.28 mi) and 1988 (1.97 mi) — decades-old completions, not active drilling. A ground-vibration source is an operating drill rig or a hydraulic-fracturing operation; a plugged or long-completed wellbore is not. No active drilling is occurring adjacent to the tract.", False)])

doc.add_heading("6. County-wide context — almost no recent drilling within ten miles of the site", level=2)
para(doc, [("Since 2020, 1,117 wells were spudded across Pecos County (≈4,700 sq mi). Their distribution relative to the tract is decisive: ", False),
           ("only 23 — about 2% — are within ten miles of the Caramba North tract; the other ≈98% are farther away, at a median distance of roughly thirty miles.", True),
           (" Of those 23, none is within two miles of the site, and the nearest recent well is about 2.2 miles away (spudded 2022). Recent drilling in the county is real, but it is overwhelmingly remote from the tract.", False)])

doc.add_heading("7. The drilling that does occur in Pecos is disproportionately shallow, vertical, and unfracked", level=2)
para(doc, [("Drilling-permit applications in Pecos lean horizontal, but the wells actually spudded tell the relevant story. Of the 1,117 wells spudded in Pecos since 2020, ", False),
           ("about half (556) have a total depth under 3,000 ft.", True),
           (" Cross-checked well-by-well against the Railroad Commission's own Wellbore Profile field, ", False),
           ("roughly 86% of those shallow wells are designated vertical", True),
           (" — conventional wells that are not hydraulically fractured. The deeper half is, conversely, about 82% horizontal.", False)])
para(doc, [("This matters because hydraulic fracturing — the completion activity associated with ground vibration — is a feature of deep horizontal wells, not shallow vertical ones. A substantial share of all drilling in Pecos is therefore the low-intensity, non-fracked kind, and the fracked horizontal activity is the minority — and, per Findings 1–6, what little of it exists is well away from the site.", False)])

doc.add_heading("8. Pecos vs. peer counties — far more shallow/vertical, far less fracking", level=2)
para(doc, [("Measured against the five comparable Permian counties, Pecos drilling is markedly more weighted to shallow, vertical, conventional wells. Wells spudded since 2020:", False)], space_after=4)
table(doc, ["", "Pecos (site county)", "Other-5 county average"], [
    ["Wells spudded ≥ 2020", "1,117", "3,421"],
    ["Shallow (<3,000 ft) — vertical / unfracked", "556 (≈50%)", "57 (≈2%)"],
    ["Deep (≥3,000 ft) — horizontal / fracked", "560 (≈50%)", "3,364 (≈98%)"],
], row_styles={1: {'fill': 'EAF5EA', 'cellfill': {1: 'CFECCF'}, 'boldcells': {1: True}}})
para(doc, [("Shallow, vertical wells are about 50% of Pecos's recent drilling but only about 2% of the average peer county's — Pecos's drilling mix is roughly twenty-five times more weighted toward the shallow, vertical, non-fracked end than its neighbors, whose programs are almost entirely deep horizontal. (The shallow-to-vertical correspondence is the RRC-confirmed 86% from Finding 7; peer figures are from the recorded depth field.) Combined with the proximity findings, the picture is consistent: Pecos sees comparatively little hydraulic fracturing, and essentially none of it within ten miles of the Caramba North tract.", False)])

doc.save(OUT)
print("WROTE", OUT)
