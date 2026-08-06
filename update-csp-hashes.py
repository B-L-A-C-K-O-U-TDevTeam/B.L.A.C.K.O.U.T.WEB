#!/usr/bin/env python3
"""
Recompute the Content-Security-Policy hashes in index.html.

The CSP pins every inline <script> and <style> by SHA-256. Any edit to that
markup - even one whitespace character - invalidates the hash and the browser
will silently refuse to run the block. Run this after every edit:

    python3 update-csp-hashes.py index.html

Commit the result. If the page ever goes blank or unstyled after a change,
this is almost always the cause; check the browser console for a CSP violation.
"""
import base64
import hashlib
import re
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "index.html"
doc = open(path, encoding="utf-8").read()


def csp_hash(text: str) -> str:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return "'sha256-" + base64.b64encode(digest).decode() + "'"


def collect(tag: str):
    pattern = r"<" + tag + r"(?![^>]*\bsrc=)[^>]*>(.*?)</" + tag + r">"
    return [csp_hash(m.group(1)) for m in re.finditer(pattern, doc, re.S)]


scripts, styles = collect("script"), collect("style")

csp = "; ".join([
    "default-src 'none'",
    "base-uri 'none'",
    "form-action 'none'",
    "object-src 'none'",
    "frame-src 'none'",
    "child-src 'none'",
    "worker-src 'none'",
    "connect-src 'none'",
    "font-src data:",
    "media-src 'none'",
    "manifest-src 'none'",
    "img-src data:",
    "style-src " + " ".join(styles),
    "script-src " + " ".join(scripts),
    "require-trusted-types-for 'script'",
    "upgrade-insecure-requests",
])

doc, count = re.subn(
    r'<meta http-equiv="Content-Security-Policy" content="[^"]*" />',
    '<meta http-equiv="Content-Security-Policy" content="' + csp + '" />',
    doc,
    count=1,
)

if not count:
    sys.exit("No Content-Security-Policy meta tag found in " + path)

open(path, "w", encoding="utf-8").write(doc)
print(f"Updated {path}: {len(scripts)} script hash(es), {len(styles)} style hash(es)")
