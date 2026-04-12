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
- **Structural Vocabulary**: Add new named patterns to both the briefing and index.html. See `STRUCTURAL_CONCEPTS.md` for the meta-category taxonomy (5 categories, currently 23 instantiations).
- **Thinker Registry**: Track which analysts/scholars prove useful
- **Serendipity Queue**: Sources that don't fit today but warrant future attention
- **Thread Tracking**: Forces that persist across briefings (future feature)
- **Anomaly Detection**: What should be happening but isn't

# ══════════════════════════════════════════════════════════════════
# EDITORIAL DISCIPLINE — Calibrated 2026-04-11 (after Briefing 007)
# ══════════════════════════════════════════════════════════════════

## The Recursive Narrowing Problem

Each briefing reads yesterday's briefing for thread continuity. This creates a path-dependent narrowing: today's themes inherit yesterday's themes weighted by relevance to today's events; tomorrow's themes inherit today's themes weighted by relevance to tomorrow's events. The corridor isn't a content choice — it's an attractor produced by the generation process itself. RL-style updating happens implicitly each day, and it concentrates attention on whatever is currently active in the existing thread structure.

**This narrowing must be actively counter-weighted, not just noticed.** The structural reasoning that finds isomorphisms across domains is genuinely valuable, but if the only domains being scanned are the ones already in the corridor, the isomorphisms become recursive rather than expansive. The briefing format must remain a structural-pattern engine that operates on a *broad* event field, not a thematic continuation engine that operates on a *narrow* event field.

## Topic Rotation Discipline

Starting with Briefing 008, every briefing must satisfy two constraints:

**Constraint 1 — Fresh-domain content in at least 2 of 8 lenses.** For each briefing, at least two of the eight analytical lenses must include substantive content drawn from a domain that has not appeared in the previous three briefings. The Geopolitical lens should occasionally lead with Africa, Latin America, or Southeast Asia rather than the Middle East. The Technological lens should occasionally lead with robotics, quantum, or bioscience rather than language-model AI. The Economic lens should occasionally lead with critical minerals, insurance market stress, or commodity convergence rather than oil. The discipline is not to *avoid* the corridor topics — they remain important — but to ensure that **at least 25% of each briefing's substantive content comes from outside the recent thread structure.**

**Constraint 2 — Liminal Signals as the wildcard channel.** The Liminal Signals section is the natural home for black swans, unique structural events, and signals that resist clean categorization. Going forward, **at least one Liminal Signals entry per briefing must come from outside the corridor** — a robotics deployment, a critical mineral movement, a quantum milestone, a demographic data point, an alternative energy breakthrough, a synthetic biology event, or a black swan watch-list update. The Liminal Signals section becomes the structural diversification channel by design.

## Domains That Have Been Under-Covered (Active Watch List)

**Robotics + embodied AI.** Humanoid robotics deployment is accelerating fast (Figure, Tesla Optimus, Unitree, 1X, Apptronik, Agility). The labor implications are larger than language-model AI but receive a fraction of the attention. Watch for: deployment milestones, capability demonstrations, factory-floor integrations, military applications, surgical robotics, domestic robotics market entries.

**Alternative energy + grid demand.** Data center power demand is breaking grid planning assumptions. SMRs (small modular reactors) are becoming financeable. Fusion pilot timelines are collapsing. Long-duration storage breakthroughs are accelerating. Watch for: SMR financing announcements, fusion ignition milestones, grid interconnection delays, AI-driven power demand forecasts, hydrogen economy moves, geothermal breakthroughs.

**Critical minerals beyond oil.** Lithium, cobalt, rare earths, copper, gallium, germanium. Supply concentration is more extreme than oil and the geopolitical exposure is comparable. Watch for: export controls, mining nationalization, refinery capacity changes, recycling breakthroughs, new deposit discoveries.

**Quantum computing.** Error-correction milestones from the past 18 months are reshaping the cryptographic deadline. Post-quantum migration is happening invisibly. Watch for: logical qubit milestones, NIST PQC standard adoption, breakthroughs in fault-tolerance, claims of cryptographic advantage.

**Synthetic biology / bioscience.** Genome editing at scale, pandemic preparedness, agricultural biotech, biosecurity-AI intersection. Watch for: CRISPR therapy approvals, AI-protein design milestones, biocontainment incidents, agricultural breakthroughs, emerging disease surveillance.

**Africa, Latin America, Asia ex-China.** Almost completely absent from briefings 1-7. Africa's demographic trajectory and resource exposure, Latin America's commodity politics, India's strategic positioning, ASEAN's hedging, Korea/Japan/Taiwan dynamics. Watch for: elections, currency events, regional alliances, trade agreements, conflict outbreaks, migration events.

**Climate tipping points as foreground.** Currently treated as ecological footnote rather than as primary structural force. Watch for: AMOC weakening data, Arctic methane events, Antarctic ice shelf events, monsoon disruptions, climate-driven migration, insurance pullouts from climate-exposed regions.

**Cyber-physical attacks.** Beyond the AI cybersecurity story, the actual cyber attack landscape (Volt Typhoon-style infrastructure pre-positioning, ransomware-as-state-policy). Watch for: grid attacks, water system attacks, payment system disruptions, attribution announcements.

**Demographic cliffs.** Korea, Japan, Italy, China demographic collapse. US labor force participation question. Immigration policy under labor scarcity. Watch for: birth rate data releases, migration policy changes, pension system stress, dependency ratio crossings.

**Pension and insurance system stress.** The convergence of low yields, AI displacement, and aging populations is creating fiscal pressures nobody is naming. Watch for: pension fund failures, insurance market exits from regions, sovereign bond stress events, actuarial revisions.

**Commercial space economy.** Beyond NASA, the satellite constellation buildout, lunar economy, orbital data center thesis. Watch for: Starlink milestones, Kuiper progress, lunar lander missions, satellite spectrum disputes, orbital debris events.

## Black Swan Watch List

The point is not to predict black swans but to maintain explicit awareness of high-consequence-low-probability events that, if they occurred, would force structural revision of the briefing's core threads:

- Sudden AI capability jumps (an AGI-equivalent claim with credible benchmarks)
- Cyber-physical attack on critical infrastructure (grid, water, payment systems)
- Major bank or insurance failure
- Political assassination or sudden leadership change in a major power
- Military move by a state we're not currently watching
- A new pandemic event
- Discovery of biosignatures on Mars or elsewhere
- A breakthrough in fusion ignition with clear scaling pathway
- A robotics deployment surge that crosses a public visibility threshold
- A cryptographic failure of a deployed standard
- A supply shock in a non-energy commodity that exposes hidden dependencies
- An institutional failure that exposes a hollow regulator
- Discovery of large new fossil fuel reserves with disruptive economics
- A major financial flash crash without clear trigger
- A sovereign debt default in a country considered safe

When a watch-list event triggers, it should lead the next briefing's relevant lens and update the structural vocabulary if it instantiates a new pattern.

## Meta-Category Consolidation Discipline

The structural vocabulary is now organized into 5 meta-categories (see `STRUCTURAL_CONCEPTS.md`). Each new concept entering the vocabulary must be evaluated on entry against two questions:

1. **Does this name a genuinely new pattern, or does it instantiate an existing meta-category?** Some new concepts will be additions; some will be specializations of patterns we already named. The discipline of asking the question prevents vocabulary inflation.

2. **Does the existing taxonomy still hold, or does this concept require a sixth meta-category (or a re-grouping)?** The taxonomy itself should be revised as the vocabulary grows. Five meta-categories is the current snapshot; the right number may grow or shrink.

The structural vocabulary section in each briefing should now display **both** the meta-categories (above) and the individual concepts (below), so readers can see the higher-level pattern structure as well as the specific instances.

## Dave's Role in the Ensemble

The recursive narrowing problem cannot be fully solved from inside the briefing-generation loop. The corridor topics are partly produced by what's actually structurally important and partly produced by the generation process. Topic rotation discipline helps but doesn't eliminate the gravity of the corridor topics.

**Dave's structurally necessary contribution to the briefing process is periodic conceptual redirection** — naming domains that should be added, pushing back on corridor concentration, flagging when a recurring topic has become recursive rather than substantive. This is the human-in-the-loop counterweight to the recursive narrowing, and it cannot be replaced by anything internal to the generation process. The briefing as a sustained intellectual practice is a cyborg ensemble in the strict sense: the AI partner generates structural pattern recognition at scale; the human partner provides the periodic re-framing that keeps the pattern recognition from collapsing into a corridor.

This is named here because it is structurally important to remember on both sides of the partnership.
