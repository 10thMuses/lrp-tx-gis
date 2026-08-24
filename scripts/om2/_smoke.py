import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import om_theme as T
pages = f'''
<div class="page" style="padding:60px 70px;display:flex;flex-direction:column">
  <div class="m" style="font-size:12px;letter-spacing:.18em;color:#8A939D">SMOKE TEST</div>
  <h1 class="d" style="font-size:54px;font-weight:500;line-height:1.05;margin-top:18px">
    9.7 GW of announced capacity sits inside 20 miles</h1>
  <p class="d" style="font-style:italic;font-size:22px;color:#B03A2E;margin-top:12px">
    This is a built corridor, not a queue position.</p>
  <div style="flex-grow:1;min-height:0;margin-top:28px;display:flex;gap:30px">
    <div style="flex:1;min-width:0">{T.svg("corridor_wide_light")}</div>
    <div style="width:330px">{T.svg("chart_rings_light")}</div>
  </div>
</div>'''
html = T.document("institutional", pages, "landscape", "Smoke")
p = pathlib.Path("/tmp/smoke.html"); p.write_text(html, encoding="utf-8")
print("html", p.stat().st_size // 1024, "KB")
T.render_pdf(str(p), "/tmp/smoke.pdf")
