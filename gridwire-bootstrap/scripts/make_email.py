#!/usr/bin/env python3
"""Grid Wire email drafts: email_source.txt -> two plain-ASCII drafts.

Usage:
    python3 scripts/make_email.py issues/vol16/600pm/email_source.txt
                                  [--outdir DIR] [--vol N]

Source format (recipient-agnostic):
    Subject: Grid Wire Vol 16 -- ...
    <blank>
    <body ... ends with the signature lines>

Output, one file per recipient (draft-only; never sent from this repo):
    Grid_Wire_Vol{N}_email_DRAFT_Mel.txt
    Grid_Wire_Vol{N}_email_DRAFT_Mark.txt

Assembly: subject line, blank, salutation ("Mel," / "Mark,"), blank, body.
Body text is authored per cut (condensed plain-text edition of the PDF);
this script only assembles, normalizes, and guards.

ASCII pipeline (locked order, per the handoff fragility table):
    1. explicit replacement dict (em-dash -> --, en-dash -> -, smart quotes
       -> straight, ellipsis -> ..., >= / <= / ->, NBSP -> space, ...)
    2. unicodedata.normalize NFKD, then drop combining marks
    3. assert_ascii LAST, always: hard-fail the build on any survivor
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

RECIPIENTS = ("Mel", "Mark")

REPLACEMENTS = {
    "—": "--",   # em dash
    "–": "-",    # en dash
    "‒": "-",    # figure dash
    "‑": "-",    # non-breaking hyphen
    "−": "-",    # minus sign
    "‘": "'",    # left single quote
    "’": "'",    # right single quote
    "“": '"',    # left double quote
    "”": '"',    # right double quote
    "′": "'",    # prime
    "″": '"',    # double prime
    "…": "...",  # ellipsis
    "≥": ">=",
    "≤": "<=",
    "→": "->",
    "←": "<-",
    "×": "x",
    " ": " ",    # non-breaking space
    " ": " ",    # thin space
    " ": " ",
    " ": " ",
    " ": " ",
    "°": " deg",
    "§": "Section ",
    "•": "-",    # bullet
    "·": "-",    # middle dot
}


def to_ascii(text):
    for src, dst in REPLACEMENTS.items():
        text = text.replace(src, dst)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return text


def assert_ascii(text, label):
    try:
        text.encode("ascii")
    except UnicodeEncodeError:
        lines = text.splitlines()
        bad = []
        for i, line in enumerate(lines, 1):
            for j, ch in enumerate(line, 1):
                if ord(ch) > 127:
                    bad.append(f"  line {i} col {j}: {ch!r} (U+{ord(ch):04X})")
        sys.exit(f"make_email: ASCII guard tripped in {label}; survivors:\n"
                 + "\n".join(bad[:40]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--outdir")
    ap.add_argument("--vol", help="vol number; default parsed from Subject")
    args = ap.parse_args()

    src = Path(args.source)
    raw = src.read_text(encoding="utf-8")
    if not raw.startswith("Subject:"):
        sys.exit("make_email: source must start with a 'Subject:' line")
    subject, _, body = raw.partition("\n\n")
    body = body.rstrip("\n") + "\n"

    vol = args.vol
    if not vol:
        m = re.search(r"Vol\s+(\d+)", subject)
        if not m:
            sys.exit("make_email: cannot parse vol from Subject; pass --vol")
        vol = m.group(1)

    outdir = Path(args.outdir) if args.outdir else src.parent
    outdir.mkdir(parents=True, exist_ok=True)
    for name in RECIPIENTS:
        draft = f"{subject}\n\n{name},\n\n{body}"
        draft = to_ascii(draft)
        assert_ascii(draft, f"draft for {name}")
        out = outdir / f"Grid_Wire_Vol{vol}_email_DRAFT_{name}.txt"
        out.write_text(draft, encoding="ascii")
        print(out)


if __name__ == "__main__":
    main()
