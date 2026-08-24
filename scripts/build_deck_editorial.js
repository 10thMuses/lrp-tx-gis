#!/usr/bin/env node
/* Caramba North — "Editorial / Narrative" style deck (brief §6.B).
 *
 * Magazine layout: the insight subheading (the "so-what" sentence) is the
 * dominant visual element of every slide — big serif pull-quote type, not a
 * small caption under a title. Tables are replaced with 2-3 large
 * called-out numbers; map exhibits get full-bleed or large photographic
 * treatment. Content and figures are sourced entirely from
 * docs/redesign_content_brief.md — nothing here is invented.
 *
 * Data plumbing follows scripts/build_caramba_om_pptx.js (icon badges,
 * shadow(), exhibitImage(), dark/light slide + footer helpers) but the
 * visual system (type, palette, grid) is built fresh for this style.
 *
 *   node scripts/build_deck_editorial.js
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");

const REPO = path.resolve(__dirname, "..");
const EXHIBIT_DIR = path.join(REPO, "outputs", "reports", "om_exhibits");
const ICON_DIR = path.join(EXHIBIT_DIR, "icons");
const OUT = path.join(REPO, "outputs", "reports", "Caramba-North-Deck-Editorial.pptx");

// Unique tmp paths — other builds may run concurrently (brief §7a).
const BASE_JSON = "/tmp/om_editorial_base.json";
const INSIGHT_JSON = "/tmp/om_editorial_insight.json";
execFileSync("python3", [path.join(REPO, "scripts", "caramba_om_data.py"), "--json", BASE_JSON], { cwd: REPO });
execFileSync("python3", [path.join(REPO, "scripts", "build_insight_pack.py"), "--json", INSIGHT_JSON], { cwd: REPO });
const M = JSON.parse(fs.readFileSync(BASE_JSON, "utf8"));
const I = JSON.parse(fs.readFileSync(INSIGHT_JSON, "utf8"));
const { config: C, section3: S3, section4: S4, section9: S9 } = M;
const STAMP = new Date().toISOString().slice(0, 10);

// Corrected edge-to-edge distances (brief §2.6/§4) — NEVER the old centroid
// figures (17.3 / 19.7 mi) that still live on the base anchor records.
const GW_RANCH_MI = I.distances_edge_to_edge.gw_ranch_mi;       // 15.5
const LONGFELLOW_MI = I.distances_edge_to_edge.longfellow_mi;   // 19.3
const RING = I.ring_analysis; // [15,30,60,100] radius_mi -> total_gw
const MATURITY = I.project_maturity;

function fmt(n) { return Math.round(n).toLocaleString("en-US"); }
function gw1(n) { return (Math.round(n * 10) / 10).toString(); } // one-decimal GW, matches brief §2.6

// ------------------------------------------------------------------ palette
// Navy is the anchor neutral (cover/close + all headings/quotes). A warm
// rust/terracotta carries the editorial accent and every big number — a
// desert-corridor palette, not generic blue. Red is reserved for the two
// feature call-outs (GW Ranch / Longfellow), per brief §8.
const NAVY = "16273B", NAVY2 = "22344A", INK = "1E2A38";
const RUST = "A85A2E", RUST_DK = "8C4A25";
const AMBER = "E3A15C"; // rust's dark-background counterpart (numbers on navy)
const RED = "B91C1C", RED_DK = "8F1616"; // feature-only
const MUTED = "6B7280", MUTED_LT = "9CA8B4";
const LINE = "E4DFD6", CARD = "F7F3EC";
const WHITE = "FFFFFF", ICE = "D7E1E8";
const PW = 13.333, PH = 7.5;

function shadow() { return { type: "outer", color: "16273B", opacity: 0.18, blur: 8, offset: 2, angle: 90 }; }

const EXHIBITS = {
  "2.1": { file: "exhibit_2_1_site-setting.jpg", w: 2400, h: 1500 },
  "3.1": { file: "exhibit_3_1_planned-grid-upgrades.jpg", w: 2400, h: 1374 },
  "4.1": { file: "exhibit_4_1_generation-cluster.jpg", w: 2400, h: 1374 },
  "amz": { file: "exhibit_amz_gwranch.jpg", w: 1410, h: 540 },
  "lf": { file: "exhibit_longfellow.jpg", w: 880, h: 315 },
  "gravity_dark": { file: "exhibit_power_gravity_dark.png", w: 1517, h: 1517 },
};

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
  const col = dark ? "5C7185" : MUTED_LT;
  s.addText("CARAMBA NORTH — STRICTLY CONFIDENTIAL, POST-NDA", {
    x: 0.65, y: PH - 0.42, w: 8, h: 0.3, fontSize: 8, color: col, fontFace: "Calibri", charSpacing: 0.5,
  });
  s.addText(String(n), { x: PW - 1.05, y: PH - 0.42, w: 0.4, h: 0.3, fontSize: 8, color: col, align: "right", fontFace: "Calibri" });
}
function iconPath(key) { return path.join(ICON_DIR, `${key}.png`); }
function iconBadge(s, key, x, y, size, bg) {
  s.addShape("ellipse", { x, y, w: size, h: size, fill: { color: bg }, line: { type: "none" } });
  const pad = size * 0.27;
  s.addImage({ path: iconPath(key), x: x + pad, y: y + pad, w: size - pad * 2, h: size - pad * 2 });
}
// Kicker: small icon badge + tracked-caps label — the "heading" proper.
// Deliberately modest in size; the pull-quote beneath it carries the slide.
function kicker(s, key, label, opts = {}) {
  const dark = !!opts.dark;
  const accent = opts.accent || (dark ? AMBER : RUST);
  const y = opts.y !== undefined ? opts.y : 0.5;
  iconBadge(s, key, 0.65, y, 0.42, accent);
  s.addText(label.toUpperCase(), {
    x: 1.22, y, w: 10.5, h: 0.42, fontSize: 12, bold: true, color: accent,
    charSpacing: 2.2, fontFace: "Calibri", valign: "middle",
  });
}
// Pull-quote: the dominant visual element. fontSize/w/h tuned per call site.
function pullQuote(s, text, x, y, w, h, opts = {}) {
  s.addText(text, Object.assign({
    x, y, w, h, fontSize: 27, italic: true, bold: true,
    color: opts.dark ? WHITE : NAVY, fontFace: "Cambria", valign: "top", lineSpacingMultiple: 1.08,
  }, opts));
}
// A single big called-out number + label, replacing table rows.
function bigNumber(s, x, y, w, value, label, opts = {}) {
  const numColor = opts.color || RUST;
  s.addText(value, {
    x, y, w, h: opts.h || 0.95, fontSize: opts.fontSize || 46, bold: true,
    color: numColor, fontFace: "Calibri", valign: "bottom", margin: 0,
  });
  s.addText(label.toUpperCase(), {
    x, y: y + (opts.h || 0.95), w, h: opts.labelH || 0.55, fontSize: opts.labelSize || 9.5,
    color: opts.dark ? ICE : MUTED, charSpacing: 0.8, fontFace: "Calibri", valign: "top", margin: 0,
    lineSpacingMultiple: 1.05,
  });
}
function bodyText(s, text, x, y, w, h, opts = {}) {
  s.addText(text, Object.assign({
    x, y, w, h, fontSize: 12.5, color: opts.dark ? ICE : "3A4652", fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.18,
  }, opts));
}
function footnote(s, text, x, y, w, h, opts = {}) {
  s.addText(text, Object.assign({
    x, y, w, h, fontSize: 9, italic: true, color: opts.dark ? "8FA2B3" : MUTED, fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.1,
  }, opts));
}
function exhibitPath(e) { return path.isAbsolute(e.file) ? e.file : path.join(EXHIBIT_DIR, e.file); }
function exhibitImage(s, id, x, y, w, opts = {}) {
  const e = EXHIBITS[id];
  const fp = exhibitPath(e);
  const h = w * (e.h / e.w);
  s.addImage({ path: fp, x, y, w, h, shadow: opts.noShadow ? undefined : shadow() });
  if (!opts.noBorder) s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: opts.borderColor || LINE, width: 1 } });
  return h;
}
// Both feature-anchor exhibits (exhibit_amz_gwranch.jpg, exhibit_longfellow.jpg)
// are crops of the same base map (exhibit_7_1) and both carry, baked into the
// raster, a neighboring "Longfellow — Project Horizon · Poolside / CoreWeave"
// map label — a direct hit on Rule 3 (no tenant mention, ever). The brief
// says not to regenerate these exhibits from scratch, and this doesn't: it
// derives a display-only copy (crop / composited redaction) at build time,
// leaving the canonical files untouched, so both feature slides are safe to
// show without carrying that label into a deck that must not mention it.
async function cleanFeatureExhibits() {
  const amzSrc = path.join(EXHIBIT_DIR, "exhibit_amz_gwranch.jpg");
  const amzOut = "/tmp/om_editorial_amz_clean.jpg";
  // The Longfellow/CoreWeave label sits in the bottom ~15% of the frame,
  // well clear of every GW Ranch label/callout above it — plain crop.
  await sharp(amzSrc).extract({ left: 0, top: 0, width: 1410, height: 455 }).jpeg({ quality: 92 }).toFile(amzOut);
  EXHIBITS.amz = { file: amzOut, w: 1410, h: 455 };

  const lfSrc = path.join(EXHIBIT_DIR, "exhibit_longfellow.jpg");
  const lfOut = "/tmp/om_editorial_lf_clean.jpg";
  // The label sits mid-frame (measured bounds of its red highlight ring),
  // between the Caramba North marker above and the distance tag below —
  // composite a plain map-label tag over it, styled like the exhibit's own
  // "CARAMBA NORTH" tag, reading "LONGFELLOW" with no tenant reference.
  const bx0 = 27, by0 = 92, bx1 = 812, by1 = 149;
  const bw = bx1 - bx0, bh = by1 - by0;
  const svg = Buffer.from(
    `<svg width="${bw}" height="${bh}" xmlns="http://www.w3.org/2000/svg">
       <rect x="2" y="2" width="${bw - 4}" height="${bh - 4}" rx="10" fill="#FFFFFF" stroke="#000000" stroke-width="3"/>
       <text x="${bw / 2}" y="${bh / 2 + 9}" font-family="DejaVu Sans, Arial, sans-serif" font-size="27" font-weight="bold" fill="#000000" text-anchor="middle">LONGFELLOW</text>
     </svg>`
  );
  await sharp(lfSrc).composite([{ input: svg, left: bx0, top: by0 }]).jpeg({ quality: 92 }).toFile(lfOut);
  EXHIBITS.lf = { file: lfOut, w: 880, h: 315 };
}

// ==================================================================== main
async function main() {
  await cleanFeatureExhibits();
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Land Resource Partners";
  pres.title = "Caramba North — Editorial Deck";

  let n = 1;

  // ---------------------------------------------------------------- 1. COVER
  {
    const s = darkSlide(pres);
    s.addText("STRICTLY CONFIDENTIAL  ·  OFFERING MEMORANDUM  ·  POST-NDA", {
      x: 0.7, y: 0.68, w: 11, h: 0.4, fontSize: 12, bold: true, color: AMBER, charSpacing: 2.4, fontFace: "Calibri",
    });
    s.addText("CARAMBA\nNORTH", {
      x: 0.65, y: 1.15, w: 9.5, h: 2.3, fontSize: 66, bold: true, color: WHITE, fontFace: "Cambria", lineSpacingMultiple: 0.98,
    });
    pullQuote(s,
      "A 1,300-acre parcel inside an already-forming power and data-center corridor — two hyperscale-scale projects sit on the same north-south line through the property at 15.5 and 19.3 miles, backed by a transmission, water, and gas position that is already permitted, not proposed.",
      0.7, 3.55, 10.6, 2.05, { dark: true, fontSize: 21, lineSpacingMultiple: 1.16 });
    s.addShape("line", { x: 0.7, y: 5.78, w: 11.9, h: 0, line: { color: "2E4258", width: 1 } });
    const stats = [[`${fmt(C.acres_max)}`, "Contiguous acres"], [`${GW_RANCH_MI} mi`, "To GW Ranch (7.65 GW)"],
      [`${LONGFELLOW_MI} mi`, "To Longfellow"], [`${gw1(RING.find(r => r.radius_mi === 60).total_gw)} GW`, "Within 60 miles"]];
    const tw = 11.9 / stats.length;
    stats.forEach(([v, k], i) => {
      const x = 0.7 + i * tw;
      s.addText(v, { x, y: 5.98, w: tw - 0.2, h: 0.5, fontSize: 19, bold: true, color: WHITE, fontFace: "Calibri" });
      s.addText(k.toUpperCase(), { x, y: 6.46, w: tw - 0.2, h: 0.45, fontSize: 8.5, color: "8FA2B3", charSpacing: 0.4, fontFace: "Calibri" });
    });
    s.addText("Prepared by Land Resource Partners  ·  lrp-tx-gis.netlify.app", {
      x: 0.7, y: 7.05, w: 8, h: 0.35, fontSize: 9.5, color: "70839A", fontFace: "Calibri",
    });
    s.addText(STAMP, { x: 9.5, y: 7.05, w: 3.13, h: 0.35, fontSize: 9.5, color: "70839A", align: "right", fontFace: "Calibri" });
  }

  // ---------------------------------------------------------- 2. POWER GRAVITY
  {
    const s = darkSlide(pres);
    n++;
    kicker(s, "ring", "The Power Gravity Map", { dark: true });
    pullQuote(s,
      "GW Ranch sits almost due north (~19°) and Longfellow almost due south (~188°) of Caramba North — the property sits on the north-south line between them, not off to one side.",
      0.65, 1.05, 5.7, 2.65, { dark: true, fontSize: 21, lineSpacingMultiple: 1.14 });

    const nums = [
      [`${gw1(RING.find(r => r.radius_mi === 15).total_gw)} GW`, "Operating + queued, within 15 miles"],
      [`${gw1(RING.find(r => r.radius_mi === 30).total_gw)} GW`, "Operating + queued, within 30 miles"],
      [`${gw1(RING.find(r => r.radius_mi === 60).total_gw)} GW`, "Operating + queued, within 60 miles"],
    ];
    let ny = 4.0;
    nums.forEach(([v, l]) => {
      bigNumber(s, 0.65, ny, 5.2, v, l, { dark: true, color: AMBER, fontSize: 34, h: 0.62, labelSize: 9.5, labelH: 0.4 });
      ny += 1.02;
    });

    const imgW = 5.85;
    const imgX = PW - imgW - 0.55;
    const imgY = 0.75;
    s.addImage({ path: path.join(EXHIBIT_DIR, EXHIBITS.gravity_dark.file), x: imgX, y: imgY, w: imgW, h: imgW });
    footnote(s,
      "Ring analysis: region-wide operating + ERCOT-queue capacity from the same EIA-860 + ERCOT-queue layers used throughout — not county-bounded. Caramba North at center; GW Ranch and Longfellow plotted at true bearing and distance.",
      imgX, imgY + imgW + 0.12, imgW, 0.6, { dark: true });
    footer(s, n, true);
  }

  // ---------------------------------------------------------------- 3. THE PROPERTY
  {
    const s = lightSlide(pres); n++;
    kicker(s, "locationdot", "The Property");
    pullQuote(s,
      "As-of-right industrial land inside the fastest-growing load pocket in ERCOT — not a rezoning story.",
      0.65, 1.05, 5.2, 1.9, { fontSize: 28, lineSpacingMultiple: 1.12 });

    bigNumber(s, 0.65, 3.55, 2.4, `${fmt(C.acres_max)}`, "Max contiguous acres", { fontSize: 44, h: 0.85 });
    bigNumber(s, 3.15, 3.55, 2.4, "~5 mi", "To Fort Stockton", { fontSize: 44, h: 0.85 });
    bodyText(s,
      "North side of I-10, Pecos County. No zoning ordinance — industrial and energy use as of right, inside ERCOT's Far West weather zone, its highest-growth large-load pocket.",
      0.65, 5.15, 5.2, 1.4);

    const imgW = 6.55, imgX = 6.2, imgY = 1.05;
    const h = exhibitImage(s, "2.1", imgX, imgY, imgW);
    footnote(s, "Exhibit 2.1 — the Caramba North tract on the north side of I-10, five miles from Fort Stockton.",
      imgX, imgY + h + 0.12, imgW, 0.5);
    footer(s, n);
  }

  // ---------------------------------------------------------------- 4. TRANSMISSION
  {
    const s = lightSlide(pres); n++;
    kicker(s, "tower", "Transmission");
    pullQuote(s,
      "Fifteen miles from the delivery point of all three approved 765 kV Permian import lines — the transmission decision is already made, upstream of this site.",
      0.65, 1.05, 5.2, 2.5, { fontSize: 23, lineSpacingMultiple: 1.14 });

    bigNumber(s, 0.65, 3.85, 2.4, `${C.solstice_miles} mi`, "To Solstice Substation", { fontSize: 44, h: 0.85 });
    bigNumber(s, 3.15, 3.85, 2.4, "3", "Approved 765 kV import paths", { fontSize: 44, h: 0.85 });
    bodyText(s,
      "AEP/CPS Energy's Solstice Substation — western terminus of the three PUCT-approved paths (Apr 24, 2025, PBRP Docket No. 55718). 141 substation and 133 line upgrades are tracked ERCOT-wide under TPIT — the pipeline of planned upgrades, not built yet.",
      0.65, 5.45, 5.2, 1.2, { fontSize: 11.5 });

    const imgW = 6.55, imgX = 6.2, imgY = 1.05;
    const h = exhibitImage(s, "3.1", imgX, imgY, imgW);
    footnote(s, "Exhibit 3.1 — planned grid upgrades only (ERCOT TPIT); Solstice terminus circled.",
      imgX, imgY + h + 0.12, imgW, 0.5);
    footer(s, n);
  }

  // ---------------------------------------------------------------- 5. REGIONAL POWER CLUSTER
  {
    const s = lightSlide(pres); n++;
    kicker(s, "industry", "Regional Power Cluster");
    pullQuote(s,
      "12 GW already queued in this county alone — before counting the two hyperscale campuses that follow.",
      0.65, 1.05, 5.2, 2.0, { fontSize: 26, lineSpacingMultiple: 1.12 });

    bigNumber(s, 0.65, 3.55, 2.4, `${fmt(S4.pecos_queue_total_mw)}`, "MW queued, Pecos Co. (39 projects)", { fontSize: 40, h: 0.8, labelH: 0.6 });
    bigNumber(s, 3.15, 3.55, 2.4, `${fmt(S4.pecos_operating_total_mw)}`, "MW operating, Pecos Co.", { fontSize: 40, h: 0.8, labelH: 0.6 });
    bodyText(s,
      "Within 20 miles specifically: 13 queued projects, 3,973 MW — before counting the adjacent six counties' 7,022 MW operating and 24,585 MW queued.",
      0.65, 5.25, 5.2, 1.3, { fontSize: 11.5 });

    const imgW = 6.55, imgX = 6.2, imgY = 1.05;
    const h = exhibitImage(s, "4.1", imgX, imgY, imgW);
    footnote(s, "Exhibit 4.1 — operating fleet and ERCOT interconnection queue over one footprint.",
      imgX, imgY + h + 0.12, imgW, 0.5);
    footer(s, n);
  }

  // ---------------------------------------------------------------- 6. WATER
  {
    const s = lightSlide(pres); n++;
    kicker(s, "droplet", "Water");
    pullQuote(s,
      "Two-thirds of the district's industrial water rights are already permitted to this position — the water conversation is closed, not open.",
      0.65, 1.05, 11.6, 1.8, { fontSize: 29, lineSpacingMultiple: 1.14 });

    const nums = [[`${fmt(C.water_af_yr)}`, "AF/yr permitted, adjacent affiliated lands"],
      [`${C.water_mgd}`, "MGD equivalent"], ["~2/3", "Of Middle Pecos GCD industrial rights"]];
    const nw = 3.7;
    nums.forEach(([v, l], i) => bigNumber(s, 0.65 + i * nw, 3.55, nw - 0.4, v, l, { fontSize: 48, h: 0.9, labelH: 0.65 }));

    bodyText(s,
      "Source: Edwards-Trinity (Plateau) aquifer; recharge held through the 1950s drought of record. Groundwater district: Middle Pecos GCD; permitted use: industrial (cooling, hyperscale loads).",
      0.65, 5.55, 11.6, 1.0, { fontSize: 12.5, align: "left" });
    footer(s, n);
  }

  // ---------------------------------------------------------------- 7. NATURAL GAS
  {
    const s = lightSlide(pres); n++;
    kicker(s, "gaspump", "Natural Gas");
    pullQuote(s,
      "A signable 15-year gas quote at Waha basis — the same structural discount now drawing behind-the-meter generation to this corridor.",
      0.65, 1.05, 11.6, 1.9, { fontSize: 26, lineSpacingMultiple: 1.14 });

    const nums = [[`${C.waha_miles} mi`, "To Waha hub"],
      [`${fmt(C.gas_quote_mmbtu_d)}`, "MMBtu/day, indicative supply quote"],
      [`${C.gas_quote_term_years}-yr`, "Term, Waha-index pricing"]];
    const nw = 3.7;
    nums.forEach(([v, l], i) => bigNumber(s, 0.65 + i * nw, 3.6, nw - 0.4, v, l, { fontSize: 46, h: 0.9, labelH: 0.65 }));

    bodyText(s,
      `CIAC $${C.gas_ciac_musd}M; lead time ${C.gas_lead_months} months (counterparty-supplied terms). Basis context: structural discount to Henry Hub; negative Waha prints in 2024-2025 as Matterhorn, Blackcomb, Hugh Brinson, and GCX pipelines rebalance Permian egress.`,
      0.65, 5.6, 11.6, 1.1, { fontSize: 12.5 });
    footer(s, n);
  }

  // ---------------------------------------------------------------- 8. GW RANCH (feature, red)
  {
    const s = lightSlide(pres); n++;
    kicker(s, "industry", "Feature · GW Ranch", { accent: RED });
    pullQuote(s,
      "The largest air permit issued in the US this year sits fifteen miles up the same highway corridor — under construction, not announced.",
      0.65, 1.05, 5.3, 2.0, { fontSize: 21, lineSpacingMultiple: 1.12 });

    const nums = [[`${GW_RANCH_MI} mi`, "From Caramba North"], [`7.65 GW`, "TCEQ air permit — largest in the US"], [`~$12B`, "Est. total project investment"]];
    let ny = 3.55;
    nums.forEach(([v, l]) => {
      bigNumber(s, 0.65, ny, 5.3, v, l, { color: RED, fontSize: 32, h: 0.55, labelH: 0.35, labelSize: 9.5 });
      ny += 0.92;
    });

    const imgW = 6.55, imgX = 6.2, imgY = 1.05;
    const h = exhibitImage(s, "amz", imgX, imgY, imgW, { borderColor: RED });
    bodyText(s,
      "8,000-acre site, Pecos County. Amazon disclosed ownership Aug 2026 (previously Pacifico Energy Group, which remains power-plant developer/operator). 35 gas turbines plus 1.8 GW battery storage and up to 750 MW solar; three 189,000 sq ft data-center buildings (Gensler design, ~$300M each), targeted completion Dec 2026.",
      imgX, imgY + h + 0.18, imgW, 1.5, { fontSize: 11.5 });
    footnote(s,
      "Clarification: the 7.65 GW figure is a TCEQ generation air permit, not an ERCOT interconnection queue position — the project is off-grid initially and Amazon has not disclosed an ERCOT filing. Source: public reporting, Aug 2026.",
      imgX, imgY + h + 1.85, imgW, 0.7);
    footer(s, n);
  }

  // ---------------------------------------------------------------- 9. LONGFELLOW (feature, red)
  {
    const s = lightSlide(pres); n++;
    kicker(s, "gaspump", "Feature · Longfellow", { accent: RED });
    pullQuote(s,
      "A second phased gas-generation campus twenty miles south — the corridor's demand for on-site power isn't one project deep.",
      0.65, 1.05, 5.3, 2.0, { fontSize: 22, lineSpacingMultiple: 1.12 });

    const nums = [[`${LONGFELLOW_MI} mi`, "From Caramba North"], ["568 ac", "Site, Pecos County"], ["8 phases", "250 MW each, originally announced"]];
    let ny = 3.55;
    nums.forEach(([v, l]) => {
      bigNumber(s, 0.65, ny, 5.3, v, l, { color: RED, fontSize: 32, h: 0.55, labelH: 0.35, labelSize: 9.5 });
      ny += 0.92;
    });

    const imgW = 6.55, imgX = 6.2, imgY = 1.05;
    const h = exhibitImage(s, "lf", imgX, imgY, imgW, { borderColor: RED });
    bodyText(s,
      "On-site natural-gas generation planned: aero-derivative turbines with SCR and carbon-capture capability; closed-loop cooling on permitted non-potable groundwater. Originally announced Oct 2025 as a 2 GW campus. Status: phase-1 site work underway; on-site generation build planned in phases. No confirmed ERCOT queue position or TCEQ air-permit record found for this site as of Aug 2026.",
      imgX, imgY + h + 0.18, imgW, 1.7, { fontSize: 11 });
    footnote(s,
      "Distances are measured edge-to-edge, tract boundary to disclosed site location, not centroid-to-centroid. Longfellow's own public materials describe the location as more than 25 miles outside Fort Stockton, consistent with the longer figure here — this distance is not represented as shorter.",
      imgX, imgY + h + 2.05, imgW, 0.7);
    footer(s, n);
  }

  // ---------------------------------------------------------------- 10. PROJECT MATURITY
  {
    const s = lightSlide(pres); n++;
    kicker(s, "trendup", "The Corridor Is Already Built");
    pullQuote(s,
      "79.3% of the two profiled anchors' combined announced capacity is already under construction — the regional pipeline is majority-built, not majority-speculative.",
      0.65, 1.05, 11.6, 1.9, { fontSize: 25, lineSpacingMultiple: 1.14 });

    const barY = 3.6, barX = 0.65, barW = 11.6, barH = 0.55;
    const pctUC = MATURITY.under_construction.pct_of_local_mw / 100;
    const ucW = barW * pctUC, planW = barW - ucW;
    s.addShape("rect", { x: barX, y: barY, w: ucW, h: barH, fill: { color: NAVY }, line: { type: "none" } });
    s.addShape("rect", { x: barX + ucW, y: barY, w: planW, h: barH, fill: { color: RUST }, line: { type: "none" } });

    s.addText(`${MATURITY.under_construction.pct_of_local_mw}%`, { x: barX, y: barY - 0.85, w: 3.0, h: 0.75, fontSize: 40, bold: true, color: NAVY, fontFace: "Calibri", margin: 0 });
    s.addText("GW RANCH — UNDER CONSTRUCTION", { x: barX, y: barY + barH + 0.1, w: 3.5, h: 0.4, fontSize: 10, bold: true, color: NAVY, charSpacing: 1, fontFace: "Calibri" });

    s.addText(`${MATURITY.seeking_tenant.pct_of_local_mw}%`, { x: barX + ucW, y: barY - 0.85, w: 3.0, h: 0.75, fontSize: 40, bold: true, color: RUST, fontFace: "Calibri", margin: 0 });
    s.addText("LONGFELLOW — PLANNED / PHASE-1", { x: barX + ucW, y: barY + barH + 0.1, w: 3.5, h: 0.4, fontSize: 10, bold: true, color: RUST, charSpacing: 1, fontFace: "Calibri" });

    bodyText(s,
      "Basis: GW Ranch's 7.65 GW TCEQ-permitted capacity is under construction; Longfellow's originally announced 2 GW campus is in planned/phase-1 status. Figures reflect announced capacity among the two profiled anchors, not the full regional pipeline.",
      0.65, 5.55, 11.6, 1.1, { fontSize: 12 });
    footer(s, n);
  }

  // ---------------------------------------------------------------- 11. MACRO CONTEXT
  {
    const s = lightSlide(pres); n++;
    kicker(s, "exclaim", "Why This Matters Now");
    pullQuote(s,
      "The region around Caramba North sits inside a state-level interconnection queue so large it triggered a regulatory pause — the demand signal is real enough to have created a policy problem.",
      0.65, 1.05, 11.6, 1.95, { fontSize: 22, lineSpacingMultiple: 1.14 });

    const nums = [["63 GW", "End of 2024", 30], ["226 GW", "Nov 2025 — nearly quadrupled in a year", 44], ["474 GW", "Aug 2026 — statewide backlog, ~90% data-center-driven", 58]];
    const nw = 3.75;
    nums.forEach(([v, l, fs], i) => bigNumber(s, 0.65 + i * nw, 4.55 - (fs - 30) * 0.012, nw - 0.4, v, l, { fontSize: fs, h: fs / 46, labelH: 0.75 }));

    footnote(s,
      "Sources: Latitude Media, “ERCOT's large load queue has nearly quadrupled in a single year” (Dec 3, 2025); Utility Dive, “Facing an estimated 474 GW of interconnection requests, Texas hits pause on data centers” (Aug 2026). Aug 3, 2026 gubernatorial directive ordered an audit of all ERCOT-queue data centers and paused the “Batch Zero” large-load review process pending that audit.",
      0.65, 6.55, 11.6, 0.7);
    footer(s, n);
  }

  // ---------------------------------------------------------------- 12. DILIGENCE PLATFORM
  {
    const s = lightSlide(pres); n++;
    kicker(s, "shield", "The Diligence Platform");
    pullQuote(s,
      "Every figure in this document is independently re-derivable from a cited public source — this isn't a broker's summary.",
      0.65, 1.05, 11.6, 1.7, { fontSize: 28, lineSpacingMultiple: 1.12 });

    const nums = [["11", "Cited public source datasets"], ["Weekly", "RRC refresh cadence"], ["Monthly", "ERCOT queue / TPIT refresh"]];
    const nw = 3.7;
    nums.forEach(([v, l], i) => bigNumber(s, 0.65 + i * nw, 3.55, nw - 0.4, v, l, { fontSize: 44, h: 0.85, labelH: 0.65 }));

    bodyText(s,
      "Every point, line, and boundary traces to a cited public dataset (ERCOT GIS Report/TPIT, PUCT, EIA-860, TCEQ, RRC dbf900/production/W-1, FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, Census TIGER), with per-feature source popups. EIA/USGS/OSM layers refresh annually. Static, versioned build; deployed bundle byte-verified on release; access logged.",
      0.65, 5.4, 11.6, 1.2, { fontSize: 12 });
    footnote(s, "lrp-tx-gis.netlify.app — access credentials issued to the deal team separately.", 0.65, 6.7, 11.6, 0.4);
    footer(s, n);
  }

  // ---------------------------------------------------------------- 13. SUBSURFACE & DRILLING
  {
    const s = lightSlide(pres); n++;
    kicker(s, "gauge", "Subsurface & Drilling Activity");
    pullQuote(s,
      "Pecos County has the lowest new-drilling count of seven comparable Permian counties since 2020 — a 90%-below-peer-average level of activity, not merely “quiet.”",
      0.65, 1.05, 11.6, 2.05, { fontSize: 24, lineSpacingMultiple: 1.14 });

    const nums = [[`${S9.new_drilling.county_total}`, "New-drill wells, Pecos Co. since 2020"],
      [`${fmt(S9.comparison.peer_average)}`, "Peer average, six comparable counties"],
      ["0", "New-drill wells within 5 mi of the tract"]];
    const nw = 3.75;
    nums.forEach(([v, l], i) => bigNumber(s, 0.65 + i * nw, 3.7, nw - 0.4, v, l, { fontSize: 44, h: 0.85, labelH: 0.65 }));

    bodyText(s,
      "Zero new-drill wells within 2 miles of the tract since 2020; zero within 5 miles; one within 10 miles (9.37 mi away). Within 10 miles, 83% of non-plugged wellbores are marginal/end-of-life production, versus 60% at ≤ 2 mi and 62% at ≤ 5 mi — the closer ring is even quieter than the wider one.",
      0.65, 5.6, 11.6, 1.15, { fontSize: 12 });
    footer(s, n);
  }

  // ---------------------------------------------------------------- 14. NOTICES (dark close)
  {
    const s = darkSlide(pres); n++;
    kicker(s, "building", "Notices", { dark: true });
    pullQuote(s,
      "Not a speculative land bet — a parcel positioned to benefit from a buildout already underway, without carrying the exposure of being the marginal, unproven project in the queue.",
      0.65, 1.15, 11.6, 1.55, { dark: true, fontSize: 21, lineSpacingMultiple: 1.14 });

    const notice = `This Confidential Offering Memorandum has been prepared solely for the use of a limited number of prospective counterparties, under executed non-disclosure agreement, in connection with the potential acquisition of, or investment in, the Caramba North property. It is delivered on a strictly confidential basis and may not be reproduced or distributed without consent.

This document does not constitute an offer to sell or a solicitation of an offer to buy any security or interest. Information is preliminary and indicative, compiled from sources believed reliable, and subject to revision without notice.

Public data is drawn from ERCOT, PUCT, EIA, TCEQ, RRC, FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, and U.S. Census TIGER. Third-party transaction and market news is drawn from public reporting cited inline or in the companion source register. Recipients should conduct their own independent investigation, including consultation with their own legal, tax, accounting, and engineering advisors.`;
    s.addText(notice, { x: 0.65, y: 3.05, w: 11.6, h: 3.6, fontSize: 11, color: ICE, fontFace: "Calibri", valign: "top", lineSpacingMultiple: 1.22 });
    footer(s, n, true);
  }

  await pres.writeFile({ fileName: OUT });
  console.log(`pptx -> ${path.relative(REPO, OUT)}  (${n} slides)`);
}

main().catch(err => { console.error(err); process.exit(1); });
