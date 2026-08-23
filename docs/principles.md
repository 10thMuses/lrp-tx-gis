# Engineering patterns — pointer

Canonical content lives in `OPERATING.md` §6 (hard rules) and `ARCHITECTURE.md` (stack, schemas, fragility table).

Standing rules restated for grep:
- Never read source data files into model context. Tippecanoe subprocess only.
- Never `git add -A`. Explicit path staging only.
- Atomic in-place writes: `os.replace(tmp, final)`.
- Atomic deploy + merge + branch delete in one session. Never deploy without the matching merge.
- Never deploy a build with `errored>0`.
- Branch from `main` for every change; `refinement-<slug>`.
- Verification scales to blast radius.
- Curl verification requires `-A "Mozilla/5.0"`; CDN warmup 45-90 s post-deploy.

Grid Wire build pattern: WeasyPrint + Jost instanced to static weights via `fontTools.varLib.instancer`; one `FontConfiguration` passed to both `CSS(font_config=fc)` and `write_pdf(font_config=fc)`; absolute `file://` font URIs; `markdown` with `extras=["extra","tables","sane_lists"]` and smartypants disabled; ASCII email validation `LC_ALL=C grep -cP "[^\x00-\x7F]"` asserting zero.
