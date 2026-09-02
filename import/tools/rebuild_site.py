#!/usr/bin/env python3
"""
rebuild_site.py — Step 8 of the legacy build_project.py:
find the build_zip.py Gemini produced, run it, and unzip the site.

The last build script containing "_worker.js" is the repaired/expanded version
and is preferred. The script is written to import/raw/build_zip_reconstructed.py,
executed with cwd=import/raw, and its greencompute-site.zip is unzipped into site/.

Post-step (fidelity fix, see evaluation/EVALUATION.md): the zip's AI_GUIDE.md is a
truncated SOP stub; the full 11.2 KB protocol from message 1 is restored as
site/AI_GUIDE-full.md from the canonical project-root AI_GUIDE.md.

Reads:   import/raw/clean-session.jsonl
Writes:  import/raw/build_zip_reconstructed.py, import/raw/greencompute-site.zip, site/
"""
import json
import os
import subprocess
import sys
from pathlib import Path

from paths import RAW_DIR, SITE_DIR, PROJECT_ROOT

SOURCE = RAW_DIR / "clean-session.jsonl"


def load_turns(path: Path = SOURCE) -> list[dict]:
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def find_build_scripts(turns: list[dict]) -> list[tuple[int, str]]:
    """Return (message_index, code) for every code block that looks like build_zip.py."""
    found = []
    for i, t in enumerate(turns, 1):
        for cb in t["code_blocks"]:
            if isinstance(cb, dict):
                code = cb.get("code", "")
            elif isinstance(cb, str):
                code = cb
            else:
                continue
            if "zipfile" in code and "FILES" in code and "import os" in code:
                found.append((i, code))
    return found


def rebuild(turns: list[dict], raw_dir: Path, site_dir: Path) -> None:
    build_scripts = find_build_scripts(turns)
    print(f"BUILD_SCRIPTS FOUND: {[(i, len(c)) for i, c in build_scripts]}")

    if not build_scripts:
        print("No build_zip script found in session; skipping site rebuild.")
        return

    worker_scripts = [(i, c) for i, c in build_scripts if "_worker.js" in c or "_worker" in c]
    pick = worker_scripts[-1] if worker_scripts else build_scripts[-1]
    print(f"Using build_zip.py from message {pick[0]}")

    bpath = raw_dir / "build_zip_reconstructed.py"
    bpath.write_text(pick[1])
    print(f"Wrote {bpath}")

    r = subprocess.run([sys.executable, str(bpath)], cwd=raw_dir,
                       capture_output=True, text=True, timeout=60)
    print("build_zip stdout:", r.stdout[-2000:] if r.stdout else "(empty)")
    print("build_zip stderr:", r.stderr[-2000:] if r.stderr else "(empty)")
    print("build_zip rc:", r.returncode)

    zpath = raw_dir / "greencompute-site.zip"
    if zpath.exists():
        site_dir.mkdir(parents=True, exist_ok=True)
        r2 = subprocess.run(["unzip", "-o", str(zpath), "-d", str(site_dir)],
                            capture_output=True, text=True)
        print("unzip rc:", r2.returncode, r2.stderr[-500:] if r2.stderr else "")
        print("SITE FILES:", sorted(os.listdir(site_dir)))

        # Fidelity fix: restore the full AI_GUIDE protocol over the truncated zip stub
        canonical = PROJECT_ROOT / "AI_GUIDE.md"
        if canonical.exists() and canonical.stat().st_size > (site_dir / "AI_GUIDE.md").stat().st_size:
            (site_dir / "AI_GUIDE-full.md").write_text(canonical.read_text())
            print("Restored full AI_GUIDE protocol -> site/AI_GUIDE-full.md")
    else:
        print("WARNING: greencompute-site.zip not produced by build script")


def main() -> None:
    turns = load_turns()
    rebuild(turns, RAW_DIR, SITE_DIR)


if __name__ == "__main__":
    main()
