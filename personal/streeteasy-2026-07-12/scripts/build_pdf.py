#!/usr/bin/env python3
"""Build the PDF report: summary + comprehensive index + every data point per listing."""
import json, os, sys
from collections import Counter
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, KeepTogether, PageBreak)

SCRATCH = os.environ.get("SE_WORKDIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRATCH, "report.pdf")
PAGE = landscape(letter)  # 792 x 612

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
Cell = ParagraphStyle("Cell", parent=ss["Normal"], fontSize=8.4, leading=11)
CellLbl = ParagraphStyle("CellLbl", parent=Cell, textColor=INK2)
IdxCell = ParagraphStyle("IdxCell", parent=ss["Normal"], fontSize=7.2, leading=9.2)
IdxHdr = ParagraphStyle("IdxHdr", parent=IdxCell, textColor=colors.white, fontName="Helvetica-Bold")

def P(t, style=Cell): return Paragraph(str(t), style)
def mmdd(v):
    if not v: return "—"
    p = str(v).split("-")
    return f"{int(p[1])}/{int(p[2])}/{p[0][2:]}" if len(p) == 3 else v
def money(v): return f"${v:,.0f}" if isinstance(v, (int, float)) else "—"
def lst(v): return ", ".join(v) if v else "—"
def dash(v): return "—" if v in (None, "", []) else str(v)

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
    f"No broker fees appear on any fee schedule (post-FARE Act). "
    f"Square footage is published for only {sum(1 for r in rows if r.get('sqft'))} of {len(rows)} units "
    f"(one recovered by outside research); blanks reflect data no listing source publishes.", Body))
story.append(Spacer(1, 8))
story.append(t)
story.append(PageBreak())

# Comprehensive index table (landscape, 17 columns)
story.append(Paragraph("Listing Index — key data points (full detail per listing follows)", H2))
IDX_COLS = [
    ("Address", 1.32, lambda r: r["full_address"]),
    ("Hood", 0.72, lambda r: r["neighborhood"]),
    ("Rent", 0.52, lambda r: money(r["rent"])),
    ("Net eff.", 0.52, lambda r: money(r["net_effective_rent"]) if r.get("net_effective_rent") else "—"),
    ("Bd", 0.24, lambda r: r["bedrooms"]),
    ("Ba", 0.28, lambda r: r["baths"]),
    ("Rms", 0.32, lambda r: dash(r.get("rooms"))),
    ("SqFt", 0.4, lambda r: f"{r['sqft']:,}" if r.get("sqft") else "—"),
    ("$/sf/yr", 0.42, lambda r: f"${r['rent']*12/r['sqft']:,.0f}" if r.get("sqft") else "—"),
    ("Listed", 0.5, lambda r: mmdd(r.get("listed_date"))),
    ("DoM", 0.3, lambda r: dash(r.get("days_on_market"))),
    ("Avail", 0.5, lambda r: mmdd(r.get("available_date"))),
    ("Priv. outdoor", 0.62, lambda r: lst(r.get("private_outdoor_space"))),
    ("Bldg yr", 0.4, lambda r: dash(r.get("year_built"))),
    ("Deposit", 0.5, lambda r: money(r.get("security_deposit")) if r.get("security_deposit") is not None else "—"),
    ("Brokerage", 0.82, lambda r: dash(r.get("brokerage"))),
    ("Hood median*", 0.6, lambda r: money(r.get("area_median_rent_same_beds"))),
]
idx_data = [[Paragraph(h, IdxHdr) for h, _, _ in IDX_COLS]]
for r in rows:
    idx_data.append([P(fn(r), IdxCell) for _, _, fn in IDX_COLS])
t = Table(idx_data, colWidths=[w*inch for _, w, _ in IDX_COLS], hAlign="LEFT", repeatRows=1)
t.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), NAVY),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, ALT]),
    ("GRID", (0,0), (-1,-1), 0.4, LINE),
    ("VALIGN", (0,0), (-1,-1), "TOP"),
    ("TOPPADDING", (0,0), (-1,-1), 2.2), ("BOTTOMPADDING", (0,0), (-1,-1), 2.2),
    ("LEFTPADDING", (0,0), (-1,-1), 3), ("RIGHTPADDING", (0,0), (-1,-1), 3),
]))
story.append(t)
story.append(Paragraph("*StreetEasy median asking rent for the same bedroom count in the listing's area.", Small))
story.append(PageBreak())

# Per-listing sections — every data point
for r in rows:
    el = []
    net = f' &nbsp;<font color="#008300" size="9">({money(r["net_effective_rent"])} net · {r["months_free"]} mo free · {r["lease_term_months"]}-mo lease)</font>' if r.get("net_effective_rent") else ""
    el.append(Paragraph(f'{r["full_address"]} — {money(r["rent"])}/mo{net}', LTitle))
    el.append(Paragraph(
        f'{r["neighborhood"]} ({r.get("borough") or "—"} {r.get("zip") or ""}) · {r.get("unit_type_display") or r.get("unit_type") or ""} · '
        f'{r["bedrooms"]} bd / {r["baths"]} ba'
        + (f' · {r["sqft"]:,} sq ft' if r.get("sqft") else "")
        + f' · <link href="{r["url"]}" color="#0563C1">{r["url"]}</link>', LSub))

    fb, hb = r.get("full_baths"), r.get("half_baths")
    pairs = [
        ("Listing ID", r["listing_id"]),
        ("Status", r.get("status")),
        ("Listed", r.get("listed_date")),
        ("Days on market", r.get("days_on_market")),
        ("Available", r.get("available_date")),
        ("Off market", dash(r.get("off_market_date"))),
        ("First activated", (r.get("created_at") or "")[:10] or "—"),
        ("Last updated", (r.get("updated_at") or "")[:10] or "—"),
        ("Rooms", dash(r.get("rooms"))),
        ("Baths (full/half)", f"{dash(fb)} / {dash(hb)}"),
        ("Sq ft", f"{r['sqft']:,}" if r.get("sqft") else "not published"),
        ("$/sqft/yr", f"${r['rent']*12/r['sqft']:,.0f}" if r.get("sqft") else "—"),
        ("Unit type", dash(r.get("unit_type"))),
        ("Building", dash(r.get("building_name"))),
        ("Year built", dash(r.get("year_built"))),
        ("Bldg floors / units", f'{dash(r.get("building_floors"))} / {dash(r.get("building_units"))}'),
        ("Security deposit", money(r.get("security_deposit")) if r.get("security_deposit") is not None else "—"),
        ("Total monthly", money(r.get("total_monthly_price")) if r.get("total_monthly_price") else "—"),
        ("Lease term", f'{r["lease_term_months"]} mo' if r.get("lease_term_months") else "—"),
        ("Months free", dash(r.get("months_free"))),
        ("Brokerage", dash(r.get("brokerage"))),
        ("Broker license", f'{dash(r.get("broker_license_name"))} ({dash(r.get("broker_license_type"))})'),
        ("Broker address", dash(r.get("broker_address"))),
        ("Broker fee", r.get("broker_fee") or "None listed"),
        ("MLS #", dash(r.get("mls_number"))),
        ("Listing source", dash(r.get("listing_source_type"))),
        ("Open houses", lst([str(o) for o in r.get("open_houses") or []])),
        ("Media", f'{r.get("photo_count") or 0} photos · {r.get("video_count") or 0} videos · {r.get("floorplan_count") or 0} floorplans · 3D: {dash(r.get("tour_3d_url"))}'),
        ("Coordinates", f'{r.get("latitude")}, {r.get("longitude")}'),
        ("Area median (same beds)", money(r.get("area_median_rent_same_beds"))),
    ]
    grid = []
    for a in range(0, len(pairs), 3):
        chunk = pairs[a:a+3] + [("", "")] * (3 - len(pairs[a:a+3]))
        row_cells = []
        for k, v in chunk:
            row_cells += [P(f"<b>{k}</b>" if k else "", CellLbl), P(dash(v))]
        grid.append(row_cells)
    t = Table(grid, colWidths=[1.05*inch, 2.1*inch, 1.05*inch, 2.15*inch, 1.05*inch, 2.6*inch], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 1.2), ("BOTTOMPADDING", (0,0), (-1,-1), 1.2),
        ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LINEBELOW", (0,0), (-1,-2), 0.25, colors.HexColor("#eceae4")),
    ]))
    el.append(t)
    el.append(Spacer(1, 4))

    details = [
        ("Private outdoor space", lst(r.get("private_outdoor_space"))),
        ("Views", lst(r.get("views"))),
        ("Fireplace", lst(r.get("fireplace_types"))),
        ("Unit features", lst(r.get("unit_features"))),
        ("Building amenities", lst(r.get("building_amenities"))),
        ("Doorman", lst(r.get("doorman_types"))),
        ("Parking", lst(r.get("parking_types"))),
        ("Shared outdoor", lst(r.get("shared_outdoor_space"))),
        ("Storage", lst(r.get("storage_types"))),
        ("Fees", lst(r.get("fees"))),
        ("Price history (this listing)", "; ".join(f'{c["date"]}: {money(c["price"])}' for c in r.get("price_changes") or []) or "—"),
    ]
    uh = [h for h in (r.get("unit_history") or []) if h.get("listing_id") != r["listing_id"]]
    details.append(("Unit rental history (prior listings)",
                    "; ".join(f'{h["date"]}: {money(h["price"])} {(h["status"] or "").lower()}' for h in uh) or "—"))
    if r.get("sqft_source"):
        details.append(("SqFt source", r["sqft_source"] + " (researched, not from StreetEasy)"))
    for k, v in details:
        el.append(Paragraph(f'<b>{k}:</b> {v}', Small))
    desc = (r.get("description") or "").replace("\n", " ").strip()
    el.append(Paragraph(f'<b>Description:</b> {desc}', Small))
    el.append(Spacer(1, 6))
    el.append(HRFlowable(width="100%", thickness=0.6, color=LINE))
    el.append(Spacer(1, 8))
    # header block + field grid stay together; long tails may flow
    story.append(KeepTogether(el[:3]))
    for e in el[3:]:
        story.append(e)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(INK2)
    canvas.drawString(0.6*inch, 0.42*inch, "StreetEasy listings shared 7/12/2026 — personal compilation")
    canvas.drawRightString(PAGE[0]-0.6*inch, 0.42*inch, f"Page {doc.page}")
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=PAGE,
                        leftMargin=0.6*inch, rightMargin=0.6*inch,
                        topMargin=0.6*inch, bottomMargin=0.65*inch,
                        title="StreetEasy Rental Listings — 2026-07-12")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUT)
