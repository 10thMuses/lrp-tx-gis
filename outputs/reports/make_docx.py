from docx import Document
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "/home/andreahimmel/lrp-tx-gis/outputs/reports/Pecos-Shallow-Drilling-Caramba-Vibration.docx"
MAP_URL = "https://lrp-tx-gis.netlify.app"

def shade(el, fill):
    pr = el.get_or_add_pPr() if el.tag.endswith('}p') else el.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto'); shd.set(qn('w:fill'), fill); pr.append(shd)

def runs(p, segs, size=11, color=None):
    for text, bold in segs:
        r = p.add_run(text); r.bold = bold; r.font.size = Pt(size); r.font.name = 'Calibri'
        if color: r.font.color.rgb = RGBColor(*color)

def para(doc, segs, size=11, fill=None, space_after=6, italic=False):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.2
    runs(p, segs, size)
    if italic:
        for r in p.runs: r.italic = True
    if fill: shade(p._p, fill)
    return p

def bullet(doc, segs, fill=None, space_after=4):
    p = doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.2
    runs(p, segs, 11)
    if fill: shade(p._p, fill)
    return p

def cell_text(cell, text, bold=False, fill=None, color=None):
    cell.text = ''; p = cell.paragraphs[0]; r = p.add_run(text)
    r.bold = bold; r.font.size = Pt(10)
    if color: r.font.color.rgb = RGBColor(*color)
    if fill: shade(cell._tc, fill)

def table(doc, headers, rows, hdr_fill='DBE8FD', row_styles=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell_text(t.rows[0].cells[i], h, bold=True, fill=hdr_fill, color=(0x1F, 0x3A, 0x63))
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        st = (row_styles or {}).get(ri, {})
        for ci, val in enumerate(row):
            cf = st.get('fill')
            col = (0x14, 0x53, 0x2D) if cf == 'CFECCF' else None
            cell_text(cells[ci], val, bold=st.get('bold', False), fill=cf, color=col)
    return t

def add_hyperlink(paragraph, url, text, color=(0x05, 0x63, 0xC1)):
    """Insert a clickable hyperlink in a paragraph."""
    part = paragraph.part
    r_id = part.relate_to(url, 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink', is_external=True)
    hyperlink = OxmlElement('w:hyperlink'); hyperlink.set(qn('r:id'), r_id)
    new_run = OxmlElement('w:r')
    rPr = OxmlElement('w:rPr')
    c = OxmlElement('w:color'); c.set(qn('w:val'), '%02X%02X%02X' % color); rPr.append(c)
    u = OxmlElement('w:u'); u.set(qn('w:val'), 'single'); rPr.append(u)
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '22'); rPr.append(sz)
    new_run.append(rPr)
    t = OxmlElement('w:t'); t.text = text; new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)

def add_toc(doc):
    """Insert a Word TOC field. Word auto-populates on open (or via Right-click -> Update Field)."""
    p = doc.add_paragraph(); run = p.add_run()
    f1 = OxmlElement('w:fldChar'); f1.set(qn('w:fldCharType'), 'begin')
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'), 'preserve')
    instr.text = 'TOC \\o "1-3" \\h \\z \\u'
    f2 = OxmlElement('w:fldChar'); f2.set(qn('w:fldCharType'), 'separate')
    ft = OxmlElement('w:t'); ft.text = "Table of Contents — right-click and choose 'Update Field' in Word to populate."
    f3 = OxmlElement('w:fldChar'); f3.set(qn('w:fldCharType'), 'end')
    for el in (f1, instr, f2, ft, f3):
        run._r.append(el)
    p.paragraph_format.space_after = Pt(12)

doc = Document()
s = doc.styles['Normal']
s.font.name = 'Calibri'; s.font.size = Pt(11)
s.paragraph_format.line_spacing = 1.2
# Apply Calibri across heading styles too (Word defaults Headings to Calibri Light;
# we keep the same family for consistency).
for hn in ('Heading 1', 'Heading 2', 'Title', 'List Bullet'):
    try:
        st = doc.styles[hn]
        if st.font is not None:
            st.font.name = 'Calibri'
    except KeyError:
        pass

# Running header (every page): CONFIDENTIAL classification stripe.
hdr = doc.sections[0].header
hp = hdr.paragraphs[0]
hr = hp.add_run("CONFIDENTIAL — PECOS COUNTY · CARAMBA NORTH")
hr.bold = True; hr.font.size = Pt(9); hr.font.color.rgb = RGBColor(0xB0, 0, 0)

doc.add_heading("Pecos County Drilling Activity — Historical & Recent Record", level=0)
para(doc, [("Prepared: 2026-05-19  ·  Subject site: Caramba North tract (≈1,300 ac), Pecos County, TX — centroid ≈ 30.9032° N, 102.9747° W  ·  Classification: Confidential", False)], size=9)

doc.add_heading("Purpose", level=1)
para(doc, [("This memorandum summarizes the historical and recent record of oil-and-gas drilling — with attention to shallow (<3,000 ft) wells — at and within ten miles of the Caramba North tract, drawn from the Railroad Commission of Texas (RRC) wellbore and drilling-permit records. It is provided as context for evaluating potential ground-vibration considerations for a data-center development on the site. Throughout, ", False),
           ("new drilling (a new wellbore) is distinguished from recompletions (rework of an existing wellbore — no new hole drilled)", True),
           ("; only new drilling involves a drilling rig and the hydraulic-fracturing completion associated with ground vibration.", False)])
para(doc, [("Proximity is reported at explicit distances from the tract centroid — principally ", False), ("within two miles", True), (" and ", False), ("within ten miles", True), (". Ten miles is a deliberately generous boundary: ground vibration from drilling and completion attenuates well within that distance.", False)])
_map_p = doc.add_paragraph()
_map_p.paragraph_format.space_after = Pt(6)
_r_intro = _map_p.add_run("This report is intended to accompany and utilizes the data underlying the interactive map of Caramba North, which can be accessed through ")
_r_intro.italic = True; _r_intro.font.size = Pt(11)
add_hyperlink(_map_p, MAP_URL, "this link")
_r_close = _map_p.add_run(".")
_r_close.italic = True; _r_close.font.size = Pt(11)

doc.add_heading("Table of Contents", level=1)
add_toc(doc)
doc.add_page_break()

doc.add_heading("Summary of findings", level=1)
para(doc, [
    ("No new drilling is occurring at or near the Caramba North site. ", True),
    ("Counting only genuine new wells (RRC “New Drill” permits, excluding recompletions): ", False),
    ("no well of any kind has been spudded within two miles of the tract in over a decade", True),
    (", ", False), ("no new-drill well lies within five miles", True),
    (", and only ", False), ("three new-drill wells sit within ten miles", True),
    (" across all of 2020–2025 (nearest ≈ 6.9 miles; all three are deep ≥9,200 ft, spud 2020 and 2025).", False),
], fill='EAF2FF', space_after=6)
para(doc, [
    ("The wells within two miles are all decades-old legacy completions (drilled 1950s–2002) — mostly plugged shallow verticals plus a handful of long-completed deep wells — ", False),
    ("none representing active drilling, hydraulic fracturing, or a vibration source.", True),
], fill='EAF2FF', space_after=8)

para(doc, [("Two further points reinforce this:", True)], space_after=2)
bullet(doc, [("The shallow activity in Pecos is recompletions, not new drilling. ", True),
             ("Of permits filed in Pecos since 2020, about 45% are recompletions — reworking existing wellbores, with no new hole drilled. A single operator, Kinder Morgan Production, accounts for 96% of all recompletions (reworking existing CO₂-flood fields). Recompletions use a workover rig on an existing bore; they are not the drilling-and-fracturing activity at issue, and this program is not near the site.", False)], fill='F1F7F0')
bullet(doc, [("Genuine new drilling is deep, not shallow — and remote. ", True),
             ("Pecos saw ≈478 New Drill permits since 2020 (vs ≈405 recompletion). Tracing those to wells actually spudded, only 116 genuine new wells exist county-wide, and ≈95% are deep (≥3,000 ft) horizontal (Diamondback, XTO, Continental, Gordy); just six are shallow. New shallow drilling is therefore nearly nonexistent anywhere in Pecos, and the deep new drilling that does occur is concentrated well away from the tract.", False)], fill='F1F7F0')

doc.add_heading("Findings", level=1)

doc.add_heading("1. On the Caramba North tract", level=2)
para(doc, [("The shallowest wellbores recorded inside the tract boundary:", False)], space_after=4)
table(doc, ["Depth (ft)", "Spud year", "Status", "Oil/Gas"], [
    ["2,873", "1960", "Plugged & abandoned", "Gas"],
    ["3,067", "1991", "Plugged & abandoned", "Oil"],
    ["3,109", "1957", "Plugged & abandoned", "Oil"],
    ["3,186", "1987", "Plugged & abandoned", "Oil"],
    ["3,250", "2008", "Active", "Oil"]])
para(doc, [("Only one well on the tract lies below 3,000 ft — a 2,873-ft well spudded in 1960 and long since plugged and abandoned. The only active well on the tract (3,250 ft, spudded 2008) is deeper than 3,000 ft. There has been no shallow (<3,000 ft) drilling on the tract in the modern era. (The remaining tract records are a single deep 22,545-ft wellbore and permitted-but-undrilled location entries.)", False)])

doc.add_heading("2. Within 1 mile — no shallow wells", level=2)
para(doc, [("Three wellbores of any depth lie within one mile of the tract; ", False), ("none is shallow (<3,000 ft).", True)])

doc.add_heading("3. Within 2 miles — drilling ended over two decades ago", level=2)
para(doc, [("Of about 46 wellbores within two miles, the ten shallow wells were spudded between 1960 and 2002. The most recent shallow spud within two miles was in 2002, and most of these wells are plugged and abandoned. ", False),
           ("No well of any kind — new drill or otherwise — has been spudded within two miles in over a decade.", True)])

doc.add_heading("4. New drilling since 2020, by distance", level=2)
para(doc, [("Counting only genuine new wells (RRC “New Drill” permits — recompletions of existing bores excluded):", False)], space_after=4)
table(doc, ["Radius", "New-drill wells, spudded ≥ 2020"], [
    ["≤ 2 mi", "0"],
    ["≤ 5 mi", "0"],
    ["≤ 10 mi", "3  (0 shallow, 3 deep; nearest ≈ 6.9 mi)"],
], row_styles={0: {'fill': 'CFECCF', 'bold': True}, 1: {'fill': 'CFECCF', 'bold': True}, 2: {'fill': 'EAF5EA'}})
para(doc, [("The three genuine new wells within ten miles, across all of 2020–2025, are 6.9–9.4 miles out and all deep (≈9,200–9,500 ft; spudded 2020 and 2025) — none shallow, none within five miles. Even on the loosest possible count — every record with a 2020-or-later spud date, including recompletion-restamped records — it is still ", False),
           ("zero within two miles", True),
           (" and only ≈23 within ten miles across the whole period. New drilling does not reach the site under any reading of the data.", False)])

doc.add_heading("5. The nearest non-plugged shallow wells are decades-old completions", level=2)
para(doc, [("The nearest non-plugged shallow wells were spudded in 1970 (1.28 mi) and 1988 (1.97 mi) — decades-old completions, not active drilling. A ground-vibration source is an operating drill rig or a hydraulic-fracturing operation; a plugged or long-completed wellbore is not.", False)])
para(doc, [("No active drilling is occurring adjacent to the tract.", True)], fill='E2EFDA')

doc.add_heading("6. County-wide context — new drilling is deep, and remote from the site", level=2)
para(doc, [("Since 2020 the RRC issued roughly ", False), ("478 New Drill permits", True),
           (" in Pecos County (≈4,700 sq mi), against ≈405 recompletion permits. Tracing the New Drill permits to wells actually spudded gives ", False),
           ("116 genuine new wells county-wide", True),
           (", about ", False), ("95% of them deep (≥3,000 ft)", True),
           (" — i.e., the modern Permian horizontal program. Only ", False), ("three", True),
           (" lie within ten miles of the Caramba North tract, and none within five; the activity is overwhelmingly remote from the site.", False)])

doc.add_heading("7. The shallow activity in Pecos is recompletions of existing wells — not new drilling", level=2)
para(doc, [("This is the crux of the data. Permit filings in Pecos since 2020 split roughly 53% New Drill / 45% Recompletion:", False)], space_after=4)
table(doc, ["Activity (Pecos permits, since 2020)", "Count", "Character"], [
    ["New Drill", "≈478", "≈97% deep (≥3,000 ft) horizontal — new wellbores"],
    ["Recompletion", "≈405", "rework of existing wellbores — no new hole"],
], row_styles={1: {'fill': 'EAF5EA'}})
para(doc, [("96% of every recompletion is one operator — Kinder Morgan Production — reworking existing CO₂-flood fields. The genuine new-drill operators are a different, all-deep set: Diamondback (≈30% of new drills), XTO (≈14%), Continental (≈13%), Gordy (≈11%), each essentially 100% deep.", False)])
para(doc, [("The significance for ground vibration: a recompletion is a workover on an ", False),
           ("existing", True),
           (" bore — no rig drilling a new hole, no new hydraulic-fracturing program of the kind associated with vibration. The large “shallow” footprint in Pecos is this rework activity, not drilling.", False)])
para(doc, [("Genuine new drilling — overwhelmingly the deep modern-Permian program (predominantly horizontal in this region, though hydraulic-fracturing completions are not limited to horizontal wellbores) — is the minority share, and — per Findings 1–6 — essentially none of it is near the Caramba North tract.", False)])
para(doc, [("Whether the question is framed as shallow drilling, fracking, or new drilling of any kind, the record points the same way: ", False),
           ("it is not happening at or near this site.", True)])

doc.add_heading("8. Pecos vs. peer counties — the least new drilling of the group", level=2)
para(doc, [("On the same genuine-new-drill basis (recompletions excluded), Pecos has dramatically less new drilling than comparable Permian counties. Wells spudded since 2020:", False)], space_after=4)
table(doc, ["County", "New-drill wells since 2020", "of which shallow (<3,000 ft)"], [
    ["Pecos (site county)", "116", "6"],
    ["Reeves", "1,044", "35"],
    ["Midland", "1,487", "15"],
    ["Martin", "1,616", "19"],
    ["Reagan", "629", "9"],
    ["Howard", "990", "1"],
    ["Loving", "1,121", "25"],
    ["Other-6 average", "≈1,148", "≈17"],
], row_styles={0: {'fill': 'CFECCF', 'bold': True}, 7: {'fill': 'EAF5EA', 'bold': True}})
para(doc, [("Pecos's ≈116 genuine new wells are roughly one-tenth of the average comparable county's (≈1,148); Martin, the most active, has ≈1,616, and even the next-lowest comparison county (Reagan) has ≈629. Genuine new shallow drilling is negligible in every county (≤35). On a new-drill basis Pecos is by far the least-drilled of the seven — and, per Findings 1–6, essentially none of even that activity is within ten miles of the Caramba North tract.", False)])
para(doc, [("Howard and Loving counties were pulled from the Railroad Commission's full dbf900 wellbore file and integrated on the same genuine-new-drill basis. They lie outside the six-county sale-area set and well away from the tract; they are included here only to broaden the comparison.", False)], italic=True)

doc.add_heading("9. Production near the site is decades-old completions — no active drilling or hydraulic-fracturing operations", level=2)
para(doc, [("Every well was additionally cross-referenced against the Railroad Commission's PDQ production records for the most recent six reported months (through May 2026), joined by ", False),
           ("API number", True),
           (" through the RRC's authoritative API-to-lease crosswalk — a match covering ", False),
           ("≈99.6% of all non-plugged wells", True),
           (". A well is treated as ", False),
           ("“marginal or end-of-life” when its lease's trailing-average output is at or below 125 Mcf/day of gas AND at or below 25 bbl/day of oil", True),
           (" — a strict marginal-well threshold.", False)])
para(doc, [("Of the 291 non-plugged genuine-new-drill wells within ten miles of the Caramba North tract, ", False),
           ("241 (about 83%) are marginal or end-of-life", True),
           (". The 50 still producing above that threshold are not active drilling activity: they are decades-old completions, in four groups —", False)],
     fill='DEEAF6', space_after=4)
bullet(doc, [("about 15 ", False), ("legacy deep-gas wells", True), (" (mostly 1965–1978 spud, ≈17,000–22,800 ft);", False)])
bullet(doc, [("a cluster of ~31 ", False), ("low-rate vertical conventional oil wells", True), (" at ≈3,150–3,440 ft depth (spud 1986–2012, mostly 2007–2012; all on a unitized lease producing roughly 37.5 bbl/day per well — a stripper-grade pumping operation);", False)])
bullet(doc, [("3 ", False), ("truly shallow (<3,000 ft) oil wells", True), (" at 2,824–2,945 ft (spud 2004–2011, also at stripper rates just above the threshold); and", False)])
bullet(doc, [("the single ", False), ("2020 deep-horizontal new-drill", True), (" noted in Finding 4 (9,237 ft, 9.37 mi out).", False)], space_after=8)
para(doc, [("Within five miles, ", False),
           ("52 of 86 non-plugged wells are marginal or end-of-life", True),
           (" and the 34 still producing are 3 of the legacy deep-gas wells plus 31 of the shallow vertical oil cluster — none from the modern Permian horizontal program.", False)],
     fill='DEEAF6')
para(doc, [("Within two miles, ", False),
           ("3 of 5 non-plugged wells are marginal or end-of-life", True),
           (" and the 2 still producing are the 1.13-mi 1975/≈22,100-ft legacy gas well (125.7 Mcf/d) and a 1.97-mi 2008/≈3,275-ft vertical oil well (37.5 bbl/d).", False)],
     fill='DEEAF6')
para(doc, [("A pumping wellhead or low-rate gas well on a decades-old completion is not a drill rig or a hydraulic-fracturing spread; together with the plugged legacy wells discussed above, ", False),
           ("there is no active drilling or hydraulic-fracturing operation at or near the site.", True)],
     fill='DEEAF6', space_after=8)
para(doc, [("County-wide, of the ≈35,100 genuine new-drill wellbores, ≈12,540 are plugged, ≈12,490 are marginal or end-of-life by this measure, and ≈10,060 are still producing above the threshold. The API-to-lease crosswalk matches ≈99.6% of non-plugged wells; the ≈90 that do not match are conservatively left classified “Active.” Production filings carry a normal reporting lag, which the six-month trailing window mitigates.", False)], italic=True)

doc.save(OUT)
print("WROTE", OUT)
