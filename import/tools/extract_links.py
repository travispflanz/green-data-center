#!/usr/bin/env python3
"""
extract_links.py — Step 7 of the legacy build_project.py:
extract all research links from the clean session into transcript/sources.md.

Reads:   import/raw/clean-session.jsonl
Writes:  transcript/sources.md (deduplicated table: # | message | URL)
"""
import json
from pathlib import Path

from paths import RAW_DIR, TRANSCRIPT_DIR

SOURCE = RAW_DIR / "clean-session.jsonl"


def load_turns(path: Path = SOURCE) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def extract_links(turns: list[dict]) -> list[tuple[int, str]]:
    all_links = []
    for i, t in enumerate(turns, 1):
        for l in t["links"]:
            if isinstance(l, str):
                url = l
            elif isinstance(l, dict):
                url = l.get("href") or l.get("url") or l.get("link") or json.dumps(l)
            else:
                url = str(l)
            if url.startswith("http"):
                all_links.append((i, url))
            else:
                print("  NON-HTTP LINK:", url)
    return all_links


def write_sources(turns: list[dict], out: Path) -> int:
    out.parent.mkdir(parents=True, exist_ok=True)
    seen, n = set(), 0
    lines = ["# Research Sources / Links from Session", "", "| # | Message | URL |", "|---|---|---|"]
    for i, l in extract_links(turns):
        if l in seen:
            continue
        seen.add(l)
        n += 1
        lines.append(f"| {n} | {i} | {l} |")
    out.write_text("\n".join(lines) + "\n")
    return n


def main() -> None:
    turns = load_turns()
    n = write_sources(turns, TRANSCRIPT_DIR / "sources.md")
    print(f"Wrote sources.md with {n} unique links")


if __name__ == "__main__":
    main()
