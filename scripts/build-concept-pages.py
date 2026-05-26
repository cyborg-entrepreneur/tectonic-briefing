#!/usr/bin/env python3
"""
Tectonic Briefing — Concept Pages Builder

Generates one HTML page per structural-vocabulary pattern.

Each concept page contains:
  - Meta-category color band + canonical definition
  - First-named briefing link
  - Timeline of every briefing where the pattern is cited
  - Excerpts of each citation
  - Cross-references: patterns that co-occur with this one across briefings

Also generates concepts/index.html — a navigable listing of all patterns
grouped by meta-category.

Usage: python3 scripts/build-concept-pages.py
"""

import re
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from html import escape

REPO_DIR = Path(__file__).resolve().parent.parent
BRIEFINGS_DIR = REPO_DIR / "briefings"
CONCEPTS_DIR = REPO_DIR / "concepts"
STRUCTURAL_CONCEPTS = REPO_DIR / "STRUCTURAL_CONCEPTS.md"
CONCEPT_REGISTRY_JSON = REPO_DIR / "concepts" / "registry.json"

META_NAMES = {
    1: "Coupling Failure",
    2: "Bypass Inversion",
    3: "Threshold Cascade",
    4: "Commons Enclosure",
    5: "Institutional Hollowing",
}

META_COLORS = {
    1: "#4b8ef2",  # blue
    2: "#a78bfa",  # purple
    3: "#f06050",  # red
    4: "#38d9c8",  # teal
    5: "#c97a3a",  # amber
}

META_HEADING_COLORS = {
    1: "#6da8ff",
    2: "#a78bfa",
    3: "#fca5a5",
    4: "#38d9c8",
    5: "#dcb267",
}


def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower())
    return re.sub(r"[\s_-]+", "-", s).strip("-")


# ──────────────────────────────────────────────────────────────────────
# Parse STRUCTURAL_CONCEPTS.md
# ──────────────────────────────────────────────────────────────────────
def parse_structural_concepts():
    """Parse STRUCTURAL_CONCEPTS.md to extract pattern definitions.

    Returns a list of dicts: {name, slug, meta, meta_name, source_briefing,
    description, brief}
    """
    content = STRUCTURAL_CONCEPTS.read_text()

    # Split by ## META-N headings
    meta_pattern = re.compile(r'^## META-(\d+):\s*([^\n]+)$', re.MULTILINE)
    matches = list(meta_pattern.finditer(content))

    patterns = []
    for i, m in enumerate(matches):
        meta_num = int(m.group(1))
        meta_name = m.group(2).strip()
        section_start = m.end()
        section_end = (matches[i + 1].start() if i + 1 < len(matches)
                       else content.find('\n## ', section_start))
        if section_end == -1:
            section_end = len(content)
        section = content[section_start:section_end]

        # Find instantiations (bullet items)
        # Format: - **PatternName** *(Briefing NNN)* — Description text...
        # Items may span multiple paragraphs; terminate at next - **
        item_pattern = re.compile(
            r'^- \*\*([^*]+)\*\*\s*\*\(Briefing\s+(\d+)\)\*\s*—\s*(.+?)(?=^- \*\*|^---|\Z)',
            re.MULTILINE | re.DOTALL
        )
        for it in item_pattern.finditer(section):
            name = it.group(1).strip()
            source_briefing = int(it.group(2))
            desc = it.group(3).strip()
            # Clean up trailing whitespace/markdown
            desc = re.sub(r'\n\n+', '\n\n', desc)

            # Brief one-liner for tooltips. Prefer the first sentence; if
            # the first sentence is too long, prefer the first independent
            # clause (semicolon-split). Cap at 200 chars with ellipsis,
            # always ending at a word boundary.
            first_sentence = desc.split('. ')[0].strip()
            if len(first_sentence) > 220:
                first_sentence = first_sentence.split(';')[0].strip()
            if len(first_sentence) > 220:
                # Truncate at last space before 220 chars
                cut = first_sentence[:220].rsplit(' ', 1)[0]
                first_sentence = cut + '…'
            elif not first_sentence.endswith(('.', '…', '!', '?')):
                first_sentence += '.'
            brief = first_sentence

            patterns.append({
                'name': name,
                'slug': slugify(name),
                'meta': meta_num,
                'meta_name': meta_name,
                'source_briefing': source_briefing,
                'description': desc,
                'brief': brief,
            })

    return patterns


# ──────────────────────────────────────────────────────────────────────
# Load briefings + extract metadata
# ──────────────────────────────────────────────────────────────────────
def load_briefings():
    """Return list of (path, raw_html, meta_dict) for every briefing."""
    briefings = []
    for bf in sorted(BRIEFINGS_DIR.glob('2026-*.html')):
        try:
            html = bf.read_text()
        except Exception as e:
            print(f"  ! skipped {bf.name}: {e}")
            continue
        date_str = bf.stem

        num_match = re.search(r'BRIEFING NO\.\s*(\d+)', html)
        number = num_match.group(1) if num_match else None
        if not number:
            continue

        try:
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            dow = dt.strftime('%A')
            display_date = dt.strftime('%-d %B %Y')
        except Exception:
            dt = None
            dow = ''
            display_date = date_str

        # Unifying thread title
        thread_match = re.search(
            r'<div class="th"[^>]*>\s*<h3[^>]*>([^<]+(?:<[^>]+>[^<]+)*?)</h3>',
            html
        )
        if thread_match:
            thread_title = re.sub(r'<[^>]+>', '', thread_match.group(1))
            thread_title = thread_title.replace('Unifying Thread:', '').strip()
        else:
            thread_title = ''

        # Cycle
        cycle_match = re.search(r'CYCLE\s*(\d+)', html)
        cycle = int(cycle_match.group(1)) if cycle_match else 1

        meta = {
            'filename': bf.name,
            'date': date_str,
            'display_date': display_date,
            'dow': dow,
            'number': number,
            'thread_title': thread_title,
            'cycle': cycle,
        }
        briefings.append((bf, html, meta))

    return briefings


# ──────────────────────────────────────────────────────────────────────
# Find citations in briefings
# ──────────────────────────────────────────────────────────────────────
def strip_excluded_zones(html):
    """Remove zones where pattern mentions are not 'citations' in the
    structural-vocabulary sense:
      - <div class="vi …"> vocabulary cards (definitional)
      - <div class="src …"> source archive entries (event-level)
      - <details class="footer-attest"> footer verification log
      - <footer> overall
      - <div class="tk …"> thinker registry / serendipity queue
      - <h4 class="sh2"> meta-category section headings
    """
    out = html
    out = re.sub(r'<div class="vi[^"]*">.*?</div>', '', out, flags=re.DOTALL)
    out = re.sub(r'<div class="src[^"]*">.*?</div>', '', out, flags=re.DOTALL)
    out = re.sub(r'<div class="tk[^"]*">.*?</div>', '', out, flags=re.DOTALL)
    out = re.sub(
        r'<details class="footer-attest">.*?</details>',
        '', out, flags=re.DOTALL
    )
    out = re.sub(r'<footer>.*?</footer>', '', out, flags=re.DOTALL)
    out = re.sub(r'<h4 class="sh2"[^>]*>.*?</h4>', '', out, flags=re.DOTALL)
    return out


def extract_excerpt(clean_html, name):
    """Return a ~280-char text excerpt from the first paragraph mentioning
    the pattern."""
    p_re = re.compile(r'<p[^>]*>(.*?)</p>', re.DOTALL)
    name_re = re.compile(rf'\b{re.escape(name)}\b')
    for m in p_re.finditer(clean_html):
        para = m.group(1)
        if name_re.search(para):
            text = re.sub(r'<[^>]+>', ' ', para)
            text = (text
                    .replace('&ldquo;', '"').replace('&rdquo;', '"')
                    .replace('&lsquo;', "'").replace('&rsquo;', "'")
                    .replace('&mdash;', '—').replace('&middot;', '·')
                    .replace('&amp;', '&').replace('&nbsp;', ' ')
                    .replace('&hellip;', '…'))
            text = re.sub(r'&[a-z]+;|&#\d+;', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            idx_match = name_re.search(text)
            if not idx_match:
                return text[:280]
            idx = idx_match.start()
            start = max(0, idx - 100)
            end = min(len(text), idx + 220)
            excerpt = text[start:end]
            if start > 0:
                excerpt = '…' + excerpt
            if end < len(text):
                excerpt = excerpt + '…'
            return excerpt
    return ''


def find_citations(patterns, briefings):
    """For each pattern: list of {briefing_meta + excerpt} dicts, ordered
    by briefing date."""
    citations = defaultdict(list)

    # Pre-build pattern-name regex for efficiency
    pattern_lookup = {p['name']: p for p in patterns}

    for bf, html, meta in briefings:
        clean = strip_excluded_zones(html)
        for p in patterns:
            name = p['name']
            if re.search(rf'\b{re.escape(name)}\b', clean):
                excerpt = extract_excerpt(clean, name)
                cite = dict(meta)
                cite['excerpt'] = excerpt
                cite['is_naming'] = (int(meta['number']) == p['source_briefing'])
                citations[name].append(cite)

    # Sort each pattern's citations by briefing number
    for name in citations:
        citations[name].sort(key=lambda c: int(c['number']))

    return citations


# ──────────────────────────────────────────────────────────────────────
# Cross-references
# ──────────────────────────────────────────────────────────────────────
def build_cross_references(citations):
    """For each pattern, count co-occurrences with every other pattern."""
    cross_refs = defaultdict(Counter)

    # briefing_number -> set of pattern names cited
    briefing_patterns = defaultdict(set)
    for name, cite_list in citations.items():
        for c in cite_list:
            briefing_patterns[c['number']].add(name)

    for briefing_num, names in briefing_patterns.items():
        names_list = list(names)
        for n in names_list:
            for other in names_list:
                if other != n:
                    cross_refs[n][other] += 1

    return cross_refs


# ──────────────────────────────────────────────────────────────────────
# Render concept page HTML
# ──────────────────────────────────────────────────────────────────────
CONCEPT_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&family=JetBrains+Mono:wght@300;400;500&family=Source+Sans+3:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{background-color:#0b1120!important;color:#d4dce8;font-family:'Source Sans 3',system-ui,sans-serif;font-size:16px;line-height:1.7;min-height:100vh}
body{background-image:radial-gradient(rgba(75,142,242,0.045) 1px,transparent 1px);background-size:48px 48px;background-attachment:fixed}
:root{--bg:#0b1120;--card:#111827;--alt:#141c2e;--str:#162035;--blu:#4b8ef2;--blub:#6da8ff;--blup:#a3c8ff;--teal:#38d9c8;--tealm:#2a9e92;--gold:#e5b84c;--goldm:#c9a03a;--red:#f06050;--purp:#a78bfa;--grn:#4ade80;--amb:#c97a3a;--ambb:#dcb267;--t1:#eaf0f8;--t2:#cdd6e4;--t3:#8e9bb5;--t4:#7a8aa6;--brd:rgba(75,142,242,0.18);--brds:rgba(75,142,242,0.35);--m1:#4b8ef2;--m2:#a78bfa;--m3:#f06050;--m4:#38d9c8;--m5:#c97a3a}
.w{max-width:980px;margin:0 auto;padding:0 1.8rem}
.tb-nav-bar{position:sticky;top:0;z-index:80;background:rgba(11,17,32,.94);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid rgba(75,142,242,0.18);padding:.55rem 1.2rem;display:flex;gap:.6rem;align-items:center;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;flex-wrap:wrap}
.tb-nav-bar .tb-nav-left,.tb-nav-bar .tb-nav-right{display:flex;gap:.55rem;align-items:center;flex-wrap:wrap}
.tb-nav-bar a{color:#8e9bb5;text-decoration:none;border:1px solid rgba(75,142,242,0.18);padding:.32rem .62rem;border-radius:2px;transition:all .2s;white-space:nowrap}
.tb-nav-bar a:hover{color:#6da8ff;border-color:rgba(75,142,242,0.45)}
.tb-nav-bar .tb-nav-counter{color:#6da8ff;font-weight:500}
.tb-nav-bar .tb-nav-archive{color:#cdd6e4;border-color:rgba(75,142,242,0.32)}
header.concept-head{padding:2.8rem 0 1.4rem;border-bottom:1px solid var(--brd);margin-bottom:2rem}
.concept-meta{font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;margin-bottom:.7rem;display:flex;align-items:center;gap:.6rem}
.concept-meta-tag{padding:.18rem .6rem;border-radius:2px;border:1px solid currentColor;font-weight:500}
.concept-name{font-family:'Cormorant Garamond',serif;font-weight:400;font-size:3rem;color:var(--t1);letter-spacing:.012em;line-height:1.05;margin-bottom:.7rem}
.concept-stats{font-family:'JetBrains Mono',monospace;font-size:.65rem;color:var(--t4);letter-spacing:.1em;text-transform:uppercase;display:flex;gap:.6rem;flex-wrap:wrap;align-items:center}
.concept-stats .stat-divider{color:rgba(75,142,242,.3)}
.concept-stats .stat-current{color:var(--blub);font-weight:500}
.sh{font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:400;color:var(--t1);margin-bottom:1rem;padding-bottom:.5rem;border-bottom:1px solid var(--brd)}
section.concept-section{margin-bottom:2.4rem}
.def-block{background:var(--card);border:1px solid var(--brd);border-left:3px solid var(--meta-c);border-radius:3px;padding:1.6rem 1.8rem;line-height:1.8;color:var(--t2);font-size:1rem}
.def-block strong{color:var(--t1);font-weight:600}
.def-block em{font-style:italic;color:var(--t1)}
.def-source{margin-top:1rem;padding-top:.8rem;border-top:1px dashed rgba(75,142,242,.18);font-family:'JetBrains Mono',monospace;font-size:.65rem;letter-spacing:.1em;text-transform:uppercase;color:var(--t4)}
.def-source a{color:var(--blub);text-decoration:none;border-bottom:1px solid rgba(109,168,255,.3)}
.def-source a:hover{border-color:var(--blub)}
.timeline{display:flex;flex-direction:column;gap:.6rem}
.tl-entry{background:var(--card);border:1px solid var(--brd);border-left:2px solid var(--meta-c);border-radius:2px;padding:1rem 1.2rem;transition:border-color .2s}
.tl-entry:hover{border-color:var(--brds);border-left-color:var(--meta-c)}
.tl-entry.naming{border-left-width:3px;background:linear-gradient(90deg,rgba(229,184,76,.04),transparent 30%)}
.tl-entry.naming::before{content:'★ NAMED HERE';font-family:'JetBrains Mono',monospace;font-size:.55rem;letter-spacing:.16em;color:var(--gold);display:block;margin-bottom:.4rem}
.tl-head{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;flex-wrap:wrap;margin-bottom:.5rem}
.tl-date{font-family:'Cormorant Garamond',serif;font-size:1.15rem;color:var(--t1)}
.tl-date .tl-dow{color:var(--t4);font-family:'JetBrains Mono',monospace;font-size:.7rem;letter-spacing:.06em;margin-left:.4rem;text-transform:uppercase}
.tl-num{font-family:'JetBrains Mono',monospace;font-size:.65rem;color:var(--blub);letter-spacing:.08em;text-transform:uppercase}
.tl-thread{font-style:italic;color:var(--t3);font-size:.92rem;margin-bottom:.5rem;line-height:1.5}
.tl-excerpt{color:var(--t2);font-size:.92rem;line-height:1.7;margin:.4rem 0 .7rem}
.tl-link{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;color:var(--blub);border:1px solid var(--brd);padding:.25rem .65rem;border-radius:2px;text-decoration:none;transition:all .2s}
.tl-link:hover{border-color:var(--blub);background:rgba(75,142,242,.06)}
.related-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.6rem}
.related-link{background:var(--card);border:1px solid var(--brd);border-left:2px solid var(--brd);border-radius:2px;padding:.65rem .9rem;text-decoration:none;color:var(--t2);font-size:.88rem;display:flex;justify-content:space-between;align-items:center;gap:.5rem;transition:all .2s}
.related-link:hover{border-color:var(--brds)}
.related-link.m1{border-left-color:var(--m1)}.related-link.m1 strong{color:var(--m1)}
.related-link.m2{border-left-color:var(--m2)}.related-link.m2 strong{color:var(--m2)}
.related-link.m3{border-left-color:var(--m3)}.related-link.m3 strong{color:#fca5a5}
.related-link.m4{border-left-color:var(--m4)}.related-link.m4 strong{color:var(--m4)}
.related-link.m5{border-left-color:var(--m5)}.related-link.m5 strong{color:var(--ambb)}
.related-link strong{font-weight:500;font-family:'JetBrains Mono',monospace;font-size:.78rem;letter-spacing:.02em}
.related-count{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:var(--t4);letter-spacing:.08em}
.no-citations{padding:1.2rem 1.4rem;background:rgba(17,24,39,.55);border:1px dashed var(--brd);border-radius:3px;color:var(--t3);font-style:italic;text-align:center}
.cf-back{display:inline-flex;align-items:center;gap:.4rem;font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--t3);text-decoration:none;border-bottom:1px solid transparent;transition:all .2s;margin-top:2rem}
.cf-back:hover{color:var(--blub);border-color:var(--blub)}
footer{margin-top:3rem;padding:1.5rem 0;border-top:1px solid var(--brd);text-align:center}
footer p{font-family:'JetBrains Mono',monospace;font-size:.6rem;color:var(--t4);letter-spacing:.1em;text-transform:uppercase}
@media(max-width:768px){.w{padding:0 1rem}.concept-name{font-size:2.2rem}.related-grid{grid-template-columns:1fr}}
"""


def render_concept_page(pattern, citations_for_pattern, cross_refs,
                        pattern_by_name, total_briefings):
    name = pattern['name']
    slug = pattern['slug']
    meta = pattern['meta']
    meta_name = pattern['meta_name']
    meta_color = META_COLORS[meta]
    meta_heading_color = META_HEADING_COLORS[meta]
    source_briefing_num = pattern['source_briefing']
    desc = pattern['description']
    citation_count = len(citations_for_pattern)

    # Convert markdown emphasis in description to HTML
    desc_html = desc
    desc_html = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', desc_html)
    desc_html = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', desc_html)
    desc_html = desc_html.replace('\n\n', '</p><p>')
    desc_html = f'<p>{desc_html}</p>'

    # Find the source briefing's date/filename
    source_briefing_link = ''
    source_briefing_date = ''
    for c in citations_for_pattern:
        if int(c['number']) == source_briefing_num:
            source_briefing_link = f'../briefings/{c["filename"]}'
            source_briefing_date = c['display_date']
            break
    # If not found in citations (e.g., briefing missing), try locating directly
    if not source_briefing_link:
        for bf in BRIEFINGS_DIR.glob('2026-*.html'):
            try:
                h = bf.read_text()
                if f'BRIEFING NO. {source_briefing_num:03d}' in h or \
                   f'BRIEFING NO. {source_briefing_num}' in h:
                    source_briefing_link = f'../briefings/{bf.name}'
                    break
            except Exception:
                pass

    # Timeline
    if citations_for_pattern:
        timeline_items = []
        for c in citations_for_pattern:
            naming_class = ' naming' if c.get('is_naming') else ''
            excerpt = escape(c.get('excerpt', '')) or '<em>(no inline excerpt extracted)</em>'
            thread = escape(c.get('thread_title', ''))
            timeline_items.append(f'''
<div class="tl-entry{naming_class}">
<div class="tl-head">
<div class="tl-date">{escape(c.get('display_date',''))}<span class="tl-dow">{escape(c.get('dow',''))}</span></div>
<div class="tl-num">Briefing {escape(c.get('number',''))} · Cycle {c.get('cycle','?')}</div>
</div>
{f'<div class="tl-thread">{thread}</div>' if thread else ''}
<div class="tl-excerpt">{excerpt}</div>
<a class="tl-link" href="../briefings/{escape(c.get('filename',''))}">Open briefing →</a>
</div>''')
        timeline_html = '<div class="timeline">' + ''.join(timeline_items) + '</div>'
    else:
        timeline_html = '<div class="no-citations">No citations found in current briefings.</div>'

    # Related
    related_html = ''
    top_related = cross_refs[name].most_common(10)
    if top_related:
        items = []
        for rel_name, count in top_related:
            if rel_name in pattern_by_name:
                rel_p = pattern_by_name[rel_name]
                items.append(
                    f'<a class="related-link m{rel_p["meta"]}" '
                    f'href="{rel_p["slug"]}.html">'
                    f'<strong>{escape(rel_name)}</strong>'
                    f'<span class="related-count">×{count}</span>'
                    f'</a>'
                )
        if items:
            related_html = (
                '<section class="concept-section">'
                '<h2 class="sh">Co-occurring Concepts</h2>'
                '<div class="related-grid">' + ''.join(items) + '</div>'
                '</section>'
            )

    # Stats
    stats_parts = [
        f'<span>META-{meta} · {escape(meta_name)}</span>',
        f'<span class="stat-divider">·</span>',
        f'<span>Named in Briefing {source_briefing_num:03d}</span>',
    ]
    if source_briefing_date:
        stats_parts.extend([
            '<span class="stat-divider">·</span>',
            f'<span>{escape(source_briefing_date)}</span>',
        ])
    stats_parts.extend([
        '<span class="stat-divider">·</span>',
        f'<span class="stat-current">{citation_count} citations '
        f'across {total_briefings} briefings</span>',
    ])
    stats_html = ''.join(stats_parts)

    title = f'Concept: {name} — Tectonic Briefing'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<meta name="description" content="Structural concept page for {escape(name)} (META-{meta} {escape(meta_name)}) — Tectonic Briefing.">
<style>
{CONCEPT_CSS}
</style>
</head>
<body>
<div class="tb-nav-bar">
<div class="tb-nav-left">
<a href="index.html">← All Concepts</a>
<span class="tb-nav-counter">{escape(name)}</span>
</div>
<div class="tb-nav-right">
<a href="../index.html" class="tb-nav-archive">Briefing Archive</a>
</div>
</div>

<div class="w" style="--meta-c:{meta_color}">

<header class="concept-head">
<div class="concept-meta" style="color:{meta_heading_color}">
<span class="concept-meta-tag">META-{meta}</span>
<span>{escape(meta_name)}</span>
</div>
<h1 class="concept-name">{escape(name)}</h1>
<div class="concept-stats">
{stats_html}
</div>
</header>

<section class="concept-section">
<h2 class="sh">Canonical Definition</h2>
<div class="def-block">
{desc_html}
<div class="def-source">First named in <a href="{source_briefing_link or '#'}">Briefing {source_briefing_num:03d}</a></div>
</div>
</section>

<section class="concept-section">
<h2 class="sh">Citation Timeline</h2>
<p style="color:var(--t3);font-style:italic;margin-bottom:1rem;font-size:.92rem">Every briefing where this pattern is cited in prose. The naming briefing is highlighted.</p>
{timeline_html}
</section>

{related_html}

<a class="cf-back" href="index.html">← Back to all concepts</a>

</div>

<footer>
<p>Tectonic Briefing · Structural Vocabulary · {escape(name)} (META-{meta})</p>
</footer>

</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────
# Concepts index page
# ──────────────────────────────────────────────────────────────────────
def render_concepts_index(patterns, citations, total_briefings):
    by_meta = defaultdict(list)
    for p in patterns:
        by_meta[p['meta']].append(p)

    meta_blocks = []
    for meta_num in sorted(by_meta.keys()):
        meta_name = META_NAMES[meta_num]
        meta_color = META_HEADING_COLORS[meta_num]
        pattern_items = []
        for p in by_meta[meta_num]:
            n_cites = len(citations[p['name']])
            pattern_items.append(f'''
<a class="cidx-item m{meta_num}" href="{p['slug']}.html">
<div class="cidx-name">{escape(p['name'])}</div>
<div class="cidx-brief">{escape(p['brief'])}</div>
<div class="cidx-stats"><span>Briefing {p['source_briefing']:03d}</span><span class="cidx-cites">{n_cites} citations</span></div>
</a>''')
        meta_blocks.append(f'''
<section class="cidx-meta">
<h2 class="cidx-meta-head" style="color:{meta_color}"><span class="cidx-meta-tag">META-{meta_num}</span> {escape(meta_name)}</h2>
<div class="cidx-grid">{''.join(pattern_items)}</div>
</section>''')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Structural Vocabulary — Tectonic Briefing Concepts Index</title>
<meta name="description" content="All {len(patterns)} named structural patterns from the Tectonic Briefing, organized by meta-category.">
<style>
{CONCEPT_CSS}
.cidx-intro{{color:var(--t3);font-style:italic;margin-bottom:2rem;line-height:1.7;font-size:1rem}}
.cidx-meta{{margin-bottom:2.6rem}}
.cidx-meta-head{{font-family:'Cormorant Garamond',serif;font-size:1.45rem;font-weight:500;margin-bottom:.9rem;padding-bottom:.4rem;border-bottom:1px solid var(--brd);display:flex;align-items:center;gap:.7rem}}
.cidx-meta-tag{{font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.14em;padding:.2rem .55rem;border:1px solid currentColor;border-radius:2px;font-weight:500;text-transform:uppercase}}
.cidx-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.7rem}}
.cidx-item{{background:var(--card);border:1px solid var(--brd);border-left:3px solid var(--brd);border-radius:2px;padding:.95rem 1.15rem;text-decoration:none;color:var(--t2);transition:all .2s;display:flex;flex-direction:column;gap:.4rem}}
.cidx-item:hover{{border-color:var(--brds);transform:translateY(-1px)}}
.cidx-item.m1{{border-left-color:var(--m1)}}.cidx-item.m1 .cidx-name{{color:var(--m1)}}
.cidx-item.m2{{border-left-color:var(--m2)}}.cidx-item.m2 .cidx-name{{color:var(--m2)}}
.cidx-item.m3{{border-left-color:var(--m3)}}.cidx-item.m3 .cidx-name{{color:#fca5a5}}
.cidx-item.m4{{border-left-color:var(--m4)}}.cidx-item.m4 .cidx-name{{color:var(--m4)}}
.cidx-item.m5{{border-left-color:var(--m5)}}.cidx-item.m5 .cidx-name{{color:var(--ambb)}}
.cidx-name{{font-family:'JetBrains Mono',monospace;font-size:.78rem;font-weight:500;letter-spacing:.02em}}
.cidx-brief{{color:var(--t3);font-size:.84rem;line-height:1.5}}
.cidx-stats{{display:flex;justify-content:space-between;font-family:'JetBrains Mono',monospace;font-size:.6rem;color:var(--t4);letter-spacing:.08em;text-transform:uppercase;margin-top:auto;padding-top:.4rem;border-top:1px dotted rgba(75,142,242,.1)}}
.cidx-cites{{color:var(--blub)}}
.epi{{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1.04rem;color:var(--t3);margin-top:1rem;max-width:680px;line-height:1.55;padding-left:1rem;border-left:2px solid var(--brds)}}
.epi::first-letter{{font-family:'Cormorant Garamond',serif;font-size:2.6em;font-weight:400;color:var(--blub);float:left;line-height:.92;margin:.1em .12em 0 0;font-style:normal}}
.concept-name{{font-size:2.3rem;letter-spacing:.018em}}
</style>
</head>
<body>
<div class="tb-nav-bar">
<div class="tb-nav-left">
<a href="../index.html">← Briefing Archive</a>
<span class="tb-nav-counter">Structural Vocabulary · {len(patterns)} patterns</span>
</div>
</div>

<div class="w">

<header class="concept-head">
<div class="concept-meta" style="color:var(--blub)">
<span class="concept-meta-tag">Concepts</span>
<span>{len(patterns)} patterns · 5 meta-categories · {total_briefings} briefings indexed</span>
</div>
<h1 class="concept-name">Structural Vocabulary</h1>
<div class="epi">The vocabulary accumulates across briefings. Each named pattern instantiates one of five higher-level meta-categories. Click any pattern to view its canonical definition, citation timeline across briefings, and co-occurring concepts.</div>
</header>

{''.join(meta_blocks)}

<footer>
<p>Tectonic Briefing · Structural Vocabulary Index · {len(patterns)} named patterns</p>
</footer>

</div>

</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────
def main():
    CONCEPTS_DIR.mkdir(exist_ok=True)

    print("Parsing STRUCTURAL_CONCEPTS.md…")
    patterns = parse_structural_concepts()
    pattern_by_name = {p['name']: p for p in patterns}
    print(f"  ✓ Found {len(patterns)} patterns across "
          f"{len(set(p['meta'] for p in patterns))} meta-categories")

    print("Loading briefings…")
    briefings = load_briefings()
    print(f"  ✓ Loaded {len(briefings)} briefings")

    print("Finding citations in briefing prose…")
    citations = find_citations(patterns, briefings)
    total_cites = sum(len(v) for v in citations.values())
    print(f"  ✓ {total_cites} total citations across {len(citations)} patterns")

    print("Computing cross-references…")
    cross_refs = build_cross_references(citations)
    print(f"  ✓ Co-occurrence graph built")

    print("Generating concept pages…")
    for p in patterns:
        page_html = render_concept_page(
            p, citations[p['name']], cross_refs,
            pattern_by_name, len(briefings)
        )
        out = CONCEPTS_DIR / f"{p['slug']}.html"
        out.write_text(page_html)

    # Index
    idx_html = render_concepts_index(patterns, citations, len(briefings))
    (CONCEPTS_DIR / 'index.html').write_text(idx_html)

    # Registry JSON (for badge injector + search)
    registry = {
        'generated_at': datetime.now().isoformat(),
        'total_briefings': len(briefings),
        'patterns': [
            {
                'name': p['name'],
                'slug': p['slug'],
                'meta': p['meta'],
                'meta_name': p['meta_name'],
                'source_briefing': p['source_briefing'],
                'brief': p['brief'],
                'citation_count': len(citations[p['name']]),
            }
            for p in patterns
        ],
    }
    CONCEPT_REGISTRY_JSON.write_text(json.dumps(registry, indent=2))

    # Cross-briefing search index (P2B)
    search_index = {
        'generated_at': datetime.now().isoformat(),
        'briefings': [
            {
                'number': m['number'],
                'date': m['date'],
                'display_date': m['display_date'],
                'dow': m['dow'],
                'title': f"Briefing {m['number']} · {m['display_date']}",
                'thread': m['thread_title'],
                'cycle': m['cycle'],
                'url': f"briefings/{m['filename']}",
            }
            for _, _, m in sorted(
                briefings, key=lambda x: x[2]['date'], reverse=True
            )
        ],
        'concepts': [
            {
                'name': p['name'],
                'slug': p['slug'],
                'meta': p['meta'],
                'meta_name': p['meta_name'],
                'brief': p['brief'],
                'source_briefing': p['source_briefing'],
                'citation_count': len(citations[p['name']]),
                'url': f"concepts/{p['slug']}.html",
            }
            for p in patterns
        ],
    }
    (REPO_DIR / 'search-index.json').write_text(
        json.dumps(search_index, indent=2)
    )

    print(f"\n✓ {len(patterns)} concept pages + index.html generated in {CONCEPTS_DIR}")
    print(f"✓ Registry JSON: {CONCEPT_REGISTRY_JSON}")
    print(f"✓ Search index: {REPO_DIR / 'search-index.json'} "
          f"({len(search_index['briefings'])} briefings, "
          f"{len(search_index['concepts'])} concepts)")


if __name__ == '__main__':
    main()
