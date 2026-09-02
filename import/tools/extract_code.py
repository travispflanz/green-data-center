#!/usr/bin/env python3
"""
extract_code.py — Step 6 of the legacy build_project.py:
extract every code block from the clean session into code/msgNN_blockMM.ext.

Reads:   import/raw/clean-session.jsonl
Writes:  code/msgNN_blockMM.ext  (ext by declared language)
"""
import json
from pathlib import Path

from paths import RAW_DIR, CODE_DIR

SOURCE = RAW_DIR / "clean-session.jsonl"

EXT_BY_LANG = {
    "python": "py", "sql": "sql", "javascript": "js", "js": "js",
    "html": "html", "css": "css", "xml": "xml", "json": "json",
    "bash": "sh", "shell": "sh", "text": "txt", "": "txt",
}


def load_turns(path: Path = SOURCE) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def extract_all(turns: list[dict], out_dir: Path) -> list[tuple[int, str, str, int]]:
    out_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    for i, t in enumerate(turns, 1):
        for j, cb in enumerate(t["code_blocks"], 1):
            if isinstance(cb, dict):
                lang = cb.get("language", "txt")
                code = cb.get("code", "")
            elif isinstance(cb, str):
                lang, code = "txt", cb
            else:
                continue
            fname = f"msg{i:02d}_block{j:02d}"
            ext = EXT_BY_LANG.get(lang.lower(), "txt")
            p = out_dir / f"{fname}.{ext}"
            p.write_text(code)
            extracted.append((i, fname, lang, len(code)))
    return extracted


def main() -> None:
    turns = load_turns()
    extracted = extract_all(turns, CODE_DIR)
    for i, fname, lang, size in extracted:
        print(f"  CODE: {fname} ({lang}, {size} chars)")
    print(f"Wrote {len(extracted)} code files to {CODE_DIR}")


if __name__ == "__main__":
    main()
