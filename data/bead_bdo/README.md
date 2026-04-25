# BDO BEAD Final Proposal artifacts (Chat 91 archive)

Sources:
- `bead_subgrantees.xlsx` (https://comptroller.texas.gov/programs/broadband/funding/bead/docs/subgrantees.xlsx) — 41 awarded subgrantees: State, UEI, UEI Name, FRN.
- `bead_deployment-projects.xlsx` (.../deployment-projects.xlsx) — 152 projects: Project Name, Project ID, UEI, Project Description (BSL/CAI/PAU counts in prose), Priority Broadband flag, Aerial/Buried fiber miles, Estimated Jobs, Tribal Consent, BEAD Support $, Subgrantee Match $, State Match $.

Why no `bead_fiber_planned` layer shipped Chat 91: neither file carries county or coordinates. The `locations.xlsx` (7.8 MB, not archived) maps opaque FCC BSL IDs to Project IDs but contains no coords; geocoding requires the licensed FCC BSL Fabric. The public BEAD award map at register.broadband.texas.gov/award/bead/map is a JS-rendered SPA with no static endpoint. NTIA NBAM project-level data is partner-login-gated.

Future render paths (any one unblocks the layer):
1. PUC region 1–24 polygon shapefile + Project Name region-suffix parser (e.g. "217-Region 11" → BDO Region 11 polygon centroid). Requires BDO regions GIS file.
2. Subgrantee HQ geocode via UEI lookup against SAM.gov public registry — markers per awardee, not per project.
3. Authorized headless-browser scrape of register.broadband.texas.gov vector tiles (same authorization class as CRPUB/RRC MFT per spec §12.3).
