#!/usr/bin/env python3
"""
Tectonic Briefing — Index Updater
Scans briefings/ directory and regenerates the briefing list in index.html.
Extracts metadata (date, number, tagline, tags) from each briefing HTML.

Usage: python3 scripts/update-index.py
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_DIR = Path.home() / "workflow" / "tectonic-briefing"
BRIEFINGS_DIR = REPO_DIR / "briefings"
INDEX_FILE = REPO_DIR / "index.html"


def extract_metadata(filepath):
    """Extract briefing metadata from HTML file."""
    content = filepath.read_text(encoding='utf-8')
    
    meta = {
        'filename': filepath.name,
        'date_str': filepath.stem,  # YYYY-MM-DD
        'number': '???',
        'display_date': filepath.stem,
        'tagline': '',
        'tags': []
    }
    
    # Extract briefing number
    num_match = re.search(r'BRIEFING NO\.\s*(\d+)', content, re.IGNORECASE)
    if num_match:
        meta['number'] = num_match.group(1).zfill(3)
    
    # Extract display date from .bd class
    date_match = re.search(r'class="bd"[^>]*>([^<]+)<', content)
    if date_match:
        meta['display_date'] = date_match.group(1).strip()
    
    # Extract tagline from .bt class
    tag_match = re.search(r'class="bt"[^>]*>([^<]+)<', content)
    if tag_match:
        meta['tagline'] = tag_match.group(1).strip()
    
    # Extract structural force titles for tags
    force_titles = re.findall(r'<h3[^>]*>([^<]+?)(?:\s*<span class="dd")?', content)
    # Keep only substantive titles (skip generic ones)
    meta['tags'] = [t.strip() for t in force_titles[:10] if len(t.strip()) > 5]
    
    # Detect which lenses are active
    lenses = []
    if 's-ge' in content or 'Geopolitical' in content:
        lenses.append(('geo', 'Geopolitical'))
    if 's-te' in content or 'Technological' in content:
        lenses.append(('tech', 'Technological'))
    if 's-ec' in content or 'Economic' in content:
        lenses.append(('econ', 'Economic'))
    if 's-sc' in content or 'Scientific' in content:
        lenses.append(('sci', 'Scientific'))
    if 's-en' in content or 'Ecological' in content:
        lenses.append(('eco', 'Ecological'))
    if 's-ig' in content or 'Institutional' in content:
        lenses.append(('gov', 'Institutional'))
    if 'Liminal' in content:
        lenses.append(('lim', 'Liminal Signals'))
    meta['lenses'] = lenses
    
    return meta


def generate_entry_html(meta):
    """Generate HTML for a single briefing entry."""
    tags_html = '\n'.join(
        f'<span class="entry-tag {css}">{label}</span>'
        for css, label in meta['lenses']
    )
    
    return f'''<a class="entry" href="briefings/{meta['filename']}">
<div class="entry-num">Briefing No. {meta['number']}</div>
<div class="entry-date">{meta['display_date']}</div>
<div class="entry-tagline">{meta['tagline']}</div>
<div class="entry-tags">
{tags_html}
</div>
</a>'''


def update_index():
    """Scan briefings and update index.html."""
    if not BRIEFINGS_DIR.exists():
        print("Error: briefings/ directory not found")
        sys.exit(1)
    
    # Find all briefing files
    briefing_files = sorted(BRIEFINGS_DIR.glob("*.html"), reverse=True)
    
    if not briefing_files:
        print("No briefings found.")
        return
    
    print(f"Found {len(briefing_files)} briefing(s)")
    
    # Extract metadata and generate entries
    entries = []
    for f in briefing_files:
        meta = extract_metadata(f)
        entries.append(generate_entry_html(meta))
        print(f"  • {meta['date_str']} — No. {meta['number']}")
    
    entries_html = '\n\n'.join(entries)
    
    # Read current index
    index_content = INDEX_FILE.read_text(encoding='utf-8')
    
    # Replace the briefings section
    # Find the marker comments and replace between them
    pattern = r'(<!-- Briefings are listed newest-first.*?-->)\s*(.*?)\s*(<!-- TEMPLATE for new entries)'
    replacement = rf'\1\n\n{entries_html}\n\n\3'
    
    new_content = re.sub(pattern, replacement, index_content, flags=re.DOTALL)
    
    # Update stats
    new_content = re.sub(
        r'(<div class="stat-num" id="count">)\d+(<)',
        rf'\g<1>{len(briefing_files)}\2',
        new_content
    )
    
    INDEX_FILE.write_text(new_content, encoding='utf-8')
    print(f"\n✓ index.html updated with {len(briefing_files)} entries")


if __name__ == '__main__':
    update_index()
