#!/usr/bin/env python3
"""Scaffold the next cut's draft from the prior cut's state.

Usage:
    python3 scripts/new_cut.py <vol> <cut_slug> [--prior issues/volN/cut]

cut_slug is one of: 930am, 1200pm, 300pm, 600pm, 900pm (archive convention;
Vol 16 used 600pm).

Creates issues/vol{vol}/{cut_slug}/draft.md containing:
  - front matter carried from the prior cut, cut fields updated
  - a DO-NOT-REPEAT comment block listing the prior cut's section heads,
    tape rows, and deal rows (incrementality guard: cuts cover only what is
    new since the prior cut; restating prior items is drift)
  - empty scaffolding for THE TAPE / LEAD / DEALS

Vol and cut state are read from WIP_OPEN.md by the operator workflow, never
from memory; this script trusts its arguments.
"""

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

CUTS = ("930am", "1200pm", "300pm", "600pm", "900pm")
CUT_LABELS = {
    "930am": "9:30 AM ET", "1200pm": "12:00 PM ET", "300pm": "3:00 PM ET",
    "600pm": "6:00 PM ET", "900pm": "9:00 PM ET",
}


def find_prior(vol):
    issues = REPO / "issues"
    cuts = []
    for vdir in sorted(issues.glob("vol*")):
        m = re.match(r"vol(\d+)$", vdir.name)
        if not m:
            continue
        for cdir in vdir.iterdir():
            if (cdir / "draft.md").exists() and cdir.name in CUTS:
                cuts.append((int(m.group(1)), CUTS.index(cdir.name), cdir))
    if not cuts:
        return None
    return sorted(cuts)[-1][2]


def extract_do_not_repeat(draft_text):
    items = []
    for line in draft_text.splitlines():
        if line.startswith("## "):
            items.append(line[3:].strip())
        m = re.match(r"\|\s*([^|]{2,60}?)\s*\|", line)
        if m and m.group(1) not in ("---", "") and not set(m.group(1)) <= {"-", " "}:
            items.append(f"  {m.group(1)}")
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vol", type=int)
    ap.add_argument("cut_slug", choices=CUTS)
    ap.add_argument("--prior", help="path to prior cut dir (default: latest)")
    args = ap.parse_args()

    prior = Path(args.prior) if args.prior else find_prior(args.vol)
    if prior is None:
        sys.exit("new_cut: no prior cut found; pass --prior")
    prior_draft = (prior / "draft.md").read_text(encoding="utf-8")

    fm = re.match(r"\A---\s*\n(.*?)\n---\s*\n", prior_draft, re.S)
    if not fm:
        sys.exit(f"new_cut: prior draft {prior} has no front matter")
    meta = {}
    for line in fm.group(1).splitlines():
        k, _, v = line.partition(":")
        if k.strip():
            meta[k.strip()] = v.strip()

    meta["vol"] = str(args.vol)
    meta["cut_slug"] = args.cut_slug
    meta["cut_label"] = CUT_LABELS[args.cut_slug]
    if args.cut_slug == "600pm":
        meta["edition_note"] = "expanded full edition, updated through the close"
    else:
        meta["edition_note"] = "incremental cut, new since the prior cut"

    target = REPO / "issues" / f"vol{args.vol}" / args.cut_slug
    target.mkdir(parents=True, exist_ok=True)
    out = target / "draft.md"
    if out.exists():
        sys.exit(f"new_cut: {out} already exists")

    dnr = "\n".join(extract_do_not_repeat(prior_draft))
    front = "\n".join(f"{k}: {v}" for k, v in meta.items())
    out.write_text(
        f"---\n{front}\n---\n\n"
        f"<!-- DO-NOT-REPEAT: items already covered in {prior.parent.name}/"
        f"{prior.name}. Cuts are incremental; restate nothing below except\n"
        f"falsification-status updates and the tape.\n{dnr}\n-->\n\n"
        "## I. The Tape\n\n"
        '<div class="tbl t-tape" markdown="1">\n\n'
        "| Series | Level | Context |\n|---|---|---|\n\n</div>\n\n"
        "## II. Lead\n\n"
        "## III. Deals, Financings, and Capital Flows\n\n"
        '<div class="tbl t-deals" markdown="1">\n\n'
        "| Date | Transaction | Terms |\n|---|---|---|\n\n</div>\n",
        encoding="utf-8",
    )
    print(out)


if __name__ == "__main__":
    main()
