#!/usr/bin/env python3
"""
extract_full.py — Full-fidelity extraction of ONE Gemini conversation
from the live CDP Chrome (port 9222) into Markdown + JSONL + images.

Strategy for "literally everything":
  1. Fresh tab -> the exact session URL.
  2. Structural recon: find message containers (custom elements, role=article,
     data-test-id), expander buttons, code blocks, links, images.
  3. Scroll-walk the virtualized chat: at each position, click every
     "Show thinking"/"Thought process"/"View analysis"/"Show more" expander,
     then snapshot unique message nodes (dedupe by content hash) preserving
     DOM order. Stop when 3 consecutive passes add nothing new.
  4. Per message: role hint (user/model), full text, code blocks (with
     language labels), source links (citations), image URLs.
  5. Save images via the browser cookie context.
  6. Write chronological Markdown + JSONL.
"""
import sys, json, re, time, hashlib, pathlib
from playwright.sync_api import sync_playwright

CDP = "http://127.0.0.1:9222"
URL = "https://gemini.google.com/app/533c4962a18148c1"
OUT_PREFIX = "/home/assistant/gemini-extract/green-dc/green-data-center-plan"
OUT_IMGDIR = pathlib.Path(OUT_PREFIX + "_imgs")

EXPAND_RE = re.compile(r"(show thinking|thought process|view analysis|show more|reasoning|expand|view code|show code)", re.I)

def norm(s):
    return re.sub(r"\s+", " ", s or "").strip()

def content_hash(s):
    return hashlib.sha1(norm(s).encode("utf-8", "ignore")).hexdigest()[:16]

def find_scroller(page):
    """Best guess at the chat virtual scroller; returns (handle, height, clientH)."""
    best = None; bs = -1; info = None
    for el in page.query_selector_all("div"):
        try:
            d = el.evaluate("e => ({sh: e.scrollHeight, ch: e.clientHeight})")
            if d["sh"] > d["ch"] and d["ch"] > 200:
                s = d["sh"] / max(d["ch"], 1)
                if s > bs:
                    bs = s; best = el; info = d
        except Exception:
            continue
    return best, info

def click_expanders(page, limit=80):
    clicked = 0
    for _ in range(limit):
        btns = page.query_selector_all("button, [role='button']")
        targets = []
        for b in btns:
            try:
                txt = norm(b.inner_text())
                if 0 < len(txt) < 60 and EXPAND_RE.search(txt) and b.is_visible():
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
        time.sleep(0.35)
    return clicked

def detect_message_selector(page):
    """Return a list of selector strings that match message-like containers."""
    cands = []
    for sel in ["message-content", "user-query", "model-response",
                "div[data-test-id='conversation-turn']", "[role='article']",
                ".query-text", ".response-container", "div[data-message-id]"]:
        try:
            n = page.query_selector_all(sel)
            if n:
                cands.append((sel, len(n)))
        except Exception:
            pass
    # also generic: elements whose id starts with message
    try:
        ids = page.evaluate("() => Array.from(document.querySelectorAll('[id]')).map(e => e.id).filter(i => /message|turn|query|response/i.test(i)).slice(0, 20)")
    except Exception:
        ids = []
    return cands, ids

def collect(page):
    """Snapshot message-like nodes in DOM order with rich detail."""
    out = []
    seen = set()
    # primary candidate: custom elements / role=article / data-test-id
    nodes = page.query_selector_all("message-content, user-query, model-response, div[data-test-id='conversation-turn'], [role='article'], [data-message-id]")
    for n in nodes:
        try:
            txt = n.inner_text() or ""
            if not txt.strip():
                continue
            h = content_hash(txt)
            if h in seen:
                continue
            seen.add(h)
            tag = n.evaluate("e => e.tagName.toLowerCase()")
            tid = n.get_attribute("data-test-id") or ""
            role = n.get_attribute("role") or ""
            # code blocks
            codes = n.evaluate("""e => Array.from(e.querySelectorAll('pre')).map(p => {
                const langEl = p.querySelector('[class*="language"], [class*="lang"]');
                return {lang: langEl ? langEl.innerText.trim() : '', code: p.innerText};
            })""")
            # links (research sources / citations)
            links = n.evaluate("""e => Array.from(e.querySelectorAll('a[href]')).map(a => ({text: (a.innerText||'').trim().slice(0,120), href: a.href})).filter(l => l.href.startsWith('http'))""")
            # images
            imgs = n.evaluate("""e => Array.from(e.querySelectorAll('img')).map(i => i.src).filter(s => s && s.startsWith('http'))""")
            is_user = bool(re.search(r"(you said|you asked|your prompt)", txt[:120], re.I)) or "query" in (tid or "").lower() or tag == "user-query"
            out.append({"tag": tag, "test_id": tid, "role_attr": role,
                        "is_user": is_user, "text": txt, "codes": codes,
                        "links": links, "imgs": imgs})
        except Exception:
            continue
    return out

def walk(page, max_passes=500):
    sc, info = find_scroller(page)
    if sc is None:
        print("WARN: no scroller found, using mouse wheel", file=sys.stderr)
        use_mouse = True
    else:
        use_mouse = False
        print(f"scroller: sh={info['sh']} ch={info['ch']}", file=sys.stderr)
        sc.evaluate("e => e.scrollTop = 0")
        time.sleep(1.2)
    collected = {}; order = []; stable = 0
    total_scrolled = 0
    for i in range(max_passes):
        clicked = click_expanders(page)
        snap = collect(page)
        added = 0
        for m in snap:
            h = content_hash(m["text"])
            if h not in collected:
                collected[h] = m; order.append(h); added += 1
        if use_mouse:
            page.mouse.wheel(0, 1000)
        else:
            sc.evaluate("e => e.scrollTop += e.clientHeight * 0.85")
        total_scrolled += 1
        time.sleep(0.5)
        stable = stable + 1 if added == 0 else 0
        if i % 15 == 0:
            print(f"  pass {i}: {len(order)} unique | expanders={clicked}", file=sys.stderr)
        if stable >= 4:
            break
    # final sweep top->bottom
    if not use_mouse:
        sc.evaluate("e => e.scrollTop = 0"); time.sleep(1.0)
        click_expanders(page)
        snap = collect(page)
        for m in snap:
            h = content_hash(m["text"])
            if h not in collected:
                collected[h] = m; order.append(h)
    print(f"walk done: {len(order)} unique after {total_scrolled} scrolls", file=sys.stderr)
    return [collected[h] for h in order]

def save_images(page, urls, folder):
    saved = []
    for u in urls:
        try:
            r = page.request.get(u, timeout=15000)
            if r.ok:
                ext = pathlib.Path(u.split("?")[0]).suffix
                if ext not in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
                    ext = ".img"
                fn = folder / ("img_" + content_hash(u) + ext)
                fn.write_bytes(r.body())
                saved.append(str(fn))
        except Exception as e:
            print(f"  img fail: {str(e)[:70]}", file=sys.stderr)
    return saved

def render_md(msgs):
    lines = [f"# Green Data Center Research Plan — Full Gemini Session Import", "",
             f"- **Source**: {URL}", f"- **Extracted**: {time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
             f"- **Messages**: {len(msgs)}", ""]
    for i, m in enumerate(msgs, 1):
        role = "USER" if m["is_user"] else "GEMINI"
        lines.append(f"\n---\n\n## [{i}] {role}")
        if m["tag"] or m["test_id"]:
            lines.append(f"<sub>node: {m['tag']} {m['test_id']} {m['role_attr']}</sub>\n")
        if role == "USER":
            lines.append("> " + m["text"].replace("\n", "\n> "))
        else:
            lines.append(m["text"])
        if m["codes"]:
            lines.append("\n**Code blocks:**")
            for j, c in enumerate(m["codes"], 1):
                lines.append(f"\n```{c['lang'] or ''}\n{c['code']}\n```")
        if m["links"]:
            lines.append("\n**Sources / links:**")
            for lk in m["links"]:
                lines.append(f"- [{lk['text'] or lk['href'][:80]}]({lk['href']})")
        if m["imgs"]:
            lines.append("\n**Images:**")
            for u in m["imgs"]:
                lines.append(f"- {u}")
        for s in m.get("_saved", []):
            lines.append(f"\n![saved]({s})")
        lines.append("")
    return "\n".join(lines)

def main():
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(CDP)
        ctx = browser.contexts[0]
        page = ctx.new_page()
        try:
            page.goto(URL, wait_until="load", timeout=60000)
            page.wait_for_timeout(6000)
            print("loaded:", page.url, "|", page.title(), file=sys.stderr)
            cands, ids = detect_message_selector(page)
            print("selectors:", cands, file=sys.stderr)
            print("ids:", ids, file=sys.stderr)
            msgs = walk(page)
            OUT_IMGDIR.mkdir(parents=True, exist_ok=True)
            for m in msgs:
                if m["imgs"]:
                    m["_saved"] = save_images(page, m["imgs"], OUT_IMGDIR)
            md = render_md(msgs)
            pathlib.Path(OUT_PREFIX + ".md").write_text(md)
            with open(OUT_PREFIX + ".jsonl", "w") as f:
                for m in msgs:
                    f.write(json.dumps({"role": "user" if m["is_user"] else "model",
                                        "text": m["text"],
                                        "code_blocks": m["codes"],
                                        "links": m["links"],
                                        "images": m["imgs"],
                                        "saved_images": m.get("_saved", [])}) + "\n")
            print(f"DONE {len(msgs)} messages -> {OUT_PREFIX}.md/.jsonl", file=sys.stderr)
            print(f"DONE {len(msgs)} messages -> {OUT_PREFIX}.md/.jsonl")
        finally:
            page.close()

if __name__ == "__main__":
    main()
