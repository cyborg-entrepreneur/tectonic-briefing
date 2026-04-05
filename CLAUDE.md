# Tectonic Briefing — Claude Code Integration

## Overview
The Tectonic Briefing is a daily structural analysis platform deployed via GitHub Pages.
Repository location: `~/workflow/tectonic-briefing/`

## Directory Structure
```
~/workflow/tectonic-briefing/
├── index.html              # Archive page (auto-updated by scripts)
├── briefings/              # Daily HTML briefings (YYYY-MM-DD.html)
├── threads/                # Cross-briefing structural threads (future)
├── assets/                 # Shared assets
├── scripts/
│   ├── publish.sh          # One-command git add/commit/push
│   ├── new-briefing.sh     # Scaffold new briefing file
│   └── update-index.py     # Regenerate index from briefing files
└── CLAUDE.md               # This file
```

## Workflow Commands

### After generating a briefing in Claude.ai conversation:
1. Download the HTML file from the conversation
2. Save/move to `~/workflow/tectonic-briefing/briefings/YYYY-MM-DD.html`
3. Run: `python3 ~/workflow/tectonic-briefing/scripts/update-index.py`
4. Run: `~/workflow/tectonic-briefing/scripts/publish.sh`

### Or use Claude Code directly:
```bash
# Save briefing content to file
cat > ~/workflow/tectonic-briefing/briefings/2026-04-06.html << 'EOF'
[paste HTML content]
EOF

# Update index and publish
cd ~/workflow/tectonic-briefing
python3 scripts/update-index.py
./scripts/publish.sh "Briefing No. 002 — 6 Apr 2026"
```

## Briefing Architecture

### Eight Analytical Lenses
1. Geopolitical (red accent)
2. Technological (blue default)
3. Economic (blue default)
4. Scientific (blue default)
5. Social & Cultural (blue default)
6. Environmental & Ecological (green accent)
7. Institutional & Governance (amber accent)
8. Liminal Signals (gold accent)

### Integrated Systems
- Inference Engine (purple) — Conditional chains
- Force Interaction Matrix — Amplify/Dampen
- Wise Action (teal) — Entrepreneurship, Markets, Investment
- Structural Vocabulary — Named patterns
- Anomaly Detection — Conspicuous absences
- Source Archive — Annotated with Thinker Registry + Serendipity Queue
- Deep Dive Markers — ◉ signals for conversation topics
- Research Program Relevance — Knowledge problems, cyborg, Glimpse, papers

### Knowledge Problem Tags
- Knightian Uncertainty (blue)
- Equivocality (teal)
- Complexity (purple)
- Ambiguity (gold)

### Design Specs
- Background: #0b1120 (hardcoded, not CSS variable)
- Cards: #111827
- Text: #d4dce8 body, #eaf0f8 headings
- Blue accent: #4b8ef2 / #6da8ff
- Typography: Cormorant Garamond (headings), Source Sans 3 (body), JetBrains Mono (labels)
- Responsive: works on desktop, tablet, phone

## Accumulating Elements (Track Across Briefings)
- **Structural Vocabulary**: Add new named patterns to both the briefing and index.html
- **Thinker Registry**: Track which analysts/scholars prove useful
- **Serendipity Queue**: Sources that don't fit today but warrant future attention
- **Thread Tracking**: Forces that persist across briefings (future feature)
- **Anomaly Detection**: What should be happening but isn't
