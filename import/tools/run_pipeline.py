#!/usr/bin/env python3
"""
run_pipeline.py — Orchestrator for the decompiled import toolchain.

Runs every step in the same order as the legacy build_project_legacy.py:
  1. merge_turns     -> import/raw/clean-session.jsonl (dedupe + role assignment)
  2. write_transcript-> transcript/clean-session.jsonl + transcript-full.md
  3. extract_code    -> code/msgNN_blockMM.ext
  4. extract_links   -> transcript/sources.md
  5. rebuild_site    -> import/raw/build_zip_reconstructed.py + greencompute-site.zip -> site/

Usage:
    python3 run_pipeline.py            # full pipeline, stop on first error
    python3 run_pipeline.py --step merge_turns   # run one step only
"""
import argparse
import importlib
import sys

STEPS = ["merge_turns", "write_transcript", "extract_code", "extract_links", "rebuild_site"]


def run_step(name: str) -> None:
    print(f"\n=== {name} ===")
    mod = importlib.import_module(name)
    mod.main()


def main() -> None:
    parser = argparse.ArgumentParser(description="Green Data Center import pipeline")
    parser.add_argument("--step", choices=STEPS, help="run only this step")
    args = parser.parse_args()

    steps = [args.step] if args.step else STEPS
    for s in steps:
        run_step(s)
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
