#!/usr/bin/env python3
"""Capture the Caramba North OM map exhibits directly from the deployed GIS
platform, so every exhibit is reproducible and dated rather than pasted.

Each exhibit is a viewport + layer set + annotation set. Annotations are
injected into the live page and anchored to real coordinates via map.project(),
so labels track the features they name at any zoom.

    python3 scripts/capture_om_exhibits.py --out outputs/reports/om_exhibits
    python3 scripts/capture_om_exhibits.py --only 3.1 --headed

Credentials come from LRP_GIS_EMAIL / LRP_GIS_PASSWORD, falling back to the
deal-team access password documented in Appendix A.1 of the Memorandum.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SITE = os.environ.get("LRP_GIS_URL", "https://lrp-tx-gis.netlify.app")
EMAIL = os.environ.get("LRP_GIS_EMAIL", "andrea@abhcm.com")
PASSWORD = os.environ.get("LRP_GIS_PASSWORD", "LRP-Permian-2026")

# Tract centroid, read from the canonical geometry rather than hard-coded.
sys.path.insert(0, str(REPO / "scripts"))
from caramba_om_data import CX, CY  # noqa: E402

SITE_LON, SITE_LAT = round(CX, 4), round(CY, 4)

EXHIBITS = [
    {
        "id": "2.1",
        "slug": "site-setting",
        "eyebrow": "EXHIBIT 2.1 · PECOS COUNTY, TEXAS",
        "title": "The site: contiguous, interstate-front, five miles from Fort Stockton",
        "subtitle": ("Aerial view of the Caramba North tract (green boundary) on the north side "
                     "of Interstate 10, with Fort Stockton and its municipal services to the "
                     "east; the purple line is the Pecos County boundary."),
        "takeaway": ("The tract is a single contiguous block with direct I-10 frontage and town "
                     "services five miles away — the land configuration hyperscale and large-load "
                     "developers in this corridor have been assembling at premium effort elsewhere."),
        "view": {"lat": 30.93, "lon": -102.95, "zoom": 10.2, "base": "esri_imagery"},
        "layers": ["counties", "county_labels", "cities", "tiger_highways", "caramba_north"],
        "legend": {
            "title": "Pecos County, Texas — site setting",
            "items": [{"swatch": "#22c55e", "kind": "box", "label": "Caramba North (subject site)"},
                      {"swatch": "#f59e0b", "kind": "line", "label": "Interstate 10 / US highways"}],
        },
        "labels": [
            {"lon": SITE_LON, "lat": SITE_LAT, "text": "CARAMBA NORTH — up to 1,300 ac", "strong": True},
            {"lon": -102.8794, "lat": 30.8866, "text": "Fort Stockton"},
        ],
    },
    {
        "id": "3.1",
        "slug": "planned-grid-upgrades",
        "eyebrow": "EXHIBIT 3.1 · CARAMBA NORTH CORRIDOR",
        "title": "Planned grid upgrades only (ERCOT TPIT) — the Solstice hub circled, the site beside it",
        "subtitle": ("Planned transmission upgrades (red schematic routes) and planned substation "
                     "upgrades (red points) only — no existing infrastructure shown; the AEP "
                     "Solstice 765 kV terminus is circled, with the site and Fort Stockton labeled."),
        "takeaway": ("The planned-upgrade program radiates from the circled Solstice terminus on "
                     "the site's doorstep — committed grid capital converging on this exact pocket. "
                     "Routes are schematic point-to-point representations pending final CCN routing."),
        "view": {"lat": 31.15, "lon": -102.90, "zoom": 8.1, "base": "carto_light"},
        "layers": ["counties", "county_labels", "cities", "caramba_north",
                   "tpit_lines", "tpit_subs", "solstice_substation"],
        "legend": {
            "title": "Planned grid upgrades only (ERCOT TPIT) — Caramba North corridor",
            "items": [{"swatch": "#e11d48", "kind": "line", "label": "Planned transmission upgrade (route, schematic)"},
                      {"swatch": "#e11d48", "kind": "dot", "label": "Planned substation upgrade"},
                      {"swatch": "#f59e0b", "kind": "dot", "label": "AEP Solstice 765 kV substation (circled)"},
                      {"swatch": "#22c55e", "kind": "box", "label": "Caramba North"}],
        },
        "labels": [
            {"lon": SITE_LON, "lat": SITE_LAT, "text": "CARAMBA NORTH", "strong": True},
            {"lon": -102.8794, "lat": 30.8866, "text": "Fort Stockton"},
        ],
        "circles": [{"lon": -103.0329, "lat": 31.1519, "radius": 34,
                     "text": "AEP SOLSTICE SUBSTATION — 765 kV terminus (upgrade hub)"}],
    },
    {
        "id": "4.1",
        "slug": "generation-cluster",
        "eyebrow": "EXHIBIT 4.1 · PECOS COUNTY AND NEIGHBORING COUNTIES",
        "title": "The operating fleet and the interconnection queue, on one map",
        "subtitle": ("Operating generation (EIA-860 plants, batteries, solar; USGS/LBNL wind) with "
                     "the ERCOT generator-interconnection queue over the same footprint. Queue "
                     "points are sized by requested capacity."),
        "takeaway": ("The site sits inside the densest operating renewable cluster in ERCOT, with a "
                     "queue several times the installed base underwriting the same pocket."),
        "view": {"lat": 31.20, "lon": -102.90, "zoom": 7.7, "base": "carto_light"},
        "layers": ["counties", "county_labels", "cities", "caramba_north",
                   "eia860_plants", "eia860_battery", "solar", "wind", "ercot_queue"],
        "legend": {
            "title": "Operating fleet and ERCOT queue — Pecos and neighboring counties",
            "items": [{"swatch": "#22c55e", "kind": "box", "label": "Caramba North"},
                      {"swatch": "#eab308", "kind": "dot", "label": "Operating solar"},
                      {"swatch": "#38bdf8", "kind": "dot", "label": "Operating wind"},
                      {"swatch": "#a855f7", "kind": "dot", "label": "Operating storage / plants"},
                      {"swatch": "#e11d48", "kind": "dot", "label": "ERCOT interconnection queue"}],
        },
        "labels": [{"lon": SITE_LON, "lat": SITE_LAT, "text": "CARAMBA NORTH", "strong": True}],
    },
    {
        "id": "7.1",
        "slug": "datacenter-pipeline",
        "eyebrow": "EXHIBIT 7.1 · PECOS AND REEVES COUNTIES",
        "title": "The announced data-center and large-load projects surrounding the site",
        "subtitle": ("Campus land positions (red boundaries — GW Ranch, Longfellow / Project Horizon "
                     "with its Poolside / CoreWeave anchor, La Escalera / Apex) plus labeled callouts "
                     "for announced projects; callouts marked “approx.” are anchored to the "
                     "nearest public reference where sponsors have not disclosed coordinates."),
        "takeaway": ("Gigawatt-scale sponsors have taken positions on every side of the site within "
                     "the regional catchment. Caramba North is the comparable contiguous block at "
                     "the center of that ring, five miles from town services."),
        "view": {"lat": 31.05, "lon": -103.10, "zoom": 8.4, "base": "carto_light"},
        "layers": ["counties", "county_labels", "cities", "caramba_north", "waha_circle",
                   "gw_ranch", "longfellow_ranch", "la_escalera", "dc_anchors"],
        "legend": {
            "title": "Announced data-center and large-load positions",
            "items": [{"swatch": "#e11d48", "kind": "box", "label": "Announced campus land position"},
                      {"swatch": "#22c55e", "kind": "box", "label": "Caramba North (subject site)"},
                      {"swatch": "#0ea5e9", "kind": "dot", "label": "Announced project anchor point"}],
        },
        "labels": [{"lon": SITE_LON, "lat": SITE_LAT, "text": "CARAMBA NORTH", "strong": True}],
        "anchor_labels": True,
    },
]

OVERLAY_CSS = """
#om-annot{position:absolute;inset:0;z-index:800;pointer-events:none;
  font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;}
#om-annot .lbl{position:absolute;transform:translate(-50%,-50%);
  background:rgba(255,255,255,.94);border:1px solid #1f2937;border-radius:3px;
  padding:3px 7px;font-size:12px;line-height:1.15;color:#111827;white-space:nowrap;
  box-shadow:0 1px 3px rgba(0,0,0,.25);}
#om-annot .lbl.strong{font-weight:700;letter-spacing:.02em;}
#om-annot .ring{position:absolute;transform:translate(-50%,-50%);border:2.5px dashed #b91c1c;
  border-radius:50%;}
#om-annot .legend{position:absolute;left:14px;bottom:14px;background:rgba(255,255,255,.95);
  border:1px solid #cbd5e1;border-radius:4px;padding:9px 11px;font-size:11px;color:#111827;
  box-shadow:0 2px 8px rgba(0,0,0,.2);max-width:330px;}
#om-annot .legend h4{margin:0 0 6px;font-size:11px;font-weight:700;}
#om-annot .legend .row{display:flex;align-items:center;gap:7px;margin:3px 0;}
#om-annot .sw{flex:0 0 14px;height:12px;}
#om-annot .sw.box{border:1.6px solid var(--c);background:transparent;}
#om-annot .sw.line{height:0;border-top:3px solid var(--c);}
#om-annot .sw.dot{width:9px;height:9px;flex:0 0 9px;border-radius:50%;background:var(--c);
  margin-left:2px;margin-right:3px;}
#om-annot .stamp{position:absolute;right:14px;bottom:14px;font-size:10px;font-weight:700;
  letter-spacing:.14em;color:#b91c1c;background:rgba(255,255,255,.85);padding:3px 7px;
  border-radius:3px;}
"""

DRAW_JS = r"""
(spec) => {
  const map = window.map;
  const host = document.getElementById('map');
  document.getElementById('om-annot')?.remove();
  const root = document.createElement('div');
  root.id = 'om-annot';
  host.appendChild(root);

  const place = (el, lon, lat) => {
    const p = map.project([lon, lat]);
    el.style.left = p.x + 'px';
    el.style.top = p.y + 'px';
  };
  const made = [];

  (spec.circles || []).forEach(c => {
    const ring = document.createElement('div');
    ring.className = 'ring';
    ring.style.width = ring.style.height = (c.radius * 2) + 'px';
    root.appendChild(ring);
    made.push([ring, c.lon, c.lat]);
    if (c.text) {
      const t = document.createElement('div');
      t.className = 'lbl strong';
      t.textContent = c.text;
      root.appendChild(t);
      made.push([t, c.lon, c.lat, 0, -(c.radius + 18)]);
    }
  });

  (spec.labels || []).forEach(l => {
    const el = document.createElement('div');
    el.className = 'lbl' + (l.strong ? ' strong' : '');
    el.textContent = l.text;
    root.appendChild(el);
    made.push([el, l.lon, l.lat, l.dx || 0, l.dy || -16]);
  });

  if (spec.legend) {
    const lg = document.createElement('div');
    lg.className = 'legend';
    lg.innerHTML = '<h4>' + spec.legend.title + '</h4>' +
      spec.legend.items.map(i =>
        '<div class="row"><span class="sw ' + i.kind + '" style="--c:' + i.swatch +
        '"></span><span>' + i.label + '</span></div>').join('');
    root.appendChild(lg);
  }

  const stamp = document.createElement('div');
  stamp.className = 'stamp';
  stamp.textContent = 'CONFIDENTIAL — ' + spec.stamp;
  root.appendChild(stamp);

  const reflow = () => made.forEach(([el, lon, lat, dx, dy]) => {
    place(el, lon, lat);
    if (dx || dy) {
      el.style.marginLeft = (dx || 0) + 'px';
      el.style.marginTop = (dy || 0) + 'px';
    }
  });
  reflow();
  map.on('move', reflow);
  return made.length;
}
"""


def hash_for(ex):
    v = ex["view"]
    return (f"#lat={v['lat']}&lon={v['lon']}&zoom={v['zoom']}"
            f"&layers={','.join(ex['layers'])}&base={v['base']}&sb=1")


def capture(pw, ex, outdir, width, height, stamp, headed):
    from playwright.sync_api import TimeoutError as PWTimeout

    launch = {"headless": not headed,
              "args": ["--no-sandbox", "--disable-dev-shm-usage",
                       "--disable-http2", "--ignore-certificate-errors"]}
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    if proxy:
        launch["proxy"] = {"server": proxy}
    browser = pw.chromium.launch(**launch)
    ctx = browser.new_context(viewport={"width": width, "height": height},
                              device_scale_factor=2, ignore_https_errors=True)
    page = ctx.new_page()
    page.goto(SITE, wait_until="domcontentloaded", timeout=60000)

    # access gate
    try:
        page.wait_for_selector("#oxy-gate-form", timeout=8000)
        page.fill("#oxy-gate-email", EMAIL)
        page.fill("#oxy-gate-pass", PASSWORD)
        page.click("#oxy-gate-btn")
        page.wait_for_selector("#oxy-gate", state="detached", timeout=30000)
    except PWTimeout:
        pass  # already authenticated in this context

    page.evaluate("h => { location.hash = h; }", hash_for(ex))
    page.wait_for_timeout(1200)
    page.evaluate("() => window.map && window.map.resize()")
    try:
        page.wait_for_function("() => window.map && window.map.isStyleLoaded() && window.map.loaded()",
                               timeout=45000)
    except PWTimeout:
        print(f"  ! {ex['id']}: map did not report idle; capturing anyway")
    page.wait_for_timeout(3500)

    page.add_style_tag(content=OVERLAY_CSS)
    spec = {k: ex.get(k) for k in ("labels", "circles", "legend")}
    spec["stamp"] = stamp
    page.evaluate(DRAW_JS, spec)
    page.wait_for_timeout(400)

    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / f"exhibit_{ex['id'].replace('.', '_')}_{ex['slug']}.png"
    page.locator("#map").screenshot(path=str(path))
    ctx.close()
    browser.close()
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="outputs/reports/om_exhibits")
    ap.add_argument("--only", nargs="*", help="exhibit ids, e.g. 3.1 7.1")
    ap.add_argument("--width", type=int, default=1600)
    ap.add_argument("--height", type=int, default=916)
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--stamp", default=date.today().isoformat())
    a = ap.parse_args()

    from playwright.sync_api import sync_playwright

    outdir = REPO / a.out
    todo = [e for e in EXHIBITS if not a.only or e["id"] in a.only]
    manifest = []
    with sync_playwright() as pw:
        for ex in todo:
            print(f"capturing exhibit {ex['id']} — {ex['slug']}")
            p = capture(pw, ex, outdir, a.width, a.height, a.stamp, a.headed)
            print(f"  -> {p.relative_to(REPO)}  ({p.stat().st_size // 1024} KB)")
            manifest.append({
                "id": ex["id"], "slug": ex["slug"], "file": p.name,
                "eyebrow": ex["eyebrow"], "title": ex["title"],
                "subtitle": ex["subtitle"], "takeaway": ex["takeaway"],
                "captured": a.stamp, "view": ex["view"], "layers": ex["layers"],
            })
    (outdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"wrote {outdir.relative_to(REPO)}/manifest.json ({len(manifest)} exhibits)")


if __name__ == "__main__":
    main()
