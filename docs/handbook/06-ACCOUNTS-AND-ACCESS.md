# 06 — Accounts, Credentials and Access

Every external account, credential, endpoint and share link the project depends on.

> **This file contains no secret values.** It records *where* each secret lives and how
> to read or rotate it. The repository has been public for most of its life — never paste
> a token, key or password into any tracked file.

---

## 1. Account inventory

| # | Service | What it holds | Plan | Owner (pre-migration) |
|---|---|---|---|---|
| 1 | **GitHub** | Source of truth: `10thMuses/lrp-tx-gis` | Free, **public** | Personal user `10thMuses` (id 262889643) — *not an organisation* |
| 2 | **Netlify** | Production hosting, site `lrp-tx-gis` | **Pro**, team `10th Muses` (`10thmuses`), 1 member | Same person, Owner role |
| 3 | **Supabase** | Portal password gate + viewer analytics | Project `10th-Muses` (`xvlpperttnedsduscgnq`), org `zingbiabeqiodgmohtai`, us-east-1 | Same person |
| 4 | **Anthropic** | API key for the weekly `dc_anchors` diff proposer | Pay-as-you-go | Same person |
| 5 | **Claude (Code)** | The scheduled daily-refresh Routine | — | Same person, personal account |

Migration procedure for all five: [`00-MIGRATION-RUNBOOK.md`](00-MIGRATION-RUNBOOK.md).

---

## 2. Identifiers

Non-secret values that are hardcoded across the repo. Change them in lockstep — the full
list of files is in
[`00-MIGRATION-RUNBOOK.md §8`](00-MIGRATION-RUNBOOK.md#8-code-changes-required-by-the-migration).

| Identifier | Value |
|---|---|
| GitHub repo | `10thMuses/lrp-tx-gis`, default branch `main` |
| Netlify site name | `lrp-tx-gis` |
| Netlify site ID | `01b53b80-687e-4641-b088-115b7d5ef638` |
| Netlify team | `10th Muses`, slug `10thmuses`, id `699b16cf2f53328c1c8389cd` |
| Production URL | `https://lrp-tx-gis.netlify.app` |
| Supabase project ref | `xvlpperttnedsduscgnq` |
| Supabase base URL | `https://xvlpperttnedsduscgnq.supabase.co` |
| Netlify MCP endpoint | `https://netlify-mcp.netlify.app/mcp` |
| Netlify deploy API | `https://api.netlify.com/api/v1/sites/<siteId>/deploys` |

---

## 3. Credentials

### 3.1 Local `.env` (gitignored, per-operator)

Created by `bash scripts/bootstrap-claude-code.sh` from `.env.example`. Each operator
mints their own — these are **not** shared.

| Variable | Used by | Mint at | Scope |
|---|---|---|---|
| `GITHUB_PAT` | Scripted git operations. Most ordinary git commands use the local credential helper instead. | https://github.com/settings/personal-access-tokens | Fine-grained. **Contents: Read and write** on `lrp-tx-gis` only. Pull Requests is deliberately **excluded** — the protocol is direct merge to `main`, not PR review. |
| `NETLIFY_PAT` | `scripts/deploy.sh` | https://app.netlify.com/user/applications#personal-access-tokens | Full — Netlify PATs are not scopeable |

`deploy.sh` resolves `NETLIFY_PAT` in this order: repo `.env` → `/mnt/project/CREDENTIALS.md`
(legacy chat-mode path) → the `NETLIFY_PAT_ENV` shell variable. Exit code 3 means none of
the three yielded a value.

> **Fine-grained PAT gotcha.** These tokens are bound to a *resource owner*. A token
> minted against the personal account stops working the moment the repo moves to an org,
> and the failure looks like a 404 (repo not found) rather than a 403. Many orgs also
> require an owner to approve fine-grained PAT requests before they function.

### 3.2 GitHub Actions secrets

At `https://github.com/<owner>/lrp-tx-gis/settings/secrets/actions`.
**Repository transfers delete these — re-create them after any move.**

| Secret | Used by | Notes |
|---|---|---|
| `NETLIFY_AUTH_TOKEN` | `build-and-deploy.yml` | A Netlify PAT with access to the team that owns the site |
| `NETLIFY_SITE_ID` | `build-and-deploy.yml` | Expected `01b53b80-687e-4641-b088-115b7d5ef638`; the workflow fails loudly if unset |
| `ANTHROPIC_API_KEY` | `dc-anchors-refresh.yml` → `scripts/refresh_dc_anchors.py` | Model pinned to `claude-sonnet-4-5-20250929`, max 2,000 tokens per call |

### 3.3 Supabase keys

The Edge Functions read `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` from the Supabase
runtime environment. **Neither key appears anywhere in this repo**, and neither should.
The browser talks only to the function endpoints, never to the database.

Note that both `oxy-gate` and `oxy-track` run with `verify_jwt: false` — necessarily, since
they *are* the authentication layer and are called by unauthenticated visitors.

### 3.4 Rotation procedure

| Credential | Steps |
|---|---|
| `GITHUB_PAT` | Mint new → update `.env` → verify `git push` → revoke old |
| `NETLIFY_PAT` | Mint new → update `.env` → verify `bash scripts/deploy.sh` reaches step §8.3 → revoke old |
| `NETLIFY_AUTH_TOKEN` | Mint new → update the repo secret → dispatch `build-and-deploy` manually → revoke old |
| `ANTHROPIC_API_KEY` | Mint new → update the repo secret → dispatch `dc-anchors-refresh` manually → revoke old |
| **Portal gate password** | One SQL update — see [§4.3](#43-rotating-the-password) |

Rotate everything at migration time. Assume every credential minted on the personal
account is compromised for the purposes of the team account.

---

## 4. The portal password gate

### 4.1 How viewers get in

1. Open **https://lrp-tx-gis.netlify.app**
2. A full-screen "Confidential access" panel asks for an **email** and an **access password**
3. Enter any valid email (it is logged, not validated against a list) and the shared LRP
   access password
4. The session is cached in `localStorage` under `oxy_gate_v1` for **12 hours**

Behind the scenes the browser POSTs `{email, password, referrer}` to
`https://xvlpperttnedsduscgnq.supabase.co/functions/v1/oxy-gate`, which compares the
password against `oxy_config` where `key = 'gate_password'`, records a row in
`oxy_sessions`, and returns a `session_id`.

### 4.2 Where the password lives

Supabase → project `10th-Muses` → Table Editor → `public.oxy_config` → row
`key = 'gate_password'`. Or:

```sql
select value from public.oxy_config where key = 'gate_password';
```

A second row, `stats_password`, gates the analytics endpoint ([§5](#5-viewer-analytics)).

### 4.3 Rotating the password

```sql
update public.oxy_config
   set value = '<NEW_PASSWORD>', updated_at = now()
 where key = 'gate_password';
```

**No rebuild and no deploy** — the Edge Function reads the table on every login.

Existing 12-hour `localStorage` sessions survive the rotation. To force everyone out
immediately, change the `STORE` constant (`oxy_gate_v1`) in `build_template.html` and
redeploy.

### 4.4 Granting and revoking access

| Task | How |
|---|---|
| Grant access to one person | Send them the URL and the password |
| Revoke one person's access | **Not possible.** There is one shared password. Revoking anyone means rotating for everyone. |
| Audit who has been in | Query `oxy_sessions` ([§5](#5-viewer-analytics)) — but the email is self-declared, so treat it as a hint, not proof |

### 4.5 What the gate does not protect

The PMTiles archives under `/tiles/*.pmtiles` are served with
`Access-Control-Allow-Origin: *` and **no authentication at all** — that is required for
PMTiles range requests to work. Anyone who knows a tile URL can fetch the underlying data
without ever seeing the gate.

> **The gate protects the interface, not the data.** Treat the map as *unlisted*, not
> *secure*. If the data itself needs protecting, that is a different architecture — see
> [`08-ROADMAP-AND-GAPS.md §4`](08-ROADMAP-AND-GAPS.md#4-security-and-access-control).

---

## 5. Viewer analytics

Once past the gate, the page logs behaviour to
`https://xvlpperttnedsduscgnq.supabase.co/functions/v1/oxy-track`, batched (flush at 8
events or 4 s, `sendBeacon` on page hide).

| Event | Payload |
|---|---|
| `login` | Written server-side by `oxy-gate` — user agent, IP |
| `page_view` | Path + hash, referrer, viewport dimensions |
| `layer_toggle` | Layer id, on/off |
| `map_move` | Centre lat/lon, zoom (debounced 900 ms) |
| `heartbeat` | Every 30 s while the tab is visible |
| `visibility` | Tab focus changes |
| `leave` | Page hide |

Stored in `oxy_sessions` (email, IP, user agent, referrer, started/last-seen) and
`oxy_events` (session, email, timestamp, type, JSONB detail).

### 5.1 Reading the analytics

Query the tables directly in the Supabase SQL editor, or POST to the dedicated endpoint:

```bash
curl -sS -X POST https://xvlpperttnedsduscgnq.supabase.co/functions/v1/oxy-stats \
  -H 'content-type: application/json' \
  -d '{"password":"<stats_password>"}'
```

Returns `{summary: {sessions, events, emails}, sessions: [...300 most recent from the
oxy_session_summary view...], recent: [...80 most recent events...]}`.

The `stats_password` value lives in `oxy_config` alongside `gate_password`.

> **There is no UI for this endpoint.** It returns JSON and nothing in the repo consumes
> it. Building a small dashboard page is a half-day of work and is on the backlog.

### 5.2 Current usage

As of 2026-08-18: **2 sessions, 1 distinct email, last login 2026-07-22.** Either the map
has not actually been distributed through the gate, or viewers are sitting on cached
`localStorage` sessions. Worth confirming before treating the analytics as a
distribution metric.

---

## 6. Public endpoints

Everything the running map and build pipeline talk to.

| Endpoint | Purpose | Auth |
|---|---|---|
| `https://lrp-tx-gis.netlify.app` | The map | None (app-level gate) |
| `https://lrp-tx-gis.netlify.app/tiles/*.pmtiles` | Tile archives | **None**, CORS `*` |
| `https://xvlpperttnedsduscgnq.supabase.co/functions/v1/oxy-gate` | Login | Password in body |
| `…/functions/v1/oxy-track` | Analytics ingest | Session id in body |
| `…/functions/v1/oxy-stats` | Analytics read | `stats_password` in body |
| `https://api.netlify.com/api/v1/sites/<id>/deploys` | Deploy | Bearer `NETLIFY_PAT` |
| `https://api.anthropic.com/v1/messages` | DC anchors proposer | `ANTHROPIC_API_KEY` |
| Basemap tile services (CARTO, Esri ×2, OpenFreeMap, USGS NAIP) | Basemaps | None |
| `https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/...` | Inter webfont | None |

Upstream **data** sources are catalogued in [`02-DATA-SOURCES.md`](02-DATA-SOURCES.md).
None require authentication — the project uses no paid or licensed feeds.

---

## 7. Who needs what

| Role | Needs |
|---|---|
| **Viewer** (peer, counterparty) | Portal URL + access password. Nothing else. |
| **Analyst** (reads data, exports) | Same. Every export runs in the browser. |
| **Data contributor** (refreshes layers) | GitHub write access · local clone · `GITHUB_PAT` · Python + tippecanoe. No Netlify or Supabase access needed. |
| **Deployer** | All of the above **plus** `NETLIFY_PAT` |
| **Administrator** | All of the above plus Netlify team Owner, Supabase project access, the Anthropic key, and ownership of the Claude Routine |

**Minimum viable team: two administrators.** A single-admin setup on any one of the five
services is a single point of failure for the whole project.

---

## 8. Share links

| Link | Use |
|---|---|
| `https://lrp-tx-gis.netlify.app` | Default view — send this to a new viewer |
| `https://lrp-tx-gis.netlify.app/#sb=1` | Sidebar collapsed — embeds and screenshots |
| `…/#lat=…&lon=…&zoom=…&layers=…&base=…&filters=…&sb=…` | A specific view. The **Share** button in the toolbar builds this for you. |
| `https://github.com/10thMuses/lrp-tx-gis` | Repository |
| `https://app.netlify.com/teams/10thmuses` | Netlify team dashboard |
| `https://supabase.com/dashboard/project/xvlpperttnedsduscgnq` | Supabase project |

Hash-parameter reference:
[`01-PROJECT-OVERVIEW.md §2.3`](01-PROJECT-OVERVIEW.md#23-sharing-a-specific-view).

---

## 9. Security posture — stated plainly

So that whoever owns the decision owns it knowingly:

| Property | Reality |
|---|---|
| Repo visibility | **Public**, including client deliverables under `outputs/reports/` |
| Map interface | Single shared plaintext password, no allowlist, no per-user revocation |
| Map data | **Unauthenticated.** Tiles are world-readable to anyone with a URL. |
| Viewer identity | Self-declared email. Not verified. |
| Secrets in the repo | None found. `.env` and `CREDENTIALS.md` are gitignored; no key is committed. |
| Transport | HTTPS throughout |
| Password comparison | Plain `!==`, not constant-time |
| Session lifetime | 12 h in `localStorage`, no server-side revocation |
| Audit trail | Logins and in-map behaviour logged to Supabase, keyed to a self-declared email |

This is a reasonable posture for *"an unlisted map shared with a handful of known
peers"*. It is not a reasonable posture for *"a confidential deal room"* — and the gate's
own copy ("Confidential access… access is logged") promises more than the architecture
delivers. Either soften the copy or harden the architecture; do not leave the gap
undocumented.
