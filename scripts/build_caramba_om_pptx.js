#!/usr/bin/env node
/* Build a condensed executive-summary deck of the Caramba North post-NDA OM.
 * Same derived data model as build_caramba_om.py / build_caramba_om_docx.js
 * (via caramba_om_data.py --json); same exhibit rasters, plus the annotated
 * Amazon/GW Ranch exhibit from build_amz_gwranch_exhibit.py. This is a
 * summary deck, not a page-for-page copy of the 25-page document — one
 * slide per major section, key stats and tables only. The full data lives
 * in the PDF and the Word document.
 *
 * Icon badges are rendered at build time from react-icons (FontAwesome 6)
 * via sharp, so the deck has no binary icon assets to keep in sync by hand.
 *
 *   node scripts/build_caramba_om_pptx.js
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa6 = require("react-icons/fa6");

const REPO = path.resolve(__dirname, "..");
const EXHIBIT_DIR = path.join(REPO, "outputs", "reports", "om_exhibits");
const OUT = path.join(REPO, "outputs", "reports", "Caramba-North-OM-PostNDA.pptx");

const tmpJson = "/tmp/om_model_pptx.json";
execFileSync("python3", [path.join(REPO, "scripts", "caramba_om_data.py"), "--json", tmpJson], { cwd: REPO });
execFileSync("python3", [path.join(REPO, "scripts", "build_amz_gwranch_exhibit.py")], { cwd: REPO });
execFileSync("python3", [path.join(REPO, "scripts", "build_longfellow_exhibit.py")], { cwd: REPO });
const M = JSON.parse(fs.readFileSync(tmpJson, "utf8"));
const { config: C, section3: S3, section4: S4, section7: S7, section9: S9 } = M;
const STAMP = new Date().toISOString().slice(0, 10);
const GW_RANCH = S7.anchors.find(a => a.id === "gw-ranch-pacifico-pecos");
const LONGFELLOW = S7.anchors.find(a => a.id === "project-horizon-poolside-coreweave");

// ------------------------------------------------------------------ palette
const NAVY = "0F1B2D", NAVY2 = "16202E", RED = "B91C1C", SLATE = "475569", MUTED = "64748B";
const ICE = "CADCFC", LIGHT = "F1F5F9", LINE = "E2E8F0", WHITE = "FFFFFF", FLAG = "FFFBEB";

function fmt(n) { if (n === null || n === undefined) return "—"; return Math.round(n).toLocaleString("en-US"); }
function gw(mw) { if (mw === null || mw === undefined) return "—"; return mw >= 1000 ? (mw / 1000).toFixed(1) + " GW" : fmt(mw) + " MW"; }
function shadow() { return { type: "outer", color: "0F1B2D", opacity: 0.16, blur: 7, offset: 2, angle: 90 }; }

const EXHIBITS = {
  "2.1": { file: "exhibit_2_1_site-setting.jpg", w: 2400, h: 1500 },
  "3.1": { file: "exhibit_3_1_planned-grid-upgrades.jpg", w: 2400, h: 1374 },
  "4.1": { file: "exhibit_4_1_generation-cluster.jpg", w: 2400, h: 1374 },
  "7.1": { file: "exhibit_7_1_datacenter-pipeline.jpg", w: 2400, h: 1374 },
  "amz": { file: "exhibit_amz_gwranch.jpg", w: 1410, h: 540 },
  "lf": { file: "exhibit_longfellow.jpg", w: 880, h: 315 },
};

// ------------------------------------------------------------------ icons
const ICON_NAMES = {
  bolt: "FaBoltLightning", tower: "FaTowerBroadcast", droplet: "FaDroplet",
  chart: "FaChartLine", landmark: "FaLandmarkDome", gaspump: "FaGasPump",
  industry: "FaIndustry", server: "FaServer", mappin: "FaMapLocationDot",
  gauge: "FaGaugeHigh", handshake: "FaHandshake", shield: "FaShieldHalved",
  building: "FaBuildingColumns", alert: "FaTriangleExclamation",
};
async function renderIcons() {
  const out = {};
  for (const [key, name] of Object.entries(ICON_NAMES)) {
    const Comp = fa6[name];
    let svg = ReactDOMServer.renderToStaticMarkup(React.createElement(Comp, { size: 256 }));
    svg = svg.replace(/fill="currentColor"/g, 'fill="#FFFFFF"');
    const buf = await sharp(Buffer.from(svg)).resize(256, 256).png().toBuffer();
    out[key] = "image/png;base64," + buf.toString("base64");
  }
  return out;
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
  const col = dark ? "94A3B8" : MUTED;
  s.addText("CARAMBA NORTH — STRICTLY CONFIDENTIAL, POST-NDA", {
    x: 0.5, y: PH - 0.38, w: 8, h: 0.3, fontSize: 8, color: col, fontFace: "Calibri",
  });
  s.addText(String(n), { x: PW - 0.9, y: PH - 0.38, w: 0.4, h: 0.3, fontSize: 8, color: col, align: "right", fontFace: "Calibri" });
}
const PW = 13.333, PH = 7.5;

function iconBadge(s, icons, key, x, y, size, bg) {
  s.addShape("ellipse", { x, y, w: size, h: size, fill: { color: bg || RED }, line: { type: "none" }, shadow: shadow() });
  const pad = size * 0.26;
  s.addImage({ data: "data:" + icons[key], x: x + pad, y: y + pad, w: size - pad * 2, h: size - pad * 2 });
}
function eyebrow(s, icons, iconKey, text, opts = {}) {
  if (iconKey) iconBadge(s, icons, iconKey, 0.6, 0.34, 0.44, opts.badgeColor || RED);
  s.addText(text.toUpperCase(), Object.assign({
    x: iconKey ? 1.2 : 0.6, y: 0.4, w: 10, h: 0.4, fontSize: 12, bold: true, color: opts.color || RED,
    charSpacing: 2, fontFace: "Calibri", valign: "middle",
  }, opts.textOpts || {}));
}
function title(s, text, opts = {}) {
  s.addText(text, Object.assign({
    x: 0.6, y: 0.92, w: 12.1, h: 0.9, fontSize: 25, bold: true, color: NAVY, fontFace: "Cambria", valign: "top",
  }, opts));
}
function statTile(s, x, y, w, h, value, label) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.06, fill: { color: LIGHT }, line: { color: LINE, width: 0.75 }, shadow: shadow() });
  s.addText(String(value), { x: x + 0.14, y: y + 0.1, w: w - 0.28, h: h - 0.58, fontSize: 22, bold: true, color: NAVY, fontFace: "Calibri", valign: "bottom" });
  s.addText(label.toUpperCase(), { x: x + 0.14, y: y + h - 0.42, w: w - 0.28, h: 0.36, fontSize: 8.5, color: MUTED, charSpacing: 1, fontFace: "Calibri", valign: "top" });
}
function tableStyled(s, headers, rows, opts) {
  const headerRow = headers.map(h => ({ text: h.toUpperCase(), options: { bold: true, fontSize: opts.fontSize || 10, color: SLATE, fill: { color: LIGHT }, fontFace: "Calibri" } }));
  const body = rows.map((r, ri) => r.map((c, ci) => ({
    text: c, options: {
      fontSize: opts.fontSize || 10, color: NAVY2, fontFace: "Calibri",
      bold: opts.totalRowIndex === ri,
      fill: opts.totalRowIndex === ri ? { color: "FEF2F2" } : undefined,
      align: (opts.align && opts.align[ci] === "right") ? "right" : "left",
    },
  })));
  headerRow.forEach((c, i) => { c.options.align = (opts.align && opts.align[i] === "right") ? "right" : "left"; });
  s.addTable([headerRow, ...body], Object.assign({
    x: opts.x, y: opts.y, w: opts.w, colW: opts.colW,
    border: { type: "solid", color: LINE, pt: 0.5 },
    autoPage: false, valign: "middle", margin: [0.04, 0.08, 0.04, 0.08],
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
function iconRow(s, icons, iconKey, x, y, w, rowH, heading, body) {
  iconBadge(s, icons, iconKey, x, y + (rowH - 0.5) / 2, 0.5, RED);
  s.addText(heading, { x: x + 0.68, y, w: w - 0.68, h: rowH * 0.44, fontSize: 13, bold: true, color: NAVY, valign: "bottom", fontFace: "Calibri" });
  s.addText(body, { x: x + 0.68, y: y + rowH * 0.42, w: w - 0.68, h: rowH * 0.58, fontSize: 10.5, color: SLATE, valign: "top", fontFace: "Calibri" });
}

// ==================================================================== main
async function main() {
  const icons = await renderIcons();
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
  pres.author = "Land Resource Partners";
  pres.title = "Caramba North — Confidential Offering Memorandum (Post-NDA)";

  // ---------------------------------------------------------------- 1. COVER
  {
    const s = darkSlide(pres);
    s.addText("STRICTLY CONFIDENTIAL · OFFERING MEMORANDUM · POST-NDA", {
      x: 0.7, y: 1.5, w: 10, h: 0.4, fontSize: 13, bold: true, color: "F87171", charSpacing: 2, fontFace: "Calibri",
    });
    s.addText("CARAMBA NORTH", { x: 0.65, y: 1.9, w: 12, h: 1.5, fontSize: 60, bold: true, color: WHITE, fontFace: "Cambria" });
    s.addText(`Up to ${fmt(C.acres_max)} contiguous acres of powered land on the ERCOT 765 kV backbone`, {
      x: 0.7, y: 3.35, w: 11, h: 0.6, fontSize: 18, color: ICE, fontFace: "Calibri",
    });
    s.addText("PECOS COUNTY, TEXAS  ·  FAR WEST ERCOT  ·  PERMIAN BASIN  ·  I-10 CORRIDOR", {
      x: 0.7, y: 3.95, w: 11, h: 0.4, fontSize: 11, color: "94A3B8", charSpacing: 1.5, fontFace: "Calibri",
    });
    const stats = [
      [fmt(C.acres_max), "Contiguous acres"], [fmt(C.water_af_yr), "AF/yr water rights"],
      [`${C.solstice_miles} mi`, "To 765 kV Solstice sub"], [`${C.waha_miles} mi`, "To Waha gas hub"],
      [gw(S4.pecos_queue_total_mw), "ERCOT queue, Pecos Co."],
    ];
    const tw2 = 11.9 / stats.length;
    stats.forEach(([v, k], i) => {
      const x = 0.7 + i * tw2;
      s.addText(v, { x, y: 4.75, w: tw2 - 0.15, h: 0.55, fontSize: 20, bold: true, color: WHITE, fontFace: "Calibri" });
      s.addText(k.toUpperCase(), { x, y: 5.28, w: tw2 - 0.15, h: 0.5, fontSize: 8.5, color: "94A3B8", charSpacing: 0.5, fontFace: "Calibri" });
    });
    s.addShape("line", { x: 0.7, y: 4.68, w: 11.9, h: 0, line: { color: "334155", width: 1 } });
    s.addShape("line", { x: 0.7, y: 6.55, w: 11.9, h: 0, line: { color: "334155", width: 1 } });
    s.addText("Prepared by Land Resource Partners  ·  lrp-tx-gis.netlify.app", {
      x: 0.7, y: 6.68, w: 8, h: 0.4, fontSize: 10, color: "94A3B8", fontFace: "Calibri",
    });
    s.addText(`${STAMP}  ·  Executive summary deck — editable working draft`, {
      x: 8.6, y: 6.68, w: 4.0, h: 0.4, fontSize: 10, color: "94A3B8", align: "right", fontFace: "Calibri",
    });
  }

  // ---------------------------------------------------------------- 2. AGENDA
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "landmark", "Contents");
    title(s, "What's in this deck");
    const items = [
      ["bolt", "01  Executive Summary"], ["mappin", "02  The Property"], ["tower", "03  Transmission"],
      ["industry", "04  Regional Power Cluster"], ["droplet", "05 / 06  Water & Natural Gas"],
      ["server", "07  Regional Data Center Pipeline"], ["handshake", "Feature  Amazon / GW Ranch"],
      ["alert", "Feature  Longfellow / Project Horizon"],
      ["shield", "08  The Diligence Platform"], ["gauge", "09  Subsurface & Drilling Activity"],
      ["building", "Appendix  Access, Sources & Notices"],
    ];
    const colW = 5.9, rowH = 0.58;
    items.forEach(([ic, t], i) => {
      const col = i < 6 ? 0 : 1;
      const row = i < 6 ? i : i - 6;
      const x = 0.6 + col * (colW + 0.5), y = 1.95 + row * rowH;
      iconBadge(s, icons, ic, x, y + 0.03, 0.4, RED);
      s.addText(t, { x: x + 0.55, y, w: colW - 0.55, h: 0.48, fontSize: 15, bold: true, color: NAVY, fontFace: "Calibri", valign: "middle" });
    });
    s.addText("Full data compendium — every table, footnote, and source citation — is in the companion PDF and Word document.", {
      x: 0.6, y: 6.6, w: 11.9, h: 0.5, fontSize: 11, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 2);
  }

  // ---------------------------------------------------------------- 3. EXEC SUMMARY
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "bolt", "01 · Executive Summary");
    title(s, "Transmission, water, gas, and proven hyperscale demand");
    const pillars = [
      ["bolt", "Structural power cost", "Waha-basis gas at a structural discount to Henry Hub, with recurring negative prints 2024–2025."],
      ["tower", "765 kV transmission anchor", `AEP Solstice Substation ${C.solstice_miles} mi north — western terminus of the three PUCT-approved 765 kV Permian import paths.`],
      ["droplet", "Water at institutional scale", `${fmt(C.water_af_yr)} AF/yr permitted on adjacent affiliated lands — ≈ two-thirds of Middle Pecos GCD rights.`],
      ["chart", "Demand already on the ground", `${fmt(S4.pecos_queue_total_mw)} MW ERCOT queue in Pecos Co.; ${S7.local_gw} GW of announced hyperscale capacity within ${S7.local_radius_mi} mi.`],
      ["landmark", "As-of-right development", "Unincorporated Pecos County — no zoning ordinance; industrial and energy uses permitted as of right."],
    ];
    const rowH2 = 0.92;
    pillars.forEach(([ic, h, b], i) => {
      const y = 1.95 + i * rowH2;
      iconBadge(s, icons, ic, 0.6, y + 0.14, 0.52, RED);
      s.addText(h, { x: 1.35, y, w: 3.5, h: rowH2 - 0.1, fontSize: 13, bold: true, color: NAVY, valign: "middle", fontFace: "Calibri" });
      s.addText(b, { x: 4.95, y, w: 7.75, h: rowH2 - 0.1, fontSize: 11.5, color: SLATE, valign: "middle", fontFace: "Calibri" });
    });
    footer(s, 3);
  }

  // ---------------------------------------------------------------- 4. THE PROPERTY
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "mappin", "02 · The Property");
    title(s, "Contiguous, interstate-front acreage, five miles from Fort Stockton");
    const rows = [
      ["Size / configuration", `Up to ${fmt(C.acres_max)} contiguous acres, north side of I-10`],
      ["Access", "Direct I-10 frontage; UP Sunset Route proximate; long-haul fiber"],
      ["Municipal services", "Fort Stockton (~5 mi): services, regional airport"],
      ["Land-use regime", "No zoning ordinance; industrial/energy uses as of right"],
      ["ERCOT position", "Far West weather zone — highest-growth large-load pocket"],
    ];
    tableStyled(s, ["Attribute", "Detail"], rows, { x: 0.6, y: 1.95, w: 5.9, colW: [1.9, 4.0], fontSize: 10 });
    const h = exhibitImage(s, "2.1", 6.85, 1.95, 5.9);
    s.addText("Exhibit 2.1 — The Caramba North tract on the north side of I-10, five miles from Fort Stockton.", {
      x: 6.85, y: 1.95 + h + 0.1, w: 5.9, h: 0.5, fontSize: 9.5, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 4);
  }

  // ---------------------------------------------------------------- 5. TRANSMISSION
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "tower", "03 · Transmission");
    title(s, "15 miles from the western terminus of ERCOT's 765 kV backbone");
    const subs = S3.local_substations.slice(0, 4).map(x => `${x.name.replace(" Substation", "")} (${x.miles} mi)`).join(", ");
    const rows = [
      ["765 kV PUCT approval", "Three import paths approved Apr 24, 2025 (PBRP, No. 55718)"],
      ["Solstice Substation", `AEP/CPS Energy; ${C.solstice_miles} mi north of the Property`],
      ["Local substations", subs],
      ["Planned upgrades (TPIT)", `${S3.tpit_substation_upgrades} substation + ${S3.tpit_line_projects} line upgrades tracked ERCOT-wide`],
    ];
    tableStyled(s, ["Element", "Detail"], rows, { x: 0.6, y: 1.95, w: 5.9, colW: [1.9, 4.0], fontSize: 10 });
    const h = exhibitImage(s, "3.1", 6.85, 1.95, 5.9);
    s.addText("Exhibit 3.1 — Planned grid upgrades only (ERCOT TPIT); Solstice terminus circled.", {
      x: 6.85, y: 1.95 + h + 0.1, w: 5.9, h: 0.5, fontSize: 9.5, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 5);
  }

  // ---------------------------------------------------------------- 6. REGIONAL POWER CLUSTER
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "industry", "04 · Regional Power Cluster");
    title(s, `${gw(S4.pecos_queue_total_mw)} queued in Pecos County — densest renewable cluster in ERCOT`);
    const pop = S4.pecos_operating, pq = S4.pecos_queue;
    const rows = pop.map((o, i) => [o.tech, `${o.count} · ${gw(o.mw)}`, `${pq[i].count} · ${gw(pq[i].mw)}`])
      .concat([["Total", gw(S4.pecos_operating_total_mw), gw(S4.pecos_queue_total_mw)]]);
    tableStyled(s, ["Technology", "Pecos — operating", "Pecos — ERCOT queue"], rows,
      { x: 0.6, y: 1.95, w: 5.9, colW: [1.7, 2.1, 2.1], align: ["left", "right", "right"], totalRowIndex: pop.length, fontSize: 10.5 });
    const h = exhibitImage(s, "4.1", 6.85, 1.95, 5.9);
    s.addText("Exhibit 4.1 — Operating fleet and ERCOT interconnection queue over one footprint.", {
      x: 6.85, y: 1.95 + h + 0.1, w: 5.9, h: 0.5, fontSize: 9.5, italic: true, color: MUTED, fontFace: "Calibri",
    });
    s.addText(`Adjacent counties (${C.adjacent_counties.join(", ")}): ${gw(S4.adjacent_operating_total_mw)} operating, ${gw(S4.adjacent_queue_total_mw)} queued. Named-project detail in the full document.`, {
      x: 0.6, y: 6.55, w: 12.1, h: 0.5, fontSize: 9.5, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 6);
  }

  // ---------------------------------------------------------------- 7. WATER & GAS
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "droplet", "05 / 06 · Water & Natural Gas");
    title(s, "Permitted water at scale, and a Waha-basis gas quote in hand");
    s.addShape("roundRect", { x: 0.6, y: 1.95, w: 5.9, h: 4.6, rectRadius: 0.05, fill: { color: LIGHT }, line: { color: LINE, width: 0.75 }, shadow: shadow() });
    iconBadge(s, icons, "droplet", 0.85, 2.12, 0.5, RED);
    s.addText("WATER", { x: 1.48, y: 2.15, w: 4.8, h: 0.45, fontSize: 13, bold: true, color: RED, charSpacing: 1.5, fontFace: "Calibri", valign: "middle" });
    s.addText(`${fmt(C.water_af_yr)} AF/yr`, { x: 0.85, y: 2.75, w: 5.4, h: 0.6, fontSize: 30, bold: true, color: NAVY, fontFace: "Calibri" });
    s.addText(`(~${C.water_mgd} MGD) permitted on adjacent affiliated lands — ≈ two-thirds of total Middle Pecos GCD rights. Source: Edwards-Trinity (Plateau) aquifer; recharge held through the 1950s drought of record.`, {
      x: 0.85, y: 3.4, w: 5.4, h: 1.9, fontSize: 11.5, color: SLATE, fontFace: "Calibri",
    });
    s.addText("Groundwater district: Middle Pecos GCD  ·  Permitted use: industrial (cooling, hyperscale loads)", {
      x: 0.85, y: 5.9, w: 5.4, h: 0.5, fontSize: 10, italic: true, color: MUTED, fontFace: "Calibri",
    });
    s.addShape("roundRect", { x: 6.85, y: 1.95, w: 5.9, h: 4.6, rectRadius: 0.05, fill: { color: LIGHT }, line: { color: LINE, width: 0.75 }, shadow: shadow() });
    iconBadge(s, icons, "gaspump", 7.1, 2.12, 0.5, RED);
    s.addText("NATURAL GAS", { x: 7.73, y: 2.15, w: 4.8, h: 0.45, fontSize: 13, bold: true, color: RED, charSpacing: 1.5, fontFace: "Calibri", valign: "middle" });
    s.addText(`${C.waha_miles} mi to Waha`, { x: 7.1, y: 2.75, w: 5.4, h: 0.6, fontSize: 30, bold: true, color: NAVY, fontFace: "Calibri" });
    s.addText(`Indicative supply quote: ${fmt(C.gas_quote_mmbtu_d)} MMBtu/day, ${C.gas_quote_term_years}-year term, Waha-index pricing. CIAC $${C.gas_ciac_musd}M; lead time ${C.gas_lead_months} months (counterparty-supplied terms).`, {
      x: 7.1, y: 3.4, w: 5.4, h: 1.9, fontSize: 11.5, color: SLATE, fontFace: "Calibri",
    });
    s.addText("Basis: structural discount to Henry Hub; negative prints 2024–2025 as Matterhorn, Blackcomb, Hugh Brinson, GCX rebalance egress.", {
      x: 7.1, y: 5.9, w: 5.4, h: 0.5, fontSize: 10, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 7);
  }

  // ---------------------------------------------------------------- 8. DATA CENTER PIPELINE
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "server", "07 · Regional Data Center Pipeline");
    title(s, `${S7.local_gw} GW of announced hyperscale capacity within ${S7.local_radius_mi} miles`);
    const rows = S7.local.map(a => [a.name, a.developer.split("(")[0].trim(), gw(a.capacity_mw), `~${a.miles} mi`]);
    tableStyled(s, ["Project", "Sponsor", "Capacity", "Distance"], rows,
      { x: 0.6, y: 1.95, w: 5.9, colW: [2.0, 2.1, 0.9, 0.9], align: ["left", "left", "right", "right"], fontSize: 10 });
    const otherGw = Math.round(((S7.total_mw - S7.local_mw) / 1000) * 10) / 10;
    s.addText(`Elsewhere in Texas (context, not catchment): ${S7.other.length} campuses, ${otherGw} GW — not included above.`, {
      x: 0.6, y: 4.0, w: 5.9, h: 0.6, fontSize: 10, italic: true, color: MUTED, fontFace: "Calibri",
    });
    s.addText("GW Ranch's ownership changed in Aug 2026, and Longfellow's anchor tenant exited in Apr 2026 — see the following feature slides.", {
      x: 0.6, y: 4.65, w: 5.9, h: 0.9, fontSize: 10, bold: true, color: RED, fontFace: "Calibri",
    });
    const h = exhibitImage(s, "7.1", 6.85, 1.95, 5.9);
    s.addText("Exhibit 7.1 — Announced data-center and large-load projects surrounding the site.", {
      x: 6.85, y: 1.95 + h + 0.1, w: 5.9, h: 0.5, fontSize: 9.5, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 8);
  }

  // ---------------------------------------------------------------- 9. FEATURE — AMAZON / GW RANCH
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "handshake", "Feature · Amazon / GW Ranch", { badgeColor: NAVY, color: NAVY });
    title(s, `Amazon acquires GW Ranch — ≈ ${GW_RANCH.miles} miles from Caramba North`);

    const mapW = 6.35;
    const mapH = exhibitImage(s, "amz", 0.6, 1.9, mapW);
    s.addText(`Exhibit — GW Ranch site (highlighted) and its straight-line distance to the Caramba North tract centroid, ≈ ${GW_RANCH.miles} miles. Base map: Exhibit 7.1.`, {
      x: 0.6, y: 1.9 + mapH + 0.1, w: mapW, h: 0.7, fontSize: 9.5, italic: true, color: MUTED, fontFace: "Calibri",
    });

    const rx = 7.25, rw = 5.5;
    const facts = [
      ["mappin", "8,000-acre site, Pecos County", "≈ 17 miles north of Fort Stockton — the same siting logic as Caramba North."],
      ["gaspump", "35 gas turbines · 7.65 GW TCEQ air permit", "Largest air permit issued in the US (Jan/Feb 2026) — plus 1.8 GW battery storage and up to 750 MW solar."],
      ["server", "Three data-center buildings", "189,000 sq ft each, Gensler design, ≈ $300M per building — targeted completion Dec 2026."],
      ["chart", "≈ $12B estimated total project investment", "Amazon has not disclosed its specific investment amount or ultimate buildout plans."],
      ["tower", "Off-grid initially", "Amazon has not disclosed an ERCOT large-load interconnection filing or queue position — exploring a transition to grid-connected service."],
    ];
    const rowH3 = 0.72;
    facts.forEach(([ic, h, b], i) => {
      const y = 1.85 + i * rowH3;
      iconRow(s, icons, ic, rx, y, rw, rowH3, h, b);
    });

    const flagY = 1.85 + facts.length * rowH3 + 0.06;
    s.addShape("roundRect", { x: rx, y: flagY, w: rw, h: 0.62, rectRadius: 0.04, fill: { color: FLAG }, line: { color: "FCD34D", width: 1 } });
    s.addText([
      { text: "Clarification — ", options: { bold: true, color: "78350F" } },
      { text: "the 7.65 GW figure is a TCEQ generation air permit, not an ERCOT interconnection queue position; subject to Texas Gov. Abbott's Aug 3, 2026 data-center permitting pause pending state audits.", options: { color: "78350F" } },
    ], { x: rx + 0.14, y: flagY + 0.05, w: rw - 0.28, h: 0.52, fontSize: 9, fontFace: "Calibri", valign: "middle" });

    footer(s, 9);
  }

  // ---------------------------------------------------------------- 10. FEATURE — LONGFELLOW / PROJECT HORIZON
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "alert", "Feature · Longfellow / Project Horizon", { badgeColor: NAVY, color: NAVY });
    title(s, `CoreWeave exits Project Horizon — ≈ ${LONGFELLOW.miles} miles from Caramba North`);

    const mapW2 = 6.35;
    const mapH2 = exhibitImage(s, "lf", 0.6, 1.9, mapW2);
    s.addText(`Exhibit — Longfellow / Project Horizon site (highlighted) and its straight-line distance to the Caramba North tract centroid, ≈ ${LONGFELLOW.miles} miles. Base map: Exhibit 7.1.`, {
      x: 0.6, y: 1.9 + mapH2 + 0.1, w: mapW2, h: 0.7, fontSize: 9.5, italic: true, color: MUTED, fontFace: "Calibri",
    });

    const rx2 = 7.25, rw2 = 5.5;
    const facts2 = [
      ["mappin", "568-acre site, Pecos County", "Longfellow Ranch (Mitchell family), ≈ 25 miles from Fort Stockton — announced Oct 2025 as a 2 GW, 8-phase campus."],
      ["handshake", "CoreWeave exited the anchor lease, Apr 2026", "250 MW / 15-yr lease (to 500 MW) plus 40,000+ GPUs — exited after Poolside missed its GPU timeline and its funding round fell through."],
      ["gaspump", "Behind-the-meter gas, no confirmed permit on file", "SCR-equipped aero-derivative turbines planned; no TCEQ air-permit or ERCOT queue record found for this site as of Aug 2026."],
      ["chart", "Revised to ~1.2 GW initial, scaling toward ~7 GW", "Per Jun 2026 reporting — down from the original 2 GW first-phase framing, pending a new anchor tenant."],
      ["shield", "Now under Poolside Infrastructure Company", "Spun-off infra arm continuing the site without the AI lab; named a new CFO Jul 2026 and is courting a replacement anchor tenant."],
    ];
    const rowH3b = 0.72;
    facts2.forEach(([ic, h, b], i) => {
      const y = 1.85 + i * rowH3b;
      iconRow(s, icons, ic, rx2, y, rw2, rowH3b, h, b);
    });

    const flagY2 = 1.85 + facts2.length * rowH3b + 0.06;
    s.addShape("roundRect", { x: rx2, y: flagY2, w: rw2, h: 0.62, rectRadius: 0.04, fill: { color: FLAG }, line: { color: "FCD34D", width: 1 } });
    s.addText([
      { text: "Clarification — ", options: { bold: true, color: "78350F" } },
      { text: "the original 2 GW / CoreWeave framing on Exhibit 7.1 predates the Apr 2026 lease termination; treat capacity and timeline figures for this site as unresolved pending a new anchor tenant.", options: { color: "78350F" } },
    ], { x: rx2 + 0.14, y: flagY2 + 0.05, w: rw2 - 0.28, h: 0.52, fontSize: 9, fontFace: "Calibri", valign: "middle" });

    footer(s, 10);
  }

  // ---------------------------------------------------------------- 11. DILIGENCE PLATFORM
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "shield", "08 · The Diligence Platform");
    title(s, "Every figure is independently verifiable, feature by feature");
    const rows = [
      ["Source-cited features", "Every point/line/boundary traces to a cited public dataset; per-feature popups"],
      ["Refresh discipline", "RRC weekly; ERCOT queue/TPIT monthly; EIA/USGS/OSM annually"],
      ["Analytical tooling", "Filters by county/depth/spud year/fuel/status; time scrubber; measure/share/print"],
      ["Reproducibility", "Static, versioned build; deployed bundle byte-verified on release; access logged"],
    ];
    tableStyled(s, ["Platform property", "Why it matters for diligence"], rows,
      { x: 0.6, y: 2.0, w: 12.1, colW: [3.4, 8.7], fontSize: 12 });
    s.addText("lrp-tx-gis.netlify.app  ·  access credentials issued to the deal team separately (see Appendix)", {
      x: 0.6, y: 5.4, w: 12.1, h: 0.5, fontSize: 11, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 11);
  }

  // ---------------------------------------------------------------- 12. SUBSURFACE & DRILLING
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "gauge", "09 · Subsurface & Drilling Activity");
    title(s, "No new drilling is occurring at or near the site");
    const b2 = S9.new_drilling.bands["≤ 2 mi"], b5 = S9.new_drilling.bands["≤ 5 mi"], b10 = S9.new_drilling.bands["≤ 10 mi"];
    const stats = [
      [b2.count, "New-drill wells ≤ 2 mi since 2020"], [b5.count, "New-drill wells ≤ 5 mi since 2020"],
      [b10.count, "New-drill wells ≤ 10 mi since 2020"], [S9.fracfocus.bands["0 – 2 mi"].count, "New-drill fracks ≤ 2 mi, ever"],
    ];
    const tw3 = 11.9 / 4;
    stats.forEach(([v, k], i) => statTile(s, 0.6 + i * tw3, 1.95, tw3 - 0.15, 1.15, v, k));

    const peer = Object.entries(S9.comparison.counties).sort((a, b) => a[1].new_drill - b[1].new_drill);
    s.addChart(pres.ChartType.bar, [{
      name: "New-drill wells since 2020",
      labels: peer.map(([c]) => c),
      values: peer.map(([, v]) => v.new_drill),
    }], {
      x: 0.6, y: 3.35, w: 7.3, h: 3.5,
      barDir: "bar", showTitle: true, title: "New-drill wells since 2020, by county", titleFontSize: 12, titleColor: NAVY,
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY2, dataLabelFontSize: 9,
      chartColors: peer.map(([c]) => c === "Pecos" ? RED : "94A3B8"),
      catAxisLabelColor: SLATE, catAxisLabelFontSize: 10, valAxisLabelColor: SLATE, valAxisLabelFontSize: 9,
      valGridLine: { color: LINE, size: 0.75 }, catGridLine: { style: "none" }, showLegend: false,
      valAxisMinVal: 0,
    });
    s.addShape("roundRect", { x: 8.15, y: 3.35, w: 4.6, h: 3.5, rectRadius: 0.05, fill: { color: "FEF7F7" }, line: { color: RED, width: 1.25 }, shadow: shadow() });
    s.addText("BOTTOM LINE", { x: 8.4, y: 3.55, w: 4.1, h: 0.3, fontSize: 10, bold: true, color: RED, charSpacing: 1.5, fontFace: "Calibri" });
    s.addText("Shallow drilling, hydraulic fracturing, or new drilling of any kind — three independent public records point the same way: it is not happening at or near this site.", {
      x: 8.4, y: 3.9, w: 4.1, h: 1.7, fontSize: 13, bold: true, color: NAVY, fontFace: "Calibri",
    });
    s.addText(`Pecos: ${S9.comparison.counties.Pecos.new_drill} new wells since 2020 vs. peer average ${fmt(S9.comparison.peer_average)}. ${S9.production.radii["≤ 10 mi"].marginal_pct}% of non-plugged wellbores ≤10 mi are marginal/end-of-life.`, {
      x: 8.4, y: 5.6, w: 4.1, h: 1.1, fontSize: 10, color: SLATE, fontFace: "Calibri",
    });
    footer(s, 12);
  }

  // ---------------------------------------------------------------- 13. APPENDIX — ACCESS & SOURCES
  {
    const s = lightSlide(pres);
    eyebrow(s, icons, "building", "Appendix");
    title(s, "GIS platform access & source register");
    const rows = [
      ["URL", "https://lrp-tx-gis.netlify.app"],
      ["Login", "Business email + access password (issued to deal team separately)"],
      ["Primary sources", "ERCOT (GIS Report, TPIT), PUCT, EIA-860, TCEQ, RRC (dbf900, production, W-1), FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, U.S. Census TIGER"],
      ["Refresh cadence", "RRC weekly; ERCOT queue/TPIT monthly; EIA/USGS/OSM annually"],
    ];
    tableStyled(s, ["Element", "Detail"], rows, { x: 0.6, y: 2.0, w: 12.1, colW: [2.4, 9.7], fontSize: 11.5 });
    s.addText("Full footnotes (13), source register, and exhibit-provenance table are in Appendix A.1–A.2 of the companion PDF and Word document.", {
      x: 0.6, y: 5.6, w: 12.1, h: 0.5, fontSize: 10.5, italic: true, color: MUTED, fontFace: "Calibri",
    });
    footer(s, 13);
  }

  // ---------------------------------------------------------------- 14. NOTICES (dark bookend)
  {
    const s = darkSlide(pres);
    s.addText("IMPORTANT NOTICES", {
      x: 0.6, y: 0.75, w: 11, h: 0.5, fontSize: 15, bold: true, color: "F87171", charSpacing: 2, fontFace: "Calibri",
    });
    const notice = `This Confidential Offering Memorandum has been prepared solely for the use of a limited number of prospective counterparties, under executed non-disclosure agreement, in connection with the potential acquisition of, or investment in, the Caramba North property. It contains proprietary data of Harvest Energy, LLC and is delivered on a strictly confidential basis; it may not be reproduced or distributed without consent.

This document does not constitute an offer to sell or a solicitation of an offer to buy any security or interest. Information is preliminary and indicative, compiled from sources believed reliable, and subject to revision without notice. No representation or warranty, express or implied, is made as to accuracy or completeness.

Public data is drawn from ERCOT, PUCT, EIA, TCEQ, RRC, FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, and U.S. Census TIGER, supplemented by project-level GIS analysis and counterparty-supplied indicative terms. News on third-party transactions (e.g. Section "Feature") is drawn from public reporting cited in the companion Word/PDF data model. Recipients should conduct their own independent investigation, including consultation with their own legal, tax, accounting, and engineering advisors.`;
    s.addText(notice, { x: 0.6, y: 1.5, w: 12.1, h: 5.2, fontSize: 12, color: ICE, fontFace: "Calibri", valign: "top", paraSpaceAfter: 10 });
    footer(s, 14, true);
  }

  await pres.writeFile({ fileName: OUT });
  console.log(`pptx  -> ${path.relative(REPO, OUT)}`);
}

main().catch(err => { console.error(err); process.exit(1); });
