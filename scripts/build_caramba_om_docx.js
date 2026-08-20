#!/usr/bin/env node
/* Build the Caramba North post-NDA Offering Memorandum as an editable Word
 * document. Same derived data model as build_caramba_om.py (via
 * caramba_om_data.py --json); same exhibit rasters. Content mirrors the PDF's
 * sections and tables; pagination is not reproduced pixel-for-pixel since the
 * point of this artifact is that a human can edit it.
 *
 *   python3 scripts/build_caramba_om.py --json-only   (not needed directly —
 *   this script shells caramba_om_data.py itself)
 *   node scripts/build_caramba_om_docx.js
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, BorderStyle, ShadingType,
  ImageRun, PageBreak, VerticalAlign, Header, Footer, PageNumber,
} = require("docx");

const REPO = path.resolve(__dirname, "..");
const EXHIBIT_DIR = path.join(REPO, "outputs", "reports", "om_exhibits");
const OUT = path.join(REPO, "outputs", "reports", "Caramba-North-OM-PostNDA.docx");

// ---------------------------------------------------------------- data model
const tmpJson = "/tmp/om_model_docx.json";
execFileSync("python3", [path.join(REPO, "scripts", "caramba_om_data.py"), "--json", tmpJson], { cwd: REPO });
const M = JSON.parse(fs.readFileSync(tmpJson, "utf8"));
const { config: C, section3: S3, section4: S4, section7: S7, section9: S9 } = M;
const STAMP = new Date().toISOString().slice(0, 10);

const EXHIBITS = [
  { id: "2.1", file: "exhibit_2_1_site-setting.jpg", w: 2400, h: 1500, captured: "2026-07-06",
    eyebrow: "EXHIBIT 2.1 · PECOS COUNTY, TEXAS",
    title: "The site: contiguous, interstate-front, five miles from Fort Stockton",
    subtitle: "Aerial view of the Caramba North tract (green boundary) on the north side of Interstate 10, with Fort Stockton and its municipal services to the east.",
    takeaway: "The tract is a single contiguous block with direct I-10 frontage and town services five miles away." },
  { id: "3.1", file: "exhibit_3_1_planned-grid-upgrades.jpg", w: 2400, h: 1374, captured: "2026-07-06",
    eyebrow: "EXHIBIT 3.1 · CARAMBA NORTH CORRIDOR",
    title: "Planned grid upgrades only (ERCOT TPIT) — the Solstice hub circled, the site beside it",
    subtitle: "Planned transmission upgrades and planned substation upgrades only — no existing infrastructure shown.",
    takeaway: "The planned-upgrade program radiates from the circled Solstice terminus on the site's doorstep." },
  { id: "4.1", file: "exhibit_4_1_generation-cluster.jpg", w: 2400, h: 1374, captured: "2026-07-06",
    eyebrow: "EXHIBIT 4.1 · PECOS COUNTY AND NEIGHBORING COUNTIES",
    title: "The operating fleet and the interconnection queue, on one map",
    subtitle: "Operating generation with the ERCOT generator-interconnection queue over the same footprint.",
    takeaway: "The site sits inside the densest operating renewable cluster in ERCOT." },
  { id: "7.1", file: "exhibit_7_1_datacenter-pipeline.jpg", w: 2400, h: 1374, captured: "2026-07-06",
    eyebrow: "EXHIBIT 7.1 · PECOS AND REEVES COUNTIES",
    title: "The announced data-center and large-load projects surrounding the site",
    subtitle: "Campus land positions plus labeled callouts for announced projects.",
    takeaway: "Gigawatt-scale sponsors have taken positions on every side of the site." },
];
const exById = Object.fromEntries(EXHIBITS.map(e => [e.id, e]));

// ---------------------------------------------------------------- utilities
const NAVY = "0F1B2D", RED = "B91C1C", SLATE = "475569", MUTED = "64748B";
const LINE = "E2E8F0", LINE_DK = "CBD5E1", FILL_HEAD = "F1F5F9", FILL_TOTAL = "FEF2F2", FILL_FLAG = "FFFBEB";

function fmt(n, unit = "") {
  if (n === null || n === undefined) return "—";
  if (typeof n === "number") n = Math.round(n);
  return n.toLocaleString("en-US") + unit;
}
function gw(mw) {
  if (mw === null || mw === undefined) return "—";
  return mw >= 1000 ? (mw / 1000).toFixed(1) + " GW" : fmt(mw) + " MW";
}

function eyebrow(text, muted) {
  return new Paragraph({
    spacing: { after: 80 },
    children: [new TextRun({ text: text.toUpperCase(), bold: true, size: 15,
      color: muted ? MUTED : RED, characterSpacing: 30 })],
  });
}
function sectionHeading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1, spacing: { after: 200 },
    children: [new TextRun({ text, color: NAVY, size: 32, bold: true })],
  });
}
function subHeading(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2, spacing: { before: 260, after: 120 },
    children: [new TextRun({ text, color: NAVY, size: 22, bold: true })],
  });
}
function lede(text) {
  return new Paragraph({
    spacing: { after: 220 }, indent: { left: 200 },
    border: { left: { style: BorderStyle.SINGLE, size: 18, color: RED, space: 8 } },
    children: [new TextRun({ text, color: "24354C", size: 21 })],
  });
}
function body(text) {
  return new Paragraph({ spacing: { after: 140 }, children: [new TextRun({ text, size: 19 })] });
}
function note(text) {
  return new Paragraph({ spacing: { after: 200 },
    children: [new TextRun({ text, size: 15, color: MUTED, italics: true })] });
}
function flagBox(text) {
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    rows: [new TableRow({ children: [new TableCell({
      shading: { type: ShadingType.CLEAR, fill: FILL_FLAG },
      margins: { top: 120, bottom: 120, left: 160, right: 160 },
      borders: allBorders(1, "FCD34D"),
      children: [new Paragraph({ children: [new TextRun({ text: "Classification note — ", bold: true, size: 17, color: "78350F" }),
        new TextRun({ text, size: 17, color: "78350F" })] })],
    })] })],
  });
}
function pageBreak() { return new Paragraph({ children: [new PageBreak()] }); }

function allBorders(size, color) {
  const b = { style: BorderStyle.SINGLE, size, color };
  return { top: b, bottom: b, left: b, right: b };
}

const CONTENT_TWIPS = 10080; // 7in at 0.75in margins on Letter

function table(headers, rows, ratios, opts = {}) {
  const widths = ratios.map(r => Math.round(CONTENT_TWIPS * r));
  const headerRow = new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => new TableCell({
      width: { size: widths[i], type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, fill: FILL_HEAD },
      borders: { bottom: { style: BorderStyle.SINGLE, size: 6, color: LINE_DK } },
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({
        alignment: (opts.align && opts.align[i] === "right") ? AlignmentType.RIGHT : AlignmentType.LEFT,
        children: [new TextRun({ text: h.toUpperCase(), bold: true, size: 13, color: SLATE, characterSpacing: 15 })],
      })],
    })),
  });
  const bodyRows = rows.map((r, ri) => {
    const isTotal = opts.totalRowIndex === ri;
    return new TableRow({
      children: r.map((cell, i) => new TableCell({
        width: { size: widths[i], type: WidthType.DXA },
        shading: isTotal ? { type: ShadingType.CLEAR, fill: FILL_TOTAL } : undefined,
        borders: { bottom: { style: BorderStyle.SINGLE, size: 3, color: isTotal ? "FECACA" : LINE } },
        margins: { top: 55, bottom: 55, left: 100, right: 100 },
        children: [new Paragraph({
          alignment: (opts.align && opts.align[i] === "right") ? AlignmentType.RIGHT : AlignmentType.LEFT,
          children: (typeof cell === "string" ? [new TextRun({ text: cell, size: 17, bold: isTotal })]
                                                : cell.map(rn => new TextRun(Object.assign({ size: 17 }, rn)))),
        })],
      })),
    });
  });
  return new Table({ width: { size: 100, type: WidthType.PERCENTAGE }, rows: [headerRow, ...bodyRows] });
}

function statsRow(items) {
  const w = Math.round(CONTENT_TWIPS / items.length);
  return new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 10, color: NAVY },
      bottom: { style: BorderStyle.SINGLE, size: 10, color: NAVY },
      insideVertical: { style: BorderStyle.SINGLE, size: 2, color: LINE },
      insideHorizontal: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
      left: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
      right: { style: BorderStyle.NONE, size: 0, color: "FFFFFF" },
    },
    rows: [new TableRow({ children: items.map(([v, k]) => new TableCell({
      width: { size: w, type: WidthType.DXA },
      margins: { top: 140, bottom: 160, left: 90, right: 90 },
      children: [
        new Paragraph({ children: [new TextRun({ text: String(v), bold: true, size: 27, color: NAVY })] }),
        new Paragraph({ spacing: { before: 40 },
          children: [new TextRun({ text: k.toUpperCase(), size: 12, color: MUTED, characterSpacing: 12 })] }),
      ],
    })) })],
  });
}

function exhibitImage(id) {
  const e = exById[id];
  if (!e) return [];
  const fp = path.join(EXHIBIT_DIR, e.file);
  if (!fs.existsSync(fp)) return [];
  const data = fs.readFileSync(fp);
  const widthPx = 620; // ~6.46in at 96dpi, fits inside 7in content column with room
  const heightPx = Math.round(widthPx * (e.h / e.w));
  return [
    eyebrow(e.eyebrow),
    new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: e.title, bold: true, size: 24, color: NAVY })] }),
    new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: e.subtitle, size: 15, color: SLATE })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [
      new ImageRun({ type: "jpg", data, transformation: { width: widthPx, height: heightPx } }),
    ] }),
    new Paragraph({ spacing: { after: 260 }, border: { left: { style: BorderStyle.SINGLE, size: 18, color: RED, space: 8 } },
      indent: { left: 200 },
      children: [new TextRun({ text: "Takeaway — ", bold: true, size: 16, color: "24354C" }),
        new TextRun({ text: e.takeaway, size: 16, color: "24354C" })] }),
  ];
}

// ---------------------------------------------------------------- content
const children = [];
const w = (...items) => children.push(...items);

// Cover
w(
  new Paragraph({ spacing: { before: 1200, after: 40 },
    children: [new TextRun({ text: "STRICTLY CONFIDENTIAL · OFFERING MEMORANDUM · POST-NDA", bold: true, size: 15, color: RED, characterSpacing: 30 })] }),
  new Paragraph({ spacing: { after: 160 },
    children: [new TextRun({ text: "CARAMBA NORTH", bold: true, size: 72, color: NAVY })] }),
  new Paragraph({ spacing: { after: 160 },
    children: [new TextRun({ text: `Up to ${fmt(C.acres_max)} contiguous acres of powered land on the ERCOT 765 kV backbone`, size: 26, color: "24354C" })] }),
  new Paragraph({ spacing: { after: 400 },
    children: [new TextRun({ text: "PECOS COUNTY, TEXAS · FAR WEST ERCOT · PERMIAN BASIN · I-10 CORRIDOR", size: 16, color: SLATE, characterSpacing: 25 })] }),
  statsRow([
    [fmt(C.acres_max), "Contiguous acres (up to)"],
    [fmt(C.water_af_yr), "AF/yr permitted water rights"],
    [`${C.solstice_miles} mi`, "To 765 kV Solstice substation"],
  ]),
  statsRow([
    [`${C.waha_miles} mi`, "To Waha natural gas hub"],
    [gw(S4.pecos_queue_total_mw), "ERCOT queue, Pecos Co."],
    [String(S9.new_drilling.bands["≤ 5 mi"].count), "New-drill wells within 5 mi since 2020"],
  ]),
  new Paragraph({ spacing: { before: 500 },
    children: [new TextRun({ text: "Prepared by Land Resource Partners · Interactive diligence platform: lrp-tx-gis.netlify.app", size: 15, color: SLATE })] }),
  new Paragraph({ children: [new TextRun({ text: `${STAMP} · Data compendium for the buyer data room · Editable working draft`, size: 15, color: SLATE })] }),
  pageBreak(),
);

// TOC
const toc = [
  ["01", "Executive Summary"], ["02", "The Property"],
  ["03", "Transmission — the 765 kV Grid Anchor & Planned Upgrades"],
  ["04", "Regional Power Cluster — Operating Fleet & ERCOT Queue, Named Projects"],
  ["05", "Water Rights at Institutional Scale"], ["06", "Waha-Basis Natural Gas"],
  ["07", "Regional Data Center Pipeline"], ["08", "The Diligence Platform"],
  ["09", "Subsurface & Drilling Activity — the Vibration Record"],
];
const appx = [["A.1", "GIS Platform — Access & Navigation"], ["A.2", "Footnotes, References & Sources"], ["A.3", "Important Notices"]];
w(eyebrow("Contents", true), sectionHeading("Table of Contents"));
for (const [n, t] of toc) {
  w(new Paragraph({ spacing: { after: 100 }, children: [
    new TextRun({ text: n + "   ", bold: true, color: RED, size: 18 }),
    new TextRun({ text: t, bold: true, color: NAVY, size: 20 }),
  ] }));
}
for (const [n, t] of appx) {
  w(new Paragraph({ spacing: { after: 90 }, children: [
    new TextRun({ text: n + "   ", bold: true, color: MUTED, size: 17 }),
    new TextRun({ text: t, color: MUTED, size: 17 }),
  ] }));
}
w(pageBreak());

// 01 Executive Summary
const pillars = [
  ["Structural power cost", "Waha-basis natural gas at a structural discount to Henry Hub, with recurring negative prints in 2024–2025 as Matterhorn, Blackcomb, Hugh Brinson, and GCX expansions rebalance basin egress."],
  ["765 kV transmission anchor", `AEP Solstice Substation ${C.solstice_miles} miles north — the western terminus of the three PUCT-approved 765 kV Permian import paths under the Permian Basin Reliability Plan.`],
  ["Water rights at institutional scale", `${fmt(C.water_af_yr)} AF/yr (~${C.water_mgd} MGD) permitted on adjacent affiliated lands — nearly two-thirds of total Middle Pecos GCD rights — from the Edwards-Trinity (Plateau) aquifer, whose recharge record held through the 1950s drought of record.`],
  ["Demand already on the ground", `${fmt(S4.pecos_queue_total_mw)} MW in the ERCOT queue in Pecos County across ${S4.pecos_queue_projects} projects; Pecos and adjacent counties host ${S7.local_gw} GW of announced hyperscale and large-load capacity within ${S7.local_radius_mi} miles.`],
  ["As-of-right development", "Unincorporated Pecos County has no zoning ordinance — no use districts, density limits, height restrictions, or setbacks. Industrial and energy uses are permitted as of right with no discretionary land-use review."],
];
w(
  eyebrow("01 · Executive Summary"),
  sectionHeading("A powered-land site at the intersection of transmission, water, gas, and proven hyperscale demand"),
  lede(`Caramba North is an up-to-${fmt(C.acres_max)}-acre contiguous site on the north side of Interstate 10 in Pecos County, Texas — the Far West weather zone of ERCOT, the highest-growth large-load pocket in North America. The site combines a 765 kV transmission anchor ${C.solstice_miles} miles north, permitted groundwater at institutional scale on adjacent affiliated lands, Waha-basis natural gas ${C.waha_miles} miles away, and a surrounding project pipeline of more than ${S7.total_gw} GW of announced data-center and large-load capacity. Its subsurface record is unusually clean: no new-drill well lies within five miles, and no new-drill hydraulic-fracturing job has ever been filed within two miles.`),
  subHeading("Five pillars of the opportunity"),
  table(["#", "Pillar", "Substance"], pillars.map((p, i) => [String(i + 1), p[0], p[1]]), [0.06, 0.24, 0.70], { align: ["right", "left", "left"] }),
  subHeading("What this document is"),
  body("This Memorandum is the post-NDA data compendium for the Caramba North data room. Each section opens with the conclusion the data supports, followed by the data itself — including named-project detail for the operating fleet and interconnection queue (Section 4) and the full drilling-activity study of the tract and its ten-mile radius (Section 9). Every figure derives from the public sources registered in Appendix A.2 or from counterparty-supplied indicative terms identified as such, and every mapped feature is independently verifiable on the companion GIS platform (Section 8, Appendix A.1). Map exhibits are captured directly from that platform."),
  pageBreak(),
);

// 02 The Property
w(
  eyebrow("02 · The Property"),
  sectionHeading("Contiguous interstate-frontage acreage with rail, fiber, and municipal services within five miles"),
  lede(`The Property comprises up to ${fmt(C.acres_max)} contiguous acres on the north side of Interstate 10, approximately five miles west of Fort Stockton (tract centroid ${M.tract_centroid.lat}° N, ${Math.abs(M.tract_centroid.lon)}° W). It carries direct interstate frontage, proximity to the Union Pacific Sunset Route rail line, and long-haul fiber along the I-10 corridor. Fort Stockton provides municipal services and a regional airport within approximately five miles. The Property is offered to accommodate a range of institutional counterparty structures — hyperscale data-center development, large-load industrial siting, or combined-cycle generation with co-located storage and renewables.`),
  subHeading("Site fundamentals"),
  table(["Attribute", "Detail"], [
    ["Size / configuration", `Up to ${fmt(C.acres_max)} contiguous acres, north side of I-10`],
    ["Access", "Direct interstate frontage; Union Pacific Sunset Route proximate; long-haul fiber along the I-10 corridor"],
    ["Municipal services", "Fort Stockton (~5 mi): municipal services, regional airport"],
    ["Land-use regime", "Unincorporated Pecos County — no zoning ordinance; industrial and energy uses as of right; no discretionary land-use review"],
    ["Groundwater regulation", "Middle Pecos Groundwater Conservation District (see Section 5)"],
    ["ERCOT position", "Far West weather zone — highest-growth large-load pocket in ERCOT"],
  ], [0.28, 0.72]),
  ...exhibitImage("2.1"),
  pageBreak(),
);

// 03 Transmission
const subs = S3.local_substations.slice(0, 4).map(s => `${s.name.replace(" Substation", "")} (${s.miles} mi)`).join(", ");
w(
  eyebrow("03 · Transmission"),
  sectionHeading("Fifteen miles from the western terminus of ERCOT's 765 kV import backbone — inside an active grid-upgrade corridor"),
  lede(`AEP's Solstice Substation, ${C.solstice_miles} miles north of the Property, is the western terminus of the three PUCT-approved 765 kV Permian import paths — the largest transmission program in ERCOT history, approved April 24, 2025 under the Permian Basin Reliability Plan. Multiple 138 kV substations sit within seven miles of the site, and ERCOT's Transmission Project Information Tracking (TPIT) shows a dense program of planned line and substation upgrades across Pecos County and its neighbors. The Property is positioned to interconnect into a grid pocket that regulators have already committed to reinforcing at extra-high voltage.`),
  table(["Element", "Detail"], [
    ["765 kV PUCT approval", "Three import paths approved April 24, 2025 (Permian Basin Reliability Plan, Project No. 55718)"],
    ["Solstice Substation", `AEP / CPS Energy; western terminus of the three 765 kV paths; ${C.solstice_miles} mi north of the Property`],
    ["Howard–Solstice line", "~300–370 miles to San Antonio; AEP / CPS Energy; CCN routing in progress (PUCT Docket 59366)"],
    ["Local substations", subs],
    ["Planned upgrades (TPIT)", `${S3.tpit_substation_upgrades} planned substation upgrades and ${S3.tpit_line_projects} planned transmission projects tracked ERCOT-wide, refreshed monthly; the regional concentration is shown in Exhibit 3.1`],
    ["Planning basis", "ERCOT Permian Basin Reliability Plan Study (July 2024); PBRP approved September 2024"],
  ], [0.28, 0.72]),
  ...exhibitImage("3.1"),
  pageBreak(),
);

// 04 Regional Power Cluster
function grpRows(op, qu) {
  return op.map((o, i) => {
    const qq = qu[i];
    return [o.tech, `${o.count} · ${gw(o.mw)}`, `${qq.count} · ${gw(qq.mw)}`];
  });
}
function namedTable(group) {
  const blocks = [];
  for (const g of group) {
    if (!g.count) continue;
    const shown = g.named.filter(x => (x.mw || 0) >= 5);
    blocks.push(subHeadingSmall(`${g.tech} · ${g.count} ${g.count === 1 ? "project" : "projects"} · ${gw(g.mw)}`));
    if (!shown.length) {
      blocks.push(body(`No utility-scale ${g.tech.toLowerCase()} capacity recorded`));
      continue;
    }
    const rows = shown.map(x => [x.name, fmt(x.mw) + " MW"]);
    const dropped = (g.more || 0) + (g.named.length - shown.length);
    if (dropped) rows.push([`+${dropped} more`, ""]);
    blocks.push(table(["Project", "MW"], rows, [0.8, 0.2], { align: ["left", "right"] }));
  }
  return blocks;
}
function subHeadingSmall(text) {
  return new Paragraph({ spacing: { before: 160, after: 60 },
    children: [new TextRun({ text, bold: true, size: 18, color: NAVY })] });
}

const pop = S4.pecos_operating, pq = S4.pecos_queue, aop = S4.adjacent_operating, aq = S4.adjacent_queue;
w(
  eyebrow("04 · Regional Power Cluster"),
  sectionHeading(`Embedded in the densest renewable generation cluster in ERCOT, with ${gw(S4.pecos_queue_total_mw)} queued in Pecos County`),
  lede(`Pecos County is the number-one solar-producing county in Texas — ${pop[0].count} operating plants totalling ${gw(pop[0].mw)} — and the ERCOT generator-interconnection queue in the county totals ${fmt(S4.pecos_queue_total_mw)} MW across ${S4.pecos_queue_projects} projects. Operating storage is already on the ground at the site's doorstep. Named-project detail for the operating fleet and the queue follows in 4.2–4.5.`),
  subHeading("4.1  Operating fleet and queue, by county group"),
  table(["Technology", "Pecos Co. — operating", "Pecos Co. — ERCOT queue"], grpRows(pop, pq)
    .concat([["Total", gw(S4.pecos_operating_total_mw), gw(S4.pecos_queue_total_mw)]]),
    [0.34, 0.33, 0.33], { align: ["left", "right", "right"], totalRowIndex: pop.length }),
  table(["Technology", "Adjacent — operating", "Adjacent — ERCOT queue"], grpRows(aop, aq)
    .concat([["Total", gw(S4.adjacent_operating_total_mw), gw(S4.adjacent_queue_total_mw)]]),
    [0.34, 0.33, 0.33], { align: ["left", "right", "right"], totalRowIndex: aop.length }),
  note(`Adjacent counties: ${C.adjacent_counties.join(", ")}. Operating fleet on an EIA-860 plant basis; queue on an ERCOT Generator Interconnection Status Report basis, one row per interconnection request, grouped by project name. Sources: ERCOT GIS Report; EIA-860; USGS/LBNL USWTDB.`),
  subHeading("Selected proximity markers"),
  table(["Asset", "Distance", "Capacity"], S4.proximity_markers.map(x => [`${x.name} (${x.kind})`, `${x.miles} mi`, `${fmt(x.mw)} MW`]),
    [0.5, 0.25, 0.25], { align: ["left", "right", "right"] }),
  pageBreak(),
  subHeadingSmall(`4.2  Operating fleet, Pecos County — ${gw(S4.pecos_operating_total_mw)} across ${pop.reduce((a, g) => a + g.count, 0)} plants`),
  ...namedTable(pop),
  subHeadingSmall(`4.3  ERCOT queue, Pecos County — ${gw(S4.pecos_queue_total_mw)} queued, ${(S4.pecos_queue_total_mw / Math.max(S4.pecos_operating_total_mw, 1)).toFixed(1)}× the operating base`),
  ...namedTable(pq),
  pageBreak(),
  subHeadingSmall(`4.4  Operating fleet, adjacent counties — ${gw(S4.adjacent_operating_total_mw)}`),
  ...namedTable(aop),
  subHeadingSmall(`4.5  ERCOT queue, adjacent counties — ${gw(S4.adjacent_queue_total_mw)}, skewed to storage and firm gas`),
  ...namedTable(aq),
  ...exhibitImage("4.1"),
  pageBreak(),
);

// 05 Water / 06 Gas
w(
  eyebrow("05 · Water"),
  sectionHeading("Permitted groundwater at a scale few competing sites can document"),
  lede(`An affiliated party holds permits for ${fmt(C.water_af_yr)} acre-feet per year (~${C.water_mgd} million gallons per day) on adjacent lands — nearly two-thirds of the total permitted rights in the Middle Pecos Groundwater Conservation District. The source is the Edwards-Trinity (Plateau) aquifer, recharged from the mountains to the south, with an annual recharge record that held through the 1950s drought of record. The permit base is designated for industrial use and is sufficient for combined-cycle cooling and hyperscale data-center loads.`),
  table(["Element", "Detail"], [
    ["Permitted volume", `${fmt(C.water_af_yr)} AF/yr (~${C.water_mgd} MGD) on adjacent affiliated lands — ≈ two-thirds of total district rights`],
    ["Groundwater district", "Middle Pecos GCD (MPGCD)"],
    ["Aquifer source", "Edwards-Trinity (Plateau); recharge from southern mountains"],
    ["Drought resilience", "Well-established annual recharge record; held through the 1950s drought of record"],
    ["Permitted use profile", "Industrial; sufficient for combined-cycle cooling and hyperscale data-center loads"],
  ], [0.28, 0.72]),
  eyebrow("06 · Natural Gas"),
  sectionHeading("Twenty miles from Waha, with an indicative long-term supply quote in hand"),
  lede(`The Property sits approximately ${C.waha_miles} miles from the Waha hub, the West Texas gas pricing and delivery point that has traded at a structural discount to Henry Hub — including recurring negative prints through 2024–2025 — as Matterhorn, Blackcomb, Hugh Brinson, and the GCX expansion rebalance basin takeaway. An indicative supply quote has been secured for ${fmt(C.gas_quote_mmbtu_d)} MMBtu per day on a ${C.gas_quote_term_years}-year term at Waha-index pricing, with contribution-in-aid-of-construction of $${C.gas_ciac_musd} million and a build lead time of ${C.gas_lead_months} months.`),
  table(["Element", "Detail"], [
    ["Indicative supply quote", `${fmt(C.gas_quote_mmbtu_d)} MMBtu/day · ${C.gas_quote_term_years}-year term · Waha-index pricing (counterparty-supplied indicative terms)`],
    ["CIAC / lead time", `$${C.gas_ciac_musd} million; ${C.gas_lead_months} months from counterparty`],
    ["Basis dynamic", "Structural discount vs. Henry Hub; recurring negative prints 2024–2025"],
    ["Takeaway expansion", "Matterhorn in service; Blackcomb, Hugh Brinson, GCX expansion in the pipeline"],
  ], [0.28, 0.72]),
  pageBreak(),
);

// 07 Data Center Pipeline
function anchorRow(a) {
  let prox = a.county || "—";
  if (a.miles !== null && a.miles !== undefined) prox += ` · ~${a.miles} mi`;
  const status = (a.status || "").replace(/\b\w/g, c => c.toUpperCase());
  return [a.name || "", a.developer || "—", gw(a.capacity_mw), prox, status];
}
const otherGw = Math.round(((S7.total_mw - S7.local_mw) / 1000) * 10) / 10;
w(
  eyebrow("07 · Regional Data Center Pipeline"),
  sectionHeading(`Announced hyperscale and large-load capacity inside ${S7.local_radius_mi} miles totals ${S7.local_gw} GW`),
  lede(`Pecos and Reeves counties are emerging as the Permian Basin's gigawatt-scale AI computing corridor. The announced campuses within ${S7.local_radius_mi} miles of the Property — sponsors including Pacifico Energy and Poolside/CoreWeave — target ${S7.local_gw} GW between them, the nearest inside twenty miles. Each validates the same siting logic the Property offers: cheap Waha gas, big flat land, groundwater, and a reinforced grid.`),
  subHeading(`Announced projects within ${S7.local_radius_mi} miles`),
  table(["Project", "Sponsor", "Capacity", "County · distance", "Status"], S7.local.map(anchorRow),
    [0.26, 0.28, 0.13, 0.20, 0.13], { align: ["left", "left", "right", "left", "left"] }),
);
if (S7.other && S7.other.length) {
  w(
    subHeading("Elsewhere in Texas — context, not catchment"),
    body(`The register also tracks ${S7.other.length} announced Texas campuses outside the regional catchment, totalling ${otherGw} GW. They are listed for market context and are not included in the ${S7.local_gw} GW figure above.`),
    table(["Project", "Sponsor", "Capacity", "County · distance", "Status"], S7.other.map(anchorRow),
      [0.26, 0.28, 0.13, 0.20, 0.13], { align: ["left", "left", "right", "left", "left"] }),
  );
}
w(
  note(`Anchor register compiled from corporate announcements, TCEQ air permits, ERCOT queue entries, and county tax-abatement filings; last compiled ${S7.generated || "—"}. Distances are straight-line from the tract centroid. Coordinates marked approximate in the register are anchored to the nearest public reference where sponsors have not disclosed a location. The register covers announced or under-construction Texas campuses at or above roughly 100 MW; it is not a complete census of regional load.`),
  ...exhibitImage("7.1"),
  pageBreak(),
);

// 08 Diligence Platform
w(
  eyebrow("08 · The Diligence Platform"),
  sectionHeading("Every figure in this Memorandum is independently verifiable, feature by feature"),
  lede("The data behind this Memorandum lives on a password-protected interactive GIS platform carrying the Property boundary, the regional generation fleet and ERCOT queue, transmission and planned upgrades, midstream networks, the announced campus land positions, permits and tax abatements, and the complete wellbore record used in Section 9. Layers refresh on weekly-to-monthly cadences from the primary sources registered in Appendix A.2, every feature carries its source citation in its popup, and map states can be shared as URLs that reproduce exact views, layers, and filters. The map exhibits in this Memorandum were captured directly from the platform. Access credentials and a navigation guide are provided in Appendix A.1."),
  table(["Property of the platform", "Why it matters for diligence"], [
    ["Source-cited features", "Every point, line, and boundary traces to a cited public dataset; per-feature citations in popups. Nothing is hand-placed except labeled reference toponyms; the single approximated boundary (the groundwater management zone) is disclosed as such."],
    ["Refresh discipline", "RRC wells/permits and abatements weekly; ERCOT queue and TPIT monthly; EIA/USGS/OSM annually on release."],
    ["Analytical tooling", "Field-level filters (wells by county/depth/spud year; queue by fuel/capacity/status), pre-built analytical views with exportable statistics, a time scrubber animating the drilling record by year, and measure/share/print tools."],
    ["Reproducibility", "Static, versioned build; the deployed bundle is byte-verified against the build on every release. Access is logged."],
  ], [0.30, 0.70]),
  pageBreak(),
);

// 09 Subsurface
const ev = S9.events, px = S9.proximity, ndd = S9.new_drilling, cmp = S9.comparison, pr = S9.production, ff = S9.fracfocus;
const b2 = ndd.bands["≤ 2 mi"], b5 = ndd.bands["≤ 5 mi"], b10 = ndd.bands["≤ 10 mi"];
const p10 = pr.radii["≤ 10 mi"];
w(
  eyebrow("09 · Subsurface & Drilling Activity"),
  sectionHeading("No new drilling is occurring at or near the site — and the public record proves it three independent ways"),
  lede(`This section reproduces the drilling-activity study of the tract and its ten-mile radius, prepared as vibration-context due diligence for data-center development. Counting only genuine new wells — wellbore records with recompletion re-stamps excluded — no new-drill well lies within five miles of the tract, only ${b10.count} sit within ten miles across 2020–present, and the public hydraulic-fracturing disclosure record shows no new-drill frack within two miles, ever. The wellbore record, the production record, and the fracturing disclosure record each independently support the same conclusion.`),
  statsRow([
    [String(b2.count), "New-drill wells within 2 mi since 2020"],
    [String(b5.count), "New-drill wells within 5 mi since 2020"],
    [String(b10.count), `New-drill wells within 10 mi${b10.nearest ? ` — nearest ${b10.nearest} mi` : ""}`],
  ]),
  statsRow([
    [String(ff.bands["0 – 2 mi"].count), "New-drill fracks within 2 mi, ever"],
    [String(px.shallow_spud_max), "Most recent shallow spud within 2 mi"],
    [`${ev.new_drill_pct}%`, "Share of 2020+ Pecos wellbore events that are new drilling"],
  ]),
  subHeading("9.1  On the tract itself: legacy completions, no modern shallow drilling"),
  body("The wellbores recorded inside the tract boundary are decades-old completions. The table below is the complete record."),
  table(["Depth (ft)", "Spud year", "Status", "Oil / gas"], S9.tract_wellbores.map(t => [
    fmt(t.depth_ft), String(t.spud_year), t.plugged ? "Plugged & abandoned" : (t.active ? "Active" : "Not plugged"),
    t.oil_gas === "G" ? "Gas" : "Oil",
  ]), [0.25, 0.25, 0.30, 0.20], { align: ["right", "right", "left", "left"] }),
  subHeading(`9.2  Pecos "drilling activity" is ~${100 - ev.new_drill_pct}% rework of existing wells, not new drilling`),
  body(`The Railroad Commission of Texas maintains a master wellbore database (dbf900) in which every drilling, completion, and workover event is logged against a unique API well number. Tracing every Pecos wellbore with any recorded activity since 2020: of ${fmt(ev.total)} wellbore-record events, only ≈ ${ev.new_drill_pct}% (${ev.new_drill}) are genuine new drilling. The remaining ≈ ${100 - ev.new_drill_pct}% (${fmt(ev.rework)}) are recompletion or workover events on existing wellbores. A workover rig on an existing bore is not the drilling-and-fracturing activity associated with ground vibration, and the program is not near the site.`),
  pageBreak(),
  subHeading("9.3  Proximity: drilling near the tract ended over two decades ago"),
  body(`Within one mile — ${px.wellbores_within_1mi} wellbores of any depth; ${px.shallow_within_1mi || "none"} shallow (< 3,000 ft). Within two miles — of ${px.wellbores_within_2mi} wellbores, the ${px.shallow_within_2mi} shallow wells were spudded ${px.shallow_spud_min}–${px.shallow_spud_max}; most are plugged and abandoned. The nearest non-plugged shallow wells were spudded ${px.nearest_nonplugged_shallow.map(n => `${n.spud_year} (${n.miles} mi)`).join(" and ")} — decades-old completions, not active drilling.`),
  subHeading("9.4  New drilling since 2020, by distance and depth"),
  body(`Counting only genuine new wells drilled in Pecos since 2020 (recompletion re-stamps excluded), the activity is deep and remote. The ${fmt(ndd.beyond_10mi.count)} new wells beyond ten miles sit at a median distance of ≈ ${ndd.beyond_10mi.median_mi} miles (max ${ndd.beyond_10mi.max_mi}), and the great majority are deep — the modern Permian unconventional program.`),
  table(["Radius", "New-drill wells, spudded ≥ 2020"], [
    ["≤ 2 mi", String(b2.count)],
    ["≤ 5 mi", String(b5.count)],
    ["≤ 10 mi", `${b10.count}${b10.nearest ? ` (nearest ≈ ${b10.nearest} mi)` : ""}`],
    ["> 10 mi", `${fmt(ndd.beyond_10mi.count)} (median ${ndd.beyond_10mi.median_mi} mi, max ${ndd.beyond_10mi.max_mi} mi)`],
    ["County-wide total", fmt(ndd.county_total)],
  ], [0.5, 0.5], { align: ["left", "right"], totalRowIndex: 4 }),
  table(["Depth band (wells > 10 mi)", "Wells", "Share"], Object.entries(ndd.depth_bands).map(([k, v]) => {
    const tot = Object.values(ndd.depth_bands).reduce((a, b) => a + b, 0) || 1;
    return [k, String(v), `${Math.round((100 * v) / tot)}%`];
  }), [0.5, 0.25, 0.25], { align: ["left", "right", "right"] }),
);
if (ndd.rule_h_boundary_within_10mi && ndd.rule_h_boundary_within_10mi.length) {
  const bd = ndd.rule_h_boundary_within_10mi;
  const detail = bd.map(b => `${b.miles} mi, spud ${b.spud_year}, completion ${b.completion_year}, ${fmt(b.depth_ft)} ft`).join("; ");
  w(flagBox(`${bd.length} wellbore(s) within ten miles carry a completion year exactly one year before a 2020-or-later spud year (${detail}). The locked recompletion filter excludes them from the new-drill counts above. They are disclosed here because a reader comparing against an earlier vintage of this study will see them counted as new drills.`));
}
const peerMax = Math.max(...Object.values(cmp.counties).map(v => v.new_drill)) || 1;
w(
  subHeading("9.5  County-wide, Pecos has a fraction of the new drilling of its peers"),
  body(`On the same genuine-new-drill basis, Pecos — at ≈ 4,700 square miles — has dramatically less new drilling than comparable Permian counties. Its ${cmp.counties.Pecos.new_drill} new wells since 2020 are a small fraction of the comparable-county average (≈ ${fmt(cmp.peer_average)}). Genuine new shallow drilling is negligible in every county.`),
  table(["County", "New-drill wells since 2020 (shallow)"],
    Object.entries(cmp.counties).sort((a, b) => a[1].new_drill - b[1].new_drill)
      .map(([c, v]) => [c + (c === "Pecos" ? " (site county)" : ""), `${fmt(v.new_drill)} (${v.shallow} shallow)`]),
    [0.5, 0.5], { align: ["left", "right"] }),
  note("New-drill wells spudded since 2020 (shallow < 3,000 ft in parentheses). RRC dbf900, genuine-new-drill basis. Howard and Loving lie outside the six-county sale-area set and are included only to broaden the comparison."),
  pageBreak(),
  subHeading(`9.6  Production near the site is decades-old completions — ${p10.marginal_pct}% marginal or end-of-life`),
  body(`Every well was additionally cross-referenced against the Railroad Commission's production records, joined by API number. A well is treated as "marginal or end-of-life" when its trailing-average output is at or below ${fmt(C.marginal_gas_mcf_d)} Mcf/day of gas and at or below ${fmt(C.marginal_oil_bbl_d)} bbl/day of oil — a strict marginal-well threshold.`),
  body(`Of the ${fmt(p10.nonplugged)} non-plugged wellbores within ten miles of the tract, ${fmt(p10.marginal)} (≈ ${p10.marginal_pct}%) are marginal or end-of-life. These are not new drilling: they are decades-old completions that have depleted over 30–60 years of production. The vintage distribution makes the point.`),
  table(["Radius", "Non-plugged wellbores", "Marginal / EOL", "Share"], Object.entries(pr.radii).map(([k, v]) =>
    [k, fmt(v.nonplugged), fmt(v.marginal), `${v.marginal_pct}%`]), [0.30, 0.28, 0.24, 0.18],
    { align: ["left", "right", "right", "right"] }),
  table(["Spud decade", "Non-plugged wellbores ≤ 10 mi"], Object.entries(pr.vintage).map(([k, v]) => [k, String(v)]),
    [0.5, 0.5], { align: ["left", "right"] }),
  note("Spud-decade distribution of the non-plugged wellbores within ten miles."),
  subHeading("9.7  The public fracking record independently confirms the wellbore record"),
  body(`The Texas FracFocus disclosure database is the public record of every hydraulic-fracturing job filed in Texas since 2011. Every Pecos County disclosure (${fmt(ff.pecos_disclosures)} in total) was cross-referenced against the RRC wellbore record by API number to exclude re-fracs on existing wells; the figures below are confirmed new-drill fracks only — a frack performed at the original completion of a newly drilled wellbore.`),
  table(["Distance band from tract", "New-drill fracks (2011–present)", "Most recent"], Object.entries(ff.bands).map(([k, v]) =>
    [k, String(v.count), v.latest ? String(v.latest) : "— none, ever"]), [0.4, 0.3, 0.3], { align: ["left", "right", "right"] }),
  body(`No new-drill hydraulic-fracturing job has ever been performed within two miles of the tract. The broader Permian program does exist — ${fmt(ff.within_20mi_total)} new-drill fracks within twenty miles since 2011, dominated by the deep-horizontal unconventional players (${ff.top_operators.slice(0, 3).map(([o, n]) => `${o} ${n}`).join(", ")}) — but it is concentrated outside the ten-mile buffer, almost entirely at unconventional depths.`),
);
w(new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  rows: [new TableRow({ children: [new TableCell({
    shading: { type: ShadingType.CLEAR, fill: "FEF7F7" }, borders: allBorders(9, RED),
    margins: { top: 200, bottom: 200, left: 220, right: 220 },
    children: [
      new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: "BOTTOM LINE — SECTION 9", bold: true, size: 15, color: RED, characterSpacing: 25 })] }),
      new Paragraph({ spacing: { after: 100 }, children: [new TextRun({ text: "Whether the question is framed as shallow drilling, hydraulic fracturing, or new drilling of any kind, three independent public records point the same way: it is not happening at or near this site.", bold: true, size: 22, color: NAVY })] }),
      new Paragraph({ children: [new TextRun({ text: "Wellbore record (RRC dbf900) · production record (RRC, API-matched) · fracturing disclosures (FracFocus, API-cross-referenced). Method detail and thresholds are stated in-line above; sources in Appendix A.2.", size: 15, color: MUTED })] }),
    ],
  })] })],
}));
w(pageBreak());

// Appendix A.1
const exlist = EXHIBITS.map(e => [`Exhibit ${e.id}`, e.title, e.captured]);
w(
  eyebrow("Appendix A.1", true),
  sectionHeading("GIS Platform — Access & Navigation"),
  table(["Access", "Detail"], [
    ["URL", "https://lrp-tx-gis.netlify.app"],
    ["Login", "Business email + access password (issued to the deal team separately)"],
    ["Notes", "No installation; desktop Chrome/Edge/Safari recommended. Sessions persist per browser. Access is logged; credentials are for the deal team only."],
  ], [0.22, 0.78]),
  subHeading("Layout"),
  body("Left sidebar — layer groups with individual on/off toggles and live feature counts. High-density layers activate as you zoom in. Top bar — Measure (distance/area), Reset (default view), Share (copies a URL capturing your exact view, layers, and filters — the standard way to circulate a specific exhibit), Print (landscape print/PDF). Basemaps — Esri World Imagery (default), Carto Light (best for dense layer work). Popups — click any feature for its attributes with source and as-of date."),
  subHeading("Analysis tools"),
  body("Filters — wells by county/depth/spud year; the ERCOT queue by fuel/capacity/status; permits by operator. Views — pre-built analytical views of the drilling record with exportable summary statistics. Time scrubber — animates the well record by year."),
  subHeading("Exhibit provenance"),
  table(["Exhibit", "Title", "Captured"], exlist, [0.14, 0.66, 0.20]),
  pageBreak(),
);

// Appendix A.2
const footnotes = [
  ["1", "PUCT Order approving three 765 kV import paths, April 24, 2025 — Permian Basin Reliability Plan, Project No. 55718. interchange.puc.texas.gov (No. 55718)"],
  ["2", "AEP Texas / CPS Energy, Howard–Solstice Transmission Line Project; PUCT Docket 59366. interchange.puc.texas.gov (No. 59366)"],
  ["3", "ERCOT Permian Basin Reliability Plan Study, July 2024; PBRP approved September 2024. ercot.com/gridinfo/planning"],
  ["4", "ERCOT Long-Term Load Forecast. ercot.com/gridinfo/load/forecast"],
  ["5", "Apex Clean Energy disclosures, Pecos Flats project area. apexcleanenergy.com"],
  ["6", "EIA Form 860; USGS/LBNL U.S. Wind Turbine Database; project-level GIS analysis. eia.gov/electricity/data/eia860"],
  ["7", "ERCOT GIS Report of projects in the Generator Interconnection Queue. ercot.com/gridinfo/resource"],
  ["8", "TCEQ Air Permit filings; sponsor press releases, 2025–2026. tceq.texas.gov/permitting/air"],
  ["9", "ERCOT Generator Interconnection Queue entries, Longfellow cluster, Pecos County."],
  ["10", "Middle Pecos Groundwater Conservation District — permit registry and district rules. middlepecosgcd.org"],
  ["11", "Railroad Commission of Texas, dbf900 Full Wellbore ASCII master file (weekly release), genuine-new-drill basis: every event tagged to a unique API number; recompletion/workover re-stamps excluded. rrc.texas.gov"],
  ["12", "RRC production records joined by API number. Marginal threshold: ≤ 125 Mcf/d gas AND ≤ 25 bbl/d oil, trailing average. webapps.rrc.texas.gov/PDQ"],
  ["13", "FracFocus Chemical Disclosure Registry, Texas disclosures 2011–present, API-cross-referenced against the RRC wellbore record to isolate new-drill fracks. fracfocus.org"],
];
const register = [
  ["County / highway reference", "U.S. Census TIGER/Line 2023", "Static", "census.gov"],
  ["Rail", "BTS North American Rail Network", "Static", "geodata.bts.gov"],
  ["Plants, batteries, solar", "EIA-860 annual + generator detail", "Annual", "eia.gov"],
  ["Wind turbines", "USGS/LBNL U.S. Wind Turbine Database", "Annual", "eerscmap.usgs.gov/uswtdb"],
  ["Transmission; NG/crude/NGL pipelines; processing", "EIA U.S. Energy Atlas (HIFLD)", "Annual", "atlas.eia.gov"],
  ["Substations", "OpenStreetMap", "Annual", "openstreetmap.org"],
  ["Interconnection queue", "ERCOT GIS Report", "Monthly", "ercot.com/gridinfo/resource"],
  ["Planned grid upgrades", "ERCOT TPIT", "Monthly", "ercot.com/gridinfo/transmission"],
  ["Wellbore & permit record", "RRC public datasets (dbf900, W-1)", "Weekly", "rrc.texas.gov"],
  ["Large-diameter pipelines", "RRC digital pipeline data", "Annual", "rrc.texas.gov/pipeline-safety"],
  ["Air permits", "TCEQ air permitting records", "Annual", "tceq.texas.gov/permitting/air"],
  ["Tax abatements (Ch. 381/312)", "County commissioners-court records (compiled)", "Weekly", "County clerk agendas"],
  ["Groundwater district", "Middle Pecos GCD (zone boundary approximate, disclosed)", "On publication", "middlepecosgcd.org"],
];
w(
  eyebrow("Appendix A.2", true),
  sectionHeading("Footnotes, References & Sources"),
  subHeading("Numbered footnotes"),
  table(["#", "Reference"], footnotes, [0.06, 0.94], { align: ["right", "left"] }),
  subHeading("General source register (GIS platform layers)"),
  table(["Domain", "Source", "Cadence", "Link"], register, [0.28, 0.32, 0.14, 0.26]),
  note(`Distances stated in this Memorandum are straight-line from the tract centroid unless labeled otherwise. Map exhibits were captured from the companion GIS platform on the dates shown in Appendix A.1. Every figure in Sections 3, 4, 7 and 9 is derived programmatically from the layer data at build time; the indicative gas terms in Section 6 and the permitted water volume in Section 5 are counterparty-supplied and identified as such. Compiled ${STAMP}.`),
  pageBreak(),
);

// Appendix A.3
const notices = [
  `This Confidential Offering Memorandum (the "Memorandum") has been prepared solely for the use of a limited number of prospective counterparties, under executed non-disclosure agreement, in connection with the potential acquisition of, or investment in, the Caramba North property (the "Property"). The Memorandum contains proprietary data of Harvest Energy, LLC and is delivered on a strictly confidential basis. By accepting this Memorandum, the recipient agrees that it will not be reproduced or distributed, in whole or in part, to any other person, and that the information contained herein will be used solely for the purpose of evaluating the potential transaction described.`,
  `This Memorandum does not constitute an offer to sell or a solicitation of an offer to buy any security or interest. Any such offer or solicitation will be made only by means of definitive transaction documents and in compliance with applicable law. The information contained in this Memorandum is preliminary and indicative, has been compiled from sources believed to be reliable, and is subject to revision, correction, completion, and update without notice. No representation or warranty, express or implied, is made as to the accuracy or completeness of any information set forth herein.`,
  `Public data referenced in this Memorandum is drawn from ERCOT, the Public Utility Commission of Texas, the U.S. Energy Information Administration, the Texas Commission on Environmental Quality, the Railroad Commission of Texas, the FracFocus Chemical Disclosure Registry, the Middle Pecos Groundwater Conservation District, HIFLD, USGS, BTS, and U.S. Census TIGER, supplemented by project-level GIS analysis and counterparty-supplied indicative terms. Distances stated are straight-line from property boundary or centroid, as labeled. Forward-looking statements are subject to risks, uncertainties, and assumptions.`,
  `Recipients should conduct their own independent investigation and analysis of the Property, the transaction, and the matters referred to in this Memorandum, including consultation with their own legal, tax, accounting, engineering, and other professional advisors. Any and all liability for representations or warranties, express or implied, contained in, or for omissions from, this Memorandum or any other written or oral communications transmitted to a prospective counterparty in the course of its evaluation of the transaction is expressly disclaimed.`,
];
w(
  eyebrow("Appendix A.3", true),
  sectionHeading("Important Notices"),
  ...notices.map(t => new Paragraph({ spacing: { after: 180 }, alignment: AlignmentType.JUSTIFIED,
    children: [new TextRun({ text: t, size: 16, color: "24354C" })] })),
);

// ---------------------------------------------------------------- assemble
const doc = new Document({
  creator: "Land Resource Partners",
  title: "Caramba North — Confidential Offering Memorandum (Post-NDA)",
  styles: { default: { document: { run: { font: "Calibri" } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1000, bottom: 1000, left: 1080, right: 1080 },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then(buf => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, buf);
  console.log(`docx  -> ${path.relative(REPO, OUT)}  (${Math.round(buf.length / 1024)} KB)`);
});
