#!/usr/bin/env python3
"""
paths.py — Central path resolution for the Green Data Center import toolchain.

Every decompiled tool derives the project root from THIS file's location
(import/tools/ -> project root), so the pipeline works from any checkout
without hardcoded absolute paths. The legacy monolith (build_project_legacy.py)
hardcoded /home/assistant paths; this module fixes that for future dev.
"""
from pathlib import Path

# import/tools/paths.py -> project root (parents: tools -> import -> root)
TOOLS_DIR = Path(__file__).resolve().parent
IMPORT_DIR = TOOLS_DIR.parent
PROJECT_ROOT = IMPORT_DIR.parent

RAW_DIR = IMPORT_DIR / "raw"
IMAGES_DIR = IMPORT_DIR / "images"

CODE_DIR = PROJECT_ROOT / "code"
TRANSCRIPT_DIR = PROJECT_ROOT / "transcript"
SITE_DIR = PROJECT_ROOT / "site"
EVALUATION_DIR = PROJECT_ROOT / "evaluation"

GEMINI_SESSION_URL = "https://gemini.google.com/app/533c4962a18148c1"
