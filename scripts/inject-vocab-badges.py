#!/usr/bin/env python3
"""
Tectonic Briefing — Inline Vocabulary Badges Injector

Post-processes briefing HTML files so that structural-vocabulary pattern
names mentioned in prose become inline badge-style links to their concept
pages.

Algorithm:
  1. STRIP existing vbadges (idempotency + recovery from any prior corrupt
     runs). Uses BeautifulSoup to safely unwrap any <a class="vbadge"> tag,
     including those nested inside title attributes from earlier buggy runs.
  2. Stash excluded zones (vocab cards, source archive, footer attestation,
     thinker registry, <style>, <script>, TB-NAV wrappers, meta-category
     section headings).
  3. Stash all existing <a> anchors (so links to external/internal pages
     don't get pattern-name-wrapped inside them).
  4. SINGLE-PASS regex with alternation across all 42 pattern names. The
     regex visits each character position once, so no cross-pattern
     contamination is possible — a title attribute can never contain
     another vbadge because no replacement modifies the working text
     before the regex finishes.
  5. Restore stashed anchors and zones.

Run after every briefing-creation step:
    python3 scripts/build-concept-pages.py   # update registry
    python3 scripts/inject-vocab-badges.py   # inject badges
"""

import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

REPO_DIR = Path(__file__).resolve().parent.parent
BRIEFINGS_DIR = REPO_DIR / "briefings"
REGISTRY = REPO_DIR / "concepts" / "registry.json"

EXCLUDED_PATTERNS = [
    re.compile(r'<style>.*?</style>', re.DOTALL),
    re.compile(r'<script>.*?</script>', re.DOTALL),
    re.compile(r'<div class="vi[^"]*">.*?</div>', re.DOTALL),
    re.compile(r'<div class="src[^"]*">.*?</div>', re.DOTALL),
    re.compile(r'<div class="tk[^"]*">.*?</div>', re.DOTALL),
    re.compile(r'<details class="footer-attest">.*?</details>', re.DOTALL),
    re.compile(r'<footer>.*?</footer>', re.DOTALL),
    re.compile(r'<h4 class="sh2"[^>]*>[^<]*META-\d+:[^<]*</h4>', re.DOTALL),
    re.compile(r'<!-- TB-NAV-WRAP:TOP:START -->.*?<!-- TB-NAV-WRAP:TOP:END -->', re.DOTALL),
    re.compile(r'<!-- TB-NAV-WRAP:BOT:START -->.*?<!-- TB-NAV-WRAP:BOT:END -->', re.DOTALL),
]


def load_registry():
    if not REGISTRY.exists():
        raise SystemExit(
            f"Registry not found at {REGISTRY}.\n"
            "Run scripts/build-concept-pages.py first."
        )
    return json.loads(REGISTRY.read_text())


def strip_existing_badges(html):
    """Remove any existing <a class="vbadge"> wrappers, including malformed
    nested ones from buggy prior runs. Uses BeautifulSoup which handles
    malformed HTML correctly.

    Returns cleaned HTML with badge anchors unwrapped to plain text.
    """
    # Only touch the body — preserve <style>, <script>, head, etc.
    # Split into pre-body / body / post-body to keep BeautifulSoup limited.
    body_split = re.split(r'(<body[^>]*>)', html, maxsplit=1)
    if len(body_split) != 3:
        return html
    pre, body_open, rest = body_split
    body_close_match = re.search(r'</body>', rest)
    if not body_close_match:
        return html
    body_inner = rest[:body_close_match.start()]
    post = rest[body_close_match.start():]

    soup = BeautifulSoup(body_inner, 'html.parser')
    # Unwrap every <a class="vbadge ...">
    for a in soup.find_all('a', class_=lambda c: c and 'vbadge' in c):
        a.replace_with(a.get_text())

    new_body_inner = str(soup)
    return pre + body_open + new_body_inner + post


def stash_zones(html, regexes, prefix):
    stash = []

    def store(m):
        stash.append(m.group(0))
        return f"__{prefix}_{len(stash) - 1}__"

    out = html
    for r in regexes:
        out = r.sub(store, out)
    return out, stash


def restore_zones(html, stash, prefix):
    placeholder = re.compile(rf"__{prefix}_(\d+)__")
    return placeholder.sub(lambda m: stash[int(m.group(1))], html)


def inject_badges(html, patterns):
    """Single-pass injection of vocab-badge links into prose."""
    # Step 0: strip any existing badges (idempotency + recovery)
    html = strip_existing_badges(html)

    # Step 1: stash excluded zones
    working, excluded = stash_zones(html, EXCLUDED_PATTERNS, "EXCL")

    # Step 2: stash all existing <a> anchors
    anchor_re = [re.compile(r'<a\b[^>]*>.*?</a>', re.DOTALL)]
    working, anchors = stash_zones(working, anchor_re, "ANCH")

    # Step 3: SINGLE-PASS alternation regex
    # Sort by length desc so multi-word names take precedence over any
    # shorter name that could substring-match (defensive — none currently).
    sorted_patterns = sorted(patterns, key=lambda p: -len(p['name']))
    pattern_lookup = {p['name']: p for p in patterns}

    alternation = '|'.join(re.escape(p['name']) for p in sorted_patterns)
    big_re = re.compile(rf'\b({alternation})\b')

    n_replacements = [0]

    def replace(m):
        name = m.group(1)
        p = pattern_lookup[name]
        brief = p['brief'].replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        n_replacements[0] += 1
        return (
            f'<a class="vbadge m{p["meta"]}" '
            f'href="../concepts/{p["slug"]}.html" '
            f'title="{brief}" '
            f'data-meta="{p["meta"]}">{name}</a>'
        )

    working = big_re.sub(replace, working)

    # Step 4: restore anchors, then excluded zones
    working = restore_zones(working, anchors, "ANCH")
    working = restore_zones(working, excluded, "EXCL")

    return working, n_replacements[0]


def main():
    registry = load_registry()
    patterns = registry['patterns']
    print(f"Loaded registry: {len(patterns)} patterns")

    briefings = sorted(BRIEFINGS_DIR.glob('2026-*.html'))
    print(f"Processing {len(briefings)} briefings…")

    total_replacements = 0
    files_changed = 0
    for bf in briefings:
        original = bf.read_text()
        updated, n = inject_badges(original, patterns)
        if updated != original:
            bf.write_text(updated)
            files_changed += 1
            total_replacements += n
            print(f"  ✓ {bf.name}: {n} badge(s) injected")

    print(f"\n✓ {total_replacements} total badges across {files_changed} files")


if __name__ == '__main__':
    main()
