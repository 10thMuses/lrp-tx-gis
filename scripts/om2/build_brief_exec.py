#!/usr/bin/env python3
"""Executive Brief — condensed portrait prose memo (system: brief_exec).

Six US Letter portrait pages, one topic per page: headline, an insight
subheading that states the conclusion, a short paragraph, and one supporting
figure — either a pulled number or a single vector exhibit. No tables; every
number runs inline in the prose. Facts and copy derive from
docs/redesign_content_brief.md §0-§4.

    python3 scripts/om2/build_brief_exec.py
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import om_theme as T  # noqa: E402

S = T.SYSTEMS["brief_exec"]
OUT = T.REPO / "outputs" / "reports"
STEM = "Caramba-North-Brief-Executive"

INK, INK70, INK45, INK25 = S["ink"], S["ink70"], S["ink45"], S["ink25"]
PAPER, RULE, PANEL = S["paper"], S["rule"], S["panel"]
RED, GOLD, BLUE = S["accent"], S["second"], S["third"]

PAD_X, PAD_TOP, PAD_BOT = 74, 62, 54
COL = T.PAGE_W - 2 * PAD_X          # 668
TOTAL = 6

# --------------------------------------------------------------------------
# page shell
# --------------------------------------------------------------------------


def page(n, kicker, inner):
    """One portrait page: running head, flowed body, footer rule."""
    head = (
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;'
        f'padding-bottom:9px;border-bottom:1px solid {RULE}">'
        f'<div class="m" style="font-size:9px;letter-spacing:.2em;color:{INK45};'
        f'text-transform:uppercase">{kicker}</div>'
        f'<div class="m" style="font-size:9px;letter-spacing:.2em;color:{BLUE}">'
        f'{n:02d}&#8202;/&#8202;{TOTAL:02d}</div></div>'
    )
    foot = (
        f'<div style="position:absolute;left:{PAD_X}px;right:{PAD_X}px;bottom:{PAD_BOT - 26}px;'
        f'display:flex;justify-content:space-between;align-items:baseline;'
        f'padding-top:8px;border-top:1px solid {RULE}">'
        f'<div class="m" style="font-size:8.5px;letter-spacing:.16em;color:{INK45};'
        f'text-transform:uppercase">Confidential &#183; prepared under NDA</div>'
        f'<div class="m" style="font-size:8.5px;letter-spacing:.16em;color:{INK45}">'
        f'{n}</div></div>'
    )
    return (
        f'<div class="page" style="padding:{PAD_TOP}px {PAD_X}px {PAD_BOT}px;'
        f'display:flex;flex-direction:column">'
        f'{head}'
        f'<div class="flow" style="flex:1;min-height:0;padding-bottom:34px;'
        f'display:flex;flex-direction:column">{inner}</div>'
        f'{foot}</div>'
    )


def heading(title, sub, top=30):
    return (
        f'<h1 class="d" style="font-weight:500;font-size:33px;line-height:1.14;'
        f'letter-spacing:-.012em;margin-top:{top}px;max-width:620px">{title}</h1>'
        f'<p class="d" style="font-style:italic;font-weight:400;font-size:19px;'
        f'line-height:1.42;color:{INK70};margin-top:13px;max-width:610px;'
        f'padding-left:15px;border-left:2px solid {RED}">{sub}</p>'
    )


def para(text, top=22, size=15.6, width=640, color=None):
    return (
        f'<p style="font-size:{size}px;line-height:1.74;margin-top:{top}px;'
        f'max-width:{width}px;color:{color or INK}">{text}</p>'
    )


def figure(value, unit, label, gloss, top=26):
    """A pulled number, standing in for the exhibit on prose-only pages."""
    return (
        f'<div style="margin-top:{top}px;border-top:1px solid {RULE};'
        f'border-bottom:1px solid {RULE};padding:20px 0 21px;display:flex;'
        f'align-items:flex-start;gap:26px">'
        f'<div style="flex-shrink:0;border-left:3px solid {BLUE};padding-left:18px">'
        f'<div class="m" style="font-size:46px;font-weight:500;line-height:1;'
        f'letter-spacing:-.02em;color:{INK}">{value}'
        f'<span class="m" style="font-size:15px;font-weight:400;color:{INK70};'
        f'letter-spacing:.02em">&#8202;{unit}</span></div>'
        f'<div class="m" style="font-size:8.5px;letter-spacing:.19em;color:{INK45};'
        f'text-transform:uppercase;margin-top:11px">{label}</div></div>'
        f'<p style="font-size:13.4px;line-height:1.62;color:{INK70};max-width:352px;'
        f'padding-top:3px">{gloss}</p></div>'
    )


def exhibit(name, w, h, caption="", top=24, center=True):
    """One vector exhibit, boxed to its own aspect ratio so it never letterboxes."""
    m = "margin-left:auto;margin-right:auto;" if center else ""
    cap = (f'<div class="m" style="font-size:8.6px;letter-spacing:.13em;color:{INK45};'
           f'text-transform:uppercase;margin-top:9px;padding-top:7px;'
           f'border-top:1px solid {RULE};line-height:1.55">{caption}</div>') if caption else ""
    return (
        f'<div style="margin-top:{top}px;{m}width:{w}px">'
        f'<div style="width:{w}px;height:{h}px">{T.svg(name)}</div>{cap}</div>'
    )


def mapkey(width, top=10):
    """Key for the corridor map: the rail-less variants carry no legend.

    The wide variant plots two numbered markers at the anchors' disclosed site
    points (1 = GW Ranch, 2 = Longfellow); the subject tract is the only drawn
    polygon, so the key mirrors the plate exactly.
    """
    def badge(n):
        return (f'<span style="display:inline-block;width:13px;height:13px;'
                f'border-radius:50%;background:#A8791F;color:{PAPER};font-size:8px;'
                f'font-weight:600;line-height:13px;text-align:center;'
                f'vertical-align:-2px">{n}</span>')
    items = [
        (f'<span style="display:inline-block;width:11px;height:9px;'
         f'border:2px solid {RED};vertical-align:0px"></span>', 'Caramba North · 1,300 acres'),
        (badge(1), 'GW Ranch · 15.5 mi'),
        (badge(2), 'Longfellow · 19.3 mi'),
        (f'<span style="display:inline-block;width:11px;height:11px;'
         f'border:2px solid #1F5C7A;vertical-align:-1px"></span>', 'Solstice 765 kV'),
    ]
    cells = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:7px;'
        f'margin-right:16px">{mark}<span class="m" style="font-size:8.8px;'
        f'letter-spacing:.07em;color:{INK70}">{txt}</span></span>'
        for mark, txt in items)
    return (f'<div style="width:{width}px;margin:{top}px auto 0;padding-top:9px;'
            f'border-top:1px solid {RULE};line-height:1.9">{cells}</div>')


def note(label, text, top=20, size=10.6):
    return (
        f'<div style="margin-top:{top}px;max-width:640px">'
        f'<span class="m" style="font-size:8.4px;letter-spacing:.19em;color:{INK45};'
        f'text-transform:uppercase">{label}</span>'
        f'<p style="font-size:{size}px;line-height:1.62;color:{INK70};margin-top:5px">'
        f'{text}</p></div>'
    )


def anchor(name, text):
    """Anchor lead-in: red is reserved for the subject site and these two."""
    return (
        f'<p style="font-size:15.2px;line-height:1.72;margin-top:11px;max-width:640px">'
        f'<span class="m" style="font-size:11px;font-weight:600;letter-spacing:.14em;'
        f'color:{RED};text-transform:uppercase">{name}</span>'
        f'<span style="color:{INK25}">&#8195;</span>{text}</p>'
    )


# --------------------------------------------------------------------------
# 1 — positioning + ring diagram
# --------------------------------------------------------------------------
p1_inner = (
    f'<div style="margin-top:16px">'
    f'<div class="m" style="font-size:9.5px;letter-spacing:.26em;color:{RED};'
    f'text-transform:uppercase">Executive Brief</div>'
    f'<h1 class="d" style="font-weight:500;font-size:52px;line-height:1.02;'
    f'letter-spacing:-.02em;margin-top:16px">Caramba North</h1>'
    f'<div class="m" style="font-size:9.4px;letter-spacing:.105em;color:{INK70};'
    f'margin-top:15px;padding-top:11px;border-top:2px solid {RED};'
    f'line-height:1.7">1,300 ACRES &#183; PECOS COUNTY &#183; NORTH OF I-10 &#183; '
    f'5 MI TO FORT STOCKTON &#183; NO ZONING &#183; ERCOT FAR WEST</div>'
    f'</div>'
    f'<p class="d" style="font-style:italic;font-weight:400;font-size:21px;'
    f'line-height:1.4;color:{INK70};margin-top:20px;max-width:640px">'
    f'Projects of 7.65 GW and 2 GW sit on the same north&#8211;south line through the '
    f'property, at 15.5 and 19.3 miles &#8212; the corridor is forming around this '
    f'tract, not near it.</p>'
    + para(
        'This is a 1,300-acre parcel inside an already-forming power and data-center '
        'corridor, not a speculative land position: its transmission, water and gas '
        'position is permitted rather than proposed. The regional numbers carry the '
        'case &#8212; 32.7 GW of operating and queued capacity within 60 miles, in a '
        'state where the interconnection backlog reached 474 GW, about 90% of it data '
        'centers, and triggered a gubernatorial audit and a pause in queue processing. '
        'Caramba North benefits from that buildout without the exposure of being the '
        'marginal project in that queue: it holds water and gas on contract-ready '
        'terms, not applications.', top=18, size=15.2)
    + exhibit("chart_rings_light", 402, 402, top=12)
)

# --------------------------------------------------------------------------
# 2 — the corridor and the two anchors
# --------------------------------------------------------------------------
p2_inner = (
    heading('The corridor and its two anchors',
            '79.3% of the two anchors’ announced capacity is already under '
            'construction &#8212; this pipeline is majority-built, not '
            'majority-proposed.', top=10)
    + para(
        'The two projects that define the corridor sit at bearings of roughly '
        '19&#176; and 188&#176; from Caramba North &#8212; almost due north and almost '
        'due south, placing the property on the line between them. Both are developed '
        'around on-site generation rather than a grid interconnection.',
        top=18, size=15.2)
    + anchor(
        'GW Ranch',
        '8,000 acres, 15.5 miles north, under construction. Thirty-five gas turbines '
        'under a 7.65 GW TCEQ air permit issued in early 2026 &#8212; the largest '
        'issued in the US this year &#8212; plus 1.8 GW of storage and 750 MW of '
        'solar. Three 189,000 sq ft data-center buildings target December 2026 '
        'completion; ~$12B estimated project investment. Amazon disclosed ownership '
        'in August 2026.')
    + anchor(
        'Longfellow',
        '568 acres, 19.3 miles south. Announced in October 2025 as a 2 GW campus in '
        'eight 250 MW phases; phase-1 site work is underway, with on-site generation '
        'built in phases &#8212; aero-derivative turbines with SCR and carbon-capture '
        'capability, closed-loop cooling on permitted non-potable groundwater.')
    + exhibit("corridor_wide_light", 630, 320, top=12)
    + mapkey(630, top=6)
    + (f'<div class="m" style="width:630px;margin:7px auto 0;font-size:8.6px;'
       f'letter-spacing:.13em;color:{INK45};text-transform:uppercase">'
       f'Rings at 15 and 30 mi from the tract &#183; HIFLD transmission, ERCOT queue, '
       f'Census TIGER highways &#183; distances edge-to-edge (page 6)</div>')
)

# --------------------------------------------------------------------------
# 3 — transmission and regional power
# --------------------------------------------------------------------------
p3_inner = (
    heading('Transmission and regional power',
            'Fifteen miles from the delivery point of all three approved 765 kV '
            'Permian import lines &#8212; the transmission decision was made '
            'upstream of this site.', top=26)
    + para(
        'AEP/CPS Energy’s Solstice Substation, 15 miles away, is the western '
        'terminus of three 765 kV Permian import paths approved by the PUCT on '
        'April 24, 2025 under PBRP Docket No. 55718. Six local substations sit '
        'within ten miles, the nearest being Fort Stockton Plant at 2.0 miles '
        '(138/69 kV), with Airport at 3.3 miles and 16th Street at 6.0 miles. '
        'Around that delivery point, Pecos County alone carries 3,226 MW of '
        'operating generation &#8212; 2,178 MW solar, 542 MW wind, 505 MW of battery '
        'storage &#8212; and 12,039 MW queued across 39 ERCOT projects, while the six '
        'adjacent counties add 7,022 MW operating and 24,585 MW queued. Inside a '
        '20-mile radius there are 13 queued projects totaling 3,973 MW, and the '
        'nearest operating storage asset, St. Gall Energy Storage I, is 1.9 miles '
        'away at 103 MW.', top=20)
    + para(
        'The upgrade pipeline behind those numbers is also visible rather than '
        'assumed: 141 substation and 133 line upgrades are tracked ERCOT-wide under '
        'the Transmission Planning Improvement Tool. Those are planned upgrades and '
        'should be read as pipeline context, not as committed capacity. What is '
        'committed is the 765 kV import decision itself, which was made at the state '
        'level and lands fifteen miles from the tract boundary.', top=22)
    + para(
        'On the site side, the land carries no zoning ordinance: industrial and '
        'energy use is as-of-right, so entitlement is a permit sequence, not a '
        'rezoning. The tract fronts I-10 five miles from Fort Stockton, in ERCOT’s '
        'Far West weather zone.', top=18)
    + '<div style="margin-top:auto;padding-top:20px">'
    + note('Sources',
           'Substation distances and voltages from HIFLD and the ERCOT GIS Report; '
           'operating capacity from EIA-860; queue counts from the ERCOT '
           'interconnection queue; 765 kV approvals from PUCT PBRP Docket No. 55718.',
           top=0, size=10.4)
    + figure('12,039', 'MW', 'ERCOT queue, Pecos County alone',
             'Thirty-nine queued projects in this county before counting the two '
             'anchor campuses, which are being built around on-site generation '
             'rather than a queue position.', top=17)
    + '</div>'
)

# --------------------------------------------------------------------------
# 4 — water and gas
# --------------------------------------------------------------------------
p4_inner = (
    heading('Water and gas',
            'Two-thirds of the district’s industrial water rights are already '
            'permitted to this position and the gas quote is signable at Waha basis '
            '&#8212; both are closed conversations, not open ones.', top=26)
    + para(
        'The water position is 47,418 acre-feet per year, or 42.3 million gallons '
        'per day, permitted on adjacent affiliated lands &#8212; roughly two-thirds '
        'of all industrial water rights issued by the Middle Pecos Groundwater '
        'Conservation District. The source is the Edwards&#8211;Trinity (Plateau) '
        'aquifer, whose recharge held through the 1950s drought of record. For a '
        'large-load site in West Texas this reverses the usual sequence: the '
        'permitting is already done and the question at the table is allocation, '
        'not availability.', top=20)
    + para(
        'Gas is twenty miles away at the Waha hub, and an indicative supply quote is '
        'in hand: 200,000 MMBtu/day on a 15-year term at Waha-index pricing, with a '
        'contribution in aid of construction of $15&#8211;25M and a 9&#8211;15 month '
        'lead time, all counterparty-supplied. Waha continues to trade at a '
        'structural discount to Henry Hub, with negative prints through '
        '2024&#8211;2025 as Matterhorn, Blackcomb, Hugh Brinson and GCX rebalance '
        'Permian egress. That discount is the same one drawing behind-the-meter '
        'generation into this corridor, and it is the reason both anchor projects '
        'are being built around gas turbines on site rather than around a grid '
        'interconnection.', top=22)
    + para(
        'Taken together the two positions set the site’s power path: permitted '
        'water at scale and a quoted gas supply twenty miles from the hub mean on-site '
        'generation can be sized to a load rather than to an interconnection award.',
        top=22)
    + '<div style="margin-top:auto;padding-top:20px">'
    + note('Sources',
           'Water rights from Middle Pecos Groundwater Conservation District permit '
           'records; aquifer characterisation from USGS. Gas terms are indicative and '
           'counterparty-supplied; Waha basis from public price reporting.',
           top=0, size=10.4)
    + figure('47,418', 'AF/yr', 'Permitted &#183; 42.3 MGD',
             'Approximately two-thirds of all Middle Pecos GCD industrial water '
             'rights, held on adjacent affiliated lands.', top=17)
    + '</div>'
)

# --------------------------------------------------------------------------
# 5 — the state-level queue
# --------------------------------------------------------------------------
p5_inner = (
    heading('The state-level queue',
            'The demand signal around this site is large enough to have created a '
            'regulatory problem &#8212; a different claim than saying the area is '
            'growing.', top=26)
    + para(
        'ERCOT’s large-load interconnection queue grew from 63 GW at the end of '
        '2024 to 226 GW by November 2025, with roughly 77% of that load being data '
        'centers targeting 2030 interconnection. By August 2026 the statewide backlog '
        'reached about 474 GW of pending requests, roughly 90% data-center-driven and, '
        'in Governor Abbott’s framing, more than five times the state’s '
        'record peak demand. On August 3, 2026 that produced a directive to audit '
        'every data center in the ERCOT queue and a pause of the &#8220;Batch '
        'Zero&#8221; large-load review pending the audit.', top=20)
    + para(
        'What that means for this site is specific. The 32.7 GW within 60 miles sits '
        'inside the same backlog, but neither anchor depends on it clearing: GW '
        'Ranch’s 7.65 GW figure is a TCEQ generation air permit rather than an '
        'ERCOT interconnection position, and the project is off-grid initially, while '
        'Longfellow’s generation is planned on site. Caramba North’s own '
        'water and gas are permitted and quoted rather than applied for. In a market '
        'where the queue is the binding constraint, a position whose power path does '
        'not run through the queue is the distinction that matters.', top=22)
    + exhibit("chart_queue_growth_light", 462, 330, top=14)
)

# --------------------------------------------------------------------------
# 6 — subsurface, verification, notices
# --------------------------------------------------------------------------
p6_inner = (
    heading('Subsurface and verification',
            'Pecos County has the lowest new-drill count of seven comparable Permian '
            'counties since 2020, roughly 90% below the peer average &#8212; the '
            'quiet here is measured, not asserted.', top=18)
    + para(
        'Since 2020 the county has recorded 115 new-drill wellbore events out of '
        '1,140 total Railroad Commission events, so nine of every ten events are '
        'workovers and reworks. Against the tract itself there are zero new-drill '
        'wells within two miles, zero within five, and one within ten, at 9.37 miles; '
        'the remaining 114 sit beyond ten miles at a median distance of 19.9 miles. '
        'Within ten miles, 83% of non-plugged wellbores are marginal or end-of-life '
        'production, against 60% at two miles and 62% at five.', top=16, size=15.0)
    + exhibit("chart_peer_drilling_light", 560, 267, top=14)
    + note('Verification',
           'Every point, line and boundary behind these figures traces to a cited '
           'public dataset &#8212; ERCOT GIS Report and TPIT, PUCT, EIA-860, TCEQ, '
           'RRC dbf900 / production / W-1, FracFocus, Middle Pecos GCD, HIFLD, USGS, '
           'BTS and Census TIGER &#8212; with per-feature source popups on the '
           'diligence platform at lrp-tx-gis.netlify.app (credentials issued to the '
           'deal team separately). Refresh cadence is weekly for RRC, monthly for the '
           'ERCOT queue and TPIT, annual for EIA and USGS. The build is static and '
           'versioned, byte-verified on release, and access is logged.',
           top=14, size=10.1)
    + note('Distance methodology',
           'Distances to GW Ranch and Longfellow are measured edge-to-edge, from the '
           'nearest point on the Caramba North tract boundary to each site’s '
           'disclosed location, rather than centroid-to-centroid; this is '
           'consistently shorter because the tract has spatial extent. GW Ranch: '
           '15.5 mi (vs. 17.3 mi centroid). Longfellow: 19.3 mi (vs. 19.7 mi '
           'centroid) &#8212; Longfellow’s own public materials describe the '
           'site as more than 25 miles outside Fort Stockton, consistent with the '
           'longer figure; the distance should not be represented as shorter.',
           top=9, size=10.1)
    + note('Notices',
           'Confidential offering memorandum prepared for a limited number of '
           'prospective counterparties under NDA. Not an offer to sell or a '
           'solicitation of an offer to buy any security. Information is preliminary '
           'and indicative, from sources believed reliable but not independently '
           'verified; third-party transaction news is sourced to public reporting '
           'cited in the companion source register.', top=9, size=10.1)
)

PAGES = [
    page(1, 'Caramba North &#183; Pecos County, Texas', p1_inner),
    page(2, 'The corridor and its two anchors', p2_inner),
    page(3, 'Transmission and regional power', p3_inner),
    page(4, 'Water and gas', p4_inner),
    page(5, 'The state-level queue', p5_inner),
    page(6, 'Subsurface and verification', p6_inner),
]


def main():
    html = T.document("brief_exec", "\n".join(PAGES), "portrait",
                      "Caramba North — Executive Brief")
    OUT.mkdir(parents=True, exist_ok=True)
    hp = OUT / f"{STEM}.html"
    hp.write_text(html, encoding="utf-8")
    print("html ->", hp, hp.stat().st_size // 1024, "KB")
    T.render_pdf(str(hp), str(OUT / f"{STEM}.pdf"), "portrait")


if __name__ == "__main__":
    main()
