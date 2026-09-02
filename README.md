# Green Data Center — Project Home

Sustainable data center **architecture, regulation & engineering** reference site, imported verbatim from Gemini session `533c4962a18148c1`.

## What's in here

```
green-data-center/
├── site/          # Reconstructed production site (13 files, from Gemini's build_zip.py)
│   ├── index.html            # Topic pillar hub
│   ├── facilities.html       # Facility case studies
│   ├── cooling-tech.html     # Cooling technology
│   ├── regulations.html      # Regulatory matrix (EU/GER/US)
│   ├── baseload-nuclear.html # Baseload nuclear analysis
│   ├── sources.html          # Research bibliography
│   ├── styles.css            # Swiss-editorial design system
│   ├── _worker.js            # Cloudflare Pages Advanced Mode worker (D1 API)
│   ├── schema.sql            # D1 database schema (subscribers)
│   ├── AI_GUIDE.md           # AI maintenance SOP (zip copy)
│   ├── AI_GUIDE-full.md      # FULL 11.2 KB AI protocol (restored from msg 1)
│   ├── _headers / robots.txt / sitemap.xml
│   └── build_zip.py          # The generator script Gemini wrote
├── transcript/
│   ├── transcript-full.md    # FULL session transcript (verbatim, 379 KB)
│   ├── clean-session.jsonl   # Structured: roles + code + links + images
│   └── sources.md            # Extracted URLs
├── code/                     # Every code block from the session, in order
├── import/                   # Import toolchain + raw extraction assets (from this Hermes session)
│   ├── tools/                # DECOMPILED pipeline — one module per step (see below)
│   ├── raw/                  # Raw DOM-extracted records, deduped JSONL, build script, site zip
│   └── images/               # Images saved from the Gemini session
└── evaluation/               # Evaluation, research & advancement plan (added post-import)
```

## Import toolchain (decompiled for future dev)

The original monolithic `build_project.py` (206 lines) was split into one module per step, all project-relative (no hardcoded paths):

| Step | Module | Writes |
|---|---|---|
| 1–3 | `merge_turns.py` | `import/raw/clean-session.jsonl` — dedupe 24 raw records → 16 turns + role assignment |
| 4–5 | `write_transcript.py` | `transcript/clean-session.jsonl`, `transcript/transcript-full.md` |
| 6 | `extract_code.py` | `code/msgNN_blockMM.ext` (25 files) |
| 7 | `extract_links.py` | `transcript/sources.md` |
| 8 | `rebuild_site.py` | `import/raw/build_zip_reconstructed.py` + `greencompute-site.zip` → `site/` (+ full AI_GUIDE restore) |
| — | `run_pipeline.py` | Orchestrator: `python3 run_pipeline.py [--step NAME]` |

Legacy reference: `import/tools/build_project_legacy.py` (unchanged original). Re-import helpers `extract_full.py` (CDP extraction) and `cdp_gemini_extract.py` (recon) live alongside.

**Verified 2026-09-02:** re-running the full decompiled pipeline reproduces every artifact byte-for-byte vs git HEAD (transcript ×3, code ×25, site ×13).

## Origin
- Gemini session: https://gemini.google.com/app/533c4962a18148c1
- Imported by Hermes 2026-09-02 via CDP live-browser extraction (full fidelity — no thinking blocks existed in the session; all 16 turns captured).
- 8 user turns, 8 model turns, ~379 KB transcript, 25 code blocks, 13-file site reconstructed.
- Gemini's own final message was a complete session archive (95.8 KB) — preserved in the transcript.
- This Hermes session (20260902_141557_3224f1) is bound to this project (`cwd`/`git_repo_root` → project path).
