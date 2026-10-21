# Grid Wire

LRP's weekly Texas energy & AI-infrastructure intelligence product. Separate
workstream from the GIS map (per the repo cross-walk it is deliberately *not*
documented in `OPERATING.md`/`ARCHITECTURE.md`) — this folder is its home.

## Beat

ERCOT & the Texas grid · data centers and large load · AI-infrastructure
financing · advanced nuclear · grid/energy policy (Texas + federal).

## Producing an issue

1. **Research** the window (typically the trailing week) across the five lanes.
   Every item must trace to a dated primary or first-tier source; date-check
   each one — recycled prior-year coverage and out-of-window deals are the
   recurring trap. Quarantine anything unverified; do not publish it.
2. **Write** `YYYY-MM-DD-grid-wire.md` in the LRP voice (peer-level, concise,
   data integrated, inline source links).
3. **Render** to branded HTML + PDF:
   ```bash
   python3 outputs/grid-wire/render_grid_wire.py outputs/grid-wire/YYYY-MM-DD-grid-wire.md
   ```
   The renderer uses python-`markdown` + WeasyPrint. Jost (masthead) and Inter
   (body) are fetched to `~/.fonts` on demand — never committed to the repo, per
   the bootstrap font convention. Font fetch and PDF render are both non-fatal:
   the HTML always lands and CSS falls back to a system stack. Writes are atomic
   (`os.replace`) per `OPERATING.md` §3 rule 4.

## Files

| File | What |
|---|---|
| `render_grid_wire.py` | Reusable MD → branded HTML + PDF renderer |
| `YYYY-MM-DD-grid-wire.md` | Issue source (canonical) |
| `YYYY-MM-DD-grid-wire.html` | Print-ready styled HTML (open + Cmd-P to PDF) |
| `YYYY-MM-DD-grid-wire.pdf` | Distribution artifact |

## Dependencies

`pip install markdown weasyprint` (WeasyPrint needs Pango/Cairo system libs,
present in the standard bootstrap). No network needed at render time except the
one-time font fetch.
