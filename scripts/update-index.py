#!/usr/bin/env python3
"""
Tectonic Briefing — Index Updater + Per-Day Nav Wrapper

Two-phase regenerator:
  1. Rewrites index.html as a hero landing page surfacing today's briefing
     (date, unifying thread, top deep-dive titles, vocabulary status,
     liminal highlight, CTA) plus a Cycle 2 status panel plus a grouped,
     filterable archive of every briefing.
  2. Idempotently injects a top-of-page and bottom-of-page navigation
     wrapper (prev/next briefing, archive link, view on GitHub) into
     every per-day briefing file. Body content of the per-day briefings
     is NEVER touched — only HTML inside well-delimited
     <!-- TB-NAV-WRAP --> markers.

Usage: python3 scripts/update-index.py
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
BRIEFINGS_DIR = REPO_DIR / "briefings"
INDEX_FILE = REPO_DIR / "index.html"

GITHUB_BASE = "https://github.com/cyborg-entrepreneur/tectonic-briefing/blob/main/briefings"

# ──────────────────────────────────────────────────────────────────────
# Cycle boundary: briefings 001-030 are Cycle 1, 031+ are Cycle 2.
# (Documented in CLAUDE.md / STRUCTURAL_CONCEPTS.md.)
# ──────────────────────────────────────────────────────────────────────
CYCLE2_THRESHOLD = 31


# ──────────────────────────────────────────────────────────────────────
# Metadata extraction
# ──────────────────────────────────────────────────────────────────────
def extract_metadata(filepath):
    """Extract briefing metadata from HTML file.

    Critically, we strip any previously-injected TB-NAV-WRAP blocks before
    running regex extraction so that the script is fully idempotent — if the
    previous run injected wrappers that themselves contain "Briefing No. NNN"
    text, those must not leak back into metadata extraction.
    """
    content = filepath.read_text(encoding='utf-8')

    # Remove our own injected nav blocks before extracting metadata.
    content = re.sub(
        rf'{re.escape(NAV_TOP_MARK_START)}.*?{re.escape(NAV_TOP_MARK_END)}\s*',
        '', content, flags=re.DOTALL)
    content = re.sub(
        rf'{re.escape(NAV_BOT_MARK_START)}.*?{re.escape(NAV_BOT_MARK_END)}\s*',
        '', content, flags=re.DOTALL)
    content = re.sub(
        rf'{re.escape(NAV_STYLE_MARK)}.*?{re.escape(NAV_STYLE_MARK)}\s*',
        '', content, flags=re.DOTALL)

    meta = {
        'filename': filepath.name,
        'date_str': filepath.stem,            # YYYY-MM-DD
        'number': '???',
        'number_int': 0,
        'display_date': filepath.stem,
        'day_of_week': '',
        'tagline': '',
        'unifying_thread_title': '',
        'unifying_thread_excerpt': '',
        'deep_dive_titles': [],
        'vocab_status': '',
        'liminal_highlight': '',
        'cycle': 1,
        'cycle_day': None,
        'tags': [],
        'lenses': [],
    }

    # Briefing number — target the canonical <div class="bn"> block to avoid
    # being tripped by in-body cross-references like "See Briefing No. 039..."
    # added in errata. Fall back to a permissive search if the bn block is absent.
    num_match = re.search(
        r'class="bn"[^>]*>\s*BRIEFING NO\.\s*(\d+)', content, re.IGNORECASE)
    if not num_match:
        num_match = re.search(r'BRIEFING NO\.\s*(\d+)', content, re.IGNORECASE)
    if num_match:
        meta['number'] = num_match.group(1).zfill(3)
        meta['number_int'] = int(num_match.group(1))
        meta['cycle'] = 2 if meta['number_int'] >= CYCLE2_THRESHOLD else 1

    # Cycle / Day marker (e.g., "CYCLE 2 · DAY 9")
    cycle_day = re.search(r'CYCLE\s*(\d+)\s*(?:&middot;|·)\s*DAY\s*(\d+)',
                          content, re.IGNORECASE)
    if cycle_day:
        meta['cycle'] = int(cycle_day.group(1))
        meta['cycle_day'] = int(cycle_day.group(2))

    # Display date from .bd class
    date_match = re.search(r'class="bd"[^>]*>([^<]+)<', content)
    if date_match:
        raw = date_match.group(1).strip()
        meta['display_date'] = raw
        # Try to extract day-of-week if present after a middot
        dow = re.search(r'(?:&middot;|·)\s*(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)',
                        raw)
        if dow:
            meta['day_of_week'] = dow.group(1)
    # Derive day-of-week from filename if not surfaced in .bd
    if not meta['day_of_week']:
        try:
            dt = datetime.strptime(meta['date_str'], '%Y-%m-%d')
            meta['day_of_week'] = dt.strftime('%A')
        except ValueError:
            pass

    # Tagline (the .bt block — typically the unifying-thread paragraph at top)
    tag_match = re.search(r'class="bt"[^>]*>(.*?)</div>', content, re.DOTALL)
    if tag_match:
        raw = tag_match.group(1)
        # Strip inner tags for the short tagline preview
        stripped = re.sub(r'<[^>]+>', '', raw).strip()
        meta['tagline'] = stripped

    # Unifying Thread (.th block — bold structural framing of the day)
    th_match = re.search(
        r'<div class="th"[^>]*>\s*<h3>([^<]+(?:<[^/][^>]*>[^<]*</[^>]+>[^<]*)*)</h3>(.*?)</div>\s*(?:<h3 class="sh2"|<!--)',
        content, re.DOTALL)
    if th_match:
        meta['unifying_thread_title'] = re.sub(r'<[^>]+>', '',
                                               th_match.group(1)).strip()
        # First two paragraphs of the unifying-thread body
        body = th_match.group(2)
        paras = re.findall(r'<p[^>]*>(.*?)</p>', body, re.DOTALL)
        excerpt_parts = []
        for p in paras[:2]:
            txt = re.sub(r'<[^>]+>', '', p).strip()
            if txt:
                excerpt_parts.append(txt)
        meta['unifying_thread_excerpt'] = '\n\n'.join(excerpt_parts)

    # Deep dive titles (inside .dd-panel > h4)
    dd_titles = re.findall(
        r'<div class="dd-panel">\s*(?:<div class="dd-label">[^<]*</div>\s*)?<h4>([^<]+)</h4>',
        content)
    meta['deep_dive_titles'] = [t.strip() for t in dd_titles[:6]]

    # Vocabulary status — look for "N named patterns" text
    vocab_match = re.search(r'(\d+)\s+named\s+patterns?', content, re.IGNORECASE)
    if vocab_match:
        n = vocab_match.group(1)
        # Cycle 2 candidate pool count if present
        candidates_match = re.search(
            r'Cycle 2 candidate pool[:\s]*(\d+)', content, re.IGNORECASE)
        if candidates_match:
            meta['vocab_status'] = (f"{n} named patterns + "
                                    f"{candidates_match.group(1)} Cycle 2 candidates")
        else:
            meta['vocab_status'] = f"{n} named patterns"

    # Liminal Signals highlight (first <h3> inside #s-li section)
    lim_match = re.search(
        r'id="s-li".*?<div class="c[^"]*"[^>]*>.*?<h3[^>]*>([^<]+)',
        content, re.DOTALL)
    if lim_match:
        meta['liminal_highlight'] = re.sub(r'<[^>]+>', '',
                                           lim_match.group(1)).strip()

    # Lenses (which analytical surfaces are active)
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


# ──────────────────────────────────────────────────────────────────────
# Per-day navigation wrapper (idempotent)
# ──────────────────────────────────────────────────────────────────────
NAV_TOP_MARK_START = "<!-- TB-NAV-WRAP:TOP:START -->"
NAV_TOP_MARK_END = "<!-- TB-NAV-WRAP:TOP:END -->"
NAV_BOT_MARK_START = "<!-- TB-NAV-WRAP:BOT:START -->"
NAV_BOT_MARK_END = "<!-- TB-NAV-WRAP:BOT:END -->"
NAV_STYLE_MARK = "<!-- TB-NAV-WRAP:STYLE -->"

NAV_CSS = """
/* Tectonic Briefing site-wide nav wrapper (injected by update-index.py) */
.tb-nav-bar{position:sticky;top:0;z-index:80;background:rgba(11,17,32,.94);
  backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);
  border-bottom:1px solid rgba(75,142,242,0.18);padding:.55rem 1.2rem;
  display:flex;gap:.6rem;align-items:center;justify-content:space-between;
  font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.1em;
  text-transform:uppercase;flex-wrap:wrap}
.tb-nav-bar .tb-nav-left,.tb-nav-bar .tb-nav-right{display:flex;gap:.55rem;align-items:center;flex-wrap:wrap}
.tb-nav-bar a{color:#8e9bb5;text-decoration:none;border:1px solid rgba(75,142,242,0.18);
  padding:.32rem .62rem;border-radius:2px;transition:all .2s;white-space:nowrap}
.tb-nav-bar a:hover{color:#6da8ff;border-color:rgba(75,142,242,0.45)}
.tb-nav-bar .tb-nav-disabled{color:#5f6d87;border-color:rgba(75,142,242,0.08);pointer-events:none;opacity:.55}
.tb-nav-bar .tb-nav-counter{color:#6da8ff;font-weight:500}
.tb-nav-bar .tb-nav-archive{color:#cdd6e4;border-color:rgba(75,142,242,0.32)}
.tb-nav-foot{margin-top:2rem;padding:1.4rem 1.6rem;border:1px solid rgba(75,142,242,0.18);
  border-radius:3px;display:flex;gap:.6rem;align-items:center;justify-content:space-between;
  background:#111827;font-family:'JetBrains Mono',monospace;font-size:.62rem;
  letter-spacing:.1em;text-transform:uppercase;flex-wrap:wrap}
.tb-nav-foot .tb-nav-left,.tb-nav-foot .tb-nav-right{display:flex;gap:.55rem;align-items:center;flex-wrap:wrap}
.tb-nav-foot a{color:#8e9bb5;text-decoration:none;border:1px solid rgba(75,142,242,0.18);
  padding:.32rem .62rem;border-radius:2px;transition:all .2s;white-space:nowrap}
.tb-nav-foot a:hover{color:#6da8ff;border-color:rgba(75,142,242,0.45)}
.tb-nav-foot .tb-nav-disabled{color:#5f6d87;border-color:rgba(75,142,242,0.08);pointer-events:none;opacity:.55}
.tb-site-foot{margin-top:1.4rem;padding:1.2rem 0;text-align:center;
  font-family:'JetBrains Mono',monospace;font-size:.55rem;color:#5f6d87;
  letter-spacing:.12em;text-transform:uppercase}
.tb-site-foot a{color:#8e9bb5;text-decoration:none;border-bottom:1px solid rgba(75,142,242,0.18)}
.tb-site-foot a:hover{color:#6da8ff;border-color:#6da8ff}
@media(max-width:560px){
  .tb-nav-bar{font-size:.55rem;padding:.45rem .7rem}
  .tb-nav-bar a{padding:.28rem .5rem}
  .tb-nav-foot{font-size:.55rem;padding:1.1rem 1rem}
}
"""


def build_top_nav(meta, prev_meta, next_meta):
    prev_href = (f'<a href="{prev_meta["filename"]}" '
                 f'title="Briefing No. {prev_meta["number"]} · {prev_meta["display_date"]}">'
                 f'← Prev</a>') if prev_meta else \
        '<a class="tb-nav-disabled">← Prev</a>'
    next_href = (f'<a href="{next_meta["filename"]}" '
                 f'title="Briefing No. {next_meta["number"]} · {next_meta["display_date"]}">'
                 f'Next →</a>') if next_meta else \
        '<a class="tb-nav-disabled">Next →</a>'
    counter = (f'<span class="tb-nav-counter">Briefing No. {meta["number"]}'
               + (f' · Cycle {meta["cycle"]} · Day {meta["cycle_day"]}'
                  if meta["cycle_day"] else '')
               + '</span>')
    archive = '<a href="../index.html" class="tb-nav-archive">Archive</a>'
    return (f'{NAV_TOP_MARK_START}\n'
            f'<div class="tb-nav-bar">'
            f'<div class="tb-nav-left">{prev_href}{counter}{next_href}</div>'
            f'<div class="tb-nav-right">{archive}</div>'
            f'</div>\n'
            f'{NAV_TOP_MARK_END}')


def build_bot_nav(meta, prev_meta, next_meta):
    prev_href = (f'<a href="{prev_meta["filename"]}">'
                 f'← Briefing No. {prev_meta["number"]}</a>') if prev_meta else \
        '<a class="tb-nav-disabled">← Prev</a>'
    next_href = (f'<a href="{next_meta["filename"]}">'
                 f'Briefing No. {next_meta["number"]} →</a>') if next_meta else \
        '<a class="tb-nav-disabled">Next →</a>'
    archive = '<a href="../index.html">Archive</a>'
    github = (f'<a href="{GITHUB_BASE}/{meta["filename"]}" '
              f'target="_blank" rel="noopener">View on GitHub</a>')
    foot = ('<div class="tb-site-foot">'
            f'Tectonic Briefing No. {meta["number"]} · {meta["display_date"]} · '
            'Cyborg Entrepreneurship Research Lab · '
            '<a href="../index.html">Return to archive</a>'
            '</div>')
    return (f'{NAV_BOT_MARK_START}\n'
            f'<div class="tb-nav-foot">'
            f'<div class="tb-nav-left">{prev_href}{next_href}</div>'
            f'<div class="tb-nav-right">{archive}{github}</div>'
            f'</div>\n'
            f'{foot}\n'
            f'{NAV_BOT_MARK_END}')


def inject_per_day_nav(filepath, meta, prev_meta, next_meta):
    """Idempotently inject top + bottom nav wrappers + nav CSS into a per-day file."""
    content = filepath.read_text(encoding='utf-8')
    original_len = len(content)

    # Strip any previous TB-NAV-WRAP markers (so we re-emit cleanly).
    content = re.sub(
        rf'{re.escape(NAV_TOP_MARK_START)}.*?{re.escape(NAV_TOP_MARK_END)}\s*',
        '', content, flags=re.DOTALL)
    content = re.sub(
        rf'{re.escape(NAV_BOT_MARK_START)}.*?{re.escape(NAV_BOT_MARK_END)}\s*',
        '', content, flags=re.DOTALL)
    # Strip the previous CSS block if present.
    content = re.sub(
        rf'{re.escape(NAV_STYLE_MARK)}.*?{re.escape(NAV_STYLE_MARK)}\s*',
        '', content, flags=re.DOTALL)

    # Inject CSS just before </style>. If no style block, skip silently.
    style_block = f'{NAV_STYLE_MARK}{NAV_CSS}{NAV_STYLE_MARK}\n'
    if '</style>' in content:
        content = content.replace('</style>', style_block + '</style>', 1)

    # Inject top nav directly after <body ...>
    top_nav_html = build_top_nav(meta, prev_meta, next_meta)
    body_match = re.search(r'<body[^>]*>', content)
    if body_match:
        insert_pos = body_match.end()
        content = (content[:insert_pos] + '\n' + top_nav_html + '\n'
                   + content[insert_pos:])

    # Inject bottom nav directly before </body>
    bot_nav_html = build_bot_nav(meta, prev_meta, next_meta)
    if '</body>' in content:
        content = content.replace('</body>', bot_nav_html + '\n</body>', 1)

    filepath.write_text(content, encoding='utf-8')
    return len(content) - original_len


# ──────────────────────────────────────────────────────────────────────
# Landing page (index.html) generator
# ──────────────────────────────────────────────────────────────────────
INDEX_HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tectonic Briefing — Daily Structural Analysis</title>
<meta name="description" content="Daily structural analysis of geopolitical, technological, economic, scientific, social, ecological, institutional, and liminal forces — Cyborg Entrepreneurship Research Lab.">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;0,700;1,300;1,400&family=JetBrains+Mono:wght@300;400;500&family=Source+Sans+3:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
html,body{background-color:#0b1120!important;color:#d4dce8;font-family:'Source Sans 3',system-ui,sans-serif;font-size:16px;line-height:1.7;min-height:100vh}
:root{--bg:#0b1120;--card:#111827;--alt:#141c2e;--str:#162035;--blu:#4b8ef2;--blub:#6da8ff;--blup:#a3c8ff;--teal:#38d9c8;--gold:#e5b84c;--red:#f06050;--purp:#a78bfa;--grn:#4ade80;--amb:#c89545;--ambb:#dcb267;--ambp:#ecca8e;--t1:#eaf0f8;--t2:#cdd6e4;--t3:#8e9bb5;--t4:#5f6d87;--brd:rgba(75,142,242,0.18);--brds:rgba(75,142,242,0.35);--brdg:rgba(229,184,76,0.32)}
.w{max-width:980px;margin:0 auto;padding:0 1.6rem}

/* Site header */
.site-head{padding:2.6rem 0 1.4rem;border-bottom:1px solid var(--brd);margin-bottom:2rem}
.site-head h1{font-family:'Cormorant Garamond',serif;font-weight:300;font-size:2.7rem;color:var(--t1);letter-spacing:.025em;line-height:1.1}
.site-head h1 em{font-style:normal;color:var(--blub);font-weight:500}
.site-head .sub{font-family:'JetBrains Mono',monospace;font-size:.7rem;color:var(--t4);letter-spacing:.14em;text-transform:uppercase;margin-top:.5rem;display:flex;gap:.65rem;flex-wrap:wrap;align-items:center}
.site-head .sub .badge{display:inline-block;border:1px solid var(--brds);color:var(--blub);padding:.16rem .55rem;border-radius:2px;font-size:.6rem;letter-spacing:.08em}
.site-head .epi{font-family:'Cormorant Garamond',serif;font-style:italic;font-size:1rem;color:var(--t3);margin-top:1rem;max-width:680px;line-height:1.55;padding-left:1rem;border-left:2px solid var(--brds)}

/* HERO — today's briefing */
.hero{background:linear-gradient(135deg,rgba(75,142,242,0.06),rgba(167,139,250,0.05));border:1px solid var(--brds);border-radius:4px;padding:2rem 2.1rem;margin-bottom:2.6rem;position:relative;overflow:hidden}
.hero::before{content:'';position:absolute;top:0;right:0;width:160px;height:160px;background:radial-gradient(circle at top right,rgba(109,168,255,0.10),transparent 70%);pointer-events:none}
.hero .hero-eyebrow{font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.16em;text-transform:uppercase;color:var(--blub);display:flex;gap:.55rem;flex-wrap:wrap;align-items:center;margin-bottom:.55rem}
.hero .hero-eyebrow .dot{width:6px;height:6px;border-radius:50%;background:var(--blub);animation:pulse 2.4s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:.4}50%{opacity:1}}
.hero h2.hero-date{font-family:'Cormorant Garamond',serif;font-weight:400;font-size:2.1rem;color:var(--t1);margin-bottom:.5rem;line-height:1.2;letter-spacing:.01em}
.hero .hero-thread-title{font-family:'Cormorant Garamond',serif;font-weight:500;font-size:1.3rem;color:var(--blup);margin-bottom:1rem;line-height:1.35}
.hero .hero-thread-excerpt{color:var(--t2);font-size:1rem;line-height:1.7;max-width:760px;margin-bottom:1.4rem}
.hero .hero-thread-excerpt p{margin-bottom:.8rem}
.hero .hero-thread-excerpt p:last-child{margin-bottom:0}

.hero-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.4rem;margin:1.4rem 0}
.hero-grid .hero-block{background:rgba(11,17,32,0.55);border:1px solid var(--brd);border-radius:3px;padding:1rem 1.2rem}
.hero-grid .hero-block h4{font-family:'JetBrains Mono',monospace;font-size:.58rem;letter-spacing:.14em;text-transform:uppercase;color:var(--t4);margin-bottom:.55rem}
.hero-grid .hero-block ul{list-style:none;padding:0;margin:0}
.hero-grid .hero-block li{color:var(--t2);font-size:.92rem;line-height:1.5;padding:.3rem 0;border-bottom:1px dotted rgba(75,142,242,0.10)}
.hero-grid .hero-block li:last-child{border-bottom:none}
.hero-grid .hero-block .vocab-num{font-family:'Cormorant Garamond',serif;font-size:1.8rem;color:var(--blub);font-weight:500;display:block;line-height:1.1}
.hero-grid .hero-block .vocab-sub{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:var(--t3);letter-spacing:.06em;margin-top:.25rem;text-transform:uppercase}
.hero-grid .hero-block .liminal{color:var(--gold);font-size:.92rem;line-height:1.55;font-style:italic}
/* Vocabulary growth sparkline */
.vocab-spark{display:block;width:100%;height:48px;margin-top:.7rem;overflow:visible}
.vocab-spark .spark-line{fill:none;stroke:var(--blub);stroke-width:1.4;stroke-linejoin:round;stroke-linecap:round}
.vocab-spark .spark-area{fill:url(#sparkGrad);opacity:.65}
.vocab-spark .spark-axis{stroke:rgba(75,142,242,0.12);stroke-width:.5}
.vocab-spark .spark-cycle{stroke:rgba(229,184,76,0.35);stroke-width:.6;stroke-dasharray:2 2}
.vocab-spark .spark-current{fill:var(--gold);stroke:rgba(11,17,32,.9);stroke-width:1.2}
.vocab-spark .spark-current-pulse{fill:none;stroke:var(--gold);stroke-width:1;opacity:.5;animation:sparkPulse 2.2s ease-out infinite}
@keyframes sparkPulse{0%{r:3;opacity:.5}100%{r:9;opacity:0}}
.vocab-spark-label{font-family:'JetBrains Mono',monospace;font-size:.5rem;color:var(--t4);letter-spacing:.1em;text-transform:uppercase;margin-top:.3rem;display:flex;justify-content:space-between}
/* Drop cap on epigraph */
.site-head .epi::first-letter{font-family:'Cormorant Garamond',serif;font-size:2.6em;font-weight:400;color:var(--blub);float:left;line-height:.92;margin:.1em .12em 0 0;font-style:normal}

.hero-cta{display:inline-block;margin-top:.6rem;padding:.8rem 1.5rem;background:var(--blu);color:#fff;text-decoration:none;font-family:'JetBrains Mono',monospace;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;border-radius:3px;transition:all .25s;border:1px solid var(--blu)}
.hero-cta:hover{background:var(--blub);border-color:var(--blub);transform:translateX(2px)}

/* Stats bar */
.stats{display:flex;gap:1.8rem;margin:0 0 2.2rem;flex-wrap:wrap;padding-bottom:1.4rem;border-bottom:1px solid var(--brd)}
.stat{text-align:left}
.stat-num{font-family:'Cormorant Garamond',serif;font-size:2.1rem;color:var(--blub);font-weight:500;line-height:1.05}
.stat-num.amber{color:var(--ambb)}
.stat-num.gold{color:var(--gold)}
.stat-label{font-family:'JetBrains Mono',monospace;font-size:.58rem;color:var(--t4);letter-spacing:.12em;text-transform:uppercase;margin-top:.2rem}

/* Cycle 2 status panel */
.cycle-panel{background:var(--card);border:1px solid var(--brdg);border-radius:3px;padding:1.6rem 1.8rem;margin-bottom:2.6rem}
.cycle-panel h2{font-family:'Cormorant Garamond',serif;font-weight:400;font-size:1.55rem;color:var(--ambb);margin-bottom:.5rem}
.cycle-panel .cycle-sub{font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--t4);margin-bottom:1rem}
.cycle-panel p{color:var(--t2);font-size:.94rem;line-height:1.65;margin-bottom:.9rem}
.cycle-panel p:last-child{margin-bottom:0}
.cycle-panel .meta-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:.6rem;margin:1rem 0 .8rem}
.cycle-panel .meta-tile{background:rgba(11,17,32,0.55);border:1px solid var(--brd);border-radius:2px;padding:.7rem .9rem}
.cycle-panel .meta-tile .mt-tag{font-family:'JetBrains Mono',monospace;font-size:.54rem;color:var(--ambb);letter-spacing:.12em;text-transform:uppercase;margin-bottom:.3rem}
.cycle-panel .meta-tile .mt-name{color:var(--t1);font-size:.92rem;font-weight:500}
.cycle-panel .candidate-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.5rem;margin-top:.8rem}
.cycle-panel .candidate{background:rgba(229,184,76,0.05);border:1px solid var(--brdg);border-radius:2px;padding:.55rem .8rem;font-size:.82rem;color:var(--t2)}
.cycle-panel .candidate strong{color:var(--gold);font-family:'JetBrains Mono',monospace;font-size:.7rem;letter-spacing:.04em;display:block;margin-bottom:.15rem}

/* Section heading */
.sh2{font-family:'Cormorant Garamond',serif;font-size:1.55rem;font-weight:400;color:var(--t1);margin:0 0 .4rem;padding-bottom:.4rem;border-bottom:1px solid var(--brd)}
.sh2-sub{font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--t4);margin-bottom:1.2rem}

/* Archive filters */
.filter-bar{display:flex;gap:.45rem;align-items:center;flex-wrap:wrap;margin-bottom:1.2rem;padding:.7rem .9rem;background:rgba(17,24,39,0.55);border:1px solid var(--brd);border-radius:3px}
.filter-bar .fl-label{font-family:'JetBrains Mono',monospace;font-size:.58rem;color:var(--t4);letter-spacing:.12em;text-transform:uppercase;margin-right:.3rem}
.filter-bar button{font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.08em;text-transform:uppercase;padding:.32rem .62rem;border:1px solid var(--brd);border-radius:2px;background:transparent;color:var(--t3);cursor:pointer;transition:all .2s}
.filter-bar button:hover{border-color:var(--brds);color:var(--blup)}
.filter-bar button.active{border-color:var(--blu);color:var(--blub);background:rgba(75,142,242,.06)}
.filter-bar button.gold.active{border-color:var(--gold);color:var(--gold);background:rgba(229,184,76,.05)}
.filter-bar button.amb.active{border-color:var(--amb);color:var(--ambb);background:rgba(200,149,69,.06)}

/* Archive grouping */
.month-group{margin-bottom:1.4rem}
.month-group h3{font-family:'Cormorant Garamond',serif;font-size:1.15rem;color:var(--blub);font-weight:500;letter-spacing:.02em;margin:1.2rem 0 .6rem;padding-bottom:.3rem;border-bottom:1px dashed rgba(75,142,242,.18)}
.month-group h3 .count{font-family:'JetBrains Mono',monospace;font-size:.6rem;color:var(--t4);letter-spacing:.1em;margin-left:.5rem;text-transform:uppercase}

/* Briefing entries */
.entry{background-color:var(--card);border:1px solid var(--brd);border-radius:3px;padding:1rem 1.3rem;margin-bottom:.6rem;text-decoration:none;display:grid;grid-template-columns:90px 1fr auto;gap:1.1rem;align-items:center;transition:all .2s}
.entry:hover{border-color:var(--brds);transform:translateX(3px)}
.entry-num-cell{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:var(--t4);letter-spacing:.08em;text-transform:uppercase;line-height:1.3}
.entry-num-cell strong{display:block;color:var(--blub);font-size:.78rem;font-weight:500}
.entry-num-cell .entry-cycle2{color:var(--gold)}
.entry-body{min-width:0}
.entry-date{font-family:'Cormorant Garamond',serif;font-size:1.18rem;color:var(--t1);line-height:1.25;margin-bottom:.22rem}
.entry-date .dow{color:var(--t4);font-size:.85rem;font-family:'JetBrains Mono',monospace;letter-spacing:.06em;margin-left:.45rem;text-transform:uppercase}
.entry-tagline{color:var(--t3);font-size:.85rem;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.entry-arrow{font-family:'JetBrains Mono',monospace;font-size:.8rem;color:var(--t4);transition:all .2s}
.entry:hover .entry-arrow{color:var(--blub);transform:translateX(3px)}
.entry.cycle2{border-left:2px solid var(--brdg)}

/* Contingency Audits */
.audit-card{background:rgba(200,149,69,0.04);border:1px solid rgba(200,149,69,0.22);border-left:3px solid var(--amb);padding:1.1rem 1.4rem;border-radius:3px;margin-bottom:.8rem;text-decoration:none;display:block;transition:all .2s}
.audit-card:hover{border-color:rgba(200,149,69,0.45);transform:translateX(3px)}
.audit-card .audit-num{font-family:'JetBrains Mono',monospace;font-size:.6rem;color:var(--ambb);letter-spacing:.1em;text-transform:uppercase;margin-bottom:.2rem}
.audit-card .audit-title{font-family:'Cormorant Garamond',serif;font-size:1.05rem;color:var(--ambp);margin-bottom:.3rem}
.audit-card .audit-blurb{color:var(--t3);font-size:.85rem;line-height:1.5}

/* Site footer */
.site-foot{margin-top:3.4rem;padding:1.6rem 0;border-top:1px solid var(--brd);text-align:center}
.site-foot p{font-family:'JetBrains Mono',monospace;font-size:.58rem;color:var(--t4);letter-spacing:.11em;text-transform:uppercase;margin-bottom:.35rem}
.site-foot a{color:var(--t3);text-decoration:none;border-bottom:1px solid rgba(75,142,242,.18)}
.site-foot a:hover{color:var(--blub);border-color:var(--blub)}

@media(max-width:760px){
  .w{padding:0 1rem}
  .site-head h1{font-size:2.1rem}
  .hero{padding:1.3rem 1.2rem}
  .hero h2.hero-date{font-size:1.6rem}
  .hero .hero-thread-title{font-size:1.05rem}
  .hero-grid{grid-template-columns:1fr;gap:.9rem}
  .stats{gap:1rem}
  .stat-num{font-size:1.6rem}
  .cycle-panel{padding:1.2rem 1.1rem}
  .entry{grid-template-columns:74px 1fr;gap:.7rem;padding:.85rem 1rem}
  .entry-arrow{display:none}
  .entry-date{font-size:1.02rem}
  .entry-tagline{font-size:.8rem;-webkit-line-clamp:3}
}
@media(max-width:420px){
  .site-head h1{font-size:1.75rem}
  .hero h2.hero-date{font-size:1.4rem}
}

/* P2B — Cmd+K search modal */
.cmdk-modal{position:fixed;inset:0;z-index:200;display:none;align-items:flex-start;justify-content:center;padding-top:12vh}
.cmdk-modal.open{display:flex}
.cmdk-backdrop{position:absolute;inset:0;background:rgba(11,17,32,0.85);backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px)}
.cmdk-panel{position:relative;width:min(680px,92vw);max-height:75vh;background:var(--card);border:1px solid var(--brds);border-radius:6px;box-shadow:0 24px 60px rgba(0,0,0,0.5);display:flex;flex-direction:column;animation:cmdkIn .18s ease;overflow:hidden}
@keyframes cmdkIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}
.cmdk-header{display:flex;align-items:center;gap:.6rem;padding:.85rem 1.1rem;border-bottom:1px solid var(--brd)}
.cmdk-input{flex:1;background:transparent;border:none;outline:none;color:var(--t1);font-family:'Source Sans 3',system-ui,sans-serif;font-size:1.05rem;padding:.2rem 0}
.cmdk-input::placeholder{color:var(--t4);font-style:italic}
.cmdk-hint{font-family:'JetBrains Mono',monospace;font-size:.55rem;color:var(--t4);letter-spacing:.12em;text-transform:uppercase}
.cmdk-results{flex:1;overflow-y:auto;padding:.4rem 0;max-height:55vh}
.cmdk-result{display:flex;align-items:flex-start;gap:.8rem;padding:.55rem 1.1rem;cursor:pointer;text-decoration:none;color:inherit;border-left:2px solid transparent;transition:all .12s}
.cmdk-result:hover,.cmdk-result.sel{background:rgba(75,142,242,0.08);border-left-color:var(--blu)}
.cmdk-result-type{font-family:'JetBrains Mono',monospace;font-size:.55rem;color:var(--t4);letter-spacing:.1em;text-transform:uppercase;padding-top:.18rem;min-width:60px;flex-shrink:0}
.cmdk-result-type.concept{color:var(--gold)}
.cmdk-result-body{flex:1;min-width:0}
.cmdk-result-title{font-family:'Cormorant Garamond',serif;font-size:1.02rem;color:var(--t1);line-height:1.3;margin-bottom:.18rem}
.cmdk-result-sub{font-size:.78rem;color:var(--t3);line-height:1.4;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.cmdk-result-meta{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.52rem;color:var(--blub);letter-spacing:.08em;margin-right:.4rem;text-transform:uppercase}
.cmdk-result-meta.m1{color:#a3c8ff}.cmdk-result-meta.m2{color:var(--purp)}.cmdk-result-meta.m3{color:#fca5a5}.cmdk-result-meta.m4{color:var(--teal)}.cmdk-result-meta.m5{color:var(--ambb)}
.cmdk-empty{padding:1.4rem;color:var(--t4);text-align:center;font-style:italic;font-size:.9rem}
.cmdk-footer{padding:.5rem 1.1rem;border-top:1px solid var(--brd);display:flex;gap:1rem;font-family:'JetBrains Mono',monospace;font-size:.55rem;color:var(--t4);letter-spacing:.1em;text-transform:uppercase;align-items:center}
.cmdk-counts{margin-left:auto;color:var(--blub)}
.cmdk-trigger{font-family:'JetBrains Mono',monospace;font-size:.58rem;letter-spacing:.1em;text-transform:uppercase;padding:.35rem .7rem;border:1px solid var(--brd);border-radius:2px;color:var(--t3);cursor:pointer;background:transparent;transition:all .2s;display:inline-flex;align-items:center;gap:.45rem}
.cmdk-trigger:hover{border-color:var(--brds);color:var(--blub)}
.cmdk-kbd{font-family:'JetBrains Mono',monospace;font-size:.5rem;padding:.1rem .35rem;border:1px solid rgba(75,142,242,.32);border-radius:2px;color:var(--t4);background:rgba(75,142,242,.04)}
@media(max-width:560px){.cmdk-trigger .cmdk-kbd-label{display:none}}
</style>
</head>
<body>
<div class="w">

<header class="site-head">
<h1><em>Tectonic</em> Briefing</h1>
<div class="sub">
  <span>Structural forces · Inference engine · Wise action</span>
  <span class="badge">{{ARCHIVE_COUNT}} briefings</span>
  <button class="cmdk-trigger" onclick="cmdkOpen()" aria-label="Open search">
    <span class="cmdk-kbd-label">Search</span>
    <span class="cmdk-kbd">⌘K</span>
  </button>
</div>
<div class="epi">"We soon observe that little or nothing is really fixed but all is a perpetual flux." — Frank Knight (1913)</div>
</header>
"""

INDEX_FOOT = """
<footer class="site-foot">
<p>Tectonic Briefing · Cyborg Entrepreneurship Research Lab · A collaborative structural analysis</p>
<p><a href="https://github.com/cyborg-entrepreneur/tectonic-briefing">Source on GitHub</a></p>
</footer>

</div>

<!-- Cmd+K search modal -->
<div class="cmdk-modal" id="cmdkModal" hidden aria-hidden="true">
  <div class="cmdk-backdrop" onclick="cmdkClose()"></div>
  <div class="cmdk-panel" role="dialog" aria-label="Search briefings and concepts">
    <div class="cmdk-header">
      <input type="text" id="cmdkInput" class="cmdk-input"
             placeholder="Search briefings, concepts, dates…"
             autocomplete="off" spellcheck="false">
      <span class="cmdk-hint"><span class="cmdk-kbd">ESC</span> close</span>
    </div>
    <div class="cmdk-results" id="cmdkResults" role="listbox"></div>
    <div class="cmdk-footer">
      <span><span class="cmdk-kbd">↑↓</span> navigate</span>
      <span><span class="cmdk-kbd">↵</span> open</span>
      <span class="cmdk-counts" id="cmdkCounts"></span>
    </div>
  </div>
</div>

<script>
function applyFilter(group){
  var entries = document.querySelectorAll('.entry, .month-group');
  document.querySelectorAll('.filter-bar button').forEach(function(b){b.classList.remove('active');});
  document.querySelector('.filter-bar button[data-filter="'+group+'"]').classList.add('active');
  document.querySelectorAll('.entry').forEach(function(e){
    var cycle = e.getAttribute('data-cycle');
    if(group === 'all'){ e.style.display = ''; }
    else if(group === 'cycle1'){ e.style.display = (cycle === '1') ? '' : 'none'; }
    else if(group === 'cycle2'){ e.style.display = (cycle === '2') ? '' : 'none'; }
  });
  document.querySelectorAll('.month-group').forEach(function(mg){
    var visible = mg.querySelectorAll('.entry').length > 0 &&
                  Array.from(mg.querySelectorAll('.entry')).some(function(e){return e.style.display !== 'none';});
    mg.style.display = visible ? '' : 'none';
  });
}

// P2B — Cmd+K command palette
(function(){
  var idx = null, selected = 0, visible = [];
  function pathPrefix(){
    if(/\\/(briefings|concepts)\\//.test(location.pathname)) return '../';
    return '';
  }
  function loadIndex(cb){
    if(idx){ cb(idx); return; }
    fetch(pathPrefix() + 'search-index.json')
      .then(function(r){ return r.json(); })
      .then(function(j){ idx = j; cb(j); })
      .catch(function(){ idx = {briefings:[], concepts:[]}; cb(idx); });
  }
  window.cmdkOpen = function(){
    var m = document.getElementById('cmdkModal');
    if(!m) return;
    m.classList.add('open');
    m.removeAttribute('hidden');
    var input = document.getElementById('cmdkInput');
    setTimeout(function(){ input.focus(); input.select(); }, 30);
    loadIndex(function(){ cmdkSearch(input.value); });
  };
  window.cmdkClose = function(){
    var m = document.getElementById('cmdkModal');
    if(!m) return;
    m.classList.remove('open');
    m.setAttribute('hidden', '');
  };
  function esc(s){
    return (s||'').replace(/[<>&\"]/g, function(c){
      return ({'<':'&lt;','>':'&gt;','&':'&amp;','\"':'&quot;'})[c];
    });
  }
  function renderResult(r, i){
    var pre = pathPrefix();
    if(r.type === 'briefing'){
      var b = r.item;
      return '<a class=\"cmdk-result' + (i===0?' sel':'') + '\" href=\"' + pre + b.url + '\" data-i=\"' + i + '\">' +
        '<div class=\"cmdk-result-type\">Briefing</div>' +
        '<div class=\"cmdk-result-body\">' +
        '<div class=\"cmdk-result-title\">' + esc(b.display_date) + ' · ' + esc(b.dow) + '</div>' +
        '<div class=\"cmdk-result-sub\"><span class=\"cmdk-result-meta\">No. ' + esc(b.number) + ' · Cycle ' + esc(String(b.cycle)) + '</span>' + esc(b.thread||'(no thread title)') + '</div>' +
        '</div></a>';
    }
    var c = r.item;
    return '<a class=\"cmdk-result' + (i===0?' sel':'') + '\" href=\"' + pre + c.url + '\" data-i=\"' + i + '\">' +
      '<div class=\"cmdk-result-type concept\">Concept</div>' +
      '<div class=\"cmdk-result-body\">' +
      '<div class=\"cmdk-result-title\">' + esc(c.name) + '</div>' +
      '<div class=\"cmdk-result-sub\"><span class=\"cmdk-result-meta m' + c.meta + '\">META-' + c.meta + ' · ' + esc(c.meta_name) + '</span>' + esc(c.brief) + '</div>' +
      '</div></a>';
  }
  window.cmdkSearch = function(q){
    if(!idx){ loadIndex(function(){ cmdkSearch(q); }); return; }
    q = (q||'').trim().toLowerCase();
    visible = [];
    var results = document.getElementById('cmdkResults');
    var counts = document.getElementById('cmdkCounts');
    if(!results) return;
    idx.concepts.forEach(function(c){
      var hay = (c.name + ' ' + (c.brief||'') + ' ' + (c.meta_name||'')).toLowerCase();
      if(!q || hay.indexOf(q) !== -1) visible.push({type:'concept', item:c});
    });
    idx.briefings.forEach(function(b){
      var hay = ((b.title||'') + ' ' + (b.thread||'') + ' ' + b.date + ' ' + (b.dow||'') + ' Cycle ' + b.cycle).toLowerCase();
      if(!q || hay.indexOf(q) !== -1) visible.push({type:'briefing', item:b});
    });
    if(q){
      visible.sort(function(a, b){
        var aName = (a.item.name || a.item.title || '').toLowerCase();
        var bName = (b.item.name || b.item.title || '').toLowerCase();
        var aHit = aName.indexOf(q), bHit = bName.indexOf(q);
        if(aHit === -1) aHit = 9999; if(bHit === -1) bHit = 9999;
        if(aHit !== bHit) return aHit - bHit;
        return 0;
      });
    }
    visible = visible.slice(0, 50);
    selected = 0;
    if(!visible.length){
      results.innerHTML = '<div class=\"cmdk-empty\">No matches.</div>';
      if(counts) counts.textContent = '';
      return;
    }
    results.innerHTML = visible.map(function(r, i){ return renderResult(r, i); }).join('');
    if(counts) counts.textContent = visible.length + ' result' + (visible.length===1?'':'s');
  };
  // Wire up input event
  document.addEventListener('DOMContentLoaded', function(){
    var input = document.getElementById('cmdkInput');
    if(input) input.addEventListener('input', function(){ cmdkSearch(this.value); });
  });
  // Keyboard handling
  document.addEventListener('keydown', function(e){
    var isCmdK = (e.key === 'k' || e.key === 'K') && (e.metaKey || e.ctrlKey);
    if(isCmdK){ e.preventDefault(); cmdkOpen(); return; }
    var m = document.getElementById('cmdkModal');
    if(!m || !m.classList.contains('open')) return;
    if(e.key === 'Escape'){ e.preventDefault(); cmdkClose(); return; }
    if(e.key === 'ArrowDown' || e.key === 'ArrowUp'){
      e.preventDefault();
      var max = visible.length - 1;
      selected = (e.key === 'ArrowDown') ? Math.min(max, selected+1) : Math.max(0, selected-1);
      document.querySelectorAll('.cmdk-result').forEach(function(el, i){
        el.classList.toggle('sel', i === selected);
        if(i === selected) el.scrollIntoView({block:'nearest'});
      });
    }
    if(e.key === 'Enter'){
      e.preventDefault();
      var el = document.querySelectorAll('.cmdk-result')[selected];
      if(el) window.location.href = el.getAttribute('href');
    }
  });
})();
</script>
</body>
</html>
"""


def build_sparkline_svg(total_briefings, vocab_count, cycle2_start=CYCLE2_THRESHOLD):
    """Build an SVG vocabulary-growth sparkline.

    Coordinates approximate vocabulary growth: ~linear 1→33 across Cycle 1
    (briefings 1-30), then a step up at the Cycle 1 audit (briefing 31 = 38),
    then slow accumulation to current count through Cycle 2.

    The sparkline is a visual impression of cadence, not a precise time series.
    """
    if total_briefings <= 0:
        return ''
    width = 220.0
    height = 48.0
    top_pad = 4.0
    bot_pad = 4.0
    max_y = height - bot_pad
    min_y = top_pad
    # Approximate vocab count per briefing index — gradual then post-audit step
    def vocab_at(i):
        if i <= 1:
            return 1
        if i <= 30:
            # Linear 1 → 33 across Cycle 1
            return 1 + (33 - 1) * (i - 1) / 29
        if i == cycle2_start:
            return 38  # post-audit consolidation
        # Cycle 2: slow accumulation to current vocab_count
        if total_briefings <= cycle2_start:
            return 38
        return 38 + (vocab_count - 38) * (i - cycle2_start) / max(1, total_briefings - cycle2_start)
    max_v = max(vocab_count, 42)
    pts = []
    for i in range(1, total_briefings + 1):
        x = (i - 1) / max(1, total_briefings - 1) * width
        v = vocab_at(i)
        y = max_y - (v / max_v) * (max_y - min_y)
        pts.append(f'{x:.1f},{y:.1f}')
    line_pts = ' '.join(pts)
    # Cycle-2 vertical marker
    cycle2_x = (cycle2_start - 1) / max(1, total_briefings - 1) * width
    # Area path (line + bottom corners)
    first_x = pts[0].split(',')[0]
    last_x = pts[-1].split(',')[0]
    area_d = f'M{first_x},{max_y} L' + ' L'.join(pts) + f' L{last_x},{max_y} Z'
    # Current point
    last_x_f, last_y_f = pts[-1].split(',')
    return (
        f'<svg class="vocab-spark" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'preserveAspectRatio="none" '
        f'aria-label="Vocabulary growth across {total_briefings} briefings, '
        f'accumulating to {vocab_count} named patterns">'
        f'<defs><linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">'
        f'<stop offset="0%" stop-color="#6da8ff" stop-opacity="0.32"/>'
        f'<stop offset="100%" stop-color="#6da8ff" stop-opacity="0"/>'
        f'</linearGradient></defs>'
        f'<line class="spark-axis" x1="0" y1="{max_y:.1f}" x2="{width:.0f}" y2="{max_y:.1f}"/>'
        f'<line class="spark-cycle" x1="{cycle2_x:.1f}" y1="{min_y:.1f}" x2="{cycle2_x:.1f}" y2="{max_y:.1f}"/>'
        f'<path class="spark-area" d="{area_d}"/>'
        f'<polyline class="spark-line" points="{line_pts}"/>'
        f'<circle class="spark-current-pulse" cx="{last_x_f}" cy="{last_y_f}"/>'
        f'<circle class="spark-current" cx="{last_x_f}" cy="{last_y_f}" r="2.6"/>'
        f'</svg>'
        f'<div class="vocab-spark-label">'
        f'<span>Briefing 001</span>'
        f'<span style="color:var(--ambb)">Cycle 2 begins</span>'
        f'<span>{int(total_briefings):03d} &middot; today</span>'
        f'</div>'
    )


def render_hero(today_meta, archive_url, total_briefings=0):
    """Render the hero card for today's briefing."""
    if not today_meta:
        return ''

    cycle_label = (f'Cycle {today_meta["cycle"]} · Day {today_meta["cycle_day"]}'
                   if today_meta['cycle_day']
                   else f'Cycle {today_meta["cycle"]}')

    # Deep dive list
    if today_meta['deep_dive_titles']:
        dd_items = '\n'.join(
            f'<li>{t}</li>' for t in today_meta['deep_dive_titles'][:4])
        dd_block = (f'<div class="hero-block">'
                    f'<h4>Today\'s Deep Dives</h4>'
                    f'<ul>{dd_items}</ul>'
                    f'</div>')
    else:
        dd_block = ''

    # Vocabulary + liminal block
    vocab_text = today_meta['vocab_status'] or 'Vocabulary status pending'
    # Try to split number from descriptor
    vocab_num_match = re.match(r'(\d+)\s+(.*)', vocab_text)
    sparkline_html = ''
    if vocab_num_match:
        vocab_count_int = int(vocab_num_match.group(1))
        vocab_html = (f'<span class="vocab-num">{vocab_num_match.group(1)}</span>'
                      f'<span class="vocab-sub">{vocab_num_match.group(2)} '
                      f'&middot; {total_briefings} briefings</span>')
        sparkline_html = build_sparkline_svg(total_briefings, vocab_count_int)
    else:
        vocab_html = f'<span class="vocab-sub">{vocab_text}</span>'

    liminal_html = ''
    if today_meta['liminal_highlight']:
        liminal_html = (f'<div style="margin-top:.9rem;padding-top:.7rem;'
                        f'border-top:1px dotted rgba(229,184,76,0.2)">'
                        f'<h4 style="color:var(--gold)!important">Off-corridor Liminal Signal</h4>'
                        f'<div class="liminal">{today_meta["liminal_highlight"]}</div>'
                        f'</div>')

    vocab_block = (f'<div class="hero-block">'
                   f'<h4>Structural Vocabulary</h4>'
                   f'{vocab_html}'
                   f'{sparkline_html}'
                   f'{liminal_html}'
                   f'</div>')

    # Excerpt
    excerpt_paras = (today_meta['unifying_thread_excerpt']
                     or today_meta['tagline'])
    excerpt_html = '\n'.join(
        f'<p>{p}</p>' for p in excerpt_paras.split('\n\n') if p.strip())

    thread_title = (today_meta['unifying_thread_title']
                    or 'Today\'s Unifying Thread')

    return f"""
<section class="hero">
<div class="hero-eyebrow"><span class="dot"></span><span>Today's Briefing</span><span style="color:var(--t4)">·</span><span style="color:var(--t3)">No. {today_meta['number']} · {cycle_label}</span></div>
<h2 class="hero-date">{today_meta['display_date']}</h2>
<div class="hero-thread-title">{thread_title}</div>
<div class="hero-thread-excerpt">{excerpt_html}</div>

<div class="hero-grid">
{dd_block}
{vocab_block}
</div>

<a class="hero-cta" href="{archive_url}">Read the full briefing →</a>
</section>
"""


# Static text describing Cycle 2 + meta-categories.
CYCLE2_INTRO = """<p>Cycle 2 begins at <strong>Briefing 031</strong> (5 May 2026) and continues today. Cycle 1 (Briefings 001–030) established the core <em>five-meta-category</em> taxonomy of the structural vocabulary; Cycle 2 applies a stricter <em>candidate-and-refinement</em> discipline: provisional patterns enter monitoring, get tested by the next empirical event, and either advance toward vocabulary status, get refined, or get refuted.</p>"""

META_CATEGORIES = [
    ('META-1', 'Coupling Failure'),
    ('META-2', 'Bypass Inversion'),
    ('META-3', 'Threshold Cascade'),
    ('META-4', 'Commons Enclosure'),
    ('META-5', 'Institutional Hollowing'),
]


def render_cycle2_panel(today_meta):
    """Render the Cycle 2 status panel."""
    meta_tiles = '\n'.join(
        f'<div class="meta-tile"><div class="mt-tag">{tag}</div><div class="mt-name">{name}</div></div>'
        for tag, name in META_CATEGORIES)

    # If we have today's metadata and it lists candidates, render them.
    # We do a best-effort extraction from today's HTML below; for now use
    # the canonical list (snapshot from Briefing 039, 13 May 2026).
    candidates = extract_cycle2_candidates(today_meta) if today_meta else []
    if not candidates:
        # Fallback to a documented placeholder if extraction fails.
        candidates = [
            ('Bilateral Channel Decomposition', 'CANDIDATE',
             'Both parties decompose bundled commitments. Briefing 033+.'),
            ('Asymmetric Reversibility', 'CANDIDATE',
             'Decomposition reversibility paths are structurally asymmetric.'),
            ('Parallel-Path Persistence', 'CANDIDATE',
             'Deal-path and no-deal-path acquire substrate simultaneously.'),
            ('Information-Suppression Decomposition', 'CANDIDATE',
             'Decomposition via administrative concealment.'),
            ('Three-Bilateral Stack', 'CANDIDATE',
             'Three+ bilateral architectures occupy parallel persistence.'),
            ('Disclosure-Mode Discount', 'CANDIDATE',
             'Marketplace penalty proportional to reversal probability.'),
            ('Credential Institutionalization', 'CANDIDATE',
             'Commemorative event converted into recurring architecture.'),
            ('Surrogate Re-Disclosure', 'REFINED',
             'Delegation-level mode re-occupation preserves principal optionality.'),
        ]

    candidate_html = '\n'.join(
        f'<div class="candidate"><strong>{name} · {status}</strong>{blurb}</div>'
        for name, status, blurb in candidates)

    most_recent_vocab = (
        'Most recent vocabulary promotion: '
        '<strong style="color:var(--blub)">Mode-Switch Disarticulation</strong> '
        '(promoted in Briefing 038, 12 May 2026 — naming a single architecture '
        'executing both concealment-mode and disclosure-mode '
        'Channel Decomposition across consecutive cadence-windows on the same artifact).')

    return f"""
<section class="cycle-panel">
<h2>Cycle 2 Status</h2>
<div class="cycle-sub">Candidate-and-refinement discipline · 5 meta-categories · Monitoring threshold</div>
{CYCLE2_INTRO}

<div class="meta-grid">
{meta_tiles}
</div>

<p style="font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:var(--ambb);margin-top:1.2rem;margin-bottom:.6rem">Cycle 2 Monitoring Candidates</p>
<div class="candidate-list">
{candidate_html}
</div>

<p style="margin-top:1.2rem;color:var(--t3);font-size:.88rem">{most_recent_vocab}</p>
</section>
"""


def extract_cycle2_candidates(today_meta):
    """Pull the current Cycle-2 candidate list from today's HTML, if present."""
    filepath = BRIEFINGS_DIR / today_meta['filename']
    try:
        content = filepath.read_text(encoding='utf-8')
    except OSError:
        return []
    # Find the candidate section
    block_match = re.search(
        r'Cycle 2 Monitoring Candidates.*?</h3>(.*?)<h3',
        content, re.DOTALL)
    if not block_match:
        return []
    block = block_match.group(1)
    items = re.findall(
        r'<div class="vi"[^>]*>\s*<h4[^>]*>([^<]+)</h4>\s*<p>([^<]+)',
        block)
    out = []
    for raw_name, blurb in items[:10]:
        # Parse "Name · STATUS" — accept literal middot or &middot; entity
        parts = re.split(r'\s*(?:&middot;|·)\s*', raw_name, maxsplit=1)
        name = parts[0].strip()
        status = parts[1].strip() if len(parts) > 1 else 'CANDIDATE'
        # Trim blurb to ~110 chars at sentence boundary
        snippet = blurb.strip()
        if len(snippet) > 140:
            # cut at next period or space
            cut = snippet.rfind('. ', 0, 140)
            if cut < 70:
                cut = snippet.rfind(' ', 0, 140)
            if cut < 70:
                cut = 140
            snippet = snippet[:cut].rstrip(' .') + '.'
        out.append((name, status, snippet))
    return out


def render_archive(metas, audit_links):
    """Render filterable, month-grouped archive."""
    # Group by year-month
    groups = {}
    for m in metas:
        try:
            dt = datetime.strptime(m['date_str'], '%Y-%m-%d')
            key = dt.strftime('%B %Y')
            sort_key = dt.strftime('%Y-%m')
        except ValueError:
            key = 'Undated'
            sort_key = '0000-00'
        groups.setdefault((sort_key, key), []).append(m)

    # Render groups newest-first
    parts = []
    for (sort_key, label) in sorted(groups.keys(), reverse=True):
        entries = sorted(groups[(sort_key, label)],
                         key=lambda m: m['date_str'], reverse=True)
        entry_html = '\n'.join(render_entry(m) for m in entries)
        parts.append(
            f'<div class="month-group" data-month="{sort_key}">'
            f'<h3>{label}<span class="count">{len(entries)} briefings</span></h3>'
            f'{entry_html}'
            f'</div>')

    # Audits inline at top of archive (small section)
    audits_html = ''
    if audit_links:
        audit_cards = '\n'.join(audit_links)
        audits_html = f'''
<div style="margin-bottom:1.6rem">
  <h3 style="font-family:'Cormorant Garamond',serif;font-size:1.15rem;color:var(--ambb);font-weight:500;margin-bottom:.8rem">Contingency Audits</h3>
  <div style="color:var(--t3);font-size:.85rem;line-height:1.55;margin-bottom:.8rem;font-style:italic">Meta-analyses of the briefing's Inference Engine, every 30 briefings. The break points themselves are the data.</div>
  {audit_cards}
</div>
'''

    return f"""
<section>
<h2 class="sh2">Archive</h2>
<div class="sh2-sub">All {len(metas)} briefings · Grouped by month · Filterable</div>

<div class="filter-bar">
<span class="fl-label">Filter:</span>
<button class="active" data-filter="all" onclick="applyFilter('all')">All</button>
<button data-filter="cycle1" class="amb" onclick="applyFilter('cycle1')">Cycle 1 (001–030)</button>
<button data-filter="cycle2" class="gold" onclick="applyFilter('cycle2')">Cycle 2 (031–)</button>
</div>

{audits_html}

{''.join(parts)}
</section>
"""


def render_entry(m):
    cycle_class = 'cycle2' if m['cycle'] == 2 else ''
    cycle_marker = (f'<span class="entry-cycle2">Cycle 2</span>'
                    if m['cycle'] == 2 else 'Cycle 1')
    # Strip the trailing day-of-week from display_date if present (already in dow column)
    date_clean = re.sub(r'\s*(?:&middot;|·)\s*(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s*$',
                        '', m['display_date'])
    dow_html = (f'<span class="dow">{m["day_of_week"]}</span>'
                if m['day_of_week'] else '')
    tagline_clean = (m['tagline'] or '')
    # Limit tagline to a reasonable preview length (~280 chars at sentence boundary)
    if len(tagline_clean) > 280:
        cut = tagline_clean.rfind('. ', 0, 280)
        if cut < 140:
            cut = tagline_clean.rfind(' ', 0, 280)
        if cut < 140:
            cut = 280
        tagline_clean = tagline_clean[:cut].rstrip(' .') + '.'
    return (f'<a class="entry {cycle_class}" '
            f'href="briefings/{m["filename"]}" '
            f'data-cycle="{m["cycle"]}" '
            f'data-date="{m["date_str"]}">'
            f'<div class="entry-num-cell"><strong>No. {m["number"]}</strong>{cycle_marker}</div>'
            f'<div class="entry-body">'
            f'<div class="entry-date">{date_clean}{dow_html}</div>'
            f'<div class="entry-tagline">{tagline_clean}</div>'
            f'</div>'
            f'<div class="entry-arrow">→</div>'
            f'</a>')


def render_stats(metas):
    n_total = len(metas)
    n_cycle1 = sum(1 for m in metas if m['cycle'] == 1)
    n_cycle2 = sum(1 for m in metas if m['cycle'] == 2)
    # Today's vocab status from most-recent briefing
    vocab_n = ''
    cand_n = ''
    if metas:
        v = metas[0]['vocab_status']
        vn = re.search(r'(\d+)\s+named', v)
        if vn:
            vocab_n = vn.group(1)
        cn = re.search(r'(\d+)\s+Cycle 2', v)
        if cn:
            cand_n = cn.group(1)
    audit_n = 1  # cycle-001.html exists per repo state
    return f"""
<div class="stats">
<div class="stat"><div class="stat-num">{n_total}</div><div class="stat-label">Briefings</div></div>
<div class="stat"><div class="stat-num">{n_cycle1}</div><div class="stat-label">Cycle 1</div></div>
<div class="stat"><div class="stat-num gold">{n_cycle2}</div><div class="stat-label">Cycle 2</div></div>
<div class="stat"><div class="stat-num">{vocab_n or '—'}</div><div class="stat-label">Named patterns</div></div>
<div class="stat"><div class="stat-num gold">{cand_n or '—'}</div><div class="stat-label">Cycle 2 candidates</div></div>
<div class="stat"><div class="stat-num amber">{audit_n}</div><div class="stat-label">Contingency audits</div></div>
</div>
"""


def discover_audits():
    """Return links for known synthesis audits, if any."""
    syn_dir = REPO_DIR / 'synthesis'
    out = []
    if syn_dir.exists():
        for p in sorted(syn_dir.glob('cycle-*.html')):
            num = re.search(r'cycle-(\d+)', p.stem)
            num_str = num.group(1) if num else '?'
            out.append(
                f'<a class="audit-card" href="synthesis/{p.name}">'
                f'<div class="audit-num">Cycle No. {num_str}</div>'
                f'<div class="audit-title">Contingency Audit — Cycle {int(num_str)}</div>'
                f'<div class="audit-blurb">Meta-analysis of the Inference Engine\'s conditional chains across the cycle window. Break-point taxonomy and LLM-cognition diagnostics.</div>'
                f'</a>')
    return out


# ──────────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────────
def build_index(metas):
    """Compose the new index.html."""
    today = metas[0] if metas else None
    hero = render_hero(today, f'briefings/{today["filename"]}' if today else '#', total_briefings=len(metas))
    cycle2 = render_cycle2_panel(today)
    stats = render_stats(metas)
    audits = discover_audits()
    archive = render_archive(metas, audits)

    head = INDEX_HEAD.replace('{{ARCHIVE_COUNT}}', str(len(metas)))
    return head + hero + stats + cycle2 + archive + INDEX_FOOT


def update_index():
    if not BRIEFINGS_DIR.exists():
        print("Error: briefings/ directory not found")
        sys.exit(1)

    briefing_files = sorted(BRIEFINGS_DIR.glob("*.html"), reverse=True)
    if not briefing_files:
        print("No briefings found.")
        return

    print(f"Found {len(briefing_files)} briefing(s)")

    metas = []
    for f in briefing_files:
        m = extract_metadata(f)
        metas.append(m)
        print(f"  • {m['date_str']} — No. {m['number']} "
              f"(Cycle {m['cycle']}{', Day ' + str(m['cycle_day']) if m['cycle_day'] else ''})")

    # ── Inject per-day navigation wrappers ──
    # metas is newest-first; build prev/next pairs.
    # For each briefing m at position i: prev = older briefing (i+1); next = newer briefing (i-1).
    print("\nInjecting per-day navigation wrappers…")
    delta_total = 0
    for i, m in enumerate(metas):
        prev_meta = metas[i + 1] if i + 1 < len(metas) else None
        next_meta = metas[i - 1] if i - 1 >= 0 else None
        path = BRIEFINGS_DIR / m['filename']
        delta = inject_per_day_nav(path, m, prev_meta, next_meta)
        delta_total += delta
    avg_delta = delta_total / len(metas) if metas else 0
    print(f"  ✓ Per-day nav injected. Total byte delta: {delta_total} "
          f"(avg {avg_delta:.0f}/file)")

    # ── Rebuild index.html ──
    new_index = build_index(metas)
    INDEX_FILE.write_text(new_index, encoding='utf-8')
    print(f"\n✓ index.html regenerated ({len(new_index):,} bytes; "
          f"{len(metas)} entries).")


if __name__ == '__main__':
    update_index()
