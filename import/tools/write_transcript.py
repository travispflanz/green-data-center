#!/usr/bin/env python3
"""
write_transcript.py — Steps 4-5 of the legacy build_project.py:
write the clean 16-turn JSONL and the full Markdown transcript.

Reads:   import/raw/clean-session.jsonl (output of merge_turns.py)
Writes:  transcript/clean-session.jsonl, transcript/transcript-full.md
"""
import json
from pathlib import Path

from paths import RAW_DIR, TRANSCRIPT_DIR, GEMINI_SESSION_URL

SOURCE = RAW_DIR / "clean-session.jsonl"


def load_turns(path: Path = SOURCE) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def build_markdown(turns: list[dict]) -> str:
    md = ["# Sustainable Data Center Architecture, Regulation & Engineering — Full Session Import",
          "",
          f"*Imported from Gemini session `{GEMINI_SESSION_URL}` — {len(turns)} messages "
          f"({sum(1 for t in turns if t['role']=='user')} user, "
          f"{sum(1 for t in turns if t['role']=='model')} model).*",
          "",
          "---", ""]
    for i, t in enumerate(turns, 1):
        label = "🧑 **User**" if t["role"] == "user" else "🤖 **Gemini**"
        md.append(f"## Message {i} — {label}\n")
        md.append(t["text"].strip() + "\n")
        if t["links"]:
            md.append("\n**Links in this message:**")
            for l in t["links"]:
                if isinstance(l, str):
                    url = l
                elif isinstance(l, dict):
                    url = l.get("href") or l.get("url") or l.get("link") or str(l)
                else:
                    url = str(l)
                md.append(f"- {url}")
        if t["images"]:
            md.append("\n**Images:**")
            for im in t["images"]:
                md.append(f"- {im}")
        if t["saved_images"]:
            md.append("\n**Saved images:**")
            for im in t["saved_images"]:
                md.append(f"- {im}")
        md.append("\n---\n")
    return "\n".join(md)


def main() -> None:
    turns = load_turns()
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    with open(TRANSCRIPT_DIR / "clean-session.jsonl", "w") as f:
        for t in turns:
            f.write(json.dumps(t) + "\n")
    with open(TRANSCRIPT_DIR / "transcript-full.md", "w") as f:
        f.write(build_markdown(turns))
    print(f"Wrote {TRANSCRIPT_DIR / 'clean-session.jsonl'} ({len(turns)} turns)")
    print(f"Wrote {TRANSCRIPT_DIR / 'transcript-full.md'}")


if __name__ == "__main__":
    main()
