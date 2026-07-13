#!/usr/bin/env python3
"""Build the PDF report: summary page + one section per listing."""
import json, os, sys
from collections import Counter
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, KeepTogether, PageBreak)

SCRATCH = os.environ.get("SE_WORKDIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRATCH, "report.pdf")

rows = json.load(open(os.path.join(SCRATCH, "listings.json")))
fill_path = os.path.join(SCRATCH, "research_fill.json")
fills = json.load(open(fill_path)) if os.path.exists(fill_path) else {}
for r in rows:
    f = fills.get(r["listing_id"])
    if f and f.get("sqft") and not r.get("sqft"):
        r["sqft"] = f["sqft"]; r["sqft_source"] = f.get("source", "research")
    if f and f.get("year_built") and not r.get("year_built"):
        r["year_built"] = f["year_built"]

rows.sort(key=lambda r: (r.get("neighborhood") or "", r.get("rent") or 0))

NAVY = colors.HexColor("#1F3864")
INK2 = colors.HexColor("#52514e")
LINE = colors.HexColor("#d8d5cc")
ALT = colors.HexColor("#f2f6fc")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Title"], fontSize=20, textColor=NAVY, spaceAfter=2, alignment=0)
Sub = ParagraphStyle("Sub", parent=ss["Normal"], fontSize=10.5, textColor=INK2, spaceAfter=14)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=13, textColor=NAVY, spaceBefore=4, spaceAfter=4)
LTitle = ParagraphStyle("LTitle", parent=ss["Heading2"], fontSize=12.5, textColor=NAVY, spaceBefore=0, spaceAfter=1)
LSub = ParagraphStyle("LSub", parent=ss["Normal"], fontSize=9.5, textColor=INK2, spaceAfter=5)
Body = ParagraphStyle("Body", parent=ss["Normal"], fontSize=9, leading=12.4)
Small = ParagraphStyle("Small", parent=ss["Normal"], fontSize=8.2, leading=11, textColor=INK2)
Cell = ParagraphStyle("Cell", parent=ss["Normal"], fontSize=8.6, leading=11.4)
CellLbl = ParagraphStyle("CellLbl", parent=Cell, textColor=INK2)

def P(t, style=Cell): return Paragraph(t, style)
def money(v): return f"${v:,.0f}" if isinstance(v, (int, float)) else "—"
def lst(v): return ", ".join(v) if v else "—"

story = []
rents = sorted(r["rent"] for r in rows)
med = rents[len(rents)//2]
story.append(Paragraph("StreetEasy Rental Listings", H1))
story.append(Paragraph("31 unique listings shared on 7/12/2026 · Downtown Manhattan · compiled 7/13/2026", Sub))

# Summary stats table
hood_stats = []
for hood, n in Counter(r["neighborhood"] for r in rows).most_common():
    hr = [r["rent"] for r in rows if r["neighborhood"] == hood]
    hood_stats.append([hood, str(n), money(min(hr)), money(sorted(hr)[len(hr)//2]), money(max(hr))])
t = Table([["Neighborhood", "Listings", "Min rent", "Median", "Max rent"]] + hood_stats,
          colWidths=[1.9*inch, 0.8*inch, 1.0*inch, 1.0*inch, 1.0*inch], hAlign="LEFT")
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 9), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ALT]),
    ("GRID", (0,0), (-1,-1), 0.4, LINE),
    ("TOPPADDING", (0,0), (-1,-1), 3.5), ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
]))
story.append(Paragraph("Overview", H2))
story.append(Paragraph(
    f"Rents run {money(rents[0])}–{money(rents[-1])} (median {money(med)}). "
    f"Bedroom mix: " + ", ".join(f"{n}× {bd}BR" for bd, n in sorted(Counter(r['bedrooms'] for r in rows).items())) + ". "
    f"All listings are active rentals; two offer net-effective concessions (1 month free). "
    f"No broker fees appear on any fee schedule (post-FARE Act).", Body))
story.append(Spacer(1, 8))
story.append(t)
story.append(Spacer(1, 10))

# Index table
story.append(Paragraph("Listing Index", H2))
idx_rows = [["Address", "Hood", "Rent", "Bd", "Ba", "SqFt", "Avail", "DoM"]]
for r in rows:
    idx_rows.append([r["full_address"], r["neighborhood"], money(r["rent"]),
                     r["bedrooms"], r["baths"], f"{r['sqft']:,}" if r.get("sqft") else "—",
                     r.get("available_date") or "—", r.get("days_on_market")])
t = Table(idx_rows, colWidths=[2.15*inch, 1.15*inch, 0.75*inch, 0.35*inch, 0.4*inch, 0.55*inch, 0.85*inch, 0.45*inch], hAlign="LEFT", repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTSIZE", (0,0), (-1,-1), 7.8), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ALT]),
    ("GRID", (0,0), (-1,-1), 0.4, LINE),
    ("TOPPADDING", (0,0), (-1,-1), 2.6), ("BOTTOMPADDING", (0,0), (-1,-1), 2.6),
]))
story.append(t)
story.append(PageBreak())

# Per-listing sections
for i, r in enumerate(rows):
    el = []
    net = f' &nbsp;<font color="#008300" size="9">({money(r["net_effective_rent"])} net · {r["months_free"]} mo free)</font>' if r.get("net_effective_rent") else ""
    el.append(Paragraph(f'{r["full_address"]} — {money(r["rent"])}/mo{net}', LTitle))
    el.append(Paragraph(
        f'{r["neighborhood"]} · {r.get("unit_type") or ""} · {r["bedrooms"]} bd / {r["baths"]} ba'
        + (f' · {r["sqft"]:,} sq ft' if r.get("sqft") else "")
        + f' · <link href="{r["url"]}" color="#0563C1">{r["url"]}</link>', LSub))

    pairs = [
        ("Status", r.get("status")), ("Listed", r.get("listed_date")),
        ("Days on market", r.get("days_on_market")), ("Available", r.get("available_date")),
        ("Rooms", r.get("rooms")), ("Building", r.get("building_name") or "—"),
        ("Year built", r.get("year_built") or "—"),
        ("Bldg floors / units", f'{r.get("building_floors") or "—"} / {r.get("building_units") or "—"}'),
        ("Brokerage", r.get("brokerage")), ("License", f'{r.get("broker_license_name") or "—"} ({r.get("broker_license_type") or "—"})'),
        ("Security deposit", money(r.get("security_deposit")) if r.get("security_deposit") is not None else "—"),
        ("Area median (same beds)", money(r.get("area_median_rent_same_beds"))),
    ]
    grid = []
    for a in range(0, len(pairs), 2):
        p1 = pairs[a]; p2 = pairs[a+1] if a+1 < len(pairs) else ("", "")
        grid.append([P(f"<b>{p1[0]}</b>", CellLbl), P(str(p1[1] if p1[1] is not None else "—")),
                     P(f"<b>{p2[0]}</b>", CellLbl), P(str(p2[1] if p2[1] is not None else "—"))])
    t = Table(grid, colWidths=[1.25*inch, 2.1*inch, 1.35*inch, 2.3*inch], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("FONTSIZE", (0,0), (-1,-1), 8.6),
        ("TOPPADDING", (0,0), (-1,-1), 1.4), ("BOTTOMPADDING", (0,0), (-1,-1), 1.4),
        ("LEFTPADDING", (0,0), (-1,-1), 0),
    ]))
    el.append(t)
    el.append(Spacer(1, 3))

    details = []
    if r.get("private_outdoor_space"): details.append(("Private outdoor", lst(r["private_outdoor_space"])))
    if r.get("views"): details.append(("Views", lst(r["views"])))
    details.append(("Unit features", lst(r.get("unit_features"))))
    details.append(("Building amenities", lst(r.get("building_amenities"))))
    if r.get("fees"): details.append(("Fees", lst(r["fees"])))
    if r.get("price_changes") and len(r["price_changes"]) > 1:
        details.append(("Price history", "; ".join(f'{c["date"]}: {money(c["price"])}' for c in r["price_changes"])))
    uh = [h for h in (r.get("unit_history") or []) if h.get("listing_id") != r["listing_id"]]
    if uh:
        details.append(("Unit rental history", "; ".join(f'{h["date"]}: {money(h["price"])} {(h["status"] or "").lower()}' for h in uh[:6])))
    if r.get("sqft_source"):
        details.append(("SqFt source", r["sqft_source"]))
    for k, v in details:
        el.append(Paragraph(f'<b>{k}:</b> {v}', Small))
    desc = (r.get("description") or "").replace("\n", " ")
    if len(desc) > 600: desc = desc[:600] + "…"
    el.append(Paragraph(f'<b>Description:</b> {desc}', Small))
    el.append(Spacer(1, 6))
    el.append(HRFlowable(width="100%", thickness=0.6, color=LINE))
    el.append(Spacer(1, 8))
    story.append(KeepTogether(el))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(INK2)
    canvas.drawString(0.75*inch, 0.5*inch, "StreetEasy listings shared 7/12/2026 — personal compilation")
    canvas.drawRightString(letter[0]-0.75*inch, 0.5*inch, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=0.75*inch, rightMargin=0.75*inch,
                        topMargin=0.7*inch, bottomMargin=0.75*inch,
                        title="StreetEasy Rental Listings — 2026-07-12")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
