# 00 — Migration Runbook: personal account → team account

Ordered procedure for moving the LRP Texas Energy GIS Map off the personal
`10thMuses` accounts and onto team-owned accounts.

**Read this whole document before executing step 1.** Several steps are one-way, and
two of them (Netlify site transfer, Supabase project transfer) will take the live map
down for a few minutes if sequenced wrong.

Throughout, substitute:

| Placeholder | Meaning |
|---|---|
| `<TEAM_GH_ORG>` | Destination GitHub **organization** (e.g. `land-resource-partners`) |
| `<TEAM_NETLIFY_TEAM>` | Destination Netlify team slug |
| `<TEAM_SUPABASE_ORG>` | Destination Supabase organization |

---

## 0. What you are actually moving

The project is **not** just a Git repo. It is five separate assets across four vendors,
and only one of them moves when you transfer the repository.

| # | Asset | Current owner | Moves with repo transfer? | Section |
|---|---|---|---|---|
| 1 | GitHub repo `10thMuses/lrp-tx-gis` | GitHub **personal user** `10thMuses` (id 262889643) — *not* an org | — | [§3](#3-github-repository) |
| 2 | GitHub Actions secrets (3) | Same repo | ❌ **Deleted on transfer** | [§4](#4-github-actions-secrets) |
| 3 | Netlify site `lrp-tx-gis` (`01b53b80-687e-4641-b088-115b7d5ef638`) | Netlify team **10th Muses** (`10thmuses`), Pro plan, 1 member | ❌ Separate transfer | [§5](#5-netlify-site) |
| 4 | Supabase project **10th-Muses** (`xvlpperttnedsduscgnq`) — hosts the portal password gate | Supabase org `zingbiabeqiodgmohtai` | ❌ Separate transfer, **and it is shared with an unrelated product** | [§6](#6-supabase--the-portal-access-gate) |
| 5 | Claude scheduled Routine `lrp-gis-daily-refresh` | Andrea's personal Claude account | ❌ Cannot be transferred — must be **recreated** | [§7](#7-the-daily-refresh-claude-routine) |

Two more things that are easy to forget:

- **Personal access tokens** (`GITHUB_PAT`, `NETLIFY_PAT`) live in an untracked local
  `.env`. Fine-grained GitHub PATs are bound to a *resource owner* — the existing one
  stops working the moment the repo leaves the personal account. See [§4](#4-github-actions-secrets).
- **Hardcoded identifiers** in tracked files: the Netlify site ID and the prod URL
  appear in `scripts/deploy.sh`, `scripts/verify_deployed_layers.py`,
  `scripts/session-open.sh`, `.github/workflows/build-and-deploy.yml`, `build.py` and
  `build_template.html`. Section [§8](#8-code-changes-required-by-the-migration) lists every one.

---

## 1. Pre-migration decisions

Answer these four before touching anything. Each changes the steps you run.

### 1.1 Public or private?

The repo is **currently public** (`visibility: public`). Anyone on the internet can read:

- Every data file, including `data/fracfocus/DisclosureList_1.csv` (60 MB) and
  `combined_points.csv`.
- `outputs/reports/` — which contains **client and counterparty deliverables**:
  `OXY-Intelligence-Report.pdf/.docx`, `OXY-Partnership-Brief.pptx`,
  `Pacifico-GW-Ranch-Diligence-Report.pdf`, `Stargate-Abilene-Diligence-Report.pdf`,
  `buyer-email.md`, `owner-email.md`, `GW-Ranch-Email-*.docx`.
- The full commercial thesis in `WIP_OPEN.md` and `docs/archive/`.

The map itself sits behind a password gate ([§6](#6-supabase--the-portal-access-gate)), but the repo does not.

> **Recommendation: make it private during the transfer.** Nothing in the build or
> deploy path depends on the repo being public — prod tiles are served by Netlify, and
> `build.py`'s prebuilt-tile fallback fetches from the Netlify URL, not from GitHub.
> The only loss is unauthenticated `git clone`.

If you keep it public, at minimum move `outputs/reports/` out first — see
[§2.3](#23-decide-what-does-not-move).

### 1.2 Destination is an org, not a user

Transferring to another *personal account* buys nothing. Create a GitHub **organization**
so the team gets role-based access, org-level secrets and a survivable owner. GitHub
free orgs are sufficient; Team plan adds protected branches on private repos.

### 1.3 Does the Netlify site keep its URL?

`https://lrp-tx-gis.netlify.app` is baked into scripts, docs, and every share link you
have ever sent. A Netlify site transfer between teams normally preserves both the site
ID and the `*.netlify.app` subdomain — but **verify immediately after transfer** rather
than assuming, because if the subdomain is taken in the destination team you will get a
renamed site and every hardcoded URL breaks at once.

This is also the natural moment to attach a real custom domain (it is already on the
backlog in `ARCHITECTURE.md §7`). A custom domain makes every future host migration a
DNS change instead of a code change.

### 1.4 Does Supabase move, or does the gate get rebuilt?

The Supabase project hosting the gate is **shared with a completely unrelated product**
(107 tables — members, matches, community events, dating, referrals). Only three tables
(`oxy_config`, `oxy_sessions`, `oxy_events`) and two Edge Functions (`oxy-gate`,
`oxy-track`) belong to this map.

You have two options, and the second is better:

| Option | What it means | Cost |
|---|---|---|
| **A. Transfer the whole Supabase project** | The other product moves too. Only sensible if that product is also moving to the same team. | Low effort, high coupling |
| **B. Stand up a new Supabase project for the map and repoint the gate** ✅ | Clean separation. Three tables + two functions is under an hour of work. | ~1 h, one `build_template.html` edit |

[§6](#6-supabase--the-portal-access-gate) documents option B in full.

---

## 2. Pre-migration cleanup

Do this **before** transferring. Cleaning up after a transfer means doing it in the
team's audit log.

### 2.1 Close the 20 open pull requests

There are 20 open PRs, none of them merge candidates:

**13 automated proposal PRs** (`dc-anchors-refresh-7` … `-19`, PR #10, 11, 12, 16, 21,
26, 28, 29, 32, 34, 35, 36, 37). These are generated weekly by
`.github/workflows/dc-anchors-refresh.yml`, which is designed never to auto-merge. They
have accumulated since 2026-05-25 because nobody closes them. Each contains only
`outputs/refresh/dc_anchors_proposed.json`.

```bash
# Review the newest one for any real signal, then close all of them.
# Newest first: #37 (2026-08-17), #36, #35, #34, #32, #29, #28, #26, #21, #16, #12, #11, #10
```

Then fix the underlying cause — see [`07-AUTOMATION.md §2.3`](07-AUTOMATION.md#23-the-stale-pr-problem).

**7 `claude/*` draft PRs** carrying work that mostly is not this project:

| PR | Branch | Content | Disposition |
|---|---|---|---|
| #31 | `claude/transformer-market-research-crssta` | Transformer supply-chain white paper | Belongs to research, not the map |
| #30 | `claude/streeteasy-listings-export-map-ui9b7l` | **Personal** — StreetEasy apartment listings | **Do not migrate.** Close and delete branch |
| #27 | `claude/map-broker-email-ux-24vv93` | Newmark broker intro email draft | Business doc, not map code |
| #25 | `claude/stoic-ritchie-f4p76t` | OXY Pecos County appraisal-roll intel | Business doc |
| #20 | `claude/eager-heisenberg-7ynpfr` | Deal-Terms Compendium | Business doc |
| #17 | `claude/zealous-clarke-7be7dj` | Grid Wire weekly issue + renderer | Belongs to the Grid Wire product |
| #13 | `claude/youthful-rubin-iijipf` | `[DO NOT MERGE]` Grid Wire bootstrap — self-described "transfer vehicle for lrp-grid-wire" | Belongs to the Grid Wire product |

Target state before transfer: **0 open PRs, 0 branches other than `main`**
(`OPERATING.md §7` already sets a target of zero stranded branches; the audit has been
red for months).

```bash
bash scripts/audit.sh   # confirms stranded-branch count is 0
```

### 2.2 Close or migrate the 1 open issue

Issue #33 "do not update" — a marker issue. Decide whether it survives the move.

### 2.3 Decide what does *not* move

The repo has accreted three products' worth of material. Migrating all of it moves the
mess into the team account.

| Path | What it is | Recommendation |
|---|---|---|
| `outputs/reports/**` (≈22 MB) | Client deliverables: OXY intelligence report (PDF/DOCX/PPTX), GW Ranch and Stargate Abilene diligence reports, buyer/owner emails, analysis scripts | Move to the team document store (SharePoint/Drive), not the code repo. Keep the generator scripts (`scripts/build_oxy_*.py`) if you still generate these. |
| `docs/grid-wire-master-instructions-v4.md`, `outputs/reports/GRIDWIRE_LOG.md`, `outputs/reports/source/` | The Grid Wire briefing product — a separate deliverable with its own twice-daily Claude Routine | Split into its own repo (PR #13 was literally an attempt at this) |
| `data/fracfocus/DisclosureList_1.csv` (60 MB) | FracFocus bulk disclosure export. Not referenced by `layers.yaml`; used only by ad-hoc analysis scripts in `outputs/reports/` | Drop from the repo; it is re-downloadable from fracfocus.org. This is 55% of the working tree. |
| `docs/archive/**` (≈185 KB of chat logs) | Historical session logs from the chat-mode era | Keep — cheap, and it is the only record of several decisions |

> **Do not rewrite history to purge large files** unless you have a specific reason.
> A `git filter-repo` pass changes every commit SHA, invalidates the deploy-ID
> references in ~90 merge commit messages, and buys back ~50 MB. Not worth it. Delete
> the file in a normal commit and move on.

### 2.4 Snapshot the current state

So you can prove what the map looked like before the move.

```bash
git clone --mirror https://github.com/10thMuses/lrp-tx-gis.git lrp-tx-gis-premigration.git
tar czf lrp-tx-gis-premigration-$(date -u +%F).tar.gz lrp-tx-gis-premigration.git

# Record the live state
curl -s -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | md5sum
python3 scripts/verify_deployed_layers.py | tee premigration-layers.txt
```

Keep `premigration-layers.txt`. After migration you will diff against it to prove no
layer was lost.

---

## 3. GitHub repository

### 3.1 Transfer

GitHub → repo → **Settings** → **General** → **Danger Zone** → **Transfer ownership**.
Enter `<TEAM_GH_ORG>`. You must have permission to create repositories in that org.

What survives the transfer:
- All commits, branches, tags, releases
- Issues, pull requests, wiki, stars, watchers
- A **redirect** from the old URL, so existing clones keep working until someone
  creates a new repo at the old path

What does **not** survive:
- **GitHub Actions secrets** — deleted. Re-create them ([§4](#4-github-actions-secrets)).
- Fine-grained PAT grants scoped to the old owner.
- Any webhooks configured on the old repo (verify; this repo has none beyond Actions).

### 3.2 Immediately after transfer

```bash
# Update every local clone
git remote set-url origin https://github.com/<TEAM_GH_ORG>/lrp-tx-gis.git
git remote -v
git fetch origin && git status
```

Verify Actions are enabled in the destination org (orgs can disable Actions by default,
which would silently stop both workflows):
`Settings → Actions → General → Allow all actions`.

Set the default branch to `main` if the org enforces a different default.

### 3.3 Grant team access

`Settings → Collaborators and teams`. Recommended roles:

| Role | Who | Why |
|---|---|---|
| Admin | 2 people minimum | Single-admin repos die with the admin |
| Maintain | Anyone who deploys | Can push, manage settings, cannot delete the repo |
| Write | Data contributors | Can push branches |
| Read | Peers who only consume the map | They mostly want the URL, not the repo |

---

## 4. GitHub Actions secrets

These are **deleted by the transfer** and must be re-created at
`https://github.com/<TEAM_GH_ORG>/lrp-tx-gis/settings/secrets/actions`.

| Secret | Used by | How to obtain the new value |
|---|---|---|
| `NETLIFY_AUTH_TOKEN` | `.github/workflows/build-and-deploy.yml` | Netlify → User settings → Applications → Personal access tokens → New. Must be minted by an account with access to the **destination** Netlify team. |
| `NETLIFY_SITE_ID` | Same workflow | The site ID after transfer. Expected to remain `01b53b80-687e-4641-b088-115b7d5ef638` — **confirm, do not assume** ([§5](#5-netlify-site)). |
| `ANTHROPIC_API_KEY` | `.github/workflows/dc-anchors-refresh.yml` → `scripts/refresh_dc_anchors.py` | Anthropic Console → API keys. Mint a **new key on the team's org**; do not carry the personal key across. |

### 4.1 Local `.env` tokens

`.env` is gitignored and never transfers. Each operator regenerates their own from
`.env.example`:

```bash
cp .env.example .env
```

| Variable | Where to mint | Scope needed |
|---|---|---|
| `GITHUB_PAT` | https://github.com/settings/personal-access-tokens — **select `<TEAM_GH_ORG>` as resource owner** | Contents: Read and write, on `lrp-tx-gis` only |
| `NETLIFY_PAT` | https://app.netlify.com/user/applications#personal-access-tokens | Full (Netlify PATs are not scopeable) |

> **Fine-grained PAT gotcha:** a token whose resource owner is the personal account
> `10thMuses` returns 404/403 on the transferred repo — indistinguishable from "repo
> does not exist". If `git push` or `scripts/deploy.sh` starts 404ing after migration,
> this is why. Additionally, many orgs require an owner to **approve** fine-grained PAT
> requests before they work: `<TEAM_GH_ORG> → Settings → Personal access tokens`.

**Revoke the old personal tokens** once the new ones are verified working.

---

## 5. Netlify site

### 5.1 Current state

| Field | Value |
|---|---|
| Team | `10th Muses` (slug `10thmuses`), id `699b16cf2f53328c1c8389cd`, **Pro** plan, 1 member |
| Site name | `lrp-tx-gis` |
| Site ID | `01b53b80-687e-4641-b088-115b7d5ef638` |
| URL | `https://lrp-tx-gis.netlify.app` |
| Access model | Link-only at the Netlify layer; the real gate is in-app ([§6](#6-supabase--the-portal-access-gate)) |
| Deploy method | **Direct zip upload via the Netlify REST API** from `scripts/deploy.sh`. There is **no Git-linked build** — Netlify never clones the repo, so transferring the repo does not affect deploys. |

That last row is good news: repo and site are decoupled. You can transfer them in
either order without breaking the other.

### 5.2 Transfer

Netlify → site → **Site configuration** → **General** → **Transfer site** → select
`<TEAM_NETLIFY_TEAM>`. You must be an Owner on both teams.

Plan note: the site currently sits on a **Pro** team. If the destination team is on
Free, confirm you are not relying on a Pro-only feature. This site uses only static
hosting, `_headers`, `_redirects` and bandwidth — all available on Free — but bandwidth
allowances differ, and PMTiles range requests over 39 layers are bandwidth-heavy.

### 5.3 Verify immediately

```bash
# 1. Site ID unchanged?
#    Netlify → Site configuration → General → Site information → Site ID

# 2. URL still resolves (default curl UA gets a 503 from the edge — always pass a UA)
curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/ | head -1

# 3. All 39 layers still live
python3 scripts/verify_deployed_layers.py
diff <(python3 scripts/verify_deployed_layers.py) premigration-layers.txt
```

If the site ID changed, update it in the three places listed in [§8](#8-code-changes-required-by-the-migration).

### 5.4 Re-verify the deploy path end to end

Do not consider Netlify migrated until a real deploy succeeds from the new team:

```bash
git checkout -b refinement-post-migration-smoke
bash scripts/deploy.sh --rebuild      # prints a deployId on success
bash scripts/close-out.sh refinement-post-migration-smoke <deployId> "post-migration deploy smoke"
```

`deploy.sh` will fail at the `POST /api/v1/sites/<id>/deploys` step with an empty
`deploy_id` if the `NETLIFY_PAT` in `.env` has no access to the destination team.

---

## 6. Supabase — the portal access gate

**This is the least documented and most fragile part of the system.** Nothing in
`CLAUDE.md`, `OPERATING.md` or `ARCHITECTURE.md` mentions it.

### 6.1 How the gate actually works

`build_template.html` renders a full-screen "Confidential access" overlay before the map
is usable. On submit it POSTs `{email, password, referrer}` to a Supabase Edge Function:

```
https://xvlpperttnedsduscgnq.supabase.co/functions/v1/oxy-gate    ← auth
https://xvlpperttnedsduscgnq.supabase.co/functions/v1/oxy-track   ← analytics
```

The `oxy-gate` function:

1. Validates the email is syntactically an email. **There is no allowlist** — any
   well-formed address is accepted.
2. Reads `oxy_config` where `key = 'gate_password'` and compares the submitted password
   with `!==`. **One shared plaintext password for everyone.**
3. On match, inserts a row into `oxy_sessions` (email, IP, user-agent, referrer) and a
   `login` row into `oxy_events`, then returns `{ok: true, session_id}`.

The browser stores `{session_id, email, ts}` in `localStorage` under `oxy_gate_v1` and
skips the gate for **12 hours**. `oxy-track` then receives `page_view`, `layer_toggle`,
`map_move`, `heartbeat` (30 s), `visibility` and `leave` events — so viewer behaviour is
logged per email.

### 6.2 Honest security assessment

State this plainly to whoever owns the decision:

- A single shared password, stored in plaintext, compared without constant-time
  comparison. Anyone who has ever been given the password has permanent access until it
  is rotated for everybody.
- No allowlist means the email field is **self-declared** — a viewer can type anything.
  The analytics are therefore attribution-flavoured, not attribution.
- The gate is client-side. The PMTiles archives under `/tiles/*.pmtiles` are served with
  `Access-Control-Allow-Origin: *` and **no authentication whatsoever**. Anyone who
  knows a tile URL can fetch the underlying data without ever seeing the password
  prompt. The gate protects the *interface*, not the *data*.
- `verify_jwt` is disabled on both functions (necessarily — they are the auth layer).

This is adequate for "keep casual visitors out of a link-shared map". It is not adequate
if the map is treated as containing confidential deal information. If the team needs
real access control, that is a project, not a migration step — see
[`08-ROADMAP-AND-GAPS.md §4`](08-ROADMAP-AND-GAPS.md#4-security-and-access-control).

### 6.3 Option B — new Supabase project (recommended)

1. Create a project in `<TEAM_SUPABASE_ORG>`, e.g. `lrp-tx-gis`, region `us-east-1`.
2. Create the three tables:

```sql
create table public.oxy_config (
  key         text primary key,
  value       text not null,
  updated_at  timestamptz not null default now()
);

create table public.oxy_sessions (
  id           uuid primary key default gen_random_uuid(),
  email        text,
  started_at   timestamptz not null default now(),
  last_seen    timestamptz not null default now(),
  ip           text,
  user_agent   text,
  referrer     text,
  events_count integer not null default 0
);

create table public.oxy_events (
  id         bigint generated always as identity primary key,
  session_id uuid references public.oxy_sessions(id),
  email      text,
  ts         timestamptz not null default now(),
  type       text,
  detail     jsonb
);

-- RLS on, no public policies: only the service-role key (used by the Edge
-- Functions) may read or write. This matches the current configuration.
alter table public.oxy_config   enable row level security;
alter table public.oxy_sessions enable row level security;
alter table public.oxy_events   enable row level security;

insert into public.oxy_config (key, value) values ('gate_password', '<NEW_PASSWORD>');
```

3. Copy the two Edge Functions from the old project (`supabase functions download
   oxy-gate` / `oxy-track`, or copy the source from the Supabase dashboard) and deploy
   them to the new project with `verify_jwt` disabled.
4. Migrate history if you want it:
   `oxy_sessions` and `oxy_events` are append-only logs — export to CSV from the old
   project and import, or accept a clean slate.
5. Edit `build_template.html` (~line 2890) and change the one constant:

```javascript
var SUPA='https://<NEW_PROJECT_REF>.supabase.co';
```

6. Rebuild and deploy. Existing viewers' `oxy_gate_v1` localStorage sessions become
   invalid against the new backend, so everyone re-enters the password once.

### 6.4 Option A — transfer the existing project

Supabase → project → Settings → General → **Transfer project** to
`<TEAM_SUPABASE_ORG>`. Requires Owner on both orgs and a paid plan on the destination
for non-free features. The project ref (`xvlpperttnedsduscgnq`) and therefore the
functions URL are unchanged, so **no code edit is needed** — but you have also moved
another product's entire member/dating/events database into the team org. Only do this
if that is intended.

### 6.5 Rotating the portal password

This is the operation you will actually run most often. It is a one-row update:

```sql
update public.oxy_config
   set value = '<NEW_PASSWORD>', updated_at = now()
 where key = 'gate_password';
```

No rebuild, no deploy — the Edge Function reads the table on every login. Existing
12-hour localStorage sessions survive until they expire; to force everyone out
immediately you would need to change the `STORE` key in `build_template.html` and
redeploy.

**Rotate at migration time.** The current password has been distributed to an unknown
set of people over the life of the personal account.

---

## 7. The daily-refresh Claude Routine

### 7.1 What it is

A scheduled Claude Code Routine, `lrp-gis-daily-refresh`, that has run every day at
**06:00 UTC** since 2026-05-18 — 89 run reports in `outputs/refresh/daily/`.

| Field | Value |
|---|---|
| Trigger ID | `trig_01JtgtPFhaDrd7TajmvN6YHi` |
| Cron | `0 6 * * *` |
| Environment | `env_014kr4fojXSHmvSLCusx89TU` |
| Model | `claude-sonnet-4-6` |
| Tools allowed | `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep` |
| MCP connections | Netlify (`https://netlify-mcp.netlify.app/mcp`) |
| Source | `https://github.com/10thMuses/lrp-tx-gis` |
| Owner | Andrea's personal Claude account |

**The entire operating contract for this job — roughly 1,800 words specifying branch
naming, the four refresh steps, what counts as a deployable change, the hard rules, and
the exact summary-line format — exists only inside the trigger configuration.** It is
not in the repo. If the personal Claude account goes away, the contract goes with it and
the only remaining evidence of what the job did is 89 markdown reports.

The full contract has now been captured into
[`07-AUTOMATION.md §3`](07-AUTOMATION.md#3-the-daily-refresh-routine) so it survives this migration.

### 7.2 Migration steps

Routines cannot be transferred between accounts. Recreate:

1. In the **team** Claude account, create a cloud environment with the repo
   `https://github.com/<TEAM_GH_ORG>/lrp-tx-gis` as a source.
2. Attach the **Netlify MCP connector** using the team's Netlify credentials — the
   routine deploys through MCP, not through a local `NETLIFY_PAT`.
3. Create a scheduled Routine, cron `0 6 * * *`, with the prompt reproduced verbatim in
   [`07-AUTOMATION.md §3.2`](07-AUTOMATION.md#32-the-contract-prompt-verbatim), with one edit: replace the repo URL.
4. **Disable the old routine** in the personal account — do not delete it until the new
   one has produced three consecutive good reports. Two routines writing
   `refinement-daily-refresh-<DATE>` branches to the same repo will collide.
5. Confirm by checking that `outputs/refresh/daily/<tomorrow>.md` lands on `main`.

### 7.3 One thing to fix while you are in there

The contract's `ENVIRONMENT REALITY` section asserts that RRC MFT, Census TIGER and
ERCOT return **HTTP 403 from cloud egress** and instructs the routine to record them as
`blocked(403)` without retrying. That is **stale**: the 2026-08-18 report shows
`mft.rrc.texas.gov` returning 302 and all four steps completing successfully
(99,808 wells rows; 28,842 permits rows). Correct that paragraph when you recreate the
routine, or the job will keep under-reporting healthy runs as infrastructure failures.

### 7.4 Other Routines in the personal account

`lrp-gis-daily-refresh` is the only one that touches this project. Two others exist and
belong elsewhere:

- **The Grid Wire — 5am and 4pm ET editions** (`0 9,20 * * *`) — the briefing product.
  It uses a Resend API key and the verified sending domain `10thmuses.com`, and mails
  `andrea@abhcm.com`. Migrate with the Grid Wire split, not with the map.
- `10tm-supervised-cycle` / `10tm-session-heartbeat` — belong to the `10th-muses-app`
  product. Already disabled/ended.

---

## 8. Code changes required by the migration

Everything below is a tracked file that hardcodes something the migration may change.
Work through this list on a branch and ship it as one commit.

| File | Line(s) | Hardcoded value | Change needed |
|---|---|---|---|
| `scripts/deploy.sh` | `SITE_ID="01b53b80-…"` | Netlify site ID | Only if the site ID changed |
| `scripts/deploy.sh` | prod URL in the md5-parity poll | `https://lrp-tx-gis.netlify.app` | Only if the URL changed |
| `scripts/verify_deployed_layers.py` | `DEFAULT_BASE` | Same URL | Same |
| `scripts/session-open.sh` | prod sanity check | Same URL | Same |
| `.github/workflows/build-and-deploy.yml` | comment + verify step | Site ID and URL | Same, plus re-add secrets |
| `build.py` | `resolve_source` tier-3 prebuilt fallback | `https://lrp-tx-gis.netlify.app/tiles/<id>.pmtiles` | Same — **this one matters**: `rrc_pipelines`, `tiger_highways` and `bts_rail` have no local source file and are fetched from prod at build time. If the URL breaks, three layers silently vanish. |
| `build_template.html` | `var SUPA=` (~line 2890) | Supabase project URL | Only under option B |
| `CLAUDE.md`, `OPERATING.md`, `ARCHITECTURE.md`, `README.md` | repo URL, site ID | `10thMuses/lrp-tx-gis` | Update to `<TEAM_GH_ORG>/lrp-tx-gis` |

> The tier-3 prebuilt fallback is the sharpest edge in the whole migration. Three layers
> exist **only** as PMTiles files already on the Netlify CDN — there is no source data
> for them anywhere in the repo. Before you touch the Netlify site, download them:
>
> ```bash
> mkdir -p prebuilt-backup
> for id in rrc_pipelines tiger_highways bts_rail; do
>   curl -sSL -A "Mozilla/5.0" \
>     "https://lrp-tx-gis.netlify.app/tiles/$id.pmtiles" \
>     -o "prebuilt-backup/$id.pmtiles"
> done
> ls -lh prebuilt-backup/
> ```
> Keep these somewhere durable. If the site is ever lost, these three layers are
> unrecoverable without re-deriving them from RRC / Census TIGER / BTS.

---

## 9. Execution order

Do it in this order. Steps 1–4 are reversible; 5 onward are not.

| # | Step | Downtime | Reversible |
|---|---|---|---|
| 1 | Take the mirror backup and the prebuilt-tile backup ([§2.4](#24-snapshot-the-current-state), [§8](#8-code-changes-required-by-the-migration)) | none | n/a |
| 2 | Close the 20 PRs and delete stranded branches ([§2.1](#21-close-the-20-open-pull-requests)) | none | yes |
| 3 | Split out / relocate what should not move ([§2.3](#23-decide-what-does-not-move)) | none | yes |
| 4 | Create `<TEAM_GH_ORG>`, the team Netlify team, and (option B) the new Supabase project | none | yes |
| 5 | **Transfer the GitHub repo** | none — deploys do not go through GitHub | one-way in practice |
| 6 | Re-create the 3 Actions secrets; mint new PATs; revoke old ones ([§4](#4-github-actions-secrets)) | none | yes |
| 7 | **Transfer the Netlify site** | ~1–2 min | one-way in practice |
| 8 | Verify site ID + URL + all 39 layers ([§5.3](#53-verify-immediately)) | none | n/a |
| 9 | Stand up the new Supabase gate, rotate the password, repoint `build_template.html` ([§6](#6-supabase--the-portal-access-gate)) | gate only, ~5 min | yes |
| 10 | Apply the [§8](#8-code-changes-required-by-the-migration) code changes; full build + deploy + close-out | none | yes |
| 11 | Recreate the daily-refresh Routine on the team account; disable the old one ([§7.2](#72-migration-steps)) | none | yes |
| 12 | Run the acceptance checklist ([§10](#10-acceptance-checklist)) | none | n/a |
| 13 | Re-issue the portal URL + new password to the distribution list | none | n/a |

---

## 10. Acceptance checklist

The migration is complete when every line is true.

**Repository**
- [ ] `https://github.com/<TEAM_GH_ORG>/lrp-tx-gis` exists, `main` is default
- [ ] Visibility matches the [§1.1](#11-public-or-private) decision
- [ ] ≥2 org admins
- [ ] 0 open PRs, 0 branches other than `main` (`bash scripts/audit.sh`)
- [ ] Actions enabled; both workflows appear in the Actions tab

**Secrets and tokens**
- [ ] `NETLIFY_AUTH_TOKEN`, `NETLIFY_SITE_ID`, `ANTHROPIC_API_KEY` re-created
- [ ] `build-and-deploy` workflow dispatched manually and finished green
- [ ] New `GITHUB_PAT` / `NETLIFY_PAT` verified; **old personal tokens revoked**

**Hosting**
- [ ] Site listed under `<TEAM_NETLIFY_TEAM>`
- [ ] `curl -sI -A "Mozilla/5.0" https://lrp-tx-gis.netlify.app/` → `200`
- [ ] `python3 scripts/verify_deployed_layers.py` → exit 0, matches `premigration-layers.txt`
- [ ] A full `bash scripts/deploy.sh --rebuild` from the team account succeeded and reached md5 parity

**Portal gate**
- [ ] Gate appears on a fresh browser profile
- [ ] New password works; **old password no longer works**
- [ ] A login row lands in `oxy_sessions` in the destination Supabase project
- [ ] `oxy_events` receives `page_view` / `layer_toggle`

**Automation**
- [ ] Daily-refresh Routine recreated on the team account, old one disabled
- [ ] Three consecutive daily reports landed on `main`
- [ ] `dc-anchors-refresh.yml` ran on its Monday cron without erroring on a missing key

**Documentation**
- [ ] `CLAUDE.md`, `OPERATING.md`, `ARCHITECTURE.md`, root `README.md` reference the new org
- [ ] Distribution list re-issued the URL and password
- [ ] Backups (`lrp-tx-gis-premigration.git`, `prebuilt-backup/`) stored somewhere durable and team-owned

---

## 11. Rollback

Through step 8, rollback is cheap:

- **GitHub** — transfer the repo back. The redirect makes clones keep working either way.
- **Netlify** — transfer the site back; or, worst case, redeploy from the mirror backup
  into a fresh site and repoint DNS.
- **Supabase (option B)** — revert the one-line `SUPA` constant in
  `build_template.html`, rebuild, deploy. The old project is untouched.
- **Routine** — re-enable the old trigger, disable the new one.

After step 10 (code changes shipped and merged) you are committed; rolling back means a
revert commit and a redeploy, which is routine but no longer instant.
