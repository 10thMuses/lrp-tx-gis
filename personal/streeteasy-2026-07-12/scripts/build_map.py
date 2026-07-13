#!/usr/bin/env python3
"""Build a self-contained interactive Leaflet map of the StreetEasy listings."""
import json, os, sys
from collections import Counter

SCRATCH = os.environ.get("SE_WORKDIR", os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/data")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SCRATCH, "map.html")

rows = json.load(open(os.path.join(SCRATCH, "listings.json")))
fill_path = os.path.join(SCRATCH, "research_fill.json")
fills = json.load(open(fill_path)) if os.path.exists(fill_path) else {}
for r in rows:
    f = fills.get(r["listing_id"])
    if f and f.get("sqft") and not r.get("sqft"):
        r["sqft"] = f["sqft"]; r["sqft_source"] = f.get("source", "research")
    if f and f.get("year_built") and not r.get("year_built"):
        r["year_built"] = f["year_built"]

# fixed categorical assignment: neighborhoods by listing count desc, then name
hood_counts = Counter(r["neighborhood"] for r in rows)
hoods = [h for h, _ in sorted(hood_counts.items(), key=lambda kv: (-kv[1], kv[0]))]
PALETTE = ["#2a78d6", "#1baf7a", "#eda100", "#008300", "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
hood_color = {h: PALETTE[i % 8] for i, h in enumerate(hoods)}

feats = []
for r in rows:
    feats.append({
        "id": r["listing_id"], "url": r["url"], "lat": r["latitude"], "lng": r["longitude"],
        "addr": r.get("full_address"), "hood": r.get("neighborhood"),
        "rent": r.get("rent"), "net": r.get("net_effective_rent"),
        "beds": r.get("bedrooms"), "baths": r.get("baths"), "rooms": r.get("rooms"),
        "sqft": r.get("sqft"), "type": r.get("unit_type"),
        "listed": r.get("listed_date"), "dom": r.get("days_on_market"),
        "avail": r.get("available_date"), "status": r.get("status"),
        "pos": r.get("private_outdoor_space") or [], "views": r.get("views") or [],
        "features": r.get("unit_features") or [], "amenities": r.get("building_amenities") or [],
        "bldg": r.get("building_name"), "yr": r.get("year_built"),
        "brokerage": r.get("brokerage"), "photo": r.get("photo_url"),
        "photos": r.get("photo_count"), "fees": r.get("fees") or [],
        "deposit": r.get("security_deposit"), "free": r.get("months_free"),
        "term": r.get("lease_term_months"),
        "desc": (r.get("description") or "")[:420],
    })

data_js = json.dumps(feats)
colors_js = json.dumps(hood_color)

html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>StreetEasy Listings — 2026-07-12</title>
<style>__LEAFLET_CSS__</style>
<script>__LEAFLET_JS__</script>
<style>
  :root{
    --surface:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --ink3:#8a887f;
    --card:#ffffff; --line:#e6e4de;
  }
  *{box-sizing:border-box}
  html,body{margin:0;height:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;color:var(--ink)}
  #app{display:flex;height:100%}
  #side{width:340px;min-width:280px;overflow-y:auto;background:var(--surface);border-right:1px solid var(--line);padding:14px}
  #map{flex:1;height:100%}
  h1{font-size:15px;margin:0 0 2px}
  .sub{font-size:12px;color:var(--ink2);margin-bottom:10px}
  .filters{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:10px}
  .chip{font-size:11.5px;padding:3px 9px;border-radius:999px;border:1px solid var(--line);background:var(--card);cursor:pointer;user-select:none;display:inline-flex;align-items:center;gap:5px;color:var(--ink)}
  .chip .dot{width:9px;height:9px;border-radius:50%;display:inline-block}
  .chip.off{opacity:.35}
  .chip:hover{border-color:#b9b6ac}
  select{font-size:12px;padding:3px 6px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink)}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:9px 11px;margin-bottom:7px;cursor:pointer}
  .card:hover{border-color:#2a78d6}
  .card.active{border-color:#2a78d6;box-shadow:0 0 0 2px rgba(42,120,214,.18)}
  .card .price{font-weight:700;font-size:14px}
  .card .net{color:#008300;font-weight:400;font-size:11px;margin-left:4px}
  .card .addr{font-size:12.5px;margin:1px 0}
  .card .meta{font-size:11.5px;color:var(--ink2)}
  .count{font-size:11.5px;color:var(--ink3);margin:6px 0 8px}
  .pin{display:flex;align-items:center;justify-content:center;border-radius:999px;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,.35);color:#fff;font-weight:700;font-size:10.5px;white-space:nowrap;padding:2px 6px}
  .leaflet-popup-content{margin:0;width:308px !important}
  .leaflet-popup-content-wrapper{border-radius:12px;overflow:hidden;padding:0}
  .pp{font-size:12px;line-height:1.45}
  .pp img{width:100%;height:150px;object-fit:cover;display:block;background:#eee}
  .pp .body{padding:10px 12px 12px}
  .pp .price{font-size:16px;font-weight:700}
  .pp .net{color:#008300;font-size:11.5px;font-weight:600;margin-left:6px}
  .pp .addr{font-size:13px;font-weight:600;margin:2px 0 1px}
  .pp .hoodline{color:var(--ink2);margin-bottom:6px}
  .pp .grid{display:grid;grid-template-columns:1fr 1fr;gap:2px 10px;margin:6px 0;color:var(--ink)}
  .pp .grid b{font-weight:600}
  .pp .lbl{color:var(--ink3);font-size:10px;text-transform:uppercase;letter-spacing:.04em;margin-top:7px}
  .pp .tags{margin-top:2px}
  .pp .tag{display:inline-block;background:#f1efe9;border-radius:5px;padding:1px 6px;margin:1px 2px 1px 0;font-size:10.5px}
  .pp .desc{color:var(--ink2);margin-top:7px;font-size:11.5px;max-height:88px;overflow-y:auto}
  .pp a.btn{display:inline-block;margin-top:9px;background:#1F3864;color:#fff;text-decoration:none;padding:6px 12px;border-radius:7px;font-weight:600;font-size:12px}
  @media (max-width:720px){#app{flex-direction:column}#side{width:100%;max-height:38%;order:2}#map{order:1}}
</style>
</head>
<body>
<div id="app">
  <div id="side">
    <h1>StreetEasy Listings</h1>
    <div class="sub">31 rentals shared 7/12/26 &middot; downtown Manhattan</div>
    <div class="filters" id="hoodChips"></div>
    <div class="filters">
      <select id="bedsSel">
        <option value="">Any beds</option>
        <option value="2">2 BR</option><option value="3">3 BR</option>
        <option value="4">4 BR</option><option value="5">5 BR</option>
      </select>
      <select id="priceSel">
        <option value="">Any price</option>
        <option value="0-8000">Under $8k</option>
        <option value="8000-10000">$8k–10k</option>
        <option value="10000-13000">$10k–13k</option>
        <option value="13000-99999">$13k+</option>
      </select>
      <select id="sortSel">
        <option value="price">Sort: price</option>
        <option value="hood">Sort: neighborhood</option>
        <option value="dom">Sort: days on mkt</option>
        <option value="beds">Sort: beds</option>
      </select>
    </div>
    <div class="count" id="count"></div>
    <div id="cards"></div>
  </div>
  <div id="map"></div>
</div>
<script>
const DATA = __DATA__;
const COLORS = __COLORS__;

const map = L.map('map', {zoomSnap:.25});
L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
  attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  maxZoom:19
}).addTo(map);

const fmt$ = v => v==null ? '—' : '$'+v.toLocaleString();
const kfmt = v => v>=10000 ? '$'+(v/1000).toFixed(1).replace('.0','')+'k' : '$'+v.toLocaleString();

const state = {hoods:new Set(Object.keys(COLORS)), beds:'', price:'', sort:'price'};
const markers = {};

function makeIcon(d, dim){
  const w = Math.max(46, 12 + 7*kfmt(d.rent).length);
  return L.divIcon({className:'', iconSize:null, iconAnchor:[w/2, 13],
    html:`<div class="pin" style="background:${COLORS[d.hood]};opacity:${dim?0.25:1}">${kfmt(d.rent)}</div>`});
}

function popupHtml(d){
  const rows = [
    ['Beds', d.beds], ['Baths', d.baths],
    ['Sq ft', d.sqft ? d.sqft.toLocaleString() : '—'], ['Rooms', d.rooms ?? '—'],
    ['Listed', d.listed], ['Days on mkt', d.dom],
    ['Available', d.avail], ['Type', d.type||'—'],
    ['Building', d.bldg||'—'], ['Year built', d.yr||'—'],
    ['Deposit', d.deposit!=null?fmt$(d.deposit):'—'], ['Brokerage', d.brokerage||'—'],
  ].map(([k,v])=>`<span><b>${k}:</b> ${v??'—'}</span>`).join('');
  const tags = a => a.length? a.map(t=>`<span class="tag">${t}</span>`).join('') : '<span class="tag">—</span>';
  const net = d.net? `<span class="net">${fmt$(d.net)} net${d.free?` (${d.free} mo free)`:''}</span>`:'';
  const pos = d.pos.length? `<div class="lbl">Private outdoor</div><div class="tags">${tags(d.pos)}</div>`:'';
  const fees = d.fees.length? `<div class="lbl">Fees</div><div class="tags">${tags(d.fees)}</div>`:'';
  return `<div class="pp">
    ${d.photo?`<img src="${d.photo}" alt="">`:''}
    <div class="body">
      <span class="price">${fmt$(d.rent)}/mo</span>${net}
      <div class="addr">${d.addr}</div>
      <div class="hoodline">${d.hood} &middot; ${d.status}${d.photos?` &middot; ${d.photos} photos`:''}</div>
      <div class="grid">${rows}</div>
      ${pos}
      <div class="lbl">Unit features</div><div class="tags">${tags(d.features)}</div>
      <div class="lbl">Building amenities</div><div class="tags">${tags(d.amenities)}</div>
      ${fees}
      <div class="desc">${d.desc}${d.desc.length>=420?'…':''}</div>
      <a class="btn" href="${d.url}" target="_blank" rel="noopener">Open on StreetEasy ↗</a>
    </div></div>`;
}

DATA.forEach(d=>{
  const m = L.marker([d.lat, d.lng], {icon: makeIcon(d,false)});
  m.bindPopup(popupHtml(d), {maxWidth:320, maxHeight:520});
  m.on('click', ()=>highlight(d.id, false));
  m.addTo(map);
  markers[d.id]=m;
});
map.fitBounds(L.latLngBounds(DATA.map(d=>[d.lat,d.lng])).pad(0.12));

function passes(d){
  if(!state.hoods.has(d.hood)) return false;
  if(state.beds && d.beds !== +state.beds) return false;
  if(state.price){const [lo,hi]=state.price.split('-').map(Number); if(d.rent<lo||d.rent>=hi) return false;}
  return true;
}

function render(){
  const vis = DATA.filter(passes);
  const sorters = {price:(a,b)=>a.rent-b.rent, hood:(a,b)=>a.hood.localeCompare(b.hood)||a.rent-b.rent,
                   dom:(a,b)=>a.dom-b.dom, beds:(a,b)=>a.beds-b.beds||a.rent-b.rent};
  vis.sort(sorters[state.sort]);
  DATA.forEach(d=>{
    const ok = passes(d);
    markers[d.id].setIcon(makeIcon(d,!ok));
    markers[d.id].setZIndexOffset(ok?500:0);
  });
  document.getElementById('count').textContent = `${vis.length} of ${DATA.length} listings shown`;
  document.getElementById('cards').innerHTML = vis.map(d=>`
    <div class="card" id="card-${d.id}" onclick="focusListing('${d.id}')">
      <span class="price">${fmt$(d.rent)}</span><span class="net">${d.net?fmt$(d.net)+' net':''}</span>
      <div class="addr">${d.addr}</div>
      <div class="meta"><span class="dot" style="background:${COLORS[d.hood]};display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px"></span>${d.hood} &middot; ${d.beds} bd &middot; ${d.baths} ba${d.sqft?` &middot; ${d.sqft.toLocaleString()} sf`:''} &middot; ${d.dom}d on mkt</div>
    </div>`).join('');
}

function focusListing(id){
  const d = DATA.find(x=>x.id===id);
  map.flyTo([d.lat,d.lng], Math.max(map.getZoom(),16), {duration:.6});
  map.once('moveend', ()=>markers[id].openPopup());
  highlight(id, true);
}
function highlight(id, scroll){
  document.querySelectorAll('.card').forEach(c=>c.classList.remove('active'));
  const el = document.getElementById('card-'+id);
  if(el){el.classList.add('active'); if(scroll!==false) el.scrollIntoView({block:'nearest',behavior:'smooth'});}
}

// chips
const chipBox = document.getElementById('hoodChips');
Object.keys(COLORS).forEach(h=>{
  const n = DATA.filter(d=>d.hood===h).length;
  const el = document.createElement('span');
  el.className='chip';
  el.innerHTML=`<span class="dot" style="background:${COLORS[h]}"></span>${h} (${n})`;
  el.onclick=()=>{state.hoods.has(h)?state.hoods.delete(h):state.hoods.add(h); el.classList.toggle('off'); render();};
  chipBox.appendChild(el);
});
document.getElementById('bedsSel').onchange=e=>{state.beds=e.target.value;render();};
document.getElementById('priceSel').onchange=e=>{state.price=e.target.value;render();};
document.getElementById('sortSel').onchange=e=>{state.sort=e.target.value;render();};
render();
</script>
</body>
</html>
"""
leaflet_js = open(os.path.join(SCRATCH, "leaflet.js")).read()
leaflet_css = open(os.path.join(SCRATCH, "leaflet.css")).read()
html = (html.replace("__LEAFLET_CSS__", leaflet_css)
            .replace("__LEAFLET_JS__", leaflet_js)
            .replace("__DATA__", data_js).replace("__COLORS__", colors_js))
open(OUT, "w").write(html)
print("wrote", OUT, f"({len(html)//1024} KB, {len(feats)} listings)")
