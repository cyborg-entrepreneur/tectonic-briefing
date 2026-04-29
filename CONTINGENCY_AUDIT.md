# Contingency Audit — Protocol

**Purpose:** A meta-analysis of the Tectonic Briefing's Inference Engine, run every 30 daily briefings. The Contingency Audit traces the contingent possibilities posited by daily conditional chains, characterizes the structural mechanisms by which those chains break, and surfaces meta-principles about the limits of contingent forecasting under Knightian uncertainty.

**Last updated:** 2026-04-26 (drafted as protocol; first cycle scheduled for after Briefing 030)
**Cadence:** Every 30 daily briefings (~monthly)
**Output location:** `tectonic-briefing/synthesis/cycle-NNN.html` and `tectonic-briefing/synthesis/cycle-NNN.yaml`

---

## 1. Purpose and Epistemological Orientation

The Tectonic Briefing's Inference Engine generates conditional chains of the form *"If X holds → then Y becomes likely → which forces Z"* — roughly five per daily briefing, ~150 per 30-day cycle. These chains are contingent forecasts about how structural events will propagate.

A naive retrospective would ask: *what was our hit rate?* This is the wrong question, and asking it would degrade the briefing rather than improve it.

Dave Townsend's research program emphasizes the structural impossibility of forecasting under Knightian uncertainty: when the outcome space itself is unstable, no probability distribution can be assigned, and prediction is not a well-formed activity. The Contingency Audit proceeds from this premise. Its question is not *"did we get it right?"* but *"what structural mechanisms made the chains break?"*

This reframing turns the meta-analysis into a generative knowledge instrument. The break points themselves are the data. The taxonomy of break mechanisms is the analytical product. The meta-principles surfaced across cycles are exportable into Dave's research — particularly into the Three-Body ABM's "Moving Targets" theory paper, which models the same mechanisms (agentic novelty, competitive recursion) that produce the breaks.

The Contingency Audit is therefore best understood as **the empirical wing of the theoretical work on knowledge problems** — a long-running phenomenology of forecast invalidation, conducted on the briefing's own outputs.

## 2. Cadence and Trigger

The audit fires when the daily briefing count reaches a multiple of 30 (Briefings 030, 060, 090, etc.). Generated **the day after** the 30th briefing, alongside that day's daily briefing.

Cycle 1 fires after Briefing 030 (covering Briefings 001-030). Subsequent cycles cover the trailing 30 (Cycle 2: Briefings 031-060; Cycle 3: 061-090; etc.).

The audit does not replace a daily briefing. It is an additional artifact.

## 3. Required Reading (for the agent generating the audit)

Generate the Contingency Audit in **fresh context** via the Agent tool. The same depth-preservation logic that applies to daily briefings applies here, with greater force: the audit is reading 30 prior documents and synthesizing across them.

The agent must read in full:
1. This document (`CONTINGENCY_AUDIT.md`)
2. `CLAUDE.md` — the daily briefing's editorial protocol
3. `STRUCTURAL_CONCEPTS.md` — the 5 meta-categories and current vocabulary
4. All 30 briefings in the cycle window
5. The previous cycle's YAML artifact (Cycle 2+) — to enable cross-cycle promotion of meta-principles
6. `~/workflow/auto-memory/MEMORY.md` and selected project memories — to preserve research-program connection

## 4. What This Is NOT

To prevent drift toward conventional retrospection, the agent must explicitly avoid:

- **Hit-rate scorecards.** No "we got 47% right." Accuracy framing is a category error under Knightian uncertainty.
- **Generic improvement bullet points.** The audit's improvements emerge from the break-point taxonomy, not from generic editorial advice.
- **Forecasting accuracy improvement as a goal.** The audit characterizes failure structures; it does not try to make next cycle's chains "more accurate."
- **Praise of the briefing's coverage.** The audit is honest, not affirming.
- **Confirmation-biased classification.** Type-I and Type-II breaks are theoretically interesting; Type-V (velocity miscalibration) is probably most common. Resist the pull toward the loaded categories.

## 5. Document Structure

The audit produces nine sections, in order:

### 5.1 Headline (200 words max)

A tight standalone summary readable independent of the rest. Names: the dominant break-point modes this cycle, the most consequential meta-principle surfaced, and the 3-5 recalibrations the next 30 daily briefings should absorb. **This section closes the feedback loop into daily practice.** If a reader reads only this section, the audit has done its job.

### 5.2 Inference Inventory

A structured table of every conditional chain extracted from the cycle's 30 briefings. Roughly ~150 entries. Each entry tagged with:

- `chain_id` (briefing-number + index)
- Originating briefing and lens
- The chain's text (X → Y → Z)
- Structural patterns invoked
- Decomposed conditions (X, Y, Z separately)

### 5.3 Outcome Classification

For each chain, one of:

- **Held** — chain played out as predicted
- **Held (Spurious)** — outcome occurred but via a mechanism the chain did not specify (Type-VII; see below)
- **Failed-Y** — intermediate step did not occur
- **Failed-Z** — terminal step did not occur (Y did)
- **Pre-empted** — a new event reshaped conditions before the chain could play
- **Inverted** — the opposite of the predicted outcome occurred (most diagnostically valuable)
- **Indeterminate** — insufficient time, data, or observability

Held (Spurious) is treated as a partial failure for analytical purposes despite the surface-level "success" — the briefing's structural understanding was wrong even though the outcome arrived.

### 5.4 Break Point Taxonomy (the analytical core)

Every chain not classified Held gets a break-type assignment. Types I-VII are defined in §6 below. Multiple types may apply to a single chain; the dominant one is named first.

This section is the audit's central intellectual product. It should produce a frequency distribution across Types I-VII for the cycle, plus per-type case discussion (3-5 representative chains per type with brief structural explanation).

### 5.5 Meta-Principles

Across the break-point taxonomy, what generalizes? Each meta-principle is a structural claim about the conditions under which contingent forecasting breaks down, supported by 2+ cited chains from the cycle.

Meta-principles entering the canonical list must clear two bars:
- **Cycle 1:** named provisionally with cited supporting chains
- **Cycle 2+:** promoted to canonical only after recurring across ≥2 cycles

Provisional principles that do not recur within 3 cycles are retired. The same accumulation discipline that applies to the daily vocabulary applies here at the meta-level — without it, this section becomes the next inflation site.

### 5.6 Vocabulary Curation

Apply the 30-day sunset rule:
- Concepts named in the cycle window with **zero substantive re-citation** are flagged for retirement
- Concepts retired in prior cycles that re-appeared substantively get reactivated
- Currently deferred meta-category candidates (e.g., META-6 Verification Asymmetry) get a forced decision: promote with two instantiations, or formally table with a written reopen-condition

This section produces concrete updates to `STRUCTURAL_CONCEPTS.md`, applied immediately after the audit publishes.

### 5.7 Anomaly Accounting

For every anomaly named across the cycle's daily briefings:

- **Resolved** — the absence has been filled; characterize how
- **Silently died** — the absence stopped being tracked without resolution
- **Persistently absent** — the anomaly continues to hold; assess whether the persistence is itself diagnostic

This section is the briefing's epistemic honesty mechanism. Anomalies that silently die without acknowledgment are evidence of attention drift.

### 5.8 Research Program Connection

Explicit, substantive paragraphs (2-3) connecting the cycle's findings to Dave's active research:

- **Three-Body ABM "Moving Targets"** — Type-I and Type-II break distributions are direct empirical input
- **Glimpse ABM** — break-point dynamics in innovation forecasting under uncertainty
- **Cyborg Entrepreneurship** — the audit itself instantiates the cyborg ensemble (AI generates pattern recognition; human curates and redirects)
- **Decision Queue, GCM AI Agents, Qoheleth, Sheaf theory** — connect where structurally warranted; do not force

Output should be citation-ready paragraphs Dave can lift into manuscripts.

### 5.9 Recalibrations for the Next 30

3-5 concrete, actionable adjustments to apply to the next 30 daily briefings. Each:
- States the change in one sentence
- Cites the empirical basis from this cycle (which break-points or meta-principles motivate it)
- Names the tradeoff
- Specifies how to verify it took hold (what should be visible in Briefings 031-060 if the recalibration worked)

## 6. Break Point Taxonomy — Full Definitions

**Type-I — Agentic Novelty Break.** A new agent or unprecedented action shifts the outcome space. The chain assumed an action set; the actual action lay outside it. *Example pattern:* a chain conditioning on "regulators will act" when a novel coalition (industry self-regulation, foreign sovereign, court system) acts first and forecloses the predicted causal path. Type-I is the **Knightian** failure mode in its purest form: the world surprised us, and no probability could have been assigned to the surprise because the relevant action was not in the conceived space.

**Type-II — Competitive Recursion Break.** An agent anticipates the prediction (or anticipates others' anticipations of it) and acts to invalidate the chain. Hayek-Lucas-Goodhart territory. *Example pattern:* a chain predicting "Iran will close Hormuz to extract leverage" fails because Iran reads the consensus prediction and adopts the opposite tactic to preserve optionality. Type-II is the **reflexive** failure mode: prediction becomes performative; circulation of the forecast is itself a causal input. Type-II compounds in domains with high price-discovery (markets, prediction markets, signaling games) because the chain's logic is itself an input to the agents the chain is conditioning on.

**Type-III — Coupling Assumption Failure.** The chain assumed a binding link between two domains; the link wasn't there. *Example pattern:* "If oil hits $140 → European industrial stress → political realignment" fails because the European-industrial-to-political linkage has hollowed (this cycle's Coupling Failure pattern instantiates here). The chain treated as constraint what was in fact decoupled.

**Type-IV — Buffer Revelation.** A buffer treated as constant turned variable mid-chain. *Example pattern:* SPR drawdown assumed; SPR exhausted faster than chain modeled. Type-IV is structurally adjacent to the Buffer Collapse pattern but distinct: Buffer Collapse names the empirical event; Type-IV names the chain's failure to anticipate the buffer's variability.

**Type-V — Velocity Miscalibration.** Direction right, timing wrong. The chain's structural diagnosis was correct but the temporal scale was off (faster or slower than predicted). *Example pattern:* "AI governance will collapse within Q2" — collapse trajectory correct, timeline compressed or extended. Type-V is theoretically less loaded but probably empirically dominant. The audit should report Type-V honestly even when the diagnosis "was structurally right" — temporal accuracy is a real cost.

**Type-VI — Categorical Drift.** The categories the chain depended on shifted under it. *Example pattern:* "If China responds → escalation in trade-war terms" fails because "trade-war" as a category dissolved into a different framework (e.g., decoupling, supply-chain reorganization) that the chain didn't condition on. Type-VI overlaps with the existing Category Collapse pattern but operates at the chain-construction level: the chain was valid only as long as the categorical scaffolding held.

**Type-VII — Spurious Hit.** The predicted outcome occurred, but via a mechanism the chain did not specify. The chain "hit" but its underlying structural understanding was wrong. *Example pattern:* "If Mythos thread escalates → regulatory window opens → AI governance reform" — regulatory action occurs but driven by an unrelated incident (data breach, lawsuit) rather than by the Mythos thread. Type-VII is structurally important because it identifies the briefing's invisible compounding overconfidence: surface-level wins that mask analytical errors. The audit should flag Type-VII aggressively because it is the failure mode the briefing has the strongest incentive not to see.

## 7. YAML Artifact Schema

The audit produces a structured YAML at `tectonic-briefing/synthesis/cycle-NNN.yaml`. This is the load-bearing accumulating artifact. Its schema (abbreviated):

```yaml
cycle: 001
date_generated: 2026-05-05
briefings_covered: [001, ..., 030]
date_range: { start: 2026-04-05, end: 2026-05-04 }

inference_inventory:
  - chain_id: 001-ie-1
    briefing: 001
    lens: economic
    text: "If Hormuz remains closed past mid-April → oil $140-170 → European industrial stress"
    patterns_invoked: [chokepoint-cascade, buffer-collapse]
    conditions: { X: "...", Y: "...", Z: "..." }

outcome_classifications:
  - chain_id: 001-ie-1
    outcome: failed_at_Y
    actual: "Hormuz remained closed; Brent $85-110; never reached $140"
    classified_via: empirical_check

break_points:
  - chain_id: 001-ie-1
    primary_type: type_v_velocity_miscalibration
    secondary_type: null
    note: "Direction right; magnitude/speed off; ceiling lower than chain modeled"

meta_principles:
  - id: mp-001
    statement: "Chains terminating in Iranian behavior systematically break at step Z because Iran's strategic position is optionality, not commitment"
    instances: [001-ie-1, 008-ie-2, 014-ie-3]
    status: provisional   # canonical after recurring in cycle-002+

vocabulary_curation:
  retired:
    - concept: buffer-collapse
      reason: "named in 001; zero substantive reuse 002-030"
      reactivation_condition: "two instantiations within 30 days"
  reactivated: []
  meta_6_decision:
    decision: tabled
    condition: "two more verified Verification-Asymmetry instantiations within 30 days"

anomaly_accounting:
  resolved: [...]
  silently_died: [...]
  persistently_absent: [...]

research_connections:
  three_body_abm: "Citation-ready paragraph..."
  glimpse_abm: "Citation-ready paragraph..."

recalibrations_for_next_30:
  - change: "Conditional chains touching state actors with optionality must include a named wildcard-action slot"
    basis: "Type-I breaks concentrated in state-actor chains (8 of 14 Type-I cases)"
    tradeoff: "Adds verbosity to chains; reduces false-confidence in step Z"
    verification: "Briefings 031-060 should show 80%+ of state-actor chains with explicit wildcard slot"
```

## 8. Cross-Cycle Discipline

The audit's own meta-level is the next inflation site. Discipline:

- **Provisional → Canonical promotion** requires recurrence across ≥2 cycles
- **Provisional retirement** if no recurrence within 3 cycles
- **Canonical retirement** if a previously-canonical principle fails to apply in 2 consecutive cycles
- **Cycle 2+ must read Cycle 1's YAML programmatically** to avoid re-deriving findings the audit already produced

The canonical meta-principles list is the audit's most valuable durable artifact. It should remain small (target: 5-10 canonical principles after 3 cycles).

## 9. Visual Signature

The audit's HTML must be visually distinct from daily briefings so the artifact-type is obvious at a glance:

- **Accent color:** deep amber (`#c89545`) instead of daily blue (`#4b8ef2`)
- **Masthead:** "Contingency Audit — Cycle NNN" instead of "Tectonic Briefing No. NNN"
- **Subtitle:** "Meta-analysis of contingent forecasting under Knightian uncertainty"
- **Background, typography, body text colors:** identical to daily briefing (continuity within the system)
- **Breakpoint frequency chart:** include a small visualization of Type-I through Type-VII distribution at the top of §5.4

## 10. Failure Modes to Watch

These are the audit's own pathologies to monitor cycle-over-cycle:

1. **Recursive accumulation in meta-principles.** Every cycle adds meta-principles; without the promotion discipline (§8), the canonical list bloats and loses its load-bearing character.
2. **Confirmation bias toward Type-I/II.** They're the theoretically loaded breaks. Type-V is probably most common. If a cycle's break distribution shows <20% Type-V, suspect under-classification.
3. **Spurious-Hit blindness (Type-VII).** The briefing has the strongest incentive not to see Type-VII because it converts apparent wins into analytical losses. The audit should aggressively look for Type-VII; under-detection is the silent failure mode.
4. **Unread-artifact problem.** A 4000-word monthly document that nobody acts on is a curiosity. The §5.1 Headline and §5.9 Recalibrations are the closing-of-the-loop sections; if they aren't tight and actionable, the audit has failed regardless of its analytical depth.
5. **Type-I / Type-II conflation.** Tempting to merge into "things-we-couldn't-predict." Resist. Maintaining the distinction is what makes the meta-principles theoretically generative for Three-Body and Glimpse rather than just descriptive of the briefing.

## 11. Quality Checklist

After generation, verify:

- [ ] §5.1 Headline ≤200 words and standalone-readable
- [ ] §5.2 Inference Inventory contains every conditional chain from the cycle's 30 briefings
- [ ] §5.3 Outcome Classification covers every chain in the inventory
- [ ] §5.4 Break Point Taxonomy reports a frequency distribution across all 7 types
- [ ] §5.4 Includes 3-5 representative cases per type (where the type occurred)
- [ ] §5.5 Meta-Principles each cite ≥2 supporting chains
- [ ] §5.5 Provisional/canonical status correctly assigned per §8
- [ ] §5.6 Vocabulary Curation produces concrete updates to `STRUCTURAL_CONCEPTS.md`
- [ ] §5.6 META-6 candidate either promoted or formally tabled with reopen-condition
- [ ] §5.7 Anomaly Accounting covers every named anomaly in the cycle's briefings
- [ ] §5.8 Research Program Connection produces 2-3 citation-ready paragraphs
- [ ] §5.9 Recalibrations are 3-5 specific, actionable, with tradeoffs and verification criteria
- [ ] YAML artifact written to `tectonic-briefing/synthesis/cycle-NNN.yaml`
- [ ] HTML artifact uses amber accent (`#c89545`) and distinct masthead
- [ ] Type-V breaks are not under-classified (≥20% of break-point distribution unless empirically justified)
- [ ] Type-VII (Spurious Hit) is actively probed, not just acknowledged

## 12. First Cycle Note

Cycle 1 fires after Briefing 030 (target: 2026-05-05, assuming uninterrupted daily cadence). It will face one structural challenge subsequent cycles will not: there is no prior YAML to read.

For Cycle 1 specifically:
- Meta-principles begin as provisional with no canonical list
- Vocabulary curation operates against `STRUCTURAL_CONCEPTS.md` as it stands at cycle generation
- The recalibrations section should be modest in scope; aggressive recalibration based on a single cycle of data would over-fit
- Research-program connections should be exploratory; subsequent cycles will produce more disciplined claims

Cycle 1's primary value is establishing the YAML schema and the break-point taxonomy as working tools. The analytical accumulation begins in earnest at Cycle 2.

---

## Appendix: Relationship to the Daily Briefing Protocol

The Contingency Audit does not modify the daily briefing protocol. It produces inputs the daily briefing's Inference Engine can absorb (via §5.9 Recalibrations) and updates to the structural vocabulary (via §5.6 Vocabulary Curation). The daily briefing's `CLAUDE.md` and `STRUCTURAL_CONCEPTS.md` remain canonical; the audit operates on their outputs and produces refinements to feed back in.

The two protocols are intentionally orthogonal. The daily briefing produces structural pattern recognition at high cadence; the audit produces meta-principles at low cadence. The cyborg ensemble metaphor named in `CLAUDE.md` applies recursively here: AI generates pattern recognition (daily briefings) and pattern-of-pattern recognition (audit); human (Dave) provides the periodic re-framing that prevents either layer from collapsing into recursive narrowing.
