# Quarterly Portfolio Review — Protocol

**Purpose:** Analyze the Tectonic Briefing as a complete public knowledge
portfolio: what it has attended to, what it has learned, what it repeatedly
misses, which sources and concepts dominate it, and how the production system
should change.

**Cadence:** Every 90 nominal briefings, after the corresponding 30-briefing
Contingency Audit.

**Output:** `synthesis/quarter-NNN.yaml` and
`synthesis/quarter-NNN.html`.

The Quarterly Portfolio Review complements the Contingency Audit. The
Contingency Audit studies conditional-chain failure. The portfolio review
studies the entire artifact ecology. Do not force coverage, source, prose, or
concept-governance questions into the break-point taxonomy.

## 1. Corpus boundary

Use dated HTML files as the units of analysis. The first review includes every
published artifact from Briefing 001 through Briefing 090, including duplicate
canonical numbers. Report:

- nominal number range;
- dated artifact count;
- date range;
- duplicate and missing canonical numbers;
- excluded files, if any, with reasons.

The first review therefore covers 91 dated artifacts, not 90.

## 2. Required evidence

Read or deterministically extract:

1. Every dated briefing in scope.
2. `STRUCTURAL_CONCEPTS.md` and `concepts/registry.json`.
3. All completed Contingency Audit YAML artifacts.
4. The daily production protocol and active calibration summary.
5. The full anomaly ledger produced for the latest cycle.

Preserve the deterministic extraction as
`synthesis/_raw/quarter-NNN-corpus.json`. Every numeric claim in the public
HTML must be reproducible from that file or from a named Cycle YAML.

## 3. Required analyses

### 3.1 Theme architecture and evolution

Identify durable themes, their empirical anchors, and how their treatment
changed across cycles. Separate event frequency, structural-pattern frequency,
genuine conceptual development, and recursive restatement. Consider at least
one counter-reading for every claimed core theme.

### 3.2 Lens, domain, and geographic balance

Report item counts and density by analytical lens, cycle, domain family, and
geographic region. Test topic rotation rather than accepting footer attestations
at face value. Name persistent corridors and persistent blind spots.

### 3.3 Source ecology

Report total and unique external links, unique source domains, top-domain
concentration, source-type shares where classifiable, repeated dependence on a
small set of domains, and changes across cycles. Source diversity is not
automatically source quality; interpret concentration against the claims.

### 3.4 Structural-vocabulary health

Report concept citations and co-occurrences by cycle. Distinguish load-bearing
recurring patterns, context-bound but legitimate patterns, synonyms or
near-duplicates, source-briefing-only concepts, and candidates for retirement,
merger, or definition repair. Frequency alone does not justify retention.

### 3.5 Anomaly lifecycle

Use complete cycle ledgers to report resolved, silently died, persistently
absent, and open/not-yet-due anomalies. Test whether anomaly tracking is
cumulative or merely rhetorical.

### 3.6 Research-program and public-writing fit

Classify each claimed research connection:

- **Direct:** bears on an active construct, mechanism, boundary condition, or
  empirical design in Dave's research.
- **Adjacent:** a disciplined analogy or useful bridge that does not directly
  change an active argument.
- **Speculative:** depends mainly on shared vocabulary or a loose metaphor.
- **None:** no research surface is touched.

Only Direct connections belong in public-facing Research Program Relevance or
article-candidate promotion. Adjacent connections may remain in the private TMS
bridge ledger. Speculative connections should normally be omitted.

### 3.7 Production and reading quality

Measure and inspect lens density, word count, deep dives, section completeness,
source-archive density, inference-chain count and read-mode compliance,
prose-density proxies, factual corrections and errata, confidentiality
incidents, tag/schema drift, and build or numbering defects. Do not equate
length with depth or density with quality.

### 3.8 Recommendations

Produce 5–10 changes. Each names the observed problem, evidence, intervention,
cost or tradeoff, and a verification criterion for the next quarter. Separate
content selection, analytical method, source discipline, concept governance,
writing/design, and tooling.

## 4. Output structure

The YAML is load-bearing and contains the corpus manifest, reproducible metrics,
cycle comparisons, theme findings and counter-readings, source ecology,
vocabulary health, anomaly lifecycle, research-fit audit, production-quality
audit, recommendations, and next-quarter tests.

The HTML is a public-readable synthesis with a deep-amber visual identity
distinct from daily briefings and Contingency Audits.

## 5. Quality gates

- [ ] Every dated artifact in scope appears exactly once.
- [ ] Every aggregate number is reproducible from the raw corpus JSON or a
      named Cycle YAML.
- [ ] Theme findings separate frequency from conceptual importance.
- [ ] Geographic and source claims include an Unknown category; no denominator
      is silently discarded.
- [ ] Concept-retirement recommendations consider discriminant value, not only
      citation count.
- [ ] The research-fit audit applies Direct/Adjacent/Speculative/None and does
      not promote an Adjacent bridge into a public article.
- [ ] Recommendations include tradeoffs and measurable next-quarter tests.
- [ ] The public artifact contains no confidential editorial, review, or
      collaborator-state material.

## 6. Relationship to daily production

The portfolio review may update `CLAUDE.md`,
`STRUCTURAL_CONCEPTS.md`, validation scripts, and the active calibration
summary—but only where a finding is supported by the corpus. A quarterly review
that produces no operational change has not closed the loop.
