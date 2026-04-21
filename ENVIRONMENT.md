# ENVIRONMENT.md

What this project's Claude runtime can and can't do. Read once at session open for any chat that might hit an environment limit.

---

## Supported (Claude executes without operator involvement)

| Capability | How |
|---|---|
| Read `/mnt/project/` | `view`, `bash` |
| Write to `/mnt/user-data/outputs/` | `create_file`, `str_replace`, `bash` |
| Run Python, bash, apt | `bash_tool` |
| Install tippecanoe (cold) | apt + git clone + make |
| Fetch from public web | `web_fetch`, `bash curl`, Python `requests` |
| Query AGOL / FeatureServers | Python requests with `fetch_with_retry` |
| Deploy to Netlify | Netlify MCP (`netlify-deploy-services-updater`) |
| Read live site | `curl` against `https://lrp-tx-gis.netlify.app` |
| Search past conversations | `conversation_search`, `recent_chats` |
| Update memory | `memory_user_edits` |
| Generate files for operator | `present_files` |

---

## Not supported (requires operator action)

| Capability | Why | Workaround |
|---|---|---|
| Write to `/mnt/project/` | Mounted read-only by Anthropic platform | Operator uploads files to project knowledge between chats |
| Delete from `/mnt/project/` | Same | Operator deletes in project knowledge panel |
| Modify Settings → Instructions | Not tool-accessible | Operator pastes `PROJECT_INSTRUCTIONS.md` content into field |
| Cross-chat filesystem persistence in `/mnt/user-data/` | Container resets between chats | Bundle outputs into zip; operator re-uploads what matters |
| Access chat attachments from prior chats | New container | Operator re-uploads if needed |
| Modify project memory directly | Only `memory_user_edits` interface | Covered; no gap |
| Send email / notifications | No MCP for it | Grid Wire delivery stays operator-driven |

---

## Implications for protocol

The read-only `/mnt/project/` is the single recurring manual touchpoint the autonomy protocol does not eliminate. Protocol adaptation:

1. **Every chat's output includes an upload manifest** at close-out — named files to upload + files to delete from project knowledge.
2. **Bundle zip** emitted for multi-file changes — one drag-drop per chat cycle instead of per-file uploads.
3. **Handoff realism** — `WIP_OPEN.md` "Next chat" block assumes operator has not yet synced `/mnt/project/` to the bundle when pre-flight runs; the block accounts for this.
4. **Verification against `/mnt/project/` at session open** — if operator forgot to upload the latest bundle, pre-flight catches the drift and reports before any work starts.

**Budget cost per chat cycle:** ~30 seconds of operator time (delete + upload). Over 100 chats, that's ~50 minutes of total operator touch. Acceptable.

---

## Sister-project environments compared

If this project and the sister share learnings, the environment differences matter:

| Capability | This project | Sister (typical web app) |
|---|---|---|
| Source-of-truth writes | Read-only `/mnt/project/` | Git API push |
| Deploy | Netlify MCP | Netlify/Vercel API |
| Database | None | Supabase/Firestore/etc. |
| Environment variables | None beyond Netlify's | Hosting platform API |
| Telemetry sink | `SESSION_LOG.md` file | `error_events` table |
| Build-time enforcement | `build.py` check | Pre-deploy hook |

Rules that port without adaptation: banned phrases, acceptable-asks list, handoff quality gate, interstitial cadence, budget ceilings, circuit breaker semantics, self-correction routing.

Rules that need stack-specific adaptation: deploy verification chain, multi-file atomic commit pattern, credential hygiene (sister has DB; this project doesn't).
