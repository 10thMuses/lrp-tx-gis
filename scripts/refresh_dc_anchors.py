#!/usr/bin/env python3
"""
DC anchors weekly refresh — Claude-in-the-loop diff proposer.

Reads `data/datacenters/dc_anchors.json`, fetches each entry's source URLs,
asks the Anthropic API to propose any factual updates (status, capacity,
commissioned_target, power_source, or new sources), and writes a structured
diff proposal to `outputs/refresh/dc_anchors_proposed.json`.

Diffs are NEVER auto-applied. The companion GitHub Actions workflow
(.github/workflows/dc-anchors-refresh.yml) opens a PR with the proposal
file for human review.

Per OPERATING.md §6 hard rules:
  - Build never reads source data into model context: this is a refresh
    script, not part of build.py. The dc_anchors.json file is small (~8
    entries × ~10 fields) and is loaded into memory by design.
  - Never hand-code coordinates or feature values: this script does not
    propose coordinate edits — only status/capacity/commissioned/sources.
  - Atomic in-place writes: outputs file is written via tempfile + rename.

Auth:
  ANTHROPIC_API_KEY env var. In CI: set via repo Secrets.
  Locally: set in .env or shell.

Exit codes:
  0   clean — proposal file written (may be empty if no diffs proposed)
  1   no API key
  2   no input file
  3   API error after retries
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).resolve().parent.parent
INPUT_PATH = REPO_ROOT / "data" / "datacenters" / "dc_anchors.json"
OUTPUT_DIR = REPO_ROOT / "outputs" / "refresh"
OUTPUT_PATH = OUTPUT_DIR / "dc_anchors_proposed.json"

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 2000
FETCH_TIMEOUT_SEC = 30
FETCH_RETRY_SLEEP_SEC = 5
FETCH_MAX_ATTEMPTS = 3


def fetch_url(url: str) -> str | None:
    """Fetch a URL with retry. Returns text content or None on failure."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; LRP-DC-Refresh/1.0; +https://lrp-tx-gis.netlify.app)"
        },
    )
    for attempt in range(1, FETCH_MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT_SEC) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                # Cap body at 200 KB to keep prompt size bounded
                body = resp.read(200_000).decode(charset, errors="replace")
                return body
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            print(f"  [fetch attempt {attempt}/{FETCH_MAX_ATTEMPTS}] {url} → {e}", file=sys.stderr)
            if attempt < FETCH_MAX_ATTEMPTS:
                time.sleep(FETCH_RETRY_SLEEP_SEC)
    return None


def call_claude(api_key: str, system_prompt: str, user_message: str) -> dict[str, Any]:
    """Call Anthropic Messages API. Returns parsed JSON response."""
    payload = {
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    }
    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    for attempt in range(1, FETCH_MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:500]
            print(f"  [claude attempt {attempt}] HTTP {e.code}: {body}", file=sys.stderr)
            if e.code == 401:
                # Auth failure — no point retrying
                raise
            if attempt < FETCH_MAX_ATTEMPTS:
                time.sleep(FETCH_RETRY_SLEEP_SEC * attempt)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"  [claude attempt {attempt}] {e}", file=sys.stderr)
            if attempt < FETCH_MAX_ATTEMPTS:
                time.sleep(FETCH_RETRY_SLEEP_SEC * attempt)
    raise RuntimeError("Claude API exhausted retries")


SYSTEM_PROMPT = """You are a fact-checker reviewing Texas datacenter project tracking entries.

You will receive:
1. A current canonical entry (JSON) with id, name, developer, county, status, capacity_mw_announced, commissioned_target, power_source, sources.
2. The text content of one or more source web pages.

Your job: identify any factual updates the source pages support. Propose changes ONLY for these fields:
  - status: one of {announced, planning, under_construction, partial_operational, operational, cancelled, paused}
  - capacity_mw_announced: number (MW)
  - commissioned_target: 4-digit year
  - power_source: free-text update if material new info
  - additional_sources: array of new {url, accessed_date, claim} objects worth adding

Rules:
- Propose a change ONLY if the source page contains explicit, datable evidence of the new value.
- If the source page is paywalled, removed, or returns an error, report that instead of guessing.
- Never propose coordinate, county, name, or developer changes — those require manual review.
- If nothing has changed, return an empty diff object.
- If a source page text contradicts the canonical entry but the canonical is supported by OTHER sources, flag a conflict rather than proposing a change.

Output format (and ONLY this format, no prose around it):
{
  "id": "<entry id>",
  "diff": {
    "<field>": {"current": <current value>, "proposed": <new value>, "evidence_url": "<url>", "evidence_quote": "<≤25 word excerpt>"}
  },
  "additional_sources": [{"url": "...", "claim": "..."}],
  "conflicts": [{"field": "...", "claim": "...", "evidence_url": "..."}],
  "fetch_failures": ["<url>", ...]
}

If diff is empty AND additional_sources is empty AND conflicts is empty AND fetch_failures is empty,
return {"id": "<entry id>", "no_change": true}."""


def process_entry(api_key: str, entry: dict[str, Any]) -> dict[str, Any]:
    """Fetch all source URLs for one entry, ask Claude for proposed diffs."""
    print(f"[{entry['id']}] fetching {len(entry.get('sources', []))} source URLs")
    fetched = []
    fetch_failures = []
    for src in entry.get("sources", []):
        url = src.get("url")
        if not url:
            continue
        body = fetch_url(url)
        if body is None:
            fetch_failures.append(url)
            continue
        # Trim each source to ~30 KB of text to keep prompt size sane
        # (8 sources × 30 KB = 240 KB max prompt)
        fetched.append({"url": url, "text": body[:30_000]})

    if not fetched and fetch_failures:
        # All sources failed — return failure record without API call
        return {
            "id": entry["id"],
            "fetch_failures": fetch_failures,
            "no_change": False,
        }

    sources_block = "\n\n".join(
        f"=== SOURCE: {s['url']} ===\n{s['text']}" for s in fetched
    )

    canonical = {k: v for k, v in entry.items() if k != "sources"}
    user_message = (
        f"Canonical entry:\n```json\n{json.dumps(canonical, indent=2)}\n```\n\n"
        f"Source pages ({len(fetched)} fetched, {len(fetch_failures)} failed):\n\n"
        f"{sources_block}\n\n"
        f"Fetch failures: {fetch_failures}\n\n"
        f"Return your assessment as a single JSON object per the system prompt schema."
    )

    response = call_claude(api_key, SYSTEM_PROMPT, user_message)

    # Extract text from response.content blocks
    content_blocks = response.get("content", [])
    text = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text").strip()

    # Strip code fences if present
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        proposal = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"  [parse] failed to parse Claude response as JSON: {e}", file=sys.stderr)
        print(f"  [parse] raw text: {text[:500]}", file=sys.stderr)
        return {
            "id": entry["id"],
            "parse_error": str(e),
            "raw_response": text[:1000],
        }

    if fetch_failures and "fetch_failures" not in proposal:
        proposal["fetch_failures"] = fetch_failures

    return proposal


def atomic_write_json(path: Path, data: Any) -> None:
    """Write JSON via tempfile + rename, per OPERATING.md §6.15."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=path.parent, prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY env var not set", file=sys.stderr)
        return 1

    if not INPUT_PATH.exists():
        print(f"ERROR: {INPUT_PATH} not found", file=sys.stderr)
        return 2

    with open(INPUT_PATH) as f:
        canonical = json.load(f)

    # Allow restricting to a single entry id via CLI for smoke-testing
    target_id = sys.argv[1] if len(sys.argv) > 1 else None

    entries = canonical["entries"]
    if target_id:
        entries = [e for e in entries if e["id"] == target_id]
        if not entries:
            print(f"ERROR: no entry with id={target_id}", file=sys.stderr)
            return 2
        print(f"smoke-test mode: only processing {target_id}")

    proposals = []
    for entry in entries:
        try:
            proposal = process_entry(api_key, entry)
            proposals.append(proposal)
        except Exception as e:
            print(f"[{entry['id']}] ERROR: {e}", file=sys.stderr)
            proposals.append({"id": entry["id"], "error": str(e)})

    output = {
        "schema_version": "1.0",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": MODEL,
        "input_file": str(INPUT_PATH.relative_to(REPO_ROOT)),
        "input_entry_count": len(canonical["entries"]),
        "processed_entry_count": len(entries),
        "proposals": proposals,
    }

    atomic_write_json(OUTPUT_PATH, output)
    print(f"\nwrote {OUTPUT_PATH}")
    print(f"  proposals: {len(proposals)}")
    print(f"  with diffs: {sum(1 for p in proposals if p.get('diff'))}")
    print(f"  with new sources: {sum(1 for p in proposals if p.get('additional_sources'))}")
    print(f"  with conflicts: {sum(1 for p in proposals if p.get('conflicts'))}")
    print(f"  with fetch failures: {sum(1 for p in proposals if p.get('fetch_failures'))}")
    print(f"  with errors: {sum(1 for p in proposals if p.get('error') or p.get('parse_error'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
