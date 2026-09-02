#!/usr/bin/env python3
"""
cdp_gemini_extract.py — Extract a full gemini.google.com conversation (or a
whole project) from the live CDP Chrome (port 9222) into ordered Markdown + JSONL.

Handles Gemini's virtualized chat surface:
  - finds the scroll container, walks top->bottom incrementally
  - dedupes by content hash so re-rendered messages are captured once
  - expands 'Show thinking' / 'Thought process' / 'View analysis' / code
    expanders before capture
  - saves image URLs (and downloads them via the browser's cookie context)
  - reconstructs chronological order by DOM position across scroll passes

Usage (run with ~/.venv-playwright/bin/python3):
  python3 cdp_gemini_extract.py recon [URL]
      -> dump candidate message-node selectors / a11y roles from current page
  python3 cdp_gemini_extract.py dump <URL> [--out PREFIX]
      -> full extraction to PREFIX.md + PREFIX.jsonl (default: /home/assistant/gemini-extract/gemini_dump)
"""
import sys, json, re, time, hashlib, pathlib
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
OUT_DEFAULT = "/home/assistant/gemini-extract/gemini_dump"

EXPAND_RE = re.compile(r"(show thinking|thought process|view analysis|reasoning|show more|expand|view code|show code)", re.I)

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()

def content_hash(s):
    return hashlib.sha1(norm(s).encode("utf-8", "ignore")).hexdigest()[:16]

def find_scroll_container(page):
    """Return the element handle most likely to be the chat virtual scroller."""
    best = None; best_score = -1
    for el in page.query_selector_all("div"):
        try:
            sh = el.evaluate("e => ({sh: e.scrollHeight, ch: e.clientHeight})")
            if sh["sh"] > sh["ch"] and sh["ch"] > 200:
                score = sh["sh"] / max(sh["ch"], 1)
                if score > best_score:
                    best_score = score; best = el
        except Exception:
            continue
    return best

def click_expanders(page):
    """Click thinking/code expanders until none remain."""
    clicked = 0
    for _ in range(60):
        btns = page.query_selector_all("button, [role='button'], [role='article'] *")
        targets = []
        for b in btns:
            try:
                txt = norm(b.inner_text())
                if len(txt) < 60 and EXPAND_RE.search(txt) and b.is_visible():
                    targets.append(b)
            except Exception:
                continue
        if not targets:
            break
        for t in targets:
            try:
                t.click(); clicked += 1
            except Exception:
                pass
        time.sleep(0.4)
    return clicked

def collect_messages(page):
    """Snapshot all visible message-like nodes with role + text + imgs, in DOM order."""
    out = []
    nodes = page.query_selector_all("[data-test-id], [role='article'], [role='listitem'], message-content, .message-content, .query-text, .response-container, .conversation-container *")
    seen = set()
    for n in nodes:
        try:
            role = n.get_attribute("role") or ""
            tid = n.get_attribute("data-test-id") or ""
            txt = n.inner_text() or ""
            if not txt.strip():
                continue
            h = content_hash(txt)
            if h in seen:
                continue
            seen.add(h)
            imgs = n.evaluate("e => Array.from(e.querySelectorAll('img')).map(i => i.src).filter(s => s && !s.startsWith('data:')).slice(0, 50)")
            out.append({"role": role, "test_id": tid, "text": txt, "imgs": imgs})
        except Exception:
            continue
    return out

def walk_conversation(page, max_passes=400):
    """Scroll top->bottom collecting unique message snapshots; stop when stable."""
    sc = find_scroll_container(page)
    if sc is None:
        print("WARN: no scroll container found", file=sys.stderr)
        sc = page.mouse  # fallback: wheel over main
        use_mouse = True
    else:
        use_mouse = False
        sc.evaluate("e => e.scrollTop = 0")
        time.sleep(1.0)
    collected = {}
    order = []
    stable = 0
    for i in range(max_passes):
        snap = collect_messages(page)
        added = 0
        for m in snap:
            h = content_hash(m["text"])
            if h not in collected:
                collected[h] = m; order.append(h); added += 1
        if use_mouse:
            page.mouse.wheel(0, 900)
        else:
            sc.evaluate("e => e.scrollTop += e.clientHeight * 0.8")
        time.sleep(0.45)
        stable = stable + 1 if added == 0 else 0
        if stable >= 3:
            break
        if i % 20 == 0:
            print(f"  pass {i}: {len(order)} unique messages", file=sys.stderr)
    # one final top->bottom sweep to catch stragglers
    if not use_mouse:
        sc.evaluate("e => e.scrollTop = 0"); time.sleep(0.8)
        snap = collect_messages(page)
        for m in snap:
            h = content_hash(m["text"])
            if h not in collected:
                collected[h] = m; order.append(h)
    return [collected[h] for h in order]

def extract_images(page, imgs, outdir):
    saved = []
    for url in imgs:
        try:
            r = page.request.get(url, timeout=15000)
            if r.ok:
                ext = pathlib.Path(url.split("?")[0]).suffix or ".img"
                if len(ext) > 6: ext = ".img"
                fn = outdir / ("img_" + content_hash(url) + ext)
                fn.write_bytes(r.body())
                saved.append(str(fn))
        except Exception as e:
            print(f"  img fail: {str(e)[:80]}", file=sys.stderr)
    return saved

def render_md(title, url, msgs, imgdir):
    lines = [f"# {title}", "", f"- **Source**: {url}", f"- **Extracted**: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}", f"- **Messages**: {len(msgs)}", ""]
    for i, m in enumerate(msgs, 1):
        role = "user" if ("user" in (m.get("role") or "").lower() or "query" in (m.get("test_id") or "").lower()) else "model"
        lines.append(f"---\n\n### [{i}] {role.title()}")
        txt = m["text"]
        if role == "user":
            lines.append("> " + txt.replace("\n", "\n> "))
        else:
            lines.append(txt)
        for img in m.get("imgs", []):
            lines.append(f"\n![image]({img})")
        for s in m.get("_saved_imgs", []):
            lines.append(f"\n![saved]({s})")
        lines.append("")
    return "\n".join(lines)

def main():
    args = sys.argv[1:]
    mode = args[0] if args else "recon"
    url = args[1] if len(args) > 1 else None
    out_prefix = OUT_DEFAULT
    if "--out" in args:
        out_prefix = args[args.index("--out") + 1]

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        ctx = browser.contexts[0]
        page = ctx.new_page()
        try:
            if url:
                page.goto(url, wait_until="load", timeout=60000)
                page.wait_for_timeout(4000)

            if mode == "recon":
                print("URL:", page.url)
                print("TITLE:", page.title())
                sc = find_scroll_container(page)
                print("scroll container found:", sc is not None,
                      (sc.evaluate("e => ({sh:e.scrollHeight, ch:e.clientHeight})") if sc else ""))
                # dump a11y top-level roles
                cdp = ctx.new_cdp_session(page)
                tree = cdp.send("Accessibility.getFullAXTree")["nodes"]
                roles = {}
                for n in tree:
                    r = n.get("role", {}).get("value", "?")
                    nm = (n.get("name", {}) or {}).get("value", "")
                    roles.setdefault(r, []).append(nm[:70])
                for r, names in list(roles.items())[:25]:
                    print(f"  role={r} ({len(names)}):", names[:3])
                print("\nCandidate message elements:")
                for m in collect_messages(page)[:10]:
                    print("  -", (m["role"] or m["test_id"] or "?"), "|", norm(m["text"])[:90])
                return

            if mode == "dump":
                title = page.title()
                print("Extracting:", title, page.url, file=sys.stderr)
                clicked = click_expanders(page)
                print(f"  expanders clicked: {clicked}", file=sys.stderr)
                msgs = walk_conversation(page)
                outdir = pathlib.Path(out_prefix).parent
                imgdir = outdir / (pathlib.Path(out_prefix).name + "_imgs")
                imgdir.mkdir(parents=True, exist_ok=True)
                for m in msgs:
                    if m.get("imgs"):
                        m["_saved_imgs"] = extract_images(page, m["imgs"], imgdir)
                md = render_md(title, page.url, msgs, imgdir)
                pathlib.Path(out_prefix + ".md").write_text(md)
                with open(out_prefix + ".jsonl", "w") as f:
                    for m in msgs:
                        f.write(json.dumps({"role_hint": "user" if "query" in m.get("test_id","").lower() else "model",
                                            "text": m["text"], "images": m.get("imgs", []),
                                            "saved_images": m.get("_saved_imgs", [])}) + "\n")
                print(f"DONE: {len(msgs)} messages -> {out_prefix}.md / .jsonl", file=sys.stderr)
                print(f"DONE {len(msgs)} messages -> {out_prefix}.md / .jsonl")
            else:
                print("Unknown mode:", mode)
        finally:
            page.close()

if __name__ == "__main__":
    main()
