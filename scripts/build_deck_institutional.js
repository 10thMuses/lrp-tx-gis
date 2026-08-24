#!/usr/bin/env node
/* Caramba North — "Institutional / Banker" deck (brief §6.A).
 *
 * Sharpened navy/[accent]/Calibri institutional system: denser stat tiles,
 * more tables, a full slide for the ring-analysis table + power-gravity
 * diagram (brief §2.6). Every heading carries an insight subheading
 * directly beneath it in a smaller italic serif treatment (Rule 2).
 *
 * Per brief §8 ("reds are reserved for the two feature call-outs"): the
 * general accent here is a bronze/gold institutional tone; true red is
 * used only on the GW Ranch and Longfellow feature slides.
 *
 * Data: scripts/caramba_om_data.py (core model) + scripts/build_insight_pack.py
 * (ring analysis, project maturity, corrected edge-to-edge distances).
 * Uses unique tmp json paths per brief §7a.
 *
 *   node scripts/build_deck_institutional.js
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const pptxgen = require("pptxgenjs");

const REPO = path.resolve(__dirname, "..");
const EXHIBIT_DIR = path.join(REPO, "outputs", "reports", "om_exhibits");
const ICON_DIR = path.join(EXHIBIT_DIR, "icons");
const OUT = path.join(REPO, "outputs", "reports", "Caramba-North-Deck-Institutional.pptx");

const CORE_JSON = "/tmp/om_institutional_core.json";
const INSIGHT_JSON = "/tmp/om_institutional_insights.json";
execFileSync("python3", [path.join(REPO, "scripts", "caramba_om_data.py"), "--json", CORE_JSON], { cwd: REPO });
execFileSync("python3", [path.join(REPO, "scripts", "build_insight_pack.py"), "--json", INSIGHT_JSON], { cwd: REPO });
const M = JSON.parse(fs.readFileSync(CORE_JSON, "utf8"));
const INS = JSON.parse(fs.readFileSync(INSIGHT_JSON, "utf8"));
const { config: C, section3: S3, section4: S4, section7: S7, section9: S9 } = M;
const STAMP = new Date().toISOString().slice(0, 10);

// Corrected edge-to-edge distances (brief Rule 4) — never the centroid figures.
const GWR_MI = INS.distances_edge_to_edge.gw_ranch_mi;       // 15.5
const LF_MI = INS.distances_edge_to_edge.longfellow_mi;      // 19.3
const MATURITY = INS.project_maturity;
const RINGS = INS.ring_analysis;
const R60 = RINGS[2].total_gw.toFixed(1); // 60-mile combined GW, one decimal for display

// ------------------------------------------------------------------ palette
// Navy stays the anchor neutral throughout. General accent is a bronze/gold
// institutional tone; true red is reserved for the two feature call-outs
// (brief §8), matching this deck's "Institutional / Banker" identity while
// keeping red as a signal color, not decoration.
const NAVY = "0F1B2D", NAVY2 = "16202E", SLATE = "3D4E63", MUTED = "64748B";
const GOLD = "9C6B14", GOLD_DK = "7A5310";
const RED = "B91C1C", RED_DK = "7F1D1D";
const ICE = "CADCFC", LIGHT = "F1F5F9", LIGHT2 = "E7ECF3", LINE = "DCE3EC", WHITE = "FFFFFF";
const FLAG = "FEF9EC", FLAG_LINE = "D9B36C", FLAG_TXT = "6B4A17";

const PW = 13.333, PH = 7.5;

function fmt(n) { if (n === null || n === undefined) return "—"; return Math.round(n).toLocaleString("en-US"); }
function gw(mw) { if (mw === null || mw === undefined) return "—"; return mw >= 1000 ? (mw / 1000).toFixed(1) + " GW" : fmt(mw) + " MW"; }
function shadow(opacity) { return { type: "outer", color: "0F1B2D", opacity: opacity || 0.15, blur: 7, offset: 2, angle: 90 }; }

const EXHIBITS = {
  "2.1": { file: "exhibit_2_1_site-setting.jpg", w: 2400, h: 1500 },
  "3.1": { file: "exhibit_3_1_planned-grid-upgrades.jpg", w: 2400, h: 1374 },
  "4.1": { file: "exhibit_4_1_generation-cluster.jpg", w: 2400, h: 1374 },
  "7.1": { file: "exhibit_7_1_masked.jpg", w: 2400, h: 1374 },
  "amz": { file: "exhibit_amz_gwranch.jpg", w: 1410, h: 540 },
  "lf": { file: "exhibit_longfellow.jpg", w: 880, h: 315 },
  "gravity_light": { file: "exhibit_power_gravity_light.png", w: 1517, h: 1517 },
  "gravity_dark": { file: "exhibit_power_gravity_dark.png", w: 1517, h: 1517 },
};

// ------------------------------------------------------------------ icons
function iconData(key) {
  const fp = path.join(ICON_DIR, `${key}.png`);
  return "image/png;base64," + fs.readFileSync(fp).toString("base64");
}
const ICON_CACHE = {};
function icon(key) {
  if (!ICON_CACHE[key]) ICON_CACHE[key] = iconData(key);
  return ICON_CACHE[key];
}

// ------------------------------------------------------------------ helpers
function darkSlide(pres) {
  const s = pres.addSlide();
  s.background = { color: NAVY };
  return s;
}
function lightSlide(pres) {
  const s = pres.addSlide();
  s.background = { color: WHITE };
  return s;
}
function footer(s, n, dark) {
  const col = dark ? "8291A6" : MUTED;
  s.addText("CARAMBA NORTH  ·  CONFIDENTIAL OFFERING MEMORANDUM", {
    x: 0.6, y: PH - 0.4, w: 8, h: 0.3, fontSize: 8, color: col, fontFace: "Calibri", charSpacing: 0.5,
  });
  s.addText(String(n), { x: PW - 1.1, y: PH - 0.4, w: 0.5, h: 0.3, fontSize: 8, color: col, align: "right", fontFace: "Calibri" });
}
function iconBadge(s, key, x, y, size, bg) {
  s.addShape("ellipse", { x, y, w: size, h: size, fill: { color: bg || GOLD }, line: { type: "none" }, shadow: shadow() });
  const pad = size * 0.27;
  s.addImage({ data: "data:" + icon(key), x: x + pad, y: y + pad, w: size - pad * 2, h: size - pad * 2 });
}
function eyebrow(s, iconKey, text, opts = {}) {
  const accent = opts.color || GOLD;
  if (iconKey) iconBadge(s, iconKey, 0.6, 0.32, 0.42, opts.badgeColor || accent);
  s.addText(text.toUpperCase(), {
    x: iconKey ? 1.16 : 0.6, y: 0.34, w: 10.5, h: 0.38, fontSize: 11.5, bold: true, color: accent,
    charSpacing: 2, fontFace: "Calibri", valign: "middle",
  });
}
// Title + insight subheading directly beneath it (Rule 2), in a smaller
// italic serif treatment, per the institutional style brief.
function titleBlock(s, titleText, subheadText, opts = {}) {
  s.addText(titleText, {
    x: 0.6, y: 0.86, w: 12.1, h: opts.titleH || 0.72, fontSize: opts.titleSize || 22, bold: true,
    color: opts.titleColor || NAVY, fontFace: "Cambria", valign: "top", lineSpacingMultiple: 1.02,
  });
  s.addText(subheadText, {
    x: 0.6, y: opts.subY || 1.52, w: 12.1, h: opts.subH || 0.62, fontSize: opts.subSize || 12.5, italic: true,
    color: opts.subColor || SLATE, fontFace: "Cambria", valign: "top", lineSpacingMultiple: 1.05,
  });
}
function statTile(s, x, y, w, h, value, label, opts = {}) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.05, fill: { color: opts.fill || LIGHT }, line: { color: LINE, width: 0.75 }, shadow: shadow(0.1) });
  s.addText(String(value), {
    x: x + 0.12, y: y + 0.08, w: w - 0.24, h: h - 0.5, fontSize: opts.valSize || 18, bold: true,
    color: opts.valColor || NAVY, fontFace: "Calibri", valign: "bottom",
  });
  s.addText(label.toUpperCase(), {
    x: x + 0.12, y: y + h - 0.4, w: w - 0.24, h: 0.36, fontSize: 7.3, color: MUTED, charSpacing: 0.5,
    fontFace: "Calibri", valign: "top", lineSpacingMultiple: 0.95,
  });
}
function tableStyled(s, headers, rows, opts) {
  const fs_ = opts.fontSize || 9.5;
  const headerRow = headers.map((h, i) => ({
    text: h.toUpperCase(), options: {
      bold: true, fontSize: fs_ - 0.5, color: WHITE, fill: { color: opts.headerFill || NAVY }, fontFace: "Calibri",
      align: (opts.align && opts.align[i] === "right") ? "right" : "left",
    },
  }));
  const body = rows.map((r, ri) => r.map((c, ci) => ({
    text: c, options: {
      fontSize: fs_, color: NAVY2, fontFace: "Calibri",
      bold: opts.totalRowIndex === ri,
      fill: opts.totalRowIndex === ri ? { color: LIGHT2 } : (ri % 2 === 1 ? { color: "F8FAFC" } : { color: WHITE }),
      align: (opts.align && opts.align[ci] === "right") ? "right" : "left",
    },
  })));
  s.addTable([headerRow, ...body], Object.assign({
    x: opts.x, y: opts.y, w: opts.w, colW: opts.colW,
    border: { type: "solid", color: LINE, pt: 0.5 },
    autoPage: false, valign: "middle", margin: [0.035, 0.08, 0.035, 0.08],
  }, opts.tableOpts || {}));
}
function exhibitImage(s, id, x, y, w) {
  const e = EXHIBITS[id];
  const fp = path.join(EXHIBIT_DIR, e.file);
  if (!fs.existsSync(fp)) return 0;
  const h = w * (e.h / e.w);
  s.addImage({ path: fp, x, y, w, h, shadow: shadow() });
  s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: LINE, width: 1 } });
  return h;
}
function caption(s, x, y, w, text) {
  s.addText(text, { x, y, w, h: 0.5, fontSize: 9, italic: true, color: MUTED, fontFace: "Calibri" });
}
function iconRow(s, iconKey, x, y, w, rowH, heading, body, accent) {
  iconBadge(s, iconKey, x, y + (rowH - 0.46) / 2, 0.46, accent || GOLD);
  s.addText(heading, { x: x + 0.62, y, w: w - 0.62, h: rowH * 0.46, fontSize: 12, bold: true, color: NAVY, valign: "bottom", fontFace: "Calibri" });
  s.addText(body, { x: x + 0.62, y: y + rowH * 0.44, w: w - 0.62, h: rowH * 0.56, fontSize: 9.7, color: SLATE, valign: "top", fontFace: "Calibri", lineSpacingMultiple: 0.98 });
}
function flagBox(s, x, y, w, h, label, text) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.04, fill: { color: FLAG }, line: { color: FLAG_LINE, width: 1 } });
  s.addText([
    { text: label + " — ", options: { bold: true, color: FLAG_TXT } },
    { text: text, options: { color: FLAG_TXT } },
  ], { x: x + 0.16, y: y + 0.06, w: w - 0.32, h: h - 0.12, fontSize: 9, fontFace: "Calibri", valign: "middle", lineSpacingMultiple: 1.02 });
}

// ==================================================================== main
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
  pres.author = "Land Resource Partners";
  pres.title = "Caramba North — Confidential Offering Memorandum (Institutional)";

  // ---------------------------------------------------------------- 1. COVER
  {
    const s = darkSlide(pres);
    s.addText("STRICTLY CONFIDENTIAL  ·  OFFERING MEMORANDUM", {
      x: 0.7, y: 0.75, w: 8, h: 0.4, fontSize: 12.5, bold: true, color: "D4A73D", charSpacing: 2.2, fontFace: "Calibri",
    });
    s.addText("CARAMBA NORTH", { x: 0.65, y: 1.12, w: 8.2, h: 1.3, fontSize: 52, bold: true, color: WHITE, fontFace: "Cambria" });
    s.addText(
      `A ${fmt(C.acres_max)}-acre powered land position on the same north–south line as two hyperscale-scale power campuses — ${GWR_MI} and ${LF_MI} miles out — inside a ${R60} GW regional cluster already forming around it.`,
      { x: 0.7, y: 2.42, w: 7.1, h: 1.65, fontSize: 14, italic: true, color: ICE, fontFace: "Cambria", valign: "top", lineSpacingMultiple: 1.18, wrap: true }
    );
    s.addText("PECOS COUNTY, TEXAS  ·  FAR WEST ERCOT  ·  PERMIAN BASIN  ·  I-10 CORRIDOR", {
      x: 0.7, y: 3.95, w: 7.5, h: 0.4, fontSize: 10, color: "8291A6", charSpacing: 1.5, fontFace: "Calibri",
    });
    // Flagship power-gravity diagram, right side.
    const gx = 8.05, gy = 0.95, gsz = 5.65;
    s.addImage({ path: path.join(EXHIBIT_DIR, EXHIBITS.gravity_dark.file), x: gx, y: gy, w: gsz, h: gsz });
    caption(s, gx, gy + gsz + 0.02, gsz, "Exhibit — regional power-gravity, radius rings from the tract.");

    const stats = [
      [fmt(C.acres_max), "Contiguous acres"], [fmt(C.water_af_yr), "AF/yr water rights"],
      [`${C.solstice_miles} mi`, "To 765 kV Solstice sub"], [`${C.waha_miles} mi`, "To Waha gas hub"],
      [`${R60} GW`, "Operating + queue, ≤60 mi"],
    ];
    s.addShape("line", { x: 0.7, y: 4.55, w: 7.0, h: 0, line: { color: "2A3A50", width: 1 } });
    const tw2 = 7.0 / stats.length;
    stats.forEach(([v, k], i) => {
      const x = 0.7 + i * tw2;
      s.addText(v, { x, y: 4.7, w: tw2 - 0.12, h: 0.5, fontSize: 17, bold: true, color: WHITE, fontFace: "Calibri" });
      s.addText(k.toUpperCase(), { x, y: 5.18, w: tw2 - 0.12, h: 0.55, fontSize: 7.3, color: "8291A6", charSpacing: 0.3, fontFace: "Calibri", lineSpacingMultiple: 0.95 });
    });
    s.addShape("line", { x: 0.7, y: 5.85, w: 7.0, h: 0, line: { color: "2A3A50", width: 1 } });
    s.addText("Prepared by Land Resource Partners  ·  lrp-tx-gis.netlify.app", {
      x: 0.7, y: 6.0, w: 6.0, h: 0.4, fontSize: 9.5, color: "8291A6", fontFace: "Calibri",
    });
    s.addText(`${STAMP}  ·  Institutional deck`, {
      x: 0.7, y: 6.32, w: 6.0, h: 0.35, fontSize: 9.5, color: "8291A6", fontFace: "Calibri",
    });
    footer(s, 1, true);
  }

  // ---------------------------------------------------------------- 2. CONTENTS
  {
    const s = lightSlide(pres);
    eyebrow(s, "landmark", "Contents");
    titleBlock(s, "Eighteen sections, property through appendix",
      "Every stat in this deck traces to the source register in the closing appendix — this is a data-room summary, not a broker narrative.");
    const items = [
      ["dollar", "03  Investment Thesis"], ["chart", "04  Executive Summary"],
      ["mappin", "05  The Property"], ["tower", "06  Transmission"],
      ["industry", "07  Regional Power Cluster"], ["ring", "08  Ring Analysis / Power-Gravity"],
      ["server", "09  Regional Data-Center Pipeline"], ["handshake", "10  Feature — GW Ranch (Amazon)"],
      ["gaspump", "11  Feature — Longfellow"], ["droplet", "12  Water"],
      ["fire", "13  Natural Gas"], ["trendup", "14  Macro Context — ERCOT Backlog"],
      ["shield", "15  The Diligence Platform"], ["gauge", "16  Subsurface & Drilling Activity"],
      ["building", "17  Appendix — Distances & Sources"], ["alert", "18  Important Notices"],
    ];
    const colW = 5.9, rowH = 0.52;
    items.forEach(([ic, t], i) => {
      const col = i < 8 ? 0 : 1;
      const row = i < 8 ? i : i - 8;
      const x = 0.6 + col * (colW + 0.5), y = 2.35 + row * rowH;
      iconBadge(s, ic, x, y + 0.02, 0.38, GOLD);
      s.addText(t, { x: x + 0.52, y, w: colW - 0.52, h: 0.44, fontSize: 13.5, bold: true, color: NAVY, fontFace: "Calibri", valign: "middle" });
    });
    footer(s, 2);
  }

  // ---------------------------------------------------------------- 3. INVESTMENT THESIS
  {
    const s = lightSlide(pres);
    eyebrow(s, "dollar", "03 · Investment Thesis");
    titleBlock(s, "Inside the corridor, not adjacent to it",
      "Two hyperscale-scale projects — 7.65 GW and 2 GW — sit on the same north–south line through the property at 15.5 and 19.3 miles; the region's own numbers do the selling, not the site's.");
    const body = `Caramba North is not a speculative land bet — it is a ${fmt(C.acres_max)}-acre parcel sitting inside an already-forming power and data-center corridor. The region's own numbers do the selling: ${R60} GW of operating and queued power capacity within 60 miles, in a state where the interconnection backlog just got large enough to trigger a gubernatorial audit and a queue-processing pause. Caramba North is positioned to benefit from the same infrastructure buildout without carrying the exposure of being the marginal, unproven project in that queue — it already has water and gas under contract-ready terms, not just an application.`;
    s.addShape("roundRect", { x: 0.6, y: 2.45, w: 12.1, h: 1.85, rectRadius: 0.05, fill: { color: LIGHT }, line: { color: LINE, width: 0.75 } });
    s.addText(body, { x: 0.85, y: 2.6, w: 11.6, h: 1.55, fontSize: 12.5, color: NAVY2, fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.16 });

    const stats = [
      [fmt(C.acres_max), "Max contiguous acres"], [`${GWR_MI} mi`, "To GW Ranch, edge-to-edge"],
      [`${LF_MI} mi`, "To Longfellow, edge-to-edge"], [`${R60} GW`, "Operating + queue, ≤60 mi"],
      [fmt(C.water_af_yr), "AF/yr water, contract-ready"], [`${MATURITY.under_construction.pct_of_local_mw}%`, "Of announced local MW under construction"],
    ];
    const tw = (12.1 - 5 * 0.18) / 6;
    stats.forEach(([v, k], i) => statTile(s, 0.6 + i * (tw + 0.18), 4.55, tw, 1.55, v, k));
    footer(s, 3);
  }

  // ---------------------------------------------------------------- 4. EXECUTIVE SUMMARY
  {
    const s = lightSlide(pres);
    eyebrow(s, "chart", "04 · Executive Summary");
    titleBlock(s, "The numbers across every diligence track, on one page",
      "Ten figures spanning land, transmission, power, water, and gas — each sourced to the underlying data model, none of them estimated.");
    const stats = [
      [fmt(C.acres_max), "Contiguous acres, north of I-10"], [fmt(C.water_af_yr), "AF/yr water permitted"],
      [`${C.solstice_miles} mi`, "To 765 kV Solstice substation"], [`${C.waha_miles} mi`, "To Waha gas hub"],
      [gw(S4.pecos_queue_total_mw), "ERCOT queue, Pecos Co. alone"],
      [`${R60} GW`, "Operating + queue, ≤60 mi radius"],
      [`${GWR_MI} mi`, "To GW Ranch (7.65 GW permit)"],
      [`${LF_MI} mi`, "To Longfellow (2 GW planned)"],
      [`${MATURITY.under_construction.pct_of_local_mw}%`, "Of local announced MW under construction"],
      ["474 GW", "Statewide ERCOT backlog, Aug 2026"],
    ];
    const cols = 5, rows2 = 2, gap = 0.16;
    const tw = (12.1 - (cols - 1) * gap) / cols, th = 1.62;
    stats.forEach(([v, k], i) => {
      const col = i % cols, row = Math.floor(i / cols);
      statTile(s, 0.6 + col * (tw + gap), 2.5 + row * (th + gap), tw, th, v, k, { valSize: 19 });
    });
    footer(s, 4);
  }

  // ---------------------------------------------------------------- 5. THE PROPERTY
  {
    const s = lightSlide(pres);
    eyebrow(s, "mappin", "05 · The Property");
    titleBlock(s, "As-of-right industrial land, five miles from Fort Stockton",
      "No zoning ordinance inside ERCOT's fastest-growing large-load pocket — a permitting-timeline story, not a rezoning story.");
    const rows = [
      ["Size / configuration", `Up to ${fmt(C.acres_max)} contiguous acres, north side of I-10`],
      ["Access", "Direct I-10 frontage; long-haul fiber and rail proximate"],
      ["Municipal services", "Fort Stockton, ~5 mi — services and regional airport"],
      ["Land-use regime", "No zoning ordinance; industrial/energy uses as of right"],
      ["ERCOT weather zone", "Far West — ERCOT's highest-growth large-load pocket"],
      ["County", "Pecos County, Texas"],
    ];
    tableStyled(s, ["Attribute", "Detail"], rows, { x: 0.6, y: 2.15, w: 5.9, colW: [1.9, 4.0], fontSize: 10.5 });
    const h = exhibitImage(s, "2.1", 6.85, 2.15, 5.9);
    caption(s, 6.85, 2.15 + h + 0.1, 5.9, "Exhibit 2.1 — the Caramba North tract on the north side of I-10, five miles from Fort Stockton.");
    footer(s, 5);
  }

  // ---------------------------------------------------------------- 6. TRANSMISSION
  {
    const s = lightSlide(pres);
    eyebrow(s, "tower", "06 · Transmission");
    titleBlock(s, "Fifteen miles from the delivery point of all three approved 765 kV lines",
      "The transmission decision is already made, upstream of this site — six local substations sit within ten miles.");
    const rows = [
      ["Solstice Substation (AEP/CPS Energy)", `${C.solstice_miles} mi`, "Terminus of 3 PUCT-approved 765 kV Permian import paths (No. 55718, Apr 24 2025)"],
      ...S3.local_substations.map(x => [x.name.replace(" Substation", ""), `${x.miles} mi`, x.voltage.split(";").map(v => `${Math.round(v / 1000)} kV`).join("/")]),
      ["TPIT pipeline, ERCOT-wide", "—", `${S3.tpit_substation_upgrades} substation + ${S3.tpit_line_projects} line upgrades tracked (planned, not yet built)`],
    ];
    tableStyled(s, ["Element", "Distance", "Detail"], rows,
      { x: 0.6, y: 2.15, w: 7.15, colW: [2.35, 0.85, 3.95], align: ["left", "right", "left"], fontSize: 9.8 });
    const h = exhibitImage(s, "3.1", 8.0, 2.15, 4.75);
    caption(s, 8.0, 2.15 + h + 0.08, 4.75, "Exhibit 3.1 — planned grid upgrades only (ERCOT TPIT); Solstice terminus circled.");
    footer(s, 6);
  }

  // ---------------------------------------------------------------- 7. REGIONAL POWER CLUSTER
  {
    const s = lightSlide(pres);
    eyebrow(s, "industry", "07 · Regional Power Cluster");
    titleBlock(s, `${gw(S4.pecos_queue_total_mw)} already queued in Pecos County alone`,
      "Before counting the two hyperscale campuses profiled in the ring-analysis and feature pages — adjacent counties add 24,585 MW more.");
    const pop = S4.pecos_operating, pq = S4.pecos_queue;
    const rows = pop.map((o, i) => [o.tech, `${o.count} · ${gw(o.mw)}`, `${pq[i].count} · ${gw(pq[i].mw)}`])
      .concat([["Total, Pecos County", gw(S4.pecos_operating_total_mw), gw(S4.pecos_queue_total_mw)]]);
    tableStyled(s, ["Technology", "Operating", "ERCOT queue"], rows,
      { x: 0.6, y: 2.15, w: 5.9, colW: [1.7, 2.1, 2.1], align: ["left", "right", "right"], totalRowIndex: pop.length, fontSize: 10.2 });

    const rows2 = [
      ["Adjacent 6 counties*", gw(S4.adjacent_operating_total_mw), gw(S4.adjacent_queue_total_mw)],
      ["Within 20 mi (queue only)", "—", `13 proj · ${fmt(S4.queue_within_20mi_mw)} MW`],
    ];
    tableStyled(s, ["Ring", "Operating", "ERCOT queue"], rows2,
      { x: 0.6, y: 4.75, w: 5.9, colW: [1.7, 2.1, 2.1], align: ["left", "right", "right"], fontSize: 9.8 });
    caption(s, 0.6, 6.05, 5.9, `*Reeves, Crane, Ward, Upton, Ector, Crockett. Nearest operating storage: St. Gall Energy Storage I, 1.9 mi (103 MW BESS).`);

    const h = exhibitImage(s, "4.1", 6.85, 2.15, 5.9);
    caption(s, 6.85, 2.15 + h + 0.1, 5.9, "Exhibit 4.1 — operating fleet and ERCOT interconnection queue over one footprint.");
    footer(s, 7);
  }

  // ---------------------------------------------------------------- 8. RING ANALYSIS / POWER-GRAVITY (full slide)
  {
    const s = lightSlide(pres);
    eyebrow(s, "ring", "08 · Ring Analysis / Power-Gravity");
    titleBlock(s, "32.7 GW inside 60 miles — measured by radius, not by county line",
      "Region-wide operating + ERCOT-queue capacity, computed from the same EIA-860 and ERCOT-queue layers used throughout — not county-bounded.");

    const rows = RINGS.map(r => [`≤ ${r.radius_mi} mi`, `${r.operating_gw.toFixed(1)} GW`, `${r.queue_gw.toFixed(1)} GW`, `${r.total_gw.toFixed(1)} GW`]);
    tableStyled(s, ["Radius", "Operating", "ERCOT queue", "Combined"], rows,
      { x: 0.6, y: 2.35, w: 5.85, colW: [1.55, 1.5, 1.5, 1.3], align: ["left", "right", "right", "right"], fontSize: 12 });

    s.addShape("roundRect", { x: 0.6, y: 4.5, w: 5.85, h: 2.15, rectRadius: 0.05, fill: { color: LIGHT }, line: { color: LINE, width: 0.75 } });
    s.addText([
      { text: "Bearing:  ", options: { bold: true, color: NAVY } },
      { text: `GW Ranch sits almost due north (~19°) and Longfellow almost due south (~188°) of Caramba North — the property sits on the north–south line between them, not off to one side.`, options: { color: SLATE } },
    ], { x: 0.82, y: 4.65, w: 5.4, h: 1.0, fontSize: 10.5, fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.1 });
    s.addText([
      { text: "Maturity:  ", options: { bold: true, color: NAVY } },
      { text: `${MATURITY.under_construction.pct_of_local_mw}% of the two anchors' combined announced MW is already under construction (GW Ranch); ${MATURITY.seeking_tenant.pct_of_local_mw}% is planned / phase-1 (Longfellow) — the regional pipeline is majority-built, not majority-speculative.`, options: { color: SLATE } },
    ], { x: 0.82, y: 5.62, w: 5.4, h: 0.95, fontSize: 10.5, fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.1 });

    const gsz = 4.5;
    const gx = 7.65, gy = 2.1;
    s.addImage({ path: path.join(EXHIBIT_DIR, EXHIBITS.gravity_light.file), x: gx, y: gy, w: gsz, h: gsz });
    s.addText("Exhibit — power-gravity diagram: radius rings from Caramba North; GW Ranch and Longfellow at true bearing/distance.", {
      x: gx, y: gy + gsz + 0.04, w: gsz, h: 0.42, fontSize: 8.3, italic: true, color: MUTED, fontFace: "Calibri", lineSpacingMultiple: 0.98,
    });
    footer(s, 8);
  }

  // ---------------------------------------------------------------- 9. DATA CENTER PIPELINE
  {
    const s = lightSlide(pres);
    eyebrow(s, "server", "09 · Regional Data-Center Pipeline");
    titleBlock(s, `Two anchors, one corridor: ${S7.local_gw} GW of announced capacity within 60 miles`,
      `${MATURITY.under_construction.pct_of_local_mw}% of that combined capacity is already under construction — the regional pipeline is majority-built, not majority-speculative.`);
    const rows = [
      ["GW Ranch", "8,000-ac site, Pecos Co.", "7.65 GW (TCEQ air permit)", "Under construction", `${GWR_MI} mi`],
      ["Longfellow", "568-ac site, Pecos Co.", "2 GW planned (8-phase)", "Phase-1 site work underway", `${LF_MI} mi`],
    ];
    tableStyled(s, ["Project", "Site", "Capacity", "Status", "Distance"], rows,
      { x: 0.6, y: 2.15, w: 5.9, colW: [0.9, 1.35, 1.3, 1.45, 0.9], align: ["left", "left", "left", "left", "right"], fontSize: 8.7 });

    const stats = [[`${MATURITY.under_construction.pct_of_local_mw}%`, "Under construction (GW Ranch)"], [`${MATURITY.seeking_tenant.pct_of_local_mw}%`, "Planned / phase-1 (Longfellow)"]];
    stats.forEach(([v, k], i) => statTile(s, 0.6 + i * 3.02, 4.5, 2.85, 1.4, v, k, { valSize: 24 }));
    caption(s, 0.6, 6.15, 5.9, "Distances are corrected edge-to-edge (tract boundary to disclosed site location) — see the Appendix methodology note.");

    const h = exhibitImage(s, "7.1", 6.85, 2.15, 5.9);
    caption(s, 6.85, 2.15 + h + 0.1, 5.9, "Exhibit 7.1 — announced data-center and large-load projects surrounding the site.");
    footer(s, 9);
  }

  // ---------------------------------------------------------------- 10. FEATURE — GW RANCH (red accent, reserved)
  {
    const s = lightSlide(pres);
    eyebrow(s, "handshake", "10 · Feature — GW Ranch (Amazon)", { color: RED, badgeColor: RED });
    titleBlock(s, `The largest air permit issued in the US this year — ${GWR_MI} miles up the same corridor`,
      "Under construction, not announced: three data-center buildings targeted for completion December 2026.",
      { subColor: RED_DK });

    const mapW = 6.2;
    const mapH = exhibitImage(s, "amz", 0.6, 2.45, mapW);
    caption(s, 0.6, 2.45 + mapH + 0.1, mapW, `Exhibit — GW Ranch (highlighted), dashed distance line to Caramba North, ≈ ${GWR_MI} mi edge-to-edge. Base map: Exhibit 7.1.`);

    const rx = 7.05, rw = 5.65;
    const facts = [
      ["mappin", "8,000-acre site, Pecos County", `≈ ${GWR_MI} miles from Caramba North, edge-to-edge (TCEQ record: "~17 mi north of Fort Stockton on Highway 18").`],
      ["handshake", "Amazon disclosed ownership Aug 2026", "Pacifico Energy Group remains the power-plant developer/operator."],
      ["gaspump", "35 gas turbines · 7.65 GW TCEQ air permit", "Largest air permit issued in the US (Jan/Feb 2026), plus 1.8 GW battery storage and up to 750 MW solar."],
      ["server", "Three 189,000 sq ft data-center buildings", "Gensler design, ≈ $300M each; targeted completion Dec 2026; ≈ $12B estimated total project investment."],
    ];
    const rowH3 = 0.92;
    facts.forEach(([ic, h, b], i) => iconRow(s, ic, rx, 2.4 + i * rowH3, rw, rowH3, h, b, RED));

    const flagY = 2.4 + facts.length * rowH3 + 0.05;
    flagBox(s, rx, flagY, rw, 0.95,
      "Clarification",
      "the 7.65 GW figure is a TCEQ generation air permit, not an ERCOT interconnection queue position; Amazon has not disclosed an ERCOT filing and the project is off-grid initially — this sits inside the state-level audit context (slide 14).");
    footer(s, 10);
  }

  // ---------------------------------------------------------------- 11. FEATURE — LONGFELLOW (red accent, reserved; infrastructure-first)
  {
    const s = lightSlide(pres);
    eyebrow(s, "gaspump", "11 · Feature — Longfellow", { color: RED, badgeColor: RED });
    titleBlock(s, `A second phased gas-generation campus, ${LF_MI} miles south`,
      "The corridor's demand for on-site power isn't one project deep.",
      { subColor: RED_DK });

    const mapW2 = 6.2;
    const mapH2 = exhibitImage(s, "lf", 0.6, 2.45, mapW2);
    caption(s, 0.6, 2.45 + mapH2 + 0.1, mapW2, `Exhibit — Longfellow (highlighted), dashed distance line to Caramba North, ≈ ${LF_MI} mi edge-to-edge. Base map: Exhibit 7.1.`);

    const rx2 = 7.05, rw2 = 5.65;
    const facts2 = [
      ["mappin", "568-acre site, Pecos County", `≈ ${LF_MI} miles from Caramba North, edge-to-edge. Longfellow's own public materials describe the location as "more than 25 miles outside of Fort Stockton."`],
      ["fire", "On-site natural-gas generation planned", "Aero-derivative turbines with SCR and carbon-capture capability; closed-loop cooling on permitted non-potable groundwater."],
      ["chart", "Originally announced Oct 2025", "A 2 GW, 8-phase campus (250 MW/phase)."],
      ["gauge", "Status: phase-1 site work underway", "On-site generation build planned in phases."],
    ];
    const rowH3b = 0.92;
    facts2.forEach(([ic, h, b], i) => iconRow(s, ic, rx2, 2.4 + i * rowH3b, rw2, rowH3b, h, b, RED));

    const flagY2 = 2.4 + facts2.length * rowH3b + 0.05;
    flagBox(s, rx2, flagY2, rw2, 0.95,
      "Permitting status",
      "no confirmed ERCOT queue position or TCEQ air-permit record was found for this site as of Aug 2026 — stated here as a fact about permitting status, not as commentary on the project's viability.");
    footer(s, 11);
  }

  // ---------------------------------------------------------------- 12. WATER
  {
    const s = lightSlide(pres);
    eyebrow(s, "droplet", "12 · Water");
    titleBlock(s, "Already permitted: two-thirds of the district's industrial water rights",
      "47,418 AF/yr on adjacent affiliated lands — the water conversation is closed, not open.");
    const rows = [
      ["Permitted volume", `${fmt(C.water_af_yr)} AF/yr (≈ ${C.water_mgd} MGD)`],
      ["Position", "Adjacent affiliated lands — ≈ two-thirds of all Middle Pecos GCD industrial rights"],
      ["Source aquifer", "Edwards-Trinity (Plateau)"],
      ["Recharge history", "Recharge held through the 1950s drought of record"],
      ["Groundwater district", "Middle Pecos GCD"],
      ["Permitted use", "Industrial — cooling and hyperscale loads"],
    ];
    tableStyled(s, ["Attribute", "Detail"], rows, { x: 0.6, y: 2.2, w: 7.2, colW: [2.3, 4.9], fontSize: 11.5 });
    statTile(s, 8.1, 2.2, 4.6, 1.9, `${fmt(C.water_af_yr)}`, "AF/yr permitted, adjacent affiliated lands", { valSize: 30 });
    statTile(s, 8.1, 4.3, 4.6, 1.9, "≈ 2/3", "Of all Middle Pecos GCD industrial rights", { valSize: 30 });
    footer(s, 12);
  }

  // ---------------------------------------------------------------- 13. NATURAL GAS
  {
    const s = lightSlide(pres);
    eyebrow(s, "fire", "13 · Natural Gas");
    titleBlock(s, "A signable 15-year gas quote at Waha basis, twenty miles from the hub",
      "The same structural discount now drawing behind-the-meter generation to this corridor, at GW Ranch and Longfellow alike.");
    const rows = [
      ["Distance to hub", `${C.waha_miles} mi to Waha`],
      ["Indicative volume", `${fmt(C.gas_quote_mmbtu_d)} MMBtu/day`],
      ["Term / pricing", `${C.gas_quote_term_years}-year term, Waha-index pricing (counterparty-supplied)`],
      ["CIAC", `$${C.gas_ciac_musd}M`],
      ["Lead time", `${C.gas_lead_months} months`],
      ["Basis context", "Structural discount to Henry Hub; negative Waha prints 2024–2025 as Matterhorn, Blackcomb, Hugh Brinson, and GCX pipelines rebalance Permian egress"],
    ];
    tableStyled(s, ["Attribute", "Detail"], rows, { x: 0.6, y: 2.2, w: 7.2, colW: [2.3, 4.9], fontSize: 11 });
    statTile(s, 8.1, 2.2, 4.6, 1.9, `${C.waha_miles} mi`, "To Waha hub", { valSize: 30 });
    statTile(s, 8.1, 4.3, 4.6, 1.9, `${C.gas_quote_term_years} yr`, "Signable indicative term, Waha-index", { valSize: 30 });
    footer(s, 13);
  }

  // ---------------------------------------------------------------- 14. MACRO CONTEXT
  {
    const s = lightSlide(pres);
    eyebrow(s, "trendup", "14 · Macro Context — ERCOT Backlog");
    titleBlock(s, "The state-level queue got large enough to trigger a regulatory pause",
      "63 GW to 474 GW in under two years — a demand signal real enough to have created a policy problem, a different claim than \"this area is growing.\"");
    const rows = [
      ["End of 2024", "63 GW", "Large-load interconnection queue, statewide"],
      ["Nov 2025", "226 GW", "≈ 77% of that load is data centers targeting 2030 interconnection"],
      ["Aug 2026", "≈ 474 GW", "≈ 90% data-center-driven; \"more than five times Texas' record peak\" demand, per Gov. Abbott"],
    ];
    tableStyled(s, ["Date", "Statewide queue", "Detail"], rows,
      { x: 0.6, y: 2.25, w: 12.1, colW: [1.7, 1.6, 8.8], align: ["left", "right", "left"], fontSize: 11.5 });

    s.addShape("roundRect", { x: 0.6, y: 4.05, w: 12.1, h: 1.55, rectRadius: 0.05, fill: { color: LIGHT }, line: { color: LINE, width: 0.75 } });
    s.addText(`Aug 3, 2026: a gubernatorial directive to audit all ERCOT-queue data centers, and a pause of the "Batch Zero" large-load review process pending that audit. The region around Caramba North (${R60} GW within 60 mi) sits inside a state-level queue so large it triggered a regulatory pause.`, {
      x: 0.85, y: 4.2, w: 11.6, h: 1.25, fontSize: 11.5, color: NAVY2, fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.15,
    });
    caption(s, 0.6, 5.85, 12.1, "Source: public reporting, Aug 2026 — Latitude Media, \"ERCOT's large load queue has nearly quadrupled in a single year\" (Dec 3, 2025); Utility Dive, \"Facing an estimated 474 GW of interconnection requests, Texas hits pause on data centers\" (Aug 2026).");
    footer(s, 14);
  }

  // ---------------------------------------------------------------- 15. DILIGENCE PLATFORM
  {
    const s = lightSlide(pres);
    eyebrow(s, "shield", "15 · The Diligence Platform");
    titleBlock(s, "Every figure in this document is independently re-derivable from a cited public source",
      "Not a broker's summary — per-feature source popups, versioned builds, and a logged access record.");
    const rows = [
      ["Source-cited features", "Every point/line/boundary traces to a cited public dataset; per-feature source popups"],
      ["Refresh discipline", "RRC weekly; ERCOT queue/TPIT monthly; EIA/USGS/OSM annually"],
      ["Analytical tooling", "Filters by county/depth/spud year/fuel/status; time scrubber; measure/share/print tools"],
      ["Reproducibility", "Static, versioned build; deployed bundle byte-verified on release; access logged"],
    ];
    tableStyled(s, ["Platform property", "Why it matters for diligence"], rows,
      { x: 0.6, y: 2.2, w: 12.1, colW: [3.3, 8.8], fontSize: 12.5 });
    s.addText("lrp-tx-gis.netlify.app  ·  access credentials issued to the deal team separately", {
      x: 0.6, y: 5.35, w: 12.1, h: 0.5, fontSize: 11.5, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 15);
  }

  // ---------------------------------------------------------------- 16. SUBSURFACE & DRILLING
  {
    const s = lightSlide(pres);
    eyebrow(s, "gauge", "16 · Subsurface & Drilling Activity");
    titleBlock(s, "Pecos: the lowest new-drilling count of seven comparable Permian counties",
      `${S9.new_drilling.county_total} new-drill events since 2020 vs. a ${fmt(S9.comparison.peer_average)} peer average — roughly 90% below peer average.`);
    const b2 = S9.new_drilling.bands["≤ 2 mi"], b5 = S9.new_drilling.bands["≤ 5 mi"], b10 = S9.new_drilling.bands["≤ 10 mi"];
    const stats = [
      [b2.count, "New-drill wells ≤ 2 mi since 2020"], [b5.count, "New-drill wells ≤ 5 mi since 2020"],
      [b10.count, "New-drill wells ≤ 10 mi since 2020"], [`${S9.production.radii["≤ 10 mi"].marginal_pct}%`, "Non-plugged wellbores ≤10 mi marginal/EOL"],
    ];
    const tw3 = (12.1 - 3 * 0.16) / 4;
    stats.forEach(([v, k], i) => statTile(s, 0.6 + i * (tw3 + 0.16), 2.15, tw3, 1.15, v, k, { valSize: 22 }));

    const peer = Object.entries(S9.comparison.counties).sort((a, b) => a[1].new_drill - b[1].new_drill);
    s.addChart(pres.ChartType.bar, [{
      name: "New-drill wells since 2020",
      labels: peer.map(([c]) => c),
      values: peer.map(([, v]) => v.new_drill),
    }], {
      x: 0.6, y: 3.55, w: 7.3, h: 3.35,
      barDir: "bar", showTitle: true, title: "New-drill wells since 2020, by county", titleFontSize: 12, titleColor: NAVY,
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY2, dataLabelFontSize: 9,
      chartColors: peer.map(([c]) => c === "Pecos" ? GOLD : "94A3B8"),
      catAxisLabelColor: SLATE, catAxisLabelFontSize: 10, valAxisLabelColor: SLATE, valAxisLabelFontSize: 9,
      valGridLine: { color: LINE, size: 0.75 }, catGridLine: { style: "none" }, showLegend: false,
      valAxisMinVal: 0,
    });
    s.addShape("roundRect", { x: 8.15, y: 3.55, w: 4.55, h: 3.35, rectRadius: 0.05, fill: { color: "FBF7EF" }, line: { color: GOLD, width: 1.25 }, shadow: shadow(0.1) });
    s.addText("BOTTOM LINE", { x: 8.4, y: 3.72, w: 4.05, h: 0.3, fontSize: 10, bold: true, color: GOLD_DK, charSpacing: 1.5, fontFace: "Calibri" });
    s.addText("Shallow drilling, hydraulic fracturing, or new drilling of any kind — three independent public records point the same way: it is not happening at or near this site.", {
      x: 8.4, y: 4.05, w: 4.05, h: 1.55, fontSize: 12.5, bold: true, color: NAVY, fontFace: "Calibri", lineSpacingMultiple: 1.08,
    });
    s.addText(`Within 10 mi, 83% of non-plugged wellbores are marginal/end-of-life production (vs. 60% at ≤2 mi, 62% at ≤5 mi) — the closer ring is even quieter than the wider one.`, {
      x: 8.4, y: 5.65, w: 4.05, h: 1.15, fontSize: 9.7, color: SLATE, fontFace: "Calibri", lineSpacingMultiple: 1.08,
    });
    footer(s, 16);
  }

  // ---------------------------------------------------------------- 17. APPENDIX — DISTANCES & SOURCES
  {
    const s = lightSlide(pres);
    eyebrow(s, "building", "17 · Appendix — Distances & Sources");
    titleBlock(s, "Distances are measured edge-to-edge, and every source is named",
      "Boundary-to-site, not centroid-to-centroid — the methodology and the full source register, stated once.");
    flagBox(s, 0.6, 2.15, 12.1, 1.55,
      "Distance methodology",
      `distances to GW Ranch and Longfellow are measured edge-to-edge — from the nearest point on the Caramba North tract boundary to each site's disclosed location, rather than centroid-to-centroid, which runs measurably longer since the tract itself has spatial extent. GW Ranch: ${GWR_MI} mi (vs. ${INS.distances_edge_to_edge.gw_ranch_centroid_mi} mi centroid). Longfellow: ${LF_MI} mi (vs. ${INS.distances_edge_to_edge.longfellow_centroid_mi} mi centroid) — Longfellow's own public site describes its location as more than 25 miles outside Fort Stockton, consistent with the longer figure; this distance is not represented as shorter.`);
    const rows = [
      ["URL", "https://lrp-tx-gis.netlify.app"],
      ["Login", "Business email + access password (issued to deal team separately)"],
      ["Primary sources", "ERCOT (GIS Report, TPIT), PUCT, EIA-860, TCEQ, RRC (dbf900, production, W-1), FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, U.S. Census TIGER"],
      ["Refresh cadence", "RRC weekly; ERCOT queue/TPIT monthly; EIA/USGS/OSM annually"],
    ];
    tableStyled(s, ["Element", "Detail"], rows, { x: 0.6, y: 4.05, w: 12.1, colW: [2.4, 9.7], fontSize: 11 });
    footer(s, 17);
  }

  // ---------------------------------------------------------------- 18. NOTICES (dark bookend)
  {
    const s = darkSlide(pres);
    s.addText("IMPORTANT NOTICES", {
      x: 0.6, y: 0.72, w: 11, h: 0.5, fontSize: 15, bold: true, color: "D4A73D", charSpacing: 2, fontFace: "Calibri",
    });
    s.addText("Confidential — prepared for a limited number of counterparties under NDA.", {
      x: 0.6, y: 1.18, w: 11, h: 0.35, fontSize: 11.5, italic: true, color: ICE, fontFace: "Cambria",
    });
    const notice = `This Confidential Offering Memorandum has been prepared solely for the use of a limited number of prospective counterparties, under executed non-disclosure agreement, in connection with the potential acquisition of, or investment in, the Caramba North property. It is delivered on a strictly confidential basis and may not be reproduced or distributed without consent.

This document does not constitute an offer to sell or a solicitation of an offer to buy any security or interest. Information is preliminary and indicative, compiled from sources believed reliable, and subject to revision without notice. No representation or warranty, express or implied, is made as to accuracy or completeness.

Public data is drawn from ERCOT, PUCT, EIA, TCEQ, RRC, FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, and U.S. Census TIGER, supplemented by project-level GIS analysis and counterparty-supplied indicative terms. Third-party ownership and permitting disclosures referenced in this deck (e.g., GW Ranch) are drawn from public reporting cited in the companion source register. Recipients should conduct their own independent investigation, including consultation with their own legal, tax, accounting, and engineering advisors.`;
    s.addText(notice, { x: 0.6, y: 1.75, w: 12.1, h: 4.9, fontSize: 11.5, color: ICE, fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.12, paraSpaceAfter: 10 });
    footer(s, 18, true);
  }

  await pres.writeFile({ fileName: OUT });
  console.log(`pptx  -> ${path.relative(REPO, OUT)}`);
}

main().catch(err => { console.error(err); process.exit(1); });
