# OPERATING.md — execution rules and pipeline reference

## Cut cycle (trigger: `cut <time>.`)

1. `git checkout main && git pull --ff-only`, then branch `cut-<vol>-<time>`.
2. Read `WIP_OPEN.md`: current vol, last cut, open falsification register,
   next-cut queue. Never trust memory for vol/cut numbering.
3. Web-research deltas since the prior cut only. The 6 PM close cut is the
   expanded full edition; all other cuts are incremental and shorter.
4. `python3 scripts/new_cut.py <vol> <cut_slug>` scaffolds the draft with the
   prior cut's item list as a do-not-repeat block.
5. Write `draft.md` (PDF source) and `email_source.txt` (condensed plain-text
   edition: Subject line, blank, body; salutations are spliced per recipient).
6. `python3 scripts/render_pdf.py issues/vol{N}/{cut}/draft.md`
   - hard-fails unless pdffonts reports Jost subsets only.
7. `python3 scripts/make_email.py issues/vol{N}/{cut}/email_source.txt`
   - hard-fails on any non-ASCII survivor (guard runs after replacements).
8. Archive: `issues/vol{N}/{cut}/` holds draft.md, email_source.txt, the PDF,
   and both email .txt files. One dir per cut.
9. Update `WIP_OPEN.md` (last cut, falsification statuses, next-cut queue)
   and append one line to `WIP_LOG.md`.
10. Commit (explicit paths, never `git add -A`), push, merge to main in the
    same session. Hand the operator the three files.

## New day (trigger: `vol.`)

Increment vol, carry the open falsification register forward in WIP_OPEN.md,
reset the incremental baseline. First cut of the day proceeds as above.

## PDF pipeline (locked)

- WeasyPrint; Jost static-weight TTFs committed in `fonts/` (instanced from
  the Google Fonts variable TTF with `fonttools varLib.instancer`; weights
  400/500/600/700 + italic 400).
- `FontConfiguration()`: one module-level instance in `render_pdf.py`, passed
  to BOTH `CSS()` and `write_pdf()`. Omitting either silently falls back to
  system fonts.
- Letter (612x792 pt). Palette (sampled from the Vol 16 reference): navy
  `#1b2a4a`, crimson `#b0413e`, charcoal `#2a2f3a`, slate `#3c4250`, callout
  tint `#f1f3f7`, zebra `#f4f6f9`, hairline `#d8dce3`.
- Fixed-layout tables (`table-layout: fixed`); header rows are demoted into
  tbody so they do not repeat across page breaks (reference behavior); rows
  are atomic (`page-break-inside: avoid`).
- Running headers via `@page` margin boxes fed by `string-set`; footer
  carries `Page N of M` counters. Page 1 (`@page :first`) suppresses the
  running header and carries the masthead instead.
- Charts are inline SVG in draft.md. Every SVG `<text>` element must carry
  `font-family="Jost"` explicitly — SVG text does not inherit the document
  font and will silently fall back to DejaVu (the pdffonts gate catches it).
- Section heads `## I. Title` get the roman numeral wrapped red
  automatically. `^[12,13]` -> superscript refs. `==text==` -> crimson bold.
  `::: angle ... :::` -> ANGLE callout (label injected).
- Filename: `Grid_Wire_Vol{N}_{YYYYMMDD}_{cut}_ET.pdf`, cut in
  `{930am, 1200pm, 300pm, 600pm, 900pm}`.
- Section structure per the Vol 16 reference: I. THE TAPE -> II. LEAD ->
  III. DEALS AND FINANCINGS (term sheets) -> named forensic/thesis sections
  -> sector sections -> West Texas focal points -> conclusions ->
  footnotes/sources -> colophon. Footnotes are a numbered list; every body
  claim carries a superscript ref.

## Comprehensive edition format (green)

The long-form Weekend / Close / Special / multi-day-sweep edition is the
operator's comprehensiveness standard (set from the Vol 16 reference
editions). It renders through the same `render_pdf.py` gate.

- Front matter sets `format: edition` and the keys: `vol`, `date_compact`,
  `edition_slug` (filename token, e.g. `Weekend`), `edition_label`
  (e.g. `Saturday, June 13, 2026 - Weekend Edition`), `byline`, `timestamp`
  (the shaded intro box; `**bold**` is honored). Filename:
  `Grid_Wire_Vol{N}_{YYYYMMDD}_{edition_slug}_ET.pdf`.
- Template/CSS: `templates/gridwire-edition.html` + `gridwire-edition.css`
  (green `#1f4d3f`, ink `#1a2722`, callout tint `#eaf0ec`, hairline
  `#c8d3cc`). Jost throughout, same pdffonts gate.
- The **Table of Contents is auto-built** from the `## ` section headings in
  draft order — write the sections, the TOC follows.
- Callouts: `::: box` ... `:::` for "Practitioner read." / "Angle." /
  "Composite implication." (author supplies the bold lead-in);
  `::: quote` ... `:::` for italic on-record pull-quotes. `::: angle` still
  works for the daily format.
- Tables: `t-tape` (4-col tape), `t-src` (3-col with Source), `t-2col`
  (label + state-of-play), `t-deals`. Header rows are demoted so they do not
  repeat across page breaks; rows are atomic.
- Required topic coverage and the LRP-content rule are in `STYLE.md`. Cover
  the full topic union every edition; mark `n/d` rather than dropping a
  section. Quotes in the transcript-highlights section must be named and
  on-record. Close with the data-gaps/confidence-flags list.

## Email pipeline (locked)

- Two files per cut: `Grid_Wire_Vol{N}_email_DRAFT_Mel.txt` / `..._Mark.txt`.
- Format: `Subject:` line, blank, salutation (`Mel,` / `Mark,`), blank, 1-2
  sentence cut summary, full plain-text body (condensed edition of the PDF),
  signature `Andrea Himmel` / `Land Resource Partners`.
- Pure ASCII. Pipeline order is locked: replacement dict first (em-dash ->
  `--`, en-dash -> `-`, smart quotes -> straight, ellipsis -> `...`,
  `>=`/`<=`/`->`, NBSP -> space, `§` -> `Section `), then NFKD normalize and
  strip combining marks, then `assert_ascii` hard-fails on any survivor.
  Verified byte-for-byte against the Vol 16 reference drafts.
- Draft-only. Never send. No email integration in this repo unless the
  operator explicitly overrides in-session.

## Known fragility

| Item | Issue | Countermeasure |
|---|---|---|
| Jost from Google Fonts | Ships variable; WeasyPrint weight mapping unreliable on variable TTFs | Static instances committed to `fonts/`; @font-face maps weights explicitly |
| FontConfiguration | Must be the same instance in CSS() and write_pdf() | Single module-level instance in render_pdf.py |
| SVG chart text | Does not inherit document font; falls back silently | `font-family="Jost"` attribute on every text node; pdffonts gate |
| ASCII guard ordering | Normalize-then-replace misses chars NFKD decomposes oddly | Replacement dict first, then normalize, then assert; guard runs last, always |
| Incrementality drift | Cuts silently re-reporting prior items | new_cut.py injects prior cut's item list as a do-not-repeat block |
| Vol/cut numbering | Cached numbers go stale | Read only from WIP_OPEN.md, never from memory |
| pdffonts check | System-font fallback renders without error | Post-render assert in render_pdf.py: only Jost subsets present |
