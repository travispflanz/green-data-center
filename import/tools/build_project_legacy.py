#!/usr/bin/env python3
"""
build_project.py — Turn the raw JSONL extraction into a clean Hermes project:
1. Dedupe the raw records into the true 16-turn conversation.
2. Write a clean full-session transcript (Markdown) + JSONL.
3. Extract all code blocks into code/ and all links into sources.md.
4. Reconstruct the website codebase: run the build_zip.py Gemini produced, unzip it.
"""
import json, re, os, sys, hashlib, subprocess, pathlib

RAW = "/home/assistant/gemini-extract/green-dc/green-data-center-plan.jsonl"
OUT = "/home/assistant/gemini-extract/green-dc"
PROJ = "/home/assistant/green-data-center"

os.makedirs(f"{PROJ}/code", exist_ok=True)
os.makedirs(f"{PROJ}/transcript", exist_ok=True)

# ---- 1. Load raw records ----
records = []
with open(RAW) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
print(f"RAW RECORDS: {len(records)}")

# ---- 2. Sequential near-duplicate merge ----
# Adjacent records in the JSONL are the SAME turn captured twice (prefixed + bare),
# so merge adjacent records whose normalized texts overlap substantially.
def norm_text(t):
    t = t.replace("You said", "", 1).replace("Gemini said", "", 1)
    return re.sub(r"\s+", " ", t).strip()

def overlap_merge(a_text, b_text):
    """Return the merged text if one normalized text is contained in the other."""
    na, nb = norm_text(a_text), norm_text(b_text)
    if na in nb:
        return b_text if len(b_text) >= len(a_text) else a_text
    if nb in na:
        return a_text if len(a_text) >= len(b_text) else b_text
    return None

merged = []  # list of merged turn dicts
for r in records:
    if merged:
        last = merged[-1]
        m = overlap_merge(last["text"], r["text"])
        if m is not None:
            # Merge into last
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
print(f"MERGED TURNS: {len(merged)}")

# ---- 3. Role assignment ----
turns = []
for r in merged:
    text = r["text"]
    if text.startswith("You said"):
        role, text = "user", text[len("You said"):].strip()
    elif text.startswith("Gemini said"):
        role, text = "model", text[len("Gemini said"):].strip()
    else:
        role = "model"  # bare records are model duplicates (users always had the prefix in extraction)
    turns.append({"role": role, "text": text,
                  "code_blocks": r["code_blocks"], "links": r["links"],
                  "images": r["images"], "saved_images": r["saved_images"]})

for i, t in enumerate(turns):
    print(f"  [{i}] {t['role']:5s} len={len(t['text']):7d} code={len(t['code_blocks'])} links={len(t['links'])} imgs={len(t['images'])}")

# ---- 4. Write clean JSONL ----
with open(f"{OUT}/clean-session.jsonl", "w") as f:
    for t in turns:
        f.write(json.dumps(t) + "\n")
print("Wrote clean-session.jsonl")

# ---- 5. Write transcript Markdown ----
md = ["# Sustainable Data Center Architecture, Regulation & Engineering — Full Session Import",
      "",
      f"*Imported from Gemini session `https://gemini.google.com/app/533c4962a18148c1` — {len(turns)} messages ({sum(1 for t in turns if t['role']=='user')} user, {sum(1 for t in turns if t['role']=='model')} model).*",
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
with open(f"{OUT}/transcript-full.md", "w") as f:
    f.write("\n".join(md))
print("Wrote transcript-full.md")

# ---- 6. Extract all code blocks to files ----
code_blocks_all = []
for i, t in enumerate(turns, 1):
    for j, cb in enumerate(t["code_blocks"]):
        if isinstance(cb, dict):
            lang = cb.get("language", "txt")
            code = cb.get("code", "")
        elif isinstance(cb, str):
            lang, code = "txt", cb
        else:
            continue
        fname = f"msg{i:02d}_block{j+1:02d}"
        ext = {"python": "py", "sql": "sql", "javascript": "js", "js": "js", "html": "html",
               "css": "css", "xml": "xml", "json": "json", "bash": "sh", "shell": "sh",
               "text": "txt", "": "txt"}.get(lang.lower(), "txt")
        p = f"{PROJ}/code/{fname}.{ext}"
        with open(p, "w") as f:
            f.write(code)
        code_blocks_all.append((i, fname, lang, len(code)))
for i, fname, lang, size in code_blocks_all:
    print(f"  CODE: {fname} ({lang}, {size} chars)")

# ---- 7. Extract all links to sources.md ----
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
seen = set()
with open(f"{PROJ}/transcript/sources.md", "w") as f:
    f.write("# Research Sources / Links from Session\n\n")
    f.write("| # | Message | URL |\n|---|---|---|\n")
    n = 0
    for i, l in all_links:
        if l in seen:
            continue
        seen.add(l)
        n += 1
        f.write(f"| {n} | {i} | {l} |\n")
print(f"Wrote sources.md with {n} unique links")

# ---- 8. Find & run build_zip.py to reconstruct the website ----
# Gemini embedded the builder script in message 11 (the zip request) and message 17 (expanded)
# and message 21 (repaired). Run the LAST (most complete/repaired) build_zip.py.
build_scripts = []
for i, t in enumerate(turns, 1):
    for j, cb in enumerate(t["code_blocks"]):
        if isinstance(cb, dict):
            code = cb.get("code", "")
        elif isinstance(cb, str):
            code = cb
        else:
            continue
        if "zipfile" in code and "FILES" in code and "import os" in code:
            build_scripts.append((i, code))
print(f"BUILD_SCRIPTS FOUND: {[(i, len(c)) for i, c in build_scripts]}")

if build_scripts:
    # Prefer the one containing "_worker.js" (the repaired/expanded version)
    worker_scripts = [(i, c) for i, c in build_scripts if "_worker.js" in c or "_worker" in c]
    pick = worker_scripts[-1] if worker_scripts else build_scripts[-1]
    print(f"Using build_zip.py from message {pick[0]}")
    bpath = f"{OUT}/build_zip_reconstructed.py"
    with open(bpath, "w") as f:
        f.write(pick[1])
    print(f"Wrote {bpath}")
    r = subprocess.run([sys.executable, bpath], cwd=OUT, capture_output=True, text=True, timeout=60)
    print("build_zip stdout:", r.stdout[-2000:] if r.stdout else "(empty)")
    print("build_zip stderr:", r.stderr[-2000:] if r.stderr else "(empty)")
    print("build_zip rc:", r.returncode)
    zpath = f"{OUT}/greencompute-site.zip"
    if os.path.exists(zpath):
        os.makedirs(f"{PROJ}/site", exist_ok=True)
        r2 = subprocess.run(["unzip", "-o", zpath, "-d", f"{PROJ}/site"], capture_output=True, text=True)
        print("unzip rc:", r2.returncode, r2.stderr[-500:] if r2.stderr else "")
        files = sorted(os.listdir(f"{PROJ}/site"))
        print("SITE FILES:", files)
