#!/usr/bin/env node
/* Caramba North — "Minimalist Executive" deck (brief §6.D).
 * One idea per slide, oversized type, huge negative space, at most one
 * supporting stat row or exhibit crop per slide. Built to be read in five
 * minutes. Reuses the shadow()/exhibitImage() plumbing pattern from
 * build_caramba_om_pptx.js but with a deliberately different, reduced
 * visual system — no tables, no dense stat grids, no serif titling.
 *
 *   node scripts/build_deck_minimalist.js
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");
const pptxgen = require("pptxgenjs");

const REPO = path.resolve(__dirname, "..");
const EXHIBIT_DIR = path.join(REPO, "outputs", "reports", "om_exhibits");
const MINI_DIR = path.join(EXHIBIT_DIR, "_minimalist");
const ICON_DIR = path.join(EXHIBIT_DIR, "icons");
const OUT = path.join(REPO, "outputs", "reports", "Caramba-North-Deck-Minimalist.pptx");

const DATA_JSON = "/tmp/om_minimalist.json";
const INSIGHT_JSON = "/tmp/om_minimalist_insights.json";
execFileSync("python3", [path.join(REPO, "scripts", "caramba_om_data.py"), "--json", DATA_JSON], { cwd: REPO });
execFileSync("python3", [path.join(REPO, "scripts", "build_insight_pack.py"), "--json", INSIGHT_JSON], { cwd: REPO });
// Deck-specific crops of the two feature exhibits — see script docstring:
// both source rasters carry an incidental Longfellow/CoreWeave label that
// conflicts with brief Rule 3, so this derives (not regenerates) compliant
// crops without touching the shared canonical exhibit files.
execFileSync("python3", [path.join(REPO, "scripts", "build_minimalist_exhibit_crops.py")], { cwd: REPO });
const M = JSON.parse(fs.readFileSync(DATA_JSON, "utf8"));
const I = JSON.parse(fs.readFileSync(INSIGHT_JSON, "utf8"));
const { config: C, section3: S3, section4: S4, section9: S9 } = M;
const STAMP = new Date().toISOString().slice(0, 10);

// Corrected edge-to-edge distances (brief Rule 4 / §4) — NEVER the centroid figures.
const GW_RANCH_MI = I.distances_edge_to_edge.gw_ranch_mi;       // 15.5
const LONGFELLOW_MI = I.distances_edge_to_edge.longfellow_mi;   // 19.3
const RINGS = I.ring_analysis; // [{radius_mi, total_gw}, ...] at 15/30/60/100

// ------------------------------------------------------------------ palette
// Deliberately reduced: near-black ink, paper white, one muted slate, one
// red reserved ONLY for the two feature call-outs (GW Ranch / Longfellow)
// per brief §8. No navy-serif system, no tables, no icon rows of five.
const INK = "0B1220";     // near-black navy — dark bg + primary text
const PAPER = "FFFFFF";
const MUTE = "6B7280";    // slate — subheadings / captions
const FAINT = "9CA3AF";   // dark-bg secondary text
const HAIR = "E5E7EB";    // hairline rule
const RED = "B42318";     // reserved for the two feature anchors only
const DARKLINE = "1F2A3D";

function shadow() { return { type: "outer", color: "0B1220", opacity: 0.14, blur: 6, offset: 2, angle: 90 }; }
function fmt(n) { if (n === null || n === undefined) return "—"; return Math.round(n).toLocaleString("en-US"); }

const PW = 13.333, PH = 7.5;
const MX = 0.9; // outer margin — generous, per "huge negative space"

function iconPath(key) { return path.join(ICON_DIR, key + ".png"); }
function iconBadge(s, key, x, y, size, bg) {
  s.addShape("ellipse", { x, y, w: size, h: size, fill: { color: bg }, line: { type: "none" } });
  const pad = size * 0.27;
  const fp = iconPath(key);
  if (fs.existsSync(fp)) {
    s.addImage({ path: fp, x: x + pad, y: y + pad, w: size - pad * 2, h: size - pad * 2 });
  }
}

function darkSlide(pres) {
  const s = pres.addSlide();
  s.background = { color: INK };
  return s;
}
function lightSlide(pres) {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  return s;
}

function kicker(s, n, label, dark) {
  const col = dark ? FAINT : MUTE;
  s.addText([
    { text: n, options: { bold: true, color: dark ? PAPER : INK } },
    { text: "  /  " + label.toUpperCase(), options: { color: col } },
  ], {
    x: MX, y: 0.62, w: 10, h: 0.4, fontSize: 12.5, charSpacing: 2, fontFace: "Arial", margin: 0,
  });
}

function headline(s, text, opts = {}) {
  s.addText(text, Object.assign({
    x: MX, y: 1.18, w: 11.5, h: opts.h || 1.9, fontSize: opts.size || 46, bold: true,
    color: opts.color || INK, fontFace: "Arial", valign: "top", lineSpacingMultiple: 1.02, margin: 0,
  }, opts));
}

function sub(s, text, y, opts = {}) {
  s.addText(text, Object.assign({
    x: MX, y, w: opts.w || 10.6, h: opts.h || 1.1, fontSize: opts.size || 22,
    color: opts.color || MUTE, fontFace: "Arial", valign: "top", lineSpacingMultiple: 1.18, margin: 0,
  }, opts));
}

function pageFooter(s, n, dark) {
  const col = dark ? "3A4A63" : "C7CDD6";
  s.addText("CARAMBA NORTH — CONFIDENTIAL", {
    x: MX, y: PH - 0.55, w: 6, h: 0.3, fontSize: 8.5, color: col, fontFace: "Arial", charSpacing: 1.2, margin: 0,
  });
  s.addText(String(n), {
    x: PW - MX - 0.4, y: PH - 0.55, w: 0.4, h: 0.3, fontSize: 8.5, color: col, align: "right", fontFace: "Arial", margin: 0,
  });
}

// A single stat, big number over small caption — the ONE permitted supporting
// element besides an exhibit crop.
function statBlock(s, x, y, w, value, label, opts = {}) {
  s.addText(value, {
    x, y, w, h: opts.h || 0.85, fontSize: opts.valueSize || 34, bold: true,
    color: opts.color || INK, fontFace: "Arial", margin: 0, valign: "bottom",
  });
  s.addText(label.toUpperCase(), {
    x, y: y + (opts.h || 0.85), w, h: 0.4, fontSize: 10, color: opts.labelColor || MUTE,
    charSpacing: 1.2, fontFace: "Arial", margin: 0, valign: "top",
  });
}
function statRow(s, x, y, w, stats, opts = {}) {
  const gap = 0.5;
  const cw = (w - gap * (stats.length - 1)) / stats.length;
  stats.forEach(([v, l], i) => statBlock(s, x + i * (cw + gap), y, cw, v, l, opts));
}

function exhibitCrop(s, file, dims, x, y, w, opts = {}) {
  const fp = path.join(opts.dir || EXHIBIT_DIR, file);
  if (!fs.existsSync(fp)) return 0;
  const h = w * (dims.h / dims.w);
  s.addImage({ path: fp, x, y, w, h, shadow: opts.noShadow ? undefined : shadow() });
  if (!opts.noBorder) {
    s.addShape("rect", { x, y, w, h, fill: { type: "none" }, line: { color: HAIR, width: 1 } });
  }
  if (opts.caption) {
    s.addText(opts.caption, { x, y: y + h + 0.08, w, h: 0.3, fontSize: 8.5, italic: true, color: MUTE, fontFace: "Arial", margin: 0 });
  }
  return h;
}

// ==================================================================== main
async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "Land Resource Partners";
  pres.title = "Caramba North — Minimalist Executive Summary";

  let n = 1;

  // ---------------------------------------------------------- 1. COVER (dark)
  {
    const s = darkSlide(pres);
    s.addText("CONFIDENTIAL OFFERING MEMORANDUM", {
      x: MX, y: 1.55, w: 10, h: 0.4, fontSize: 12.5, bold: true, color: FAINT, charSpacing: 3, fontFace: "Arial", margin: 0,
    });
    s.addText("CARAMBA NORTH", {
      x: MX, y: 2.05, w: 11.6, h: 1.55, fontSize: 66, bold: true, color: PAPER, fontFace: "Arial", margin: 0,
    });
    s.addText(
      "A 1,300-acre parcel inside an already-forming power and data-center corridor — two hyperscale-scale projects sit on the same north-south line through the property, backed by transmission, water, and gas positions that are already permitted, not proposed.",
      { x: MX, y: 3.75, w: 9.6, h: 1.7, fontSize: 21, color: "CBD5E1", fontFace: "Arial", lineSpacingMultiple: 1.22, margin: 0 }
    );
    s.addShape("line", { x: MX, y: 5.85, w: 11.5, h: 0, line: { color: DARKLINE, width: 1 } });
    s.addText("PECOS COUNTY, TEXAS  ·  FAR WEST ERCOT  ·  I-10 CORRIDOR", {
      x: MX, y: 6.05, w: 8, h: 0.4, fontSize: 11, color: FAINT, charSpacing: 1.5, fontFace: "Arial", margin: 0,
    });
    s.addText(`${STAMP}  ·  Executive read — five minutes`, {
      x: PW - MX - 4, y: 6.05, w: 4, h: 0.4, fontSize: 11, color: FAINT, align: "right", fontFace: "Arial", margin: 0,
    });
  }
  n++;

  // ------------------------------------------------- 2. POWER GRAVITY (dark, flagship)
  {
    const s = darkSlide(pres);
    kicker(s, "02", "The Regional Signal", true);
    headline(s, "32.7 GW sits within 60 miles.", { color: PAPER, size: 38, w: 5.6, h: 1.65 });
    sub(s, "Caramba North is inside that radius, not adjacent to it — and the two feature anchors on the following pages sit on the same north-south line through the property.", 3.15, { color: "CBD5E1", w: 5.55, size: 16.5, h: 1.7 });

    s.addText(
      "By Aug 2026 ERCOT's statewide interconnection backlog reached ≈474 GW (≈90% data-center-driven) — large enough to trigger a gubernatorial audit and a pause of large-load queue review (public reporting, Aug 2026).",
      { x: MX, y: 5.55, w: 5.55, h: 1.15, fontSize: 10.5, italic: true, color: "5B6B85", fontFace: "Arial", margin: 0, lineSpacingMultiple: 1.2 }
    );

    const gw = 5.65;
    exhibitCrop(s, "exhibit_power_gravity_dark.png", { w: 1517, h: 1517 }, PW - MX - gw, 1.05, gw, { noBorder: true, noShadow: true });
    pageFooter(s, n, true);
  }
  n++;

  // ---------------------------------------------------------- 3. THE PROPERTY
  {
    const s = lightSlide(pres);
    kicker(s, "03", "The Property");
    headline(s, "As-of-right industrial land, not a rezoning story.", { size: 36, w: 8.0, h: 1.7 });
    sub(s, "1,300 contiguous acres on I-10, five miles from Fort Stockton, in ERCOT's fastest-growing large-load pocket — with no zoning ordinance standing between this site and use.", 3.15, { w: 7.7 });
    statRow(s, MX, 4.85, 7.7, [
      [fmt(C.acres_max), "Contiguous acres"],
      ["0", "Zoning ordinances"],
      ["~5 mi", "To Fort Stockton"],
    ]);
    exhibitCrop(s, "exhibit_2_1_site-setting.jpg", { w: 2400, h: 1500 }, PW - MX - 3.2, 1.3, 3.2, { caption: "Site setting, I-10 corridor" });
    pageFooter(s, n);
  }
  n++;

  // ---------------------------------------------------------- 4. TRANSMISSION
  {
    const s = lightSlide(pres);
    kicker(s, "04", "Transmission");
    headline(s, "The transmission decision is already made.", { size: 40, w: 7.7 });
    sub(s, `Fifteen miles from the delivery point of all three PUCT-approved 765 kV Permian import paths — this site sits downstream of a decision, not upstream of a proposal.`, 2.85, { w: 7.7 });
    statRow(s, MX, 4.7, 7.7, [
      [`${C.solstice_miles} mi`, "To Solstice Substation"],
      ["3", "Approved 765 kV import paths"],
      [`${S3.tpit_substation_upgrades}`, "Substation upgrades, ERCOT TPIT"],
    ]);
    exhibitCrop(s, "exhibit_3_1_planned-grid-upgrades.jpg", { w: 2400, h: 1374 }, PW - MX - 3.2, 1.3, 3.2, { caption: "Planned grid upgrades (ERCOT TPIT)" });
    pageFooter(s, n);
  }
  n++;

  // ---------------------------------------------------- 5. REGIONAL POWER CLUSTER
  {
    const s = lightSlide(pres);
    kicker(s, "05", "Regional Power Cluster");
    headline(s, `${fmt(S4.pecos_queue_total_mw)} MW is already queued in Pecos County alone.`, { size: 36, w: 7.7, h: 2.1 });
    sub(s, "That's before counting the two hyperscale campuses profiled next — the cluster is county-deep before it is corridor-wide.", 3.35, { w: 7.7 });
    statRow(s, MX, 4.95, 7.7, [
      [gw_(S4.pecos_operating_total_mw), "Operating, Pecos Co."],
      [gw_(S4.pecos_queue_total_mw), "ERCOT queue, Pecos Co."],
      [gw_(S4.adjacent_queue_total_mw), "Queued, 6 adjacent counties"],
    ]);
    exhibitCrop(s, "exhibit_4_1_generation-cluster.jpg", { w: 2400, h: 1374 }, PW - MX - 3.2, 1.3, 3.2, { caption: "Operating fleet + ERCOT queue" });
    pageFooter(s, n);
  }
  n++;

  // ---------------------------------------------------------------- 6. WATER
  {
    const s = lightSlide(pres);
    kicker(s, "06", "Water");
    headline(s, "The water conversation is closed, not open.", { size: 42, w: 10.6 });
    sub(s, `${fmt(C.water_af_yr)} AF/yr — roughly two-thirds of all Middle Pecos GCD industrial water rights — is already permitted on adjacent affiliated lands, drawn from Edwards-Trinity (Plateau) aquifer recharge held through the 1950s drought of record.`, 2.85, { w: 9.4, size: 20 });
    statRow(s, MX, 5.0, 7.2, [
      [fmt(C.water_af_yr), `AF/yr permitted (≈${C.water_mgd} MGD)`],
      ["≈ 2/3", "Of district industrial rights"],
    ]);
    iconBadge(s, "droplet", PW - MX - 1.1, PH - MX - 1.1, 1.1, INK);
    pageFooter(s, n);
  }
  n++;

  // ---------------------------------------------------------------- 7. NATURAL GAS
  {
    const s = lightSlide(pres);
    kicker(s, "07", "Natural Gas");
    headline(s, "A signable gas quote, at a structural discount.", { size: 42, w: 10.6 });
    sub(s, `Twenty miles to Waha, with an indicative ${fmt(C.gas_quote_mmbtu_d)} MMBtu/day, ${C.gas_quote_term_years}-year, Waha-index supply quote already in hand — the same basis discount now drawing behind-the-meter generation to this corridor.`, 2.85, { w: 9.6, size: 20 });
    statRow(s, MX, 5.05, 7.6, [
      [`${C.waha_miles} mi`, "To Waha hub"],
      [`${fmt(C.gas_quote_mmbtu_d)}`, "MMBtu/day, quoted"],
      [`${C.gas_quote_term_years} yr`, "Indicative term"],
    ]);
    iconBadge(s, "gaspump", PW - MX - 1.1, PH - MX - 1.1, 1.1, INK);
    pageFooter(s, n);
  }
  n++;

  // ------------------------------------------------------ 8. FEATURE — GW RANCH
  {
    const s = lightSlide(pres);
    kicker(s, "08", "Feature — GW Ranch (Amazon)");
    headline(s, "The largest air permit issued in the US this year — fifteen miles up the same highway.", { size: 32, w: 6.8, h: 2.1 });
    sub(s, "Under construction, not announced: 7.65 GW of TCEQ-permitted gas generation on an 8,000-acre site, disclosed as Amazon-owned in August 2026.", 3.55, { w: 6.8, size: 16.5 });
    statRow(s, MX, 5.35, 6.8, [
      [`${GW_RANCH_MI} mi`, "From Caramba North"],
      ["7.65 GW", "TCEQ air permit"],
      ["79.3%", "Of anchor MW U/C"],
    ], { color: RED, valueSize: 27 });
    const w8 = 4.5;
    exhibitCrop(s, "exhibit_amz_gwranch_crop.jpg", { w: 1410, h: 450 }, PW - MX - w8, 1.95, w8, { dir: MINI_DIR });
    s.addShape("roundRect", { x: MX, y: 0.55, w: 0.14, h: 0.14, rectRadius: 0.07, fill: { color: RED }, line: { type: "none" } });
    pageFooter(s, n);
  }
  n++;

  // ------------------------------------------------------ 9. FEATURE — LONGFELLOW
  {
    const s = lightSlide(pres);
    kicker(s, "09", "Feature — Longfellow");
    headline(s, "A second phased gas-generation campus, twenty miles south.", { size: 34, w: 6.8, h: 1.8 });
    sub(s, "On-site natural-gas generation planned — aero-derivative turbines with SCR and carbon-capture capability, closed-loop cooling on permitted non-potable groundwater. Phase-1 site work is underway; the corridor's demand for on-site power is not one project deep.", 3.35, { w: 6.8, size: 15, h: 1.9 });
    statRow(s, MX, 5.4, 6.8, [
      [`${LONGFELLOW_MI} mi`, "From Caramba North"],
      ["2 GW", "Original 8-phase design"],
      ["20.7%", "Of anchor MW, phase-1"],
    ], { color: RED, valueSize: 27 });
    const w9 = 4.5;
    exhibitCrop(s, "exhibit_longfellow_notenant.jpg", { w: 880, h: 315 }, PW - MX - w9, 1.95, w9, { dir: MINI_DIR });
    s.addShape("roundRect", { x: MX, y: 0.55, w: 0.14, h: 0.14, rectRadius: 0.07, fill: { color: RED }, line: { type: "none" } });
    pageFooter(s, n);
  }
  n++;

  // ---------------------------------------------------- 10. SUBSURFACE & DRILLING
  {
    const s = lightSlide(pres);
    kicker(s, "10", "Subsurface & Drilling");
    headline(s, "The lowest new-drilling count of seven comparable Permian counties.", { size: 34, w: 10.6, h: 1.7 });
    sub(s, `Pecos County: ${S9.comparison.counties.Pecos.new_drill} new-drill wells since 2020, against a peer average of ${fmt(S9.comparison.peer_average)} — roughly 90% below peer average, with zero new-drill wells within five miles of the tract.`, 3.05, { w: 9.8, size: 19 });
    statRow(s, MX, 5.05, 7.6, [
      [String(S9.comparison.counties.Pecos.new_drill), "New-drill wells, Pecos, since 2020"],
      [fmt(S9.comparison.peer_average), "Peer-county average"],
      ["≈ 90%", "Below peer average"],
    ]);
    iconBadge(s, "gauge", PW - MX - 1.1, PH - MX - 1.1, 1.1, INK);
    pageFooter(s, n);
  }
  n++;

  // ---------------------------------------------------- 11. THE DILIGENCE PLATFORM
  {
    const s = lightSlide(pres);
    kicker(s, "11", "The Diligence Platform");
    headline(s, "Every figure here is independently re-derivable.", { size: 40, w: 10.6 });
    sub(s, "This isn't a broker's summary — every point, line, and boundary in the underlying GIS platform traces to a cited public dataset (ERCOT, PUCT, EIA-860, TCEQ, RRC, FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, Census TIGER), refreshed on a fixed cadence and access-logged.", 2.95, { w: 9.6, size: 18 });
    statRow(s, MX, 5.2, 7.4, [
      ["Weekly", "RRC refresh"],
      ["Monthly", "ERCOT queue / TPIT refresh"],
      ["10+", "Cited public source classes"],
    ]);
    iconBadge(s, "shield", PW - MX - 1.1, PH - MX - 1.1, 1.1, INK);
    pageFooter(s, n);
  }
  n++;

  // ---------------------------------------------------------- 12. CLOSE (dark)
  {
    const s = darkSlide(pres);
    kicker(s, "12", "Close", true);
    s.addText("The region does the selling.", {
      x: MX, y: 1.55, w: 11, h: 1.0, fontSize: 44, bold: true, color: PAPER, fontFace: "Arial", margin: 0,
    });
    s.addText(
      "32.7 GW within 60 miles, a transmission position already downstream of an approved 765 kV decision, water and gas positions already contracted-ready — Caramba North is positioned to benefit from this buildout without carrying the exposure of being the marginal, unproven project in the queue.",
      { x: MX, y: 2.65, w: 9.5, h: 1.5, fontSize: 18.5, color: "CBD5E1", fontFace: "Arial", lineSpacingMultiple: 1.2, margin: 0 }
    );
    s.addShape("line", { x: MX, y: 4.5, w: 11.5, h: 0, line: { color: DARKLINE, width: 1 } });
    const notice = "Confidential Offering Memorandum prepared for a limited number of prospective counterparties under NDA. Not an offer to sell or a solicitation of an offer to buy any security. Information is preliminary and indicative, from sources believed reliable; subject to revision. Public data drawn from ERCOT, PUCT, EIA, TCEQ, RRC, FracFocus, Middle Pecos GCD, HIFLD, USGS, BTS, and U.S. Census TIGER; third-party transaction items sourced to public reporting cited in the companion source register.";
    s.addText(notice, {
      x: MX, y: 4.72, w: 11.5, h: 1.35, fontSize: 9.5, color: "5B6B85", fontFace: "Arial", lineSpacingMultiple: 1.3, margin: 0,
    });
    s.addText("Prepared by Land Resource Partners  ·  lrp-tx-gis.netlify.app", {
      x: MX, y: 6.35, w: 8, h: 0.4, fontSize: 10.5, color: FAINT, fontFace: "Arial", margin: 0,
    });
    s.addText(STAMP, {
      x: PW - MX - 3, y: 6.35, w: 3, h: 0.4, fontSize: 10.5, color: FAINT, align: "right", fontFace: "Arial", margin: 0,
    });
  }
  n++;

  await pres.writeFile({ fileName: OUT });
  console.log(`pptx -> ${path.relative(REPO, OUT)}  (${n - 1} slides)`);
}

function gw_(mw) {
  if (mw === null || mw === undefined) return "—";
  return mw >= 1000 ? (mw / 1000).toFixed(1) + " GW" : Math.round(mw).toLocaleString("en-US") + " MW";
}

main().catch(err => { console.error(err); process.exit(1); });
