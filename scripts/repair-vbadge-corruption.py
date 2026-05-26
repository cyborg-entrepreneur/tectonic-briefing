#!/usr/bin/env python3
"""
Tectonic Briefing — One-Shot Recovery for vbadge Corruption

Background: the first run of inject-vocab-badges.py used per-pattern
re.sub() in a loop. When pattern A's brief description contained pattern
B's name, the second iteration wrapped B inside A's title attribute,
producing nested <a> tags. BeautifulSoup unwrapped the outer wrappers
but left behind leaked title-attribute text in the prose, like:

    </a>'s mean-trajectory calibration succeeds … the rebound is" data-meta="5"><a class="vbadge m5" href="…">Tail Calibration Failure</a>

This script finds the corruption signature (orphan `" data-meta="N">`
between `</a>` and the next `<a class="vbadge"`) and removes the leaked
span, restoring the clean badge sequence.

Run once before re-running inject-vocab-badges.py with the fixed logic.
"""

import re
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
BRIEFINGS_DIR = REPO_DIR / "briefings"

# Match the orphan title-leak. BeautifulSoup HTML-encoded the trailing
# `>` to `&gt;`, so we look for both forms. The leak ends with
# `" data-meta="N">` or `" data-meta="N"&gt;` and is followed by
# either another <a> tag or an end-of-element boundary.
CORRUPTION = re.compile(
    r'(</a>)([^<]*?)" data-meta="\d"(?:&gt;|>)\s*(<a class="vbadge)',
    re.DOTALL
)

CORRUPTION_TAIL = re.compile(
    r'(</a>)([^<]*?)" data-meta="\d"(?:&gt;|>)(\s*(?:</p>|</div>|</h\d>|<))',
    re.DOTALL
)


def repair(html):
    new_html = html
    total = 0
    # Iterate because each pass may reveal new corruption
    for _ in range(10):
        new_html, k1 = CORRUPTION.subn(r'\1 \3', new_html)
        new_html, k2 = CORRUPTION_TAIL.subn(r'\1\3', new_html)
        if k1 == 0 and k2 == 0:
            break
        total += k1 + k2
    return new_html, total


def main():
    briefings = sorted(BRIEFINGS_DIR.glob('2026-*.html'))
    print(f"Scanning {len(briefings)} briefings for corruption signatures…")

    total = 0
    files_changed = 0
    for bf in briefings:
        original = bf.read_text()
        cleaned, n = repair(original)
        if n > 0:
            bf.write_text(cleaned)
            files_changed += 1
            total += n
            print(f"  ✓ {bf.name}: {n} corruption(s) repaired")

    print(f"\n✓ {total} corruption fragments repaired across {files_changed} files")
    print(f"   (Run inject-vocab-badges.py to re-inject any badges removed by repair.)")


if __name__ == '__main__':
    main()
