#!/usr/bin/env python3
"""
build_zip.py — one-click export builder for the GreenCompute DB site.

The zip is built by reading the actual files in ./ (the site/ directory),
NOT from embedded string constants. This guarantees the exported artifact
always matches what is deployed (and fixes the historical AI_GUIDE.md
truncation bug where an embedded copy drifted from the real file).

Usage:
    python3 build_zip.py [output.zip]
"""
import os
import zipfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Explicit manifest — add new site files here so they are shipped.
FILES = [
    "index.html",
    "facilities.html",
    "cooling-tech.html",
    "regulations.html",
    "baseload-nuclear.html",
    "sources.html",
    "styles.css",
    "newsletter.js",
    "_worker.js",
    "_headers",
    "schema.sql",
    "sitemap.xml",
    "robots.txt",
    "feed.xml",
    "AI_GUIDE.md",
]


def create_project_zip(output_filename="greencompute-site.zip"):
    print(f"Building {output_filename} from site/ directory (source of truth)...")
    missing = [f for f in FILES if not os.path.isfile(os.path.join(BASE_DIR, f))]
    if missing:
        raise SystemExit(f"✗ Missing site files: {', '.join(missing)}")

    with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in FILES:
            with open(os.path.join(BASE_DIR, file_path), "rb") as fh:
                zipf.writestr(file_path, fh.read())
            print(f"  [+] Packed: {file_path}")
    print(f"\nDone! '{output_filename}' generated ({os.path.getsize(output_filename):,} bytes).")


if __name__ == "__main__":
    import sys

    out = sys.argv[1] if len(sys.argv) > 1 else "greencompute-site.zip"
    create_project_zip(out)
