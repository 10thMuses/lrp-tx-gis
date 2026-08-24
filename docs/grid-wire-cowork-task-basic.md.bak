# Grid Wire — scheduled-task run prompt

Two Cowork scheduled tasks, one per cut. Cowork > Scheduled (left sidebar) > New task. Set Daily, time 5:00 AM ET for task 1 and 3:00 PM ET for task 2. Paste the body below verbatim into each; the only difference is the CUT SLOT line.

Prerequisites in the Team account: GitHub connector authorized (authorizations do not survive account migration), `CREDENTIALS.md` present in the project sidebar with a valid `GITHUB_PAT=` line, Cowork enabled by the org admin.

---

## Task 1 — name: `Grid Wire 5AM ET`

```
CUT SLOT: 5:00 AM ET Morning Edition.

Produce the next Grid Wire cut. Do not ask for confirmation at any point.

1. Clone github.com/10thMuses/lrp-tx-gis using the GITHUB_PAT line in CREDENTIALS.md.
2. Read Readme.md, then docs/grid-wire-master-instructions-v4.md in full, then
   docs/grid-wire-coverage-taxonomy.md, then outputs/reports/GRIDWIRE_LOG.md.
3. Take the Vol number, incremental baseline, and open items from the GRIDWIRE_LOG.md
   "## Next chat" block. Never from memory. Read the prior cut's entry to establish
   what is already covered.
4. Sweep all 23 taxonomy domains for the incremental window since the prior cut.
   Primary sources first: EDGAR and credit-agreement exhibits, EIA, RRC, TCEQ,
   PUCT/ERCOT dockets, FERC, NRC, GCD agendas, courts, county records, company IR
   and transcripts. Trade press and sell-side are data points only and must be
   flagged as such. A domain with nothing new gets nothing.
5. Six-county West Texas all-activity sweep every cut: Pecos, Reeves, Ward, Upton,
   Crane, Crockett. Not water-weighted toward Pecos/Reeves.
6. Build the edition to the Part J structure and the light-theme format spec:
   Lead, Sections I-XVII, Deals Roundup table, What to Watch dated calendar,
   Capital-Stack Spine, sources block. Every section carries primary-source data
   points, named counterparties, term-sheet detail where a financing landed, an
   Angle, and a named falsification condition.
7. Voice: Munger/Burry/Sanders register. Declarative. No hedging, no
   adjectives-as-argument, no em-dashes, no smart quotes. Named on-record quotes only.
   Crude and natural gas are separate channels, always. Water claims are
   district-specific. Comps are never averaged across entitlement stages. Undisclosed
   figures are n/d, never estimated. Derived arithmetic is labeled derived.
8. Render the PDF with WeasyPrint. Light theme only: no dark background shading
   behind text anywhere. Navy and gold are accent colors only. Body >=11.5pt,
   line-height 1.58, left-aligned. Tables 10.2pt. Stat numbers 16-17pt. Jost,
   instanced to static weights 400/500/600/700 via fontTools; one FontConfiguration
   passed to both CSS() and write_pdf(); absolute file:// font URIs.
9. Produce two plain-ASCII email drafts, one addressed to Mel, one to Mark. Mark is
   Mel with the salutation swapped. Verify ASCII with
   LC_ALL=C grep -cP "[^\x00-\x7F]" asserting zero. DRAFT ONLY. Never send.
10. Commit the edition markdown source and the build script to
    outputs/reports/source/. Append the cut entry to outputs/reports/GRIDWIRE_LOG.md
    and rewrite its "## Next chat" block with the next Vol number, baseline, and open
    items. Push to main.
11. Deliver: the PDF and both email drafts as files, plus a short chat summary of the
    lead and the three highest-information items.

Prohibited: assuming Vol number or baseline from memory; full restarts on an
incremental cut; estimating undisclosed figures; comps without primary sources;
sell-side framing presented as analysis; sending the email drafts; LRP or ABH
attribution on anything public-facing.
```

## Task 2 — name: `Grid Wire 3PM ET`

Identical, with line 1 replaced by:

```
CUT SLOT: 3:00 PM ET incremental cut. Cover only what is new since the 5:00 AM cut.
```

---

## Verification after creating each task

Hit **Run now** once. Confirm: the run reads the Vol number from `GRIDWIRE_LOG.md` rather than guessing, the PDF is light-theme with no dark panels, both email drafts are pure ASCII and unsent, and the log entry plus `## Next chat` block were pushed to `main`. Then leave it alone.
