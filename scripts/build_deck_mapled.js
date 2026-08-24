#!/usr/bin/env node
/* Caramba North — "Map-and-Infographic-led" style deck (brief §6.C).
 *
 * Every slide is built map/diagram-first: the exhibit or a native diagram
 * takes 60-70% of the slide, with callout leader-lines/boxes pinned to 3-5
 * key numbers laid directly on or beside the visual. Heading + subheading
 * live in a compact band (top on content slides, side on the cover).
 *
 * Data: caramba_om_data.py (core model) + build_insight_pack.py (ring
 * analysis, project maturity, corrected edge-to-edge distances). Exhibits:
 * outputs/reports/om_exhibits/*  (existing rasters, used as-is) plus one
 * NEW annotated exhibit built by build_pipeline5_annotated_exhibit.py
 * (numbers all five labeled projects on the base pipeline map — does not
 * touch exhibit_7_1 or the two existing feature exhibits).
 *
 *   node scripts/build_deck_mapled.js
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const pptxgen = require("pptxgenjs");

const REPO = path.resolve(__dirname, "..");
const EXHIBIT_DIR = path.join(REPO, "outputs", "reports", "om_exhibits");
const ICON_DIR = path.join(EXHIBIT_DIR, "icons");
const OUT = path.join(REPO, "outputs", "reports", "Caramba-North-Deck-MapLed.pptx");

const tmpJson = "/tmp/om_mapled.json";
execFileSync("python3", [path.join(REPO, "scripts", "caramba_om_data.py"), "--json", tmpJson], { cwd: REPO });
const tmpInsight = "/tmp/om_mapled_insights.json";
execFileSync("python3", [path.join(REPO, "scripts", "build_insight_pack.py"), "--json", tmpInsight], { cwd: REPO });
execFileSync("python3", [path.join(REPO, "scripts", "build_pipeline5_annotated_exhibit.py")], { cwd: REPO });

const M = JSON.parse(fs.readFileSync(tmpJson, "utf8"));
const INS = JSON.parse(fs.readFileSync(tmpInsight, "utf8"));
const { config: C, section3: S3, section4: S4, section7: S7, section9: S9 } = M;
const STAMP = new Date().toISOString().slice(0, 10);
const RINGS = INS.ring_analysis; // [{radius_mi, operating_gw, queue_gw, total_gw, ...}]
const MATURITY = INS.project_maturity;
const DIST = INS.distances_edge_to_edge; // gw_ranch_mi 15.5, longfellow_mi 19.3

// ------------------------------------------------------------------ palette
const NAVY = "0F1B2D", NAVY2 = "16202E", SLATE = "475569", MUTED = "64748B";
const COPPER = "B06220", COPPER_DK = "7C4315";
const RED = "B91C1C", RED_DK = "7F1D1D"; // reserved for GW Ranch / Longfellow only
const LIGHT = "F1F5F9", LINE = "E2E8F0", WHITE = "FFFFFF", ICE = "CADCFC";
const NAVY_TINT = "1E2A3D"; // panel fill on dark slides

const TITLE_FONT = "Bookman Old Style";
const BODY_FONT = "Calibri";

const PW = 13.333, PH = 7.5;

function fmt(n) { if (n === null || n === undefined) return "—"; return Math.round(n).toLocaleString("en-US"); }
function shadow(opts) { return Object.assign({ type: "outer", color: "0F1B2D", opacity: 0.18, blur: 8, offset: 2, angle: 90 }, opts || {}); }

// ------------------------------------------------------------------ icons
function iconPath(key) { return path.join(ICON_DIR, `${key}.png`); }
function iconBadge(s, key, x, y, size, bg) {
  s.addShape("ellipse", { x, y, w: size, h: size, fill: { color: bg || COPPER }, line: { type: "none" }, shadow: shadow() });
  const pad = size * 0.26;
  s.addImage({ path: iconPath(key), x: x + pad, y: y + pad, w: size - pad * 2, h: size - pad * 2 });
}

// ------------------------------------------------------------------ layout helpers
function darkSlide(pres) { const s = pres.addSlide(); s.background = { color: NAVY }; return s; }
function lightSlide(pres) { const s = pres.addSlide(); s.background = { color: WHITE }; return s; }

function footer(s, n, dark) {
  const col = dark ? "6B7A90" : MUTED;
  s.addText("CARAMBA NORTH — MAP-LED SUMMARY, CONFIDENTIAL", {
    x: 0.6, y: PH - 0.36, w: 8, h: 0.28, fontSize: 7.5, color: col, fontFace: BODY_FONT, charSpacing: 0.5,
  });
  s.addText(String(n), { x: PW - 1.1, y: PH - 0.36, w: 0.5, h: 0.28, fontSize: 7.5, color: col, align: "right", fontFace: BODY_FONT });
}

// Compact heading band across the top of a content slide.
function headerBand(s, { eyebrow, iconKey, title, subheading, dark, accent } = {}) {
  const acc = accent || COPPER;
  const titleColor = dark ? WHITE : NAVY;
  const subColor = dark ? ICE : SLATE;
  if (iconKey) iconBadge(s, iconKey, 0.6, 0.26, 0.4, acc);
  s.addText((eyebrow || "").toUpperCase(), {
    x: iconKey ? 1.12 : 0.6, y: 0.28, w: 9.5, h: 0.32, fontSize: 10.5, bold: true, color: acc,
    charSpacing: 1.8, fontFace: BODY_FONT, valign: "middle",
  });
  s.addText(title, {
    x: 0.6, y: 0.56, w: 12.1, h: 0.56, fontSize: 23, bold: true, color: titleColor, fontFace: TITLE_FONT, valign: "top",
  });
  s.addText(subheading, {
    x: 0.6, y: 1.1, w: 12.1, h: 0.42, fontSize: 12.5, italic: true, color: subColor, fontFace: BODY_FONT, valign: "top",
  });
}

// Fit an image (contain) inside a box, preserving aspect ratio; draws a
// thin border + shadow; returns geometry plus a pixel->slide mapper so
// callout leader-lines can be anchored to real features on the raster.
function placeExhibit(s, file, pxW, pxH, boxX, boxY, boxW, boxH, opts = {}) {
  const boxAR = boxW / boxH, imAR = pxW / pxH;
  let w, h;
  if (imAR > boxAR) { w = boxW; h = w / imAR; } else { h = boxH; w = h * imAR; }
  const x = boxX + (boxW - w) / 2;
  const y = boxY + (boxH - h) / 2;
  const fp = path.join(EXHIBIT_DIR, file);
  s.addImage({ path: fp, x, y, w, h, shadow: opts.noShadow ? undefined : shadow() });
  if (!opts.noBorder) s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: opts.borderColor || LINE, width: 1 } });
  return {
    x, y, w, h,
    map(px, py) { return { x: x + (px / pxW) * w, y: y + (py / pxH) * h }; },
  };
}

// A stat callout card: bold value + small caption label, optional leader
// line from one edge of the card to an anchor point on the visual.
function callout(s, { x, y, w, h, value, label, valueColor, accent, fontSize, labelSize, dark, fill } = {}) {
  const acc = accent || COPPER;
  const bg = fill || (dark ? NAVY_TINT : WHITE);
  s.addShape("roundRect", {
    x, y, w, h, rectRadius: 0.05, fill: { color: bg }, line: { color: dark ? "2B3A52" : LINE, width: 1 }, shadow: shadow(),
  });
  s.addText(String(value), {
    x: x + 0.13, y: y + 0.06, w: w - 0.26, h: h * 0.58, fontSize: fontSize || 19, bold: true,
    color: valueColor || acc, fontFace: BODY_FONT, valign: "bottom",
  });
  s.addText((label || "").toUpperCase(), {
    x: x + 0.13, y: y + h * 0.6, w: w - 0.26, h: h * 0.4 - 0.08, fontSize: labelSize || 8.3,
    color: dark ? "9FB0C6" : MUTED, charSpacing: 0.5, fontFace: BODY_FONT, valign: "top", lineSpacingMultiple: 1.05,
  });
}

// Leader line from a card edge point to an anchor point on the visual,
// plus a small marker dot at the anchor so it's clear what's referenced.
function leader(s, x1, y1, x2, y2, color, opts = {}) {
  s.addShape("line", {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1) || 0.001, h: Math.abs(y2 - y1) || 0.001,
    flipH: x2 < x1, flipV: y2 < y1,
    line: { color: color || NAVY, width: 1.25, dashType: opts.dash === false ? "solid" : "dash" },
  });
  const r = opts.r || 0.05;
  s.addShape("ellipse", { x: x2 - r, y: y2 - r, w: r * 2, h: r * 2, fill: { color: color || NAVY }, line: { color: WHITE, width: 1 } });
}

// ==================================================================== main
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Land Resource Partners";
  pres.title = "Caramba North — Map-and-Infographic-Led Summary";

  const gwRanchAnchor = S7.anchors.find(a => a.id === "gw-ranch-pacifico-pecos");
  const longfellowAnchor = S7.anchors.find(a => a.id === "project-horizon-poolside-coreweave");
  const ring15 = RINGS.find(r => r.radius_mi === 15);
  const ring30 = RINGS.find(r => r.radius_mi === 30);
  const ring60 = RINGS.find(r => r.radius_mi === 60);
  const ring100 = RINGS.find(r => r.radius_mi === 100);

  // ================================================================ 1. COVER
  {
    const s = darkSlide(pres);
    // ---- left column: identity + pinned numbers ----
    s.addText("STRICTLY CONFIDENTIAL · OFFERING MEMORANDUM", {
      x: 0.6, y: 0.55, w: 4.4, h: 0.32, fontSize: 10.5, bold: true, color: COPPER, charSpacing: 1.8, fontFace: BODY_FONT,
    });
    s.addText("CARAMBA NORTH", { x: 0.56, y: 0.86, w: 5.9, h: 0.75, fontSize: 34, bold: true, color: WHITE, fontFace: TITLE_FONT });
    s.addText("Map-and-Infographic-Led Summary", { x: 0.6, y: 1.56, w: 4.3, h: 0.34, fontSize: 13, italic: true, color: ICE, fontFace: BODY_FONT });
    s.addText(
      "A 1,300-acre parcel inside an already-forming power and data-center corridor — two hyperscale-scale projects sit on the same north–south line through the property, backed by transmission, water, and gas positions already permitted, not proposed.",
      { x: 0.6, y: 2.0, w: 4.35, h: 1.35, fontSize: 12, color: ICE, fontFace: BODY_FONT, lineSpacingMultiple: 1.18 }
    );

    const pins = [
      { v: fmt(C.acres_max), l: "ACRES — THE SITE", pt: [759, 758] },
      { v: `≈${DIST.gw_ranch_mi} MI`, l: "GW RANCH — 7.65 GW, UNDER CONSTRUCTION", pt: [797, 648] },
      { v: `≈${DIST.longfellow_mi} MI`, l: "LONGFELLOW — PHASE-1 SITE WORK UNDERWAY", pt: [741, 890] },
      { v: `${ring60.total_gw} GW`, l: "OPERATING + QUEUED WITHIN 60 MILES", pt: [1162, 758] },
    ];
    // gravity diagram placed on the right; compute mapping first so the
    // left-column leader lines can reach across into it.
    const gDia = placeExhibit(s, "exhibit_power_gravity_dark.png", 1517, 1517, 6.55, 0.68, 6.15, 6.15, { noBorder: true, noShadow: true });
    const pinY = [3.55, 4.35, 5.15, 5.95];
    pins.forEach((p, i) => {
      const y = pinY[i];
      s.addText(p.v, { x: 0.6, y, w: 2.0, h: 0.4, fontSize: 18, bold: true, color: WHITE, fontFace: BODY_FONT });
      s.addText(p.l, { x: 0.6, y: y + 0.4, w: 4.3, h: 0.32, fontSize: 8, color: "9FB0C6", charSpacing: 0.5, fontFace: BODY_FONT });
      const a = gDia.map(p.pt[0], p.pt[1]);
      leader(s, 3.0, y + 0.18, a.x, a.y, i === 1 || i === 2 ? RED : COPPER, { r: 0.045 });
    });

    s.addShape("line", { x: 0.6, y: 6.68, w: 12.13, h: 0, line: { color: "2B3A52", width: 1 } });
    s.addText("Prepared by Land Resource Partners · lrp-tx-gis.netlify.app", {
      x: 0.6, y: 6.8, w: 7, h: 0.34, fontSize: 9.5, color: "9FB0C6", fontFace: BODY_FONT,
    });
    s.addText(`${STAMP} · Pecos County, Texas · Far West ERCOT`, {
      x: 7.4, y: 6.8, w: 5.33, h: 0.34, fontSize: 9.5, color: "9FB0C6", align: "right", fontFace: BODY_FONT,
    });
  }

  // ================================================================ 2. POWER GRAVITY
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "Regional power gravity", iconKey: "ring",
      title: "Caramba North sits inside the gravity well, not outside it",
      subheading: `${ring60.total_gw} GW of operating + queued capacity sits within 60 miles — GW Ranch and Longfellow anchor the same north–south line as the tract, at ${DIST.gw_ranch_mi} and ${DIST.longfellow_mi} miles.`,
    });
    const box = { x: 0.6, y: 1.55, w: 12.13, h: 5.1 };
    const side = Math.min(box.h, box.w);
    const dx = box.x + (box.w - side) / 2;
    const dy = box.y;
    const dia = placeExhibit(s, "exhibit_power_gravity_light.png", 1517, 1517, dx, dy, side, side, { noBorder: true, noShadow: true });

    const cardW = 2.55, cardH = 0.98;
    const rightX = dx + side + 0.18;
    const leftX = dx - cardW - 0.18;

    // 15 mi -> East
    {
      const a = dia.map(858, 758);
      const cy = 3.62;
      callout(s, { x: rightX, y: cy, w: cardW, h: cardH, value: `${ring15.total_gw} GW`, label: "Combined capacity ≤ 15 mi", accent: COPPER });
      leader(s, rightX, cy + cardH / 2, a.x, a.y, COPPER);
    }
    // 30 mi -> NE
    {
      const a = dia.map(900, 617);
      const cy = 1.72;
      callout(s, { x: rightX, y: cy, w: cardW, h: cardH, value: `${ring30.total_gw} GW`, label: "Combined capacity ≤ 30 mi", accent: COPPER });
      leader(s, rightX, cy + cardH - 0.15, a.x, a.y, COPPER);
    }
    // 60 mi -> SE
    {
      const a = dia.map(1044, 1043);
      const cy = 5.55;
      callout(s, { x: rightX, y: cy, w: cardW, h: cardH, value: `${ring60.total_gw} GW`, label: "Combined capacity ≤ 60 mi", accent: NAVY, valueColor: NAVY });
      leader(s, rightX, cy + 0.15, a.x, a.y, NAVY);
    }
    // 100 mi -> West
    {
      const a = dia.map(86, 758);
      const cy = 3.62;
      callout(s, { x: leftX, y: cy, w: cardW, h: cardH, value: `${ring100.total_gw} GW`, label: "Combined capacity ≤ 100 mi", accent: NAVY, valueColor: NAVY });
      leader(s, leftX + cardW, cy + cardH / 2, a.x, a.y, NAVY);
    }

    s.addText(
      "Bearing from Caramba North: GW Ranch ≈ 19° (near-due north); Longfellow ≈ 188° (near-due south) — the tract sits on the line between them, not off to one side.",
      { x: 0.6, y: 6.78, w: 12.13, h: 0.26, fontSize: 9.5, italic: true, color: MUTED, fontFace: BODY_FONT }
    );
    footer(s, 2);
  }

  // ================================================================ 3. THE PROPERTY
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.1 · The property", iconKey: "mappin",
      title: "As-of-right industrial land, five miles from Fort Stockton",
      subheading: "No zoning ordinance and a Far West ERCOT position — this is a use-as-of-right story, not a rezoning story.",
    });
    const box = { x: 0.6, y: 1.55, w: 12.13, h: 5.35 };
    const ex = placeExhibit(s, "exhibit_2_1_site-setting.jpg", 2400, 1500, box.x, box.y, box.w, box.h);

    const site = ex.map(1176, 833);
    const ft = ex.map(1549, 813);
    const countyLine = ex.map(1300, 568);
    const openLand = ex.map(430, 833);

    callout(s, { x: box.x + 0.15, y: box.y + 0.15, w: 2.5, h: 0.92, value: fmt(C.acres_max), label: "Max contiguous acres", accent: NAVY, valueColor: NAVY });
    leader(s, box.x + 0.15 + 1.25, box.y + 0.15 + 0.92, site.x, site.y, NAVY);

    callout(s, { x: box.x + box.w - 2.75, y: box.y + 0.15, w: 2.6, h: 0.92, value: `≈${C.solstice_miles === undefined ? 5 : 5} mi`, label: "To Fort Stockton (services, airport)", accent: COPPER });
    leader(s, box.x + box.w - 0.15, box.y + 0.15 + 0.46, ft.x, ft.y, COPPER);

    callout(s, { x: box.x + 0.15, y: box.y + box.h - 1.1, w: 2.8, h: 0.95, value: "No zoning", label: "Industrial / energy use as of right", accent: COPPER });
    leader(s, box.x + 0.15 + 1.4, box.y + box.h - 1.1, countyLine.x, countyLine.y, COPPER);

    callout(s, { x: box.x + box.w - 2.9, y: box.y + box.h - 1.1, w: 2.75, h: 0.95, value: "Far West", label: "Highest-growth large-load pocket, ERCOT", accent: NAVY, valueColor: NAVY });
    leader(s, box.x + box.w - 1.5, box.y + box.h - 1.1, openLand.x, openLand.y, NAVY);

    footer(s, 3);
  }

  // ================================================================ 4. TRANSMISSION
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.2 · Transmission", iconKey: "tower",
      title: "Fifteen miles from the western terminus of ERCOT’s 765 kV backbone",
      subheading: "The transmission decision is already made, upstream of this site — not a future contingency.",
    });
    const box = { x: 0.6, y: 1.55, w: 12.13, h: 5.35 };
    const ex = placeExhibit(s, "exhibit_3_1_planned-grid-upgrades.jpg", 2400, 1374, box.x, box.y, box.w, box.h);
    const solstice = ex.map(834, 730);
    const site = ex.map(1205, 736);

    callout(s, {
      x: box.x + 0.15, y: box.y + 0.15, w: 3.55, h: 1.15, value: `${C.solstice_miles} mi`,
      label: "To AEP Solstice — western terminus of all 3 approved 765 kV Permian import paths (PBRP No. 55718, Apr 2025)", accent: COPPER,
    });
    leader(s, box.x + 0.15 + 1.7, box.y + 0.15 + 1.15, solstice.x, solstice.y, COPPER);

    callout(s, {
      x: box.x + box.w - 2.65, y: box.y + 0.15, w: 2.5, h: 0.95, value: "6", label: "Local substations within 10 miles", accent: NAVY, valueColor: NAVY,
    });
    leader(s, box.x + box.w - 2.65 + 1.25, box.y + 0.15 + 0.95, site.x, site.y, NAVY);

    callout(s, {
      x: box.x + box.w - 2.9, y: box.y + box.h - 1.05, w: 2.75, h: 0.9, value: "141 + 133", label: "Substation + line upgrades tracked ERCOT-wide (TPIT pipeline)", accent: COPPER,
    });

    footer(s, 4);
  }

  // ================================================================ 5. REGIONAL POWER CLUSTER
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.3 · Regional power cluster", iconKey: "industry",
      title: "12 GW already queued in Pecos County alone",
      subheading: "Before counting the two hyperscale campuses profiled ahead — this is the densest renewable + storage cluster in ERCOT.",
    });
    const box = { x: 0.6, y: 1.55, w: 12.13, h: 5.35 };
    const ex = placeExhibit(s, "exhibit_4_1_generation-cluster.jpg", 2400, 1374, box.x, box.y, box.w, box.h);
    const site = ex.map(1056, 687);
    const stgall = ex.map(1237, 848);

    callout(s, { x: box.x + 0.15, y: box.y + 0.15, w: 2.75, h: 0.95, value: `${fmt(S4.pecos_operating_total_mw)} MW`, label: "Operating, Pecos County", accent: NAVY, valueColor: NAVY });
    callout(s, { x: box.x + 0.15, y: box.y + 1.2, w: 2.75, h: 0.95, value: `${fmt(S4.pecos_queue_total_mw)} MW`, label: "ERCOT queue, Pecos County", accent: COPPER });

    callout(s, { x: box.x + box.w - 3.05, y: box.y + 0.15, w: 2.9, h: 0.95, value: `${S4.queue_within_20mi_projects} · ${fmt(S4.queue_within_20mi_mw)} MW`, label: "Queued projects within 20 miles", accent: NAVY, valueColor: NAVY });
    leader(s, box.x + box.w - 3.05 + 1.45, box.y + 0.15 + 0.95, site.x, site.y, NAVY);

    callout(s, { x: box.x + box.w - 3.05, y: box.y + box.h - 1.1, w: 2.9, h: 0.95, value: "1.9 mi · 103 MW", label: "Nearest operating storage — St. Gall Energy Storage I", accent: COPPER });
    leader(s, box.x + box.w - 3.05 + 1.45, box.y + box.h - 1.1, stgall.x, stgall.y, COPPER);

    footer(s, 5);
  }

  // ================================================================ 6. WATER & GAS (native diagram)
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.4 / 02.5 · Water & natural gas", iconKey: "droplet",
      title: "Water and gas positions that are already closed, not open",
      subheading: "Two-thirds of the district’s industrial water rights, and a signable 15-year Waha-basis gas quote, sit on this position today.",
    });

    const cy = 4.15; // corridor line y
    const lx = 1.9, mx = 6.67, rx = 11.4;
    s.addShape("line", { x: lx, y: cy, w: mx - lx, h: 0, line: { color: LINE, width: 2 } });
    s.addShape("line", { x: mx, y: cy, w: rx - mx, h: 0, line: { color: LINE, width: 2 } });

    // nodes
    iconBadge(s, "gaspump", lx - 0.34, cy - 0.34, 0.68, COPPER);
    s.addText("WAHA HUB", { x: lx - 0.9, y: cy + 0.42, w: 1.8, h: 0.3, fontSize: 11, bold: true, color: NAVY, align: "center", fontFace: BODY_FONT });

    iconBadge(s, "mappin", mx - 0.42, cy - 0.42, 0.84, NAVY);
    s.addText("CARAMBA NORTH", { x: mx - 1.1, y: cy + 0.5, w: 2.2, h: 0.3, fontSize: 12, bold: true, color: NAVY, align: "center", fontFace: BODY_FONT });

    iconBadge(s, "droplet", rx - 0.34, cy - 0.34, 0.68, COPPER);
    s.addText("MIDDLE PECOS GCD", { x: rx - 1.1, y: cy + 0.42, w: 2.2, h: 0.3, fontSize: 11, bold: true, color: NAVY, align: "center", fontFace: BODY_FONT });

    // distance tag on the gas segment
    const tagX = (lx + mx) / 2;
    s.addShape("roundRect", { x: tagX - 0.5, y: cy - 0.22, w: 1.0, h: 0.44, rectRadius: 0.06, fill: { color: WHITE }, line: { color: COPPER, width: 1.25 } });
    s.addText(`${C.waha_miles} MI`, { x: tagX - 0.5, y: cy - 0.22, w: 1.0, h: 0.44, fontSize: 12.5, bold: true, color: COPPER, align: "center", valign: "middle", fontFace: BODY_FONT });

    // gas callouts above the line — anchor points spread along the segment,
    // clear of the "20 MI" tag box at its midpoint
    callout(s, { x: lx - 0.6, y: 1.65, w: 3.1, h: 1.0, value: `${fmt(C.gas_quote_mmbtu_d)} MMBtu/d`, label: `${C.gas_quote_term_years}-yr term · Waha-index pricing`, accent: COPPER });
    leader(s, lx + 0.95, 2.65, lx + 1.55, cy - 0.03, COPPER);

    callout(s, { x: lx - 0.6, y: 5.05, w: 3.1, h: 1.0, value: `$${C.gas_ciac_musd}M CIAC`, label: `Lead time ${C.gas_lead_months} months · counterparty-supplied terms`, accent: COPPER });
    leader(s, lx + 0.95, 5.05, lx + 1.55, cy + 0.03, COPPER);

    // water callouts above/below the right segment — anchor points spread
    // along the segment, clear of the aquifer node icon
    callout(s, { x: rx - 2.5, y: 1.65, w: 3.1, h: 1.0, value: `${fmt(C.water_af_yr)} AF/yr`, label: `≈ ${C.water_mgd} MGD — Edwards-Trinity (Plateau) aquifer`, accent: NAVY, valueColor: NAVY });
    leader(s, rx - 0.5, 2.65, rx - 1.55, cy - 0.03, NAVY);

    callout(s, { x: rx - 2.5, y: 5.05, w: 3.1, h: 1.0, value: "≈ 2/3", label: "Of all Middle Pecos GCD industrial water rights", accent: NAVY, valueColor: NAVY });
    leader(s, rx - 0.5, 5.05, rx - 1.55, cy + 0.03, NAVY);

    s.addText(
      "Basis context: structural discount to Henry Hub, with negative Waha prints in 2024–2025 as Matterhorn, Blackcomb, Hugh Brinson, and GCX rebalance Permian egress.",
      { x: 0.6, y: 6.9, w: 12.13, h: 0.4, fontSize: 9.5, italic: true, color: MUTED, fontFace: BODY_FONT }
    );
    footer(s, 6);
  }

  // ================================================================ 7. REGIONAL DC PIPELINE (5-anchor map)
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.6 · Regional data-center / power pipeline", iconKey: "server",
      title: "Five projects on one map — the corridor is not a two-project story",
      subheading: "The two feature anchors ahead (GW Ranch, Longfellow) sit alongside three more announced positions on the same catchment.",
    });
    // The base raster is very wide/short (~2:1) relative to the slide box,
    // so a full-bleed fit leaves only slim side margins where the base
    // map's own label rows already run close to the edges. Size the
    // exhibit to leave real margins on both sides for the callout column,
    // so cards sit fully beside the map rather than clipping its labels.
    const outer = { x: 0.6, y: 1.55, w: 12.13, h: 5.15 };
    const exH = 3.4;
    const ex = placeExhibit(s, "exhibit_pipeline5_mapled.jpg", 1570, 770, outer.x, outer.y + (outer.h - exH) / 2, outer.w, exH);

    // badge anchor points, in LOCAL crop coords (crop origin 250,320 from
    // the 2400x1374 source) — see build_pipeline5_annotated_exhibit.py
    const b1 = ex.map(64, 65);    // Chevron
    const b2 = ex.map(685, 253.5); // GW Ranch
    const b3 = ex.map(421, 306);  // Alpha Digital
    const b4 = ex.map(667, 495);  // Longfellow
    const b5 = ex.map(642, 708);  // La Escalera

    const cw = 2.4, ch = 0.98;
    const rxc = outer.x + outer.w - cw;
    callout(s, { x: rxc, y: outer.y, w: cw, h: ch, value: "2.5–5 GW", label: "1 · Chevron West Texas Power Plant (announced)", accent: COPPER, fontSize: 17 });
    leader(s, rxc, outer.y + ch / 2, b1.x, b1.y, COPPER);

    callout(s, { x: rxc, y: outer.y + ch + 0.14, w: cw, h: ch, value: "7.65 GW", label: "2 · GW Ranch — under construction", accent: RED, fontSize: 17 });
    leader(s, rxc, outer.y + ch + 0.14 + ch / 2, b2.x, b2.y, RED);

    callout(s, { x: outer.x, y: outer.y, w: cw, h: ch, value: "≈ 2 GW", label: "3 · Alpha Digital Campus (Wolf Bone Ranch)", accent: COPPER, fontSize: 17 });
    leader(s, outer.x + cw, outer.y + ch / 2, b3.x, b3.y, COPPER);

    callout(s, { x: rxc, y: outer.y + outer.h - ch, w: cw, h: ch, value: `≈${DIST.longfellow_mi} mi`, label: "4 · Longfellow — phase-1 site work underway", accent: RED, fontSize: 17 });
    leader(s, rxc, outer.y + outer.h - ch / 2, b4.x, b4.y, RED);

    callout(s, { x: outer.x, y: outer.y + outer.h - ch, w: cw, h: ch, value: "Pecos Flats", label: "5 · La Escalera Ranch — Apex Clean Energy", accent: COPPER, fontSize: 15 });
    leader(s, outer.x + cw, outer.y + outer.h - ch / 2, b5.x, b5.y, COPPER);

    footer(s, 7);
  }

  // ================================================================ 8. FEATURE — GW RANCH
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "Feature · Amazon / GW Ranch", iconKey: "handshake", accent: RED,
      title: `GW Ranch — ≈ ${DIST.gw_ranch_mi} miles from Caramba North`,
      subheading: "The largest air permit issued in the US this year sits up the same highway corridor — under construction, not announced.",
    });
    // exhibit_amz_gwranch is a wide, short banner (2.6:1) — fit it full-
    // width so it reads large, then run the key numbers in a row beneath.
    const exW = 9.6;
    const exX = 0.6 + (12.13 - exW) / 2;
    const exY = 1.55;
    const exGeo = placeExhibit(s, "exhibit_amz_gwranch.jpg", 1410, 540, exX, exY, exW, 4.2);

    const facts = [
      ["7.65 GW", "TCEQ air permit — largest issued in the US (Jan/Feb 2026)"],
      ["1.8 GW + 750 MW", "Battery storage · solar, alongside 35 gas turbines"],
      ["3 buildings", "189,000 sq ft each (Gensler) — targeted Dec 2026"],
      ["≈ $12B", "Estimated total project investment"],
    ];
    const rowY = exY + exGeo.h + 0.16, rowH = 1.12, cw2 = 2.85, gap2 = 0.16;
    const rowW = facts.length * cw2 + (facts.length - 1) * gap2;
    const rowX = 0.6 + (12.13 - rowW) / 2;
    facts.forEach(([v, l], i) => {
      callout(s, { x: rowX + i * (cw2 + gap2), y: rowY, w: cw2, h: rowH, value: v, label: l, accent: RED, fontSize: 18, labelSize: 8 });
    });
    s.addText(
      "Under construction — 79.3% of the two profiled anchors’ combined announced MW. Clarification: the 7.65 GW figure is a TCEQ generation air permit, not an ERCOT interconnection queue position; the site is off-grid initially and subject to the Aug 3, 2026 state data-center permitting pause pending audit.",
      { x: 0.6, y: rowY + rowH + 0.1, w: 12.13, h: 0.42, fontSize: 8.3, italic: true, color: MUTED, fontFace: BODY_FONT, lineSpacingMultiple: 1.05 }
    );
    footer(s, 8);
  }

  // ================================================================ 9. FEATURE — LONGFELLOW
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "Feature · Longfellow", iconKey: "fire", accent: RED,
      title: `Longfellow — ≈ ${DIST.longfellow_mi} miles from Caramba North`,
      subheading: "A second phased gas-generation campus twenty miles south — the corridor’s demand for on-site power isn’t one project deep.",
    });
    // exhibit_longfellow is likewise a wide, short banner (2.79:1).
    const exW9 = 9.6;
    const exX9 = 0.6 + (12.13 - exW9) / 2;
    const exY9 = 1.55;
    const exGeo9 = placeExhibit(s, "exhibit_longfellow.jpg", 880, 315, exX9, exY9, exW9, 4.2);

    const facts = [
      ["568 acres", "Pecos County site (Longfellow Ranch)"],
      [`≈ ${DIST.longfellow_mi} mi`, "From Caramba North, edge-to-edge"],
      ["On-site gas", "Aero-derivative turbines planned, SCR + carbon-capture capability"],
      ["Phase-1 underway", "Site work underway; generation build planned in phases"],
    ];
    const rowY9 = exY9 + exGeo9.h + 0.18, rowH9 = 1.12, cw9 = 2.85, gap9 = 0.16;
    const rowW9 = facts.length * cw9 + (facts.length - 1) * gap9;
    const rowX9 = 0.6 + (12.13 - rowW9) / 2;
    facts.forEach(([v, l], i) => {
      callout(s, { x: rowX9 + i * (cw9 + gap9), y: rowY9, w: cw9, h: rowH9, value: v, label: l, accent: RED, fontSize: 17, labelSize: 8 });
    });
    s.addText(
      "Closed-loop cooling on permitted non-potable groundwater. No confirmed ERCOT interconnection queue position or TCEQ air-permit record found for this site as of Aug 2026 — a fact about permitting status, not commentary on viability.",
      { x: 0.6, y: rowY9 + rowH9 + 0.12, w: 12.13, h: 0.42, fontSize: 8.3, italic: true, color: MUTED, fontFace: BODY_FONT, lineSpacingMultiple: 1.05 }
    );
    footer(s, 9);
  }

  // ================================================================ 10. PROJECT MATURITY (donut)
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.6 · Project-maturity framing", iconKey: "chartcol",
      title: "The regional pipeline is majority-built, not majority-speculative",
      subheading: "Of the two profiled anchors’ combined announced capacity, four-fifths is already under construction.",
    });
    const uc = MATURITY.under_construction, pl = MATURITY.seeking_tenant || MATURITY.announced_permitted;
    s.addChart(pres.ChartType.doughnut, [{
      name: "Project maturity",
      labels: ["Under construction (GW Ranch)", "Planned / phase-1 (Longfellow)"],
      values: [uc.pct_of_local_mw, pl.pct_of_local_mw],
    }], {
      x: 1.3, y: 1.7, w: 5.6, h: 5.2, holeSize: 62,
      chartColors: [RED, RED_DK],
      showLegend: false, showValue: false, showPercent: false, dataBorderWidth: 2, dataBorderColor: WHITE,
    });
    s.addText(`${uc.pct_of_local_mw}%`, { x: 1.3, y: 3.55, w: 5.6, h: 0.7, fontSize: 34, bold: true, color: RED, align: "center", fontFace: BODY_FONT });
    s.addText("under construction", { x: 1.3, y: 4.2, w: 5.6, h: 0.35, fontSize: 11, color: MUTED, align: "center", charSpacing: 1, fontFace: BODY_FONT });

    const rx = 7.5, rw = 5.23;
    callout(s, { x: rx, y: 1.7, w: rw, h: 1.35, value: `${uc.pct_of_local_mw}% · ${(uc.mw / 1000).toFixed(2)} GW`, label: "GW Ranch — under construction, first power targeted H1 2027", accent: RED, fontSize: 22 });
    callout(s, { x: rx, y: 3.2, w: rw, h: 1.35, value: `${pl.pct_of_local_mw}%`, label: "Longfellow — planned / phase-1 site work underway, of combined announced capacity", accent: RED_DK, fontSize: 22 });
    callout(s, { x: rx, y: 4.7, w: rw, h: 2.05, value: "2 of 2", label: "Profiled anchors within 60 miles — the pipeline is not one project deep, and most of it is already poured concrete, not a rendering", accent: NAVY, valueColor: NAVY, fontSize: 22 });

    footer(s, 10);
  }

  // ================================================================ 11. MACRO CONTEXT (dark bookend)
  {
    const s = darkSlide(pres);
    headerBand(s, {
      eyebrow: "State-level context", iconKey: "trendup", dark: true,
      title: "A queue large enough to trigger a state audit",
      subheading: "The demand signal is real enough to have created a policy problem — a different claim than “this area is growing.”",
    });
    const steps = [
      { v: "63 GW", l: "ERCOT large-load queue, end of 2024" },
      { v: "226 GW", l: "ERCOT large-load queue, Nov 2025 — ~77% data centers targeting 2030" },
      { v: "474 GW", l: "Statewide backlog, Aug 2026 (~90% data-center-driven)" },
    ];
    const barY = 2.15, barH = 3.05, gap = 0.55;
    const heightFrac = [0.4, 0.68, 0.95];
    const totalW = 10.9, bw = (totalW - gap * 2) / 3;
    const barTops = [];
    steps.forEach((st, i) => {
      const x = 1.2 + i * (bw + gap);
      const h = barH * heightFrac[i];
      const y = barY + (barH - h);
      barTops.push(y);
      s.addShape("roundRect", { x, y, w: bw, h, rectRadius: 0.05, fill: { color: i === 2 ? RED : COPPER }, line: { type: "none" }, shadow: shadow() });
      s.addText(st.v, { x, y: y - 0.58, w: bw, h: 0.5, fontSize: 27, bold: true, color: WHITE, align: "center", fontFace: BODY_FONT });
      s.addText(st.l, { x: x - 0.25, y: barY + barH + 0.16, w: bw + 0.5, h: 0.75, fontSize: 10, color: "9FB0C6", align: "center", fontFace: BODY_FONT, lineSpacingMultiple: 1.15 });
    });
    for (let i = 0; i < 2; i++) {
      const x1 = 1.2 + i * (bw + gap) + bw, y1 = barTops[i] + 0.15;
      const x2 = 1.2 + (i + 1) * (bw + gap), y2 = barTops[i + 1] + 0.15;
      s.addShape("line", {
        x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1) || 0.001,
        flipV: y2 < y1,
        line: { color: "9FB0C6", width: 1.5, dashType: "dash", endArrowType: "triangle" },
      });
    }
    s.addText(
      `The region around Caramba North (${ring60.total_gw} GW within 60 mi) sits inside a queue so large it triggered an Aug 3, 2026 directive to audit all ERCOT-queue data centers and pause the “Batch Zero” large-load review process.`,
      { x: 1.2, y: 6.1, w: 10.9, h: 0.55, fontSize: 11, color: ICE, fontFace: BODY_FONT, lineSpacingMultiple: 1.12 }
    );
    s.addText("Source class: public reporting, Aug 2026 — Latitude Media (Dec 3, 2025); Utility Dive (Aug 2026). Full citations in the source register.", {
      x: 1.2, y: 6.78, w: 10.9, h: 0.3, fontSize: 8.5, italic: true, color: "6B7A90", fontFace: BODY_FONT,
    });
    footer(s, 11, true);
  }

  // ================================================================ 12. SUBSURFACE & DRILLING (bar chart)
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.8 · Subsurface & drilling activity", iconKey: "gauge",
      title: "No new drilling is occurring at or near the site",
      subheading: "Pecos County has the lowest new-drill count of seven comparable Permian counties since 2020 — ~90% below the peer average.",
    });
    const peer = Object.entries(S9.comparison.counties).sort((a, b) => a[1].new_drill - b[1].new_drill);
    s.addChart(pres.ChartType.bar, [{
      name: "New-drill wells since 2020",
      labels: peer.map(([c]) => c),
      values: peer.map(([, v]) => v.new_drill),
    }], {
      x: 0.6, y: 1.65, w: 7.6, h: 5.15,
      barDir: "bar", showTitle: false,
      showValue: true, dataLabelPosition: "outEnd", dataLabelColor: NAVY2, dataLabelFontSize: 10,
      chartColors: peer.map(([c]) => c === "Pecos" ? COPPER : "C9D3DE"),
      catAxisLabelColor: SLATE, catAxisLabelFontSize: 11, valAxisLabelColor: SLATE, valAxisLabelFontSize: 9,
      valGridLine: { color: LINE, size: 0.75 }, catGridLine: { style: "none" }, showLegend: false, valAxisMinVal: 0,
    });

    const rx = 8.45, rw = 4.28;
    callout(s, { x: rx, y: 1.65, w: rw, h: 1.1, value: fmt(S9.comparison.counties.Pecos.new_drill), label: `New-drill wells, Pecos, since 2020 — vs. peer avg ${fmt(S9.comparison.peer_average)}`, accent: COPPER, fontSize: 24 });
    callout(s, { x: rx, y: 2.85, w: rw, h: 1.1, value: "0", label: "New-drill wells ≤ 5 miles of the tract since 2020", accent: NAVY, valueColor: NAVY, fontSize: 24 });
    callout(s, { x: rx, y: 4.05, w: rw, h: 1.1, value: `${S9.production.radii["≤ 10 mi"].marginal_pct}%`, label: "Of non-plugged wellbores ≤ 10 mi are marginal / end-of-life", accent: COPPER, fontSize: 24 });
    callout(s, { x: rx, y: 5.25, w: rw, h: 1.45, value: "1 of 7", label: "Counties this quiet — Pecos is the lowest of all seven comparable Permian counties by a wide margin", accent: NAVY, valueColor: NAVY, fontSize: 24 });

    footer(s, 12);
  }

  // ================================================================ 13. DILIGENCE PLATFORM (orbit diagram)
  {
    const s = lightSlide(pres);
    headerBand(s, {
      eyebrow: "02.7 · The diligence platform", iconKey: "shield",
      title: "Every figure is independently re-derivable from a cited source",
      subheading: "This isn’t a broker’s summary — every point, line, and boundary traces to a public dataset with a per-feature source popup.",
    });
    const ccx = 4.55, ccy = 4.2, R = 2.05;
    iconBadge(s, "shield", ccx - 0.55, ccy - 0.55, 1.1, NAVY);
    s.addText("GIS PLATFORM", { x: ccx - 1.3, y: ccy + 0.62, w: 2.6, h: 0.3, fontSize: 11, bold: true, color: NAVY, align: "center", fontFace: BODY_FONT });
    s.addShape("ellipse", { x: ccx - R, y: ccy - R, w: R * 2, h: R * 2, fill: { type: "none" }, line: { color: LINE, width: 1.25, dashType: "dash" } });

    const sources = ["ERCOT", "PUCT", "EIA-860", "TCEQ", "RRC", "FracFocus", "Mid. Pecos GCD", "HIFLD"];
    const n = sources.length;
    const nodePts = sources.map((name, i) => {
      const ang = (-90 + (360 / n) * i) * Math.PI / 180;
      return { name, x: ccx + R * Math.cos(ang), y: ccy + R * Math.sin(ang) };
    });
    // spoke lines first, so the badges + labels drawn afterward sit cleanly on top
    nodePts.forEach(({ x, y }) => {
      s.addShape("line", { x: Math.min(x, ccx), y: Math.min(y, ccy), w: Math.abs(x - ccx) || 0.001, h: Math.abs(y - ccy) || 0.001, line: { color: LINE, width: 0.75 } });
    });
    nodePts.forEach(({ name, x, y }) => {
      s.addShape("ellipse", { x: x - 0.36, y: y - 0.36, w: 0.72, h: 0.72, fill: { color: LIGHT }, line: { color: COPPER, width: 1.5 }, shadow: shadow() });
      s.addText(name, { x: x - 0.75, y: y - 0.15, w: 1.5, h: 0.3, fontSize: 9, bold: true, color: NAVY, align: "center", fontFace: BODY_FONT });
    });

    const rx = 9.1, rw = 3.63;
    const items = [
      ["Weekly", "RRC refresh cadence"],
      ["Monthly", "ERCOT queue / TPIT refresh"],
      ["Annually", "EIA / USGS / OSM refresh"],
      ["Byte-verified", "Static, versioned build — access logged"],
    ];
    const rh = 1.15;
    items.forEach(([v, l], i) => {
      callout(s, { x: rx, y: 1.7 + i * rh, w: rw, h: rh - 0.14, value: v, label: l, accent: COPPER, fontSize: 20 });
    });

    s.addText("lrp-tx-gis.netlify.app · access credentials issued to the deal team separately", {
      x: 0.6, y: 7.02, w: 8, h: 0.3, fontSize: 9.5, italic: true, color: MUTED, fontFace: BODY_FONT,
    });
    footer(s, 13);
  }

  // ================================================================ 14. NOTICES (dark bookend)
  {
    const s = darkSlide(pres);
    s.addText("IMPORTANT NOTICES", {
      x: 0.6, y: 0.7, w: 11, h: 0.5, fontSize: 15, bold: true, color: COPPER, charSpacing: 2, fontFace: BODY_FONT,
    });
    const notice = `This Confidential Offering Memorandum has been prepared solely for the use of a limited number of prospective counterparties, under executed non-disclosure agreement, in connection with the potential acquisition of, or investment in, the Caramba North property. It is delivered on a strictly confidential basis and may not be reproduced or distributed without consent.

This document does not constitute an offer to sell or a solicitation of an offer to buy any security or interest. Information is preliminary and indicative, compiled from sources believed reliable, and subject to revision without notice. No representation or warranty, express or implied, is made as to accuracy or completeness.

Public data is drawn from ERCOT (GIS Report, TPIT), PUCT, EIA-860, TCEQ, RRC (dbf900, production, W-1), FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, and U.S. Census TIGER, supplemented by project-level GIS analysis and counterparty-supplied indicative terms. Distances to GW Ranch and Longfellow are measured edge-to-edge — tract boundary to disclosed site location — not centroid-to-centroid; see the companion source register for the full methodology note. Third-party transaction items are drawn from public reporting cited in the companion source register. Recipients should conduct their own independent investigation, including consultation with their own legal, tax, accounting, and engineering advisors.`;
    s.addText(notice, { x: 0.6, y: 1.45, w: 12.1, h: 5.3, fontSize: 11.5, color: ICE, fontFace: BODY_FONT, valign: "top", paraSpaceAfter: 10 });
    footer(s, 14, true);
  }

  await pres.writeFile({ fileName: OUT });
  console.log(`pptx  -> ${path.relative(REPO, OUT)}`);
}

main().catch(err => { console.error(err); process.exit(1); });
