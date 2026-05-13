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

**IMPORTANT — Context management for briefing generation (calibrated 2026-04-16):**

When generating a tectonic briefing in Claude Code, use the **Agent tool** with a dedicated sub-agent rather than generating in the main conversation context. Long sessions accumulate context that compresses briefing depth — deep dives drop, structural vocabulary gets abbreviated, and analyses shorten. A spawned agent operates in a fresh context window.

The agent prompt MUST include:
1. This CLAUDE.md file (read in full)
2. `STRUCTURAL_CONCEPTS.md` (read in full)
3. The designated quality-benchmark briefing (currently Briefing 010, 2026-04-14.html) as a format template
4. Today's research results and events summary
5. The full list of all named structural vocabulary patterns (currently 30)
6. Explicit instruction to include 2-4 deep dive panels, full five-meta-category vocabulary display, and all 12 section IDs

**Post-generation quality checklist (run before committing):**
After the HTML is written, verify:
- [ ] Count `dd-panel` elements → target 2-4 deep dives
- [ ] Count `.vi` vocabulary entries displayed → target all 30 (or current total)
- [ ] All 12 section IDs present: ov, ge, te, ec, sc, so, en, ig, li, ie, wa, sa
- [ ] Anomaly Detection has 4+ specific anomalies
- [ ] Research Program Relevance section has per-project connections
- [ ] Source Archive has categorized entries across 3+ subsections
- [ ] Editorial discipline note in footer confirms fresh-domain rotation

If any check fails, regenerate the missing sections before publishing.

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

# ══════════════════════════════════════════════════════════════════
# PROSE COHERENCE DISCIPLINE — Calibrated 2026-05-13 (after Briefings 037-038)
# ══════════════════════════════════════════════════════════════════

## The Jargon-Density Drift Problem

Dave flagged on 2026-05-13 that Briefings 037 and 038 had drifted toward dense compound-noun argumentation that obscures rather than carries the structural-analytical message. The structural vocabulary itself is fine — that's the apparatus working — but the prose around the vocabulary has been failing the strategic-concreteness discipline that the scholarly-writing skill already requires.

**Empirical signature of the drift** (examples from 037-038):
- "the cross-architecture cluster's pattern recognition acquires multi-temporal-scale operation" — five nouns, no concrete verb
- "the chancellery-marketplace discrimination-gap" — abstract gap of abstract entities
- "structural-information-arbitrage opportunity" — three hyphenated compounds stacked
- Paragraphs deploying 5+ named structural-vocabulary patterns in a single analytical pass

**Why this matters**: briefings are externally-facing analytical artifacts. The structural vocabulary's value depends on the prose remaining legible. Dense compound-noun stacking and vocabulary-deployment overload mean the message gets lost even when the analysis is sound.

## Five Rules — Apply on Every Briefing

### Rule 1: Compound-noun density limit

**Maximum 2 multi-hyphen compounds per sentence.** If a sentence has 3+, restructure. Move one or more compounds into a separate sentence; replace one with a concrete entity acting concretely.

Failing: *"The cross-architecture cluster's pattern recognition acquires multi-temporal-scale operation."*
Passing: *"The pattern recognition now operates across three temporal scales. The cross-architecture cluster's coverage has widened accordingly."*

### Rule 2: Concrete-anchoring frequency

**Every 3 paragraphs of conceptual prose must include at least one concrete sentence** — a named entity (Putin, the Fed, the marketplace, Boeing, the CCP, FOMC) doing a specific concrete thing with a specific number or specific event. This is the briefing's analog of scholarly-writing.md's "strategic concreteness in abstract stretches" discipline.

Failing: three paragraphs in a row using only abstract subjects ("the configuration", "the marketplace's discrimination capacity", "the cross-architecture cluster").
Passing: one of those paragraphs ends with *"Brent settled $104.71 Monday on the back of this configuration"* or *"Putin's Tuesday statement made this concrete."*

### Rule 3: Vocabulary deployment density

**Maximum 3 named structural-vocabulary patterns deployed in any single analytical paragraph** (excluding the dedicated vocabulary display section, which lists all). When more than 3 patterns are relevant to a single analytical move, split into multiple paragraphs so each pattern carries weight rather than being stacked.

Failing: a paragraph that names Mode-Switch Disarticulation + Channel Decomposition + Partial-Coupling + Recursive Re-Disclosure + Disclosure-Mode Discount in one analytical pass.
Passing: that material distributed across 2-3 paragraphs, each foregrounding 1-3 patterns.

### Rule 4: Subject-verb concreteness

**Prefer concrete subjects** (Putin, the Fed, the marketplace, Trump, the CCP, ECOWAS, FOMC, named entities) **over abstract subjects** ("the chancellery-marketplace discrimination-gap", "the cross-architecture cluster's pattern recognition"). Abstract subjects are allowed in vocabulary-definition contexts and the Inference Engine section's conditional chains; elsewhere they require justification.

Failing: *"The cross-architecture cluster's pattern recognition acquires multi-temporal-scale operation."*
Passing: *"Across three architectures (Russia, Trump's, the Manhattan Project's), the same pattern now operates across three temporal scales."*

### Rule 5: Short declarative punch frequency

**Each deep-dive panel must include at least one short declarative sentence (≤15 words)** for rhythmic variation. Long compound-noun-dense sentences without rhythmic interruption flatten the analytical signal. This mirrors the scholarly-writing skill's "Short Declarative Punches" discipline.

Failing: a deep-dive of 6 paragraphs, each 40+ words, no rhythmic interruption.
Passing: same deep dive with at least one *"This is the third instance."* or *"The marketplace priced it within ninety minutes."* among the long sentences.

## QC Checklist — New Items (post-generation, pre-publish)

In addition to the existing structural checks (12 section IDs, 2-4 deep dives, full vocabulary display, anomaly count, etc.), every generated briefing must clear these prose-coherence checks before publish:

- [ ] **Compound-noun density**: scan every sentence in the Overview, Unifying Thread, and Deep-Dive panels. Any sentence with 3+ multi-hyphen compounds? Restructure.
- [ ] **Concrete-anchoring frequency**: examine each 3-paragraph stretch of conceptual prose. Does at least one paragraph include a concrete-named-entity sentence? If not, insert one or restructure.
- [ ] **Vocabulary deployment density**: count named structural-vocabulary patterns per paragraph in the analytical prose (excluding the vocabulary display section). Any paragraph deploying 4+? Split.
- [ ] **Subject-verb concreteness**: scan paragraph-opening sentences. What is the grammatical subject? If abstract ("the X's Y", "the X-Y Z-gap"), justify or rewrite with a concrete subject.
- [ ] **Short declarative punches**: each deep-dive panel — count sentences ≤15 words. At least 1? If not, add one.

## Two-Pass Discipline

**Stage 1 — Post-generation, pre-Dave-review**: sub-agent or in-conversation pass applies the five rules to the freshly-generated HTML; rewrites failing sections. Default behavior on every briefing. Same workflow as `feedback_writing_reviewer.md` requires for externally-facing writing tasks.

**Stage 2 — Pre-publish, after Dave skims**: human/Claude pass catches remaining drift before `update-index.py` + `publish.sh`. Skip only on explicit "publish as-is" instruction.

## What This Discipline Does NOT Do

- **Does NOT reduce analytical depth.** The feedback_briefing_depth.md rule (full depth regardless of session length) still applies. Depth and coherence are not in tension; the discipline preserves depth while restoring legibility.
- **Does NOT strip the structural vocabulary.** The 42 named patterns + Cycle 2 candidates are load-bearing apparatus. The discipline applies to the prose *around* the vocabulary, keeping it legible enough that the vocabulary's analytical power lands rather than gets buried.
- **Does NOT collapse the deep-dive panels into shorter analyses.** Deep dives remain 3-6 paragraphs of sustained argument. The coherence is achieved within that length, not by abbreviating it.

The discipline is a craft constraint, not a content constraint. The briefing's analytical ambition stays the same; the prose carrying it gets tightened.

# ══════════════════════════════════════════════════════════════════
# FACTUAL VERIFICATION DISCIPLINE — Calibrated 2026-05-13 (after Briefings 038-039)
# ══════════════════════════════════════════════════════════════════

## The Cross-Year Structural-Template-Projection Failure Mode

On 2026-05-13 Dave flagged that Briefing 039 claimed Trump arrived in Riyadh that morning when he had actually landed in Beijing. Investigation revealed the sub-agent had projected May 2025 events onto May 2026 with high specificity. Affected fabrications: the Saudi Investment Forum + $600B + $142B deals + Gulf tour framing (all 2025 events); the Putin-Medinsky-Istanbul-Thursday delegation specifics (May 2025 template projected onto May 2026); Larry Fink on the Beijing delegation (actual delegation includes Musk, Cook, Huang). Briefing 038 had these fabrications projected forward as predictions; Briefing 039 had them as "confirmed" events.

**The named failure mode: Cross-Year Structural-Template Projection.** The sub-agent's web searches retrieved results that included both 2025 and 2026 content. The search engine does not always cleanly disambiguate, and the sub-agent's confidence calibration treated structurally consistent narratives as factually verified. The May 14-15, 2025 Putin-Medinsky-Istanbul event had the same structural template as the 2026 briefing narrative (Putin declines personal attendance; sends Medinsky-led delegation; Lavrov + Ushakov excluded; Zelenskyy frames as "decorative"; Trump signals from external location). The structural template repeated across years made the 2025 facts indistinguishable from 2026 facts under structural pattern matching.

**Why this matters:** tectonic briefings are externally-facing public artifacts. Factual errors damage credibility and contaminate the structural-vocabulary citation chain. The prose coherence discipline (calibrated 2026-05-13, above) does NOT catch factual errors. Adding factual verification explicitly is the architectural fix.

## Five Rules — Apply on Every Briefing

### Rule 1: Date-stamp every load-bearing factual claim

Each claim that depends on a specific date or event must include the specific date (e.g., "Trump landed in Beijing at 7:51 a.m. ET on May 13, 2026"; "April CPI released May 12, 2026 at 8:30 ET"). If a sub-agent cannot supply the date with high confidence, the claim is provisional and must be flagged for verification before publish.

### Rule 2: Cross-year disambiguation on all WebSearch results

When WebSearch returns content, verify the publication date and event date of each cited result. Any result without a clear 2026 timestamp is treated as historical-context, not as today's-event. If a search result references a recurring annual event (Gulf tours, FOMC meetings, Victory Day, Manhattan Project commemorations) or a named conference (Saudi Investment Forum, Davos, Munich Security Conference), the date of the SPECIFIC instance being referenced must be explicit.

**Specific anti-pattern**: search results from Wikipedia or topic-pages that aggregate multi-year content are particularly prone to causing this failure. When in doubt, prefer recent dated news articles over Wikipedia summaries for current-event verification.

### Rule 3: Structural-template projection check

Before claiming a 2026 event matches a 2025 structural template (Putin-Medinsky-Istanbul, Trump-Riyadh-Gulf-tour, Russian Victory Day mode-switch, FOMC pause-then-cut, OPEC+ production-cut announcement), require **independent 2026-specific confirmation** for the SPECIFIC instance. The same structural pattern occurring twice does not entitle the briefing to assume the second instance has happened; it must be empirically confirmed.

### Rule 4: Five highest-risk factual categories require explicit verification

Each requires verification (date + source + specific details) before publish:

- **Diplomatic events** (summits, talks, ceasefires, treaties): verify date, attendees, venue, outcomes
- **Economic data** (CPI, employment, GDP, market closes): verify exact numbers + release date + source publication
- **Major movements of named principals** (Trump, Putin, Xi, Netanyahu, etc.): verify location + time + activity for the specific day claimed
- **Vocabulary-promotion empirical anchors**: each cross-architecture instance must have a verified 2026 source. Promotion from Cycle 2 candidate to formal vocabulary requires 3 verified instances.
- **Cycle 2 candidate empirical anchors**: each candidate's naming event must be verified before the candidate enters the monitoring pool

### Rule 5: When in doubt, omit

A briefing that omits a fabrication-prone claim is structurally healthier than a briefing that includes a fabricated claim. The structural-vocabulary apparatus can absorb omitted material; it cannot easily absorb fabricated material. **The sub-agent's prior confidence is not a substitute for factual verification.**

## QC Checklist — Stage 1b (Factual Verification Pass)

Inserted between Stage 1 (prose coherence) and Stage 2 (pre-publish review). Apply before any briefing is published:

- [ ] **Date-stamp audit**: every load-bearing factual claim has a specific 2026 date attached or has been verified as a recurring established fact (e.g., "Mali Day 19" verified against an ongoing tracker).
- [ ] **Cross-year disambiguation**: every WebSearch result cited as a 2026 event has a verified 2026 timestamp. Wikipedia / topic-page aggregators have been cross-checked against recent dated reporting.
- [ ] **Structural-template projection check**: any claim that matches a known 2025 structural template (Trump-Gulf-tour, Putin-Medinsky-Istanbul, OPEC+ X, Fed-rate-decision Y) has independent 2026-specific confirmation. Flag and verify.
- [ ] **High-risk-category verification**: diplomatic events, economic data, principal movements, vocabulary-promotion anchors, and Cycle 2 candidate anchors have all been individually verified against current dated sources.
- [ ] **Omission preference**: any claim that resisted verification has been omitted rather than included.

## Two-Pass Discipline (updated)

**Stage 1 — Prose coherence (existing)**: apply five-rule coherence checks per the PROSE COHERENCE DISCIPLINE section above.

**Stage 1b — Factual verification (NEW 2026-05-13)**: apply the five-rule factual-verification checks above. Briefing does NOT advance to Stage 2 until Stage 1b passes.

**Stage 2 — Pre-publish review (existing)**: human/Claude pass catches remaining drift before `update-index.py` + `publish.sh`.

## What This Discipline Does NOT Do

- **Does NOT reduce analytical depth.** The feedback_briefing_depth.md rule still applies. Depth and factual accuracy are not in tension; the discipline preserves depth while restoring honesty.
- **Does NOT strip structural vocabulary candidates.** Candidates can still be named; their empirical anchors just have to be verified before the candidate enters monitoring.
- **Does NOT collapse deep-dive panels.** Deep dives remain 3-6 paragraphs of sustained argument. Verification operates at the claim level, not the section level.

## Retroactive Scope Check

After this calibration date, any briefing that surfaces a sub-agent's structural-pattern claim with a 2025 historical analog should be retroactively checked for cross-year projection. **Briefings 037, 038, 039 examined and remediated 2026-05-13** (038 received an erratum note; 039 received a surgical rewrite). **Earlier briefings have not yet been audited.** The Day-60 Cycle 2 audit should include a retroactive cross-year-projection check across Briefings 031-039 to verify no other instances of the failure mode are propagating downstream citations.
