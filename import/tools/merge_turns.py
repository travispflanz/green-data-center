#!/usr/bin/env python3
"""
merge_turns.py — Steps 1-3 of the legacy build_project.py:
load raw DOM-extracted JSONL -> sequential near-duplicate merge -> role assignment.

The raw extractor (extract_full.py) captured each Gemini turn TWICE (a prefixed
record "You said/Gemini said" plus a bare duplicate). Adjacent records whose
normalized text overlaps are merged into the true 16-turn conversation.

Outputs: import/raw/clean-session.jsonl  (intermediate; same as legacy OUT)
"""
import json
import re
from pathlib import Path

from paths import RAW_DIR

RAW_INPUT = RAW_DIR / "green-data-center-plan.jsonl"
CLEAN_OUTPUT = RAW_DIR / "clean-session.jsonl"


def norm_text(t: str) -> str:
    """Strip role prefixes and collapse whitespace for overlap comparison."""
    t = t.replace("You said", "", 1).replace("Gemini said", "", 1)
    return re.sub(r"\s+", " ", t).strip()


def overlap_merge(a_text: str, b_text: str) -> str | None:
    """Return the merged text if one normalized text is contained in the other."""
    na, nb = norm_text(a_text), norm_text(b_text)
    if na in nb:
        return b_text if len(b_text) >= len(a_text) else a_text
    if nb in na:
        return a_text if len(a_text) >= len(b_text) else b_text
    return None


def load_records(path: Path) -> list[dict]:
    records = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            records.append(json.loads(line))
    return records


def merge_records(records: list[dict]) -> list[dict]:
    """Sequential near-duplicate merge: adjacent overlapping records collapse."""
    merged: list[dict] = []
    for r in records:
        if merged:
            last = merged[-1]
            m = overlap_merge(last["text"], r["text"])
            if m is not None:
                last["text"] = m
                for k in ("code_blocks", "links", "images", "saved_images"):
                    if r.get(k):
                        existing = last.get(k) or []
                        last[k] = existing + [x for x in r[k] if x not in existing]
                continue
        merged.append({
            "text": r["text"],
            "code_blocks": r.get("code_blocks", []),
            "links": r.get("links", []),
            "images": r.get("images", []),
            "saved_images": r.get("saved_images", []),
        })
    return merged


def assign_roles(merged: list[dict]) -> list[dict]:
    """Bare records are model duplicates; prefixed records carry the role."""
    turns = []
    for r in merged:
        text = r["text"]
        if text.startswith("You said"):
            role, text = "user", text[len("You said"):].strip()
        elif text.startswith("Gemini said"):
            role, text = "model", text[len("Gemini said"):].strip()
        else:
            role = "model"  # bare records are model duplicates
        turns.append({"role": role, "text": text,
                      "code_blocks": r["code_blocks"], "links": r["links"],
                      "images": r["images"], "saved_images": r["saved_images"]})
    return turns


def main() -> list[dict]:
    records = load_records(RAW_INPUT)
    print(f"RAW RECORDS: {len(records)}")
    merged = merge_records(records)
    print(f"MERGED TURNS: {len(merged)}")
    turns = assign_roles(merged)
    for i, t in enumerate(turns):
        print(f"  [{i}] {t['role']:5s} len={len(t['text']):7d} "
              f"code={len(t['code_blocks'])} links={len(t['links'])} imgs={len(t['images'])}")
    with open(CLEAN_OUTPUT, "w") as f:
        for t in turns:
            f.write(json.dumps(t) + "\n")
    print(f"Wrote {CLEAN_OUTPUT}")
    return turns


if __name__ == "__main__":
    main()
