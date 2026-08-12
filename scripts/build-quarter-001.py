#!/usr/bin/env python3
"""Build the first 90-briefing portfolio review."""

from __future__ import annotations

import hashlib
import html
import json
from collections import Counter
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "synthesis/_raw/quarter-001-corpus.json"
CYCLE3 = REPO / "synthesis/cycle-003.yaml"
YAML_OUT = REPO / "synthesis/quarter-001.yaml"
HTML_OUT = REPO / "synthesis/quarter-001.html"


LENS_NAMES = {
    "ge": "Geopolitical", "te": "Technological", "ec": "Economic",
    "sc": "Scientific", "so": "Social", "en": "Environmental",
    "ig": "Institutional", "li": "Liminal",
}


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def pct_change(start: float, end: float) -> float:
    return round((end / start - 1) * 100, 1)


def source_shares(values: dict) -> dict:
    total = sum(values.values())
    return {key: round(value / total * 100, 1) for key, value in values.items()}


def cycle_metrics(summary: dict) -> list[dict]:
    rows = []
    for cycle, values in summary["by_cycle"].items():
        lens_total = sum(values["lens_items"].values())
        rows.append({
            "cycle": int(cycle), "dated_artifacts": values["dated_artifacts"],
            "date_range": values["dates"], "lens_items": values["lens_items"],
            "lens_total": lens_total, "themes": values["themes"],
            "regions": values["regions"], "mean_analytic_words": values["mean_analytic_words"],
            "mean_lens_items": values["mean_lens_items"],
            "mean_external_links": values["mean_external_links"],
            "mean_source_domains": values["mean_source_domains"],
            "links_per_lens_item": round(values["mean_external_links"] / values["mean_lens_items"], 3),
            "deep_dives": values["deep_dives"], "anomalies": values["anomalies"],
            "extracted_chains": values["chains"],
            "source_type_counts": values["source_type_domain_mentions"],
            "source_type_shares": source_shares(values["source_type_domain_mentions"]),
            "top_source_domains": values["top_source_domains"],
            "top_concepts": values["top_concept_document_presence"],
        })
    return rows


def bar_rows(values: dict, labels: dict | None = None, limit: int | None = None) -> str:
    labels = labels or {}
    pairs = sorted(values.items(), key=lambda item: item[1], reverse=True)
    if limit:
        pairs = pairs[:limit]
    maximum = max((value for _, value in pairs), default=1)
    return "".join(
        f'<div class="bar"><span>{esc(labels.get(key, key.replace("_", " ").title()))}</span>'
        f'<i><b style="width:{100 * value / maximum:.1f}%"></b></i><em>{value}</em></div>'
        for key, value in pairs
    )


def build_payload(raw: dict, cycle3: dict) -> dict:
    summary = raw["summary"]
    cycles = cycle_metrics(summary)
    c1, c2, c3 = cycles
    b090 = next(record for record in raw["records"] if record["number"] == 90)
    canonical_chains = {
        1: 136,
        2: 129,  # prior curated audit includes four supplemental thread/deep-dive chains
        3: 155,
    }
    themes = [
        {
            "name": "Enclosure and governance lag",
            "evidence": "Commons Enclosure appears in 82 of 91 artifacts; Governance Vacuum rises from a marginal Cycle 1 presence to 29 of 31 Cycle 3 artifacts.",
            "evolution": "The frame moved from discrete chokepoints toward AI, minerals, data, and institutional capacity, but Governance Vacuum became too general to discriminate.",
            "counter_reading": "The prevalence may partly measure the vocabulary supplied to the writer rather than independent recurrence in the world.",
        },
        {
            "name": "Instruments that stop tracking their referents",
            "evidence": "Markets/macro is the largest multi-label theme (1,897 assignments); labor/demography rises 116 → 165 → 225 across cycles, while Cycle 3 repeatedly juxtaposes improving gauges with deteriorating substrates.",
            "evolution": "The treatment sharpened from market-price anomalies into measurement design: occupation levels versus entry rates, unemployment versus participation, and policy declarations versus operations.",
            "counter_reading": "The contradiction format can over-select striking divergences and under-report cases in which instruments work normally.",
        },
        {
            "name": "Physical constraints return beneath digital abundance",
            "evidence": "Infrastructure/cyber assignments rise 457 → 492 → 597; environmental lens items rise 67 → 78 → 130; robotics rises 77 → 90 → 106.",
            "evolution": "AI coverage increasingly moves downstream into electricity, minerals, telemetry, industrial deployment, labor, and regulation rather than model launches alone.",
            "counter_reading": "Keyword co-classification inflates overlaps, so the direction is stronger evidence than the absolute assignment count.",
        },
        {
            "name": "Institutional form persists after work-doing power departs",
            "evidence": "Institutions/governance remains among the largest themes (1,497 assignments), while anomaly cards repeatedly track votes, courts, inspection regimes, and declarations that fail to alter operations.",
            "evolution": "The corpus progressed from naming hollowing to separating disclosure, operational, enforcement, and coordination channels.",
            "counter_reading": "Repeated use of Hollowing and Coupling Failure can redescribe weak implementation without identifying a distinct causal mechanism.",
        },
        {
            "name": "Orientation under flux becomes an object of study",
            "evidence": "The archive contains 420 canonical audited chains across three cycles. Cycle 3 labels all 146 prospective chains O and yields zero explicit CONFIRMS/REFUTES fields.",
            "evolution": "Cycle 1 classified break mechanisms, Cycle 2 introduced read mode, and Cycle 3 exposed metric adaptation and release-field saturation.",
            "counter_reading": "This is partly endogenous: the briefing's own protocol created the pattern it later analyzed.",
        },
    ]
    research_fit = [
        {"fit": "direct", "surface": "Task co-evolution / Shifting Sands", "items": ["Entry-level AI-exposed work declines while occupational aggregates hold (084–087).", "Humanoid deployment scales first in narrow, repeatable industrial tasks (088).", "Domestic versus metered model access changes adaptation rates (083)."], "public_action": "Retain as research relevance; these bear directly on task-boundary migration, measurement, and capability access."},
        {"fit": "direct", "surface": "Epistemic complementarity model", "items": ["Adversarial telemetry can manufacture the evidence an autonomous agent uses (090).", "A soft CPI print with falling real pay supplies a multiple-hypothesis benchmark (090).", "Agent-security norms are being written by deployers while frontier builders remain outside the coalition (089)."], "public_action": "Retain only when the item changes a mechanism, benchmark, or observable in the model."},
        {"fit": "adjacent", "surface": "Cross-domain structural bridges", "items": ["Diplomatic pauses, court channels, and climate-finance cases often share form with delegation or complementarity problems."], "public_action": "Move to the private bridge ledger; do not present analogy alone as manuscript relevance."},
        {"fit": "speculative", "surface": "Vocabulary-only mappings", "items": ["Claims that an unrelated event supports a paper because both can be described as a three-body configuration, coupling failure, or polymathy."], "public_action": "Omit unless a construct, mechanism, boundary condition, or design variable is changed."},
        {"fit": "none", "surface": "Operational and confidential work", "items": ["Routine editorial workload, manuscript handling, and ordinary market or diplomatic updates with no research surface."], "public_action": "Keep out of the public artifact; operational priorities belong in the private morning briefing."},
    ]
    recommendations = [
        {"area": "tooling", "problem": "Canonical numbering is not a unique key.", "evidence": "91 dated artifacts cover nominal 001–090; 050, 055, and 062 are duplicated, while 056 and 057 are missing.", "intervention": "Make the ISO date the primary archive key and require future canonical numbers to be unique and monotonic.", "tradeoff": "Historical URLs and displayed numbers remain irregular and must be preserved.", "test": "Briefings 091–180 produce zero duplicate or missing new numbers; validator fails before publish on a new collision."},
        {"area": "writing/design", "problem": "Coverage grew while reading burden stayed excessive.", "evidence": "Mean lens items rose 25.17 → 29.13; mean analytic words remain 11,617 in Cycle 3. Briefing 090 delivered 26 items, 31 external links, and three deep dives in 6,245 words.", "intervention": "Use the Briefing 090 architecture as the default: target 6,000–9,000 analytic words, 24–28 lens items, and 2–4 deep dives.", "tradeoff": "Less space for exhaustive thread restatement.", "test": "At least 75% of the next quarter lands in range without section or source failures."},
        {"area": "sources", "problem": "Source density fell as topic density rose.", "evidence": "Mean external links fell 28.50 → 21.97 while lens items rose; links per lens item fell 1.132 → 0.754. Scholarly-domain share fell 3.6% → 2.1%, while official-primary share improved.", "intervention": "Require at least one directly supporting source per lens item and a primary/scholarly source for every load-bearing scientific, regulatory, or macro claim when available.", "tradeoff": "Slower production and occasional omission of weakly sourced but interesting items.", "test": "Quarter 2 links per lens item ≥1.0; official+scholarly domain share ≥15%; no Wikipedia domain in the top 15."},
        {"area": "analytical method", "problem": "Orienting fields became too easy to satisfy.", "evidence": "Cycle 3 has 147 O, 8 H, 0 R reads and 0/155 explicit CONFIRMS/REFUTES fields.", "intervention": "Require CONFIRMS, REFUTES, and at most three discriminating release paths with observable tells.", "tradeoff": "Chains become more compact and less rhetorically exhaustive.", "test": "100% of Briefings 091–120 chains pass fields; the next audit can identify genuine failures without outcome-derived relabeling."},
        {"area": "anomalies", "problem": "Negative-space tracking is still mostly rhetorical.", "evidence": f"Cycle 3 ledger: {cycle3['anomaly_accounting']['counts'].get('resolved', 0)} resolved, {cycle3['anomaly_accounting']['counts'].get('persistently_absent', 0)} persistent, {cycle3['anomaly_accounting']['counts'].get('silently_died', 0)} silently died, and {cycle3['anomaly_accounting']['counts'].get('open_not_yet_due', 0)} open.", "intervention": "Give every anomaly a stable ID, next observable, and fair review date; require explicit carry-forward or closure.", "tradeoff": "Recurring absences consume daily space.", "test": "Silent-death share falls below 25% in Cycle 4 and every closure links to a later issue."},
        {"area": "concept governance", "problem": "The vocabulary contains both dead and over-broad concepts.", "evidence": "Emergent Concealment appears in one of 91 documents; Governance Vacuum appears in 29 of 31 Cycle 3 artifacts; Commons Enclosure appears in 82 of 91.", "intervention": "Retire Emergent Concealment from new use; place Sabbath Visibility on watch; require institution + missing capacity + consequence for Governance Vacuum; require a literal access gate for Commons Enclosure.", "tradeoff": "Historical continuity becomes more explicit and some familiar shorthand disappears.", "test": "No retired-concept invocation; every Vacuum/Enclosure use passes its discriminant; no concept appears in >80% of quarter documents without review."},
        {"area": "research fit", "problem": "Analogy has sometimes been promoted as direct research relevance.", "evidence": "The corpus frequently maps geopolitical, climate, and legal cases into active research streams even when no construct, mechanism, boundary, or design decision changes.", "intervention": "Apply Direct/Adjacent/Speculative/None before publishing; only Direct survives in public Research Program Relevance.", "tradeoff": "Fewer cross-domain bridges appear publicly.", "test": "Every public research bridge names the exact construct/mechanism/design variable changed; quarterly audit finds zero adjacent-as-direct cases."},
        {"area": "geography", "problem": "The portfolio remains corridor-heavy.", "evidence": "North America leads all cycles; Cycle 3 MENA=224 and Europe=213, while South/Southeast Asia=46 and Sub-Saharan Africa=79. Latin America improves 11 → 17 → 45.", "intervention": "Use a rolling seven-issue coverage debt, not a daily quota, for South/Southeast Asia and Sub-Saharan Africa; keep an explicit Unknown bucket.", "tradeoff": "Some days will add a lower-salience item to correct a persistent blind spot.", "test": "Each under-covered region appears substantively in at least five of every seven issues and Unknown assignments decline 20%."},
        {"area": "schema", "problem": "Historical markup drift obstructs deterministic audit.", "evidence": "Inference wrappers span .chain-block, .inf, and .chain; Briefing 080 embeds vocabulary inside the anomaly section; six files reuse O/R/H for epistemic status.", "intervention": "Freeze one semantic schema (section/article, data IDs, READ and OBS/INF/HYP namespaces) and validate it prospectively from Briefing 091.", "tradeoff": "Older files remain heterogeneous and require compatibility parsing.", "test": "All new files parse with one selector; no namespace or section-boundary compatibility branch is triggered."},
    ]
    return {
        "quarter": 1, "date_generated": "2026-08-12",
        "nominal_briefings": [1, 90], "dated_artifacts": 91,
        "date_range": summary["date_range"],
        "corpus_manifest": {
            "duplicates": summary["duplicate_numbers"], "missing": summary["missing_numbers"],
            "excluded": [], "raw_extract": str(RAW.relative_to(REPO)),
            "raw_extract_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
            "mechanically_extracted_chains": sum(c["extracted_chains"] for c in cycles),
            "canonical_audited_chains": sum(canonical_chains.values()),
            "chain_count_note": "Cycle 2's prior curated audit includes four supplemental thread/deep-dive chains outside the mechanical card wrappers.",
            "total_anomalies_extracted": sum(c["anomalies"] for c in cycles),
        },
        "headline": "The briefing evolved from event-dense scanning into a useful instrument for detecting moved baselines and broken measurement, but breadth, source density, concept discrimination, and falsifiability now need stronger constraints.",
        "cycle_comparison": cycles,
        "latest_compact_format": {
            "briefing": 90, "analytic_words": b090["analytic_word_count"],
            "lens_items": b090["lens_item_count"], "external_links": b090["external_link_count"],
            "deep_dives": b090["deep_dive_count"],
        },
        "themes": themes,
        "lens_balance": {
            "whole_corpus": summary["lens_items"],
            "finding": "Environmental and Social coverage strengthened materially; Geopolitical and Liminal no longer dominate every cycle, although North America remains the persistent regional corridor.",
        },
        "regional_balance": {"whole_corpus": summary["regions"], "by_cycle": {c["cycle"]: c["regions"] for c in cycles}},
        "source_ecology": {
            "unique_domains": summary["unique_source_domains"],
            "domain_mentions": summary["source_domain_mentions"],
            "domain_hhi": summary["source_domain_hhi"],
            "finding": "No single-domain concentration problem is visible, but support density and scholarly-source share decline while official-primary share improves.",
        },
        "vocabulary_health": {
            "document_presence": summary["concept_document_presence"],
            "load_bearing": ["Commons Enclosure", "Channel Decomposition", "Peripheral Assertion", "Capability Opacity"],
            "definition_repair": ["Governance Vacuum", "Commons Enclosure"],
            "retire": ["Emergent Concealment"], "retirement_watch": ["Sabbath Visibility"],
            "promotion_decision": "No Cycle 3 candidate is promoted; episode concentration remains too high.",
        },
        "anomaly_lifecycle": cycle3["anomaly_accounting"],
        "research_fit_audit": research_fit,
        "production_quality": {
            "strengths": ["Complete eight-lens structure", "Improved official-primary sourcing share", "Cross-year factual projection eliminated after Briefing 040", "Briefing 090 demonstrates a materially more compact, well-sourced form"],
            "defects": ["Duplicate/missing canonical numbers", "Schema drift", "O/R/H namespace collision", "Declining links per item", "No explicit chain refutation fields", "High anomaly silent-death share"],
        },
        "recommendations": recommendations,
        "next_quarter_tests": [item["test"] for item in recommendations],
    }


def build_html(payload: dict) -> str:
    cycles = payload["cycle_comparison"]
    cycle_rows = "".join(
        f"<tr><td>Cycle {c['cycle']}</td><td>{c['dated_artifacts']}</td><td>{c['lens_total']}</td>"
        f"<td>{c['mean_lens_items']:.2f}</td><td>{c['mean_analytic_words']:,.0f}</td>"
        f"<td>{c['mean_external_links']:.2f}</td><td>{c['links_per_lens_item']:.3f}</td>"
        f"<td>{c['deep_dives']}</td><td>{c['anomalies']}</td></tr>" for c in cycles
    )
    lens_rows = "".join(
        f"<tr><td>{esc(LENS_NAMES[key])}</td>" + "".join(f"<td>{c['lens_items'][key]}</td>" for c in cycles) + "</tr>"
        for key in LENS_NAMES
    )
    themes = "".join(
        f"<article class='card'><h3>{esc(t['name'])}</h3><p><strong>Evidence.</strong> {esc(t['evidence'])}</p>"
        f"<p><strong>Evolution.</strong> {esc(t['evolution'])}</p><p class='counter'><strong>Counter-reading.</strong> {esc(t['counter_reading'])}</p></article>"
        for t in payload["themes"]
    )
    fit_rows = "".join(
        f"<tr><td><span class='pill {esc(r['fit'])}'>{esc(r['fit'])}</span></td><td>{esc(r['surface'])}</td>"
        f"<td>{'<br>'.join(esc(x) for x in r['items'])}</td><td>{esc(r['public_action'])}</td></tr>"
        for r in payload["research_fit_audit"]
    )
    recs = "".join(
        f"<article class='rec'><div class='k'>{esc(r['area'])}</div><h3>{esc(r['problem'])}</h3>"
        f"<p><strong>Evidence:</strong> {esc(r['evidence'])}</p><p><strong>Change:</strong> {esc(r['intervention'])}</p>"
        f"<p><strong>Tradeoff:</strong> {esc(r['tradeoff'])}</p><p><strong>Next-quarter test:</strong> {esc(r['test'])}</p></article>"
        for r in payload["recommendations"]
    )
    c3_an = payload["anomaly_lifecycle"]["counts"]
    latest = payload["latest_compact_format"]
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Quarterly Portfolio Review — Q001</title>
<style>:root{{--bg:#0b1120;--card:#111827;--ink:#d7dfeb;--muted:#8e9bb5;--gold:#dcb267;--line:rgba(200,149,69,.25);--blue:#6da8ff;--red:#f08070;--green:#4ade80;--purple:#b79afa}}*{{box-sizing:border-box}}html,body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.68 system-ui,-apple-system,sans-serif}}main{{max-width:1160px;margin:auto;padding:38px 24px 90px}}header{{border-bottom:1px solid var(--line);padding-bottom:24px}}h1,h2,h3{{font-family:Georgia,serif;font-weight:400}}h1{{font-size:2.7rem;margin:.2rem 0}}h2{{color:var(--gold);border-bottom:1px solid var(--line);padding-bottom:.35rem;margin-top:2.8rem}}h3{{margin:.2rem 0 .6rem}}p{{color:#cdd6e4}}.k{{text-transform:uppercase;letter-spacing:.16em;color:var(--gold);font-size:.7rem}}.lead,.card,.rec{{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:1.25rem 1.45rem}}.lead{{border-left:4px solid var(--gold);font-size:1.06rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:1rem}}.stat strong{{display:block;color:var(--gold);font-size:1.85rem}}.stat span{{color:var(--muted)}}table{{width:100%;border-collapse:collapse;font-size:.86rem}}th,td{{text-align:left;vertical-align:top;padding:.6rem;border-bottom:1px solid #263047}}th{{color:var(--gold)}}.scroll{{overflow:auto}}.counter{{border-left:2px solid var(--purple);padding-left:.8rem;color:#b9c2d1}}.bar{{display:grid;grid-template-columns:190px 1fr 50px;gap:.65rem;align-items:center;margin:.4rem 0;font-size:.88rem}}.bar i{{display:block;height:13px;background:#1b2435}}.bar b{{display:block;height:100%;background:linear-gradient(90deg,#8b6428,var(--gold))}}.bar em{{font-style:normal;color:var(--gold)}}.pill{{display:inline-block;padding:.1rem .45rem;border-radius:12px;text-transform:uppercase;font-size:.63rem;letter-spacing:.08em}}.direct{{color:var(--green);background:#143225}}.adjacent{{color:var(--blue);background:#152a48}}.speculative{{color:var(--purple);background:#2b2145}}.none{{color:#b6bec9;background:#2b3039}}.rec{{margin-bottom:1rem;border-left:3px solid var(--gold)}}strong{{color:#edf3fa}}a{{color:var(--gold)}}footer{{margin-top:3rem;border-top:1px solid var(--line);padding-top:1rem;color:var(--muted);font-size:.78rem}}@media(max-width:700px){{h1{{font-size:2rem}}.bar{{grid-template-columns:115px 1fr 38px}}}}</style></head>
<body><main><header><div class="k">Tectonic Briefing · 90-issue portfolio review</div><h1>Quarterly Portfolio Review — Q001</h1><p>Briefings 001–090 · 91 dated artifacts · 5 April–12 August 2026</p></header>
<h2>Headline</h2><div class="lead"><p><strong>The portfolio's best development is not a topic; it is a way of seeing moved baselines.</strong> Across 91 artifacts, the briefing became increasingly good at locating cases where an aggregate remains stable while the rate, boundary, or physical substrate beneath it changes: entry-level work beneath occupation totals, participation beneath unemployment, telemetry beneath autonomous action, and enforcement beneath institutional form. But the production system now outruns some of its controls. Lens items rose, source support per item fell, two concepts became nearly universal, anomaly threads often disappeared without closure, and the read-mode intervention produced 146 prospective O labels with no comparison group. The next quarter should be shorter, more source-dense, more geographically deliberate, stricter about direct research relevance, and—above all—falsifiable.</p></div>
<h2>Corpus and integrity</h2><div class="grid"><div class="card stat"><strong>91</strong><span>dated artifacts for 90 nominal briefing numbers</span></div><div class="card stat"><strong>420</strong><span>canonical audited inference chains across three cycles</span></div><div class="card stat"><strong>426</strong><span>anomaly cards extracted across the corpus</span></div><div class="card stat"><strong>719</strong><span>unique external source domains</span></div></div><p>Canonical numbers 050, 055, and 062 each have two dated artifacts; 056 and 057 are missing. The raw extractor finds 416 card wrappers; the established Cycle 2 hand audit adds four thread/deep-dive chains, producing the canonical 420-chain portfolio total.</p>
<h2>How the artifact changed</h2><div class="scroll"><table><thead><tr><th>Cycle</th><th>Artifacts</th><th>Lens items</th><th>Items / issue</th><th>Words / issue</th><th>Links / issue</th><th>Links / item</th><th>Deep dives</th><th>Anomalies</th></tr></thead><tbody>{cycle_rows}</tbody></table></div><p>Coverage expanded by 19.6% from Cycle 1 to Cycle 3, but external links per lens item fell by 33.4%. Cycle 2 was the length peak. The compact No. 090 form is the strongest counterexample to the assumption that depth requires maximal length: <strong>{latest['analytic_words']:,} words, {latest['lens_items']} items, {latest['external_links']} external links, and {latest['deep_dives']} deep dives.</strong></p>
<h2>Core themes—with counter-readings</h2><div class="grid">{themes}</div>
<h2>Lens and geographic balance</h2><div class="grid"><div class="card"><h3>Lens items by cycle</h3><div class="scroll"><table><tr><th>Lens</th><th>C1</th><th>C2</th><th>C3</th></tr>{lens_rows}</table></div></div><div class="card"><h3>Whole-corpus regional assignments</h3>{bar_rows(payload['regional_balance']['whole_corpus'], limit=10)}</div></div><p>Environmental coverage nearly doubled from 67 items in Cycle 1 to 130 in Cycle 3; Social rose 78 → 99. North America remains the dominant corridor. Latin America improved 11 → 17 → 45, while Cycle 3 coverage of South/Southeast Asia (46) and Sub-Saharan Africa (79) fell despite greater overall density. Region counts are multi-label and preserve 550 Unknown assignments across the corpus.</p>
<h2>Source ecology</h2><div class="grid"><div class="card"><h3>Cycle 1 source-type share (%)</h3>{bar_rows(cycles[0]['source_type_shares'])}</div><div class="card"><h3>Cycle 3 source-type share (%)</h3>{bar_rows(cycles[2]['source_type_shares'])}</div></div><p>Domain concentration is low (HHI {payload['source_ecology']['domain_hhi']:.4f}); the recurring top domains are broad news and science outlets rather than one dominant source. The more consequential movement is compositional: official-primary share rose from {cycles[0]['source_type_shares']['official_primary']:.1f}% to {cycles[2]['source_type_shares']['official_primary']:.1f}%, while scholarly share fell from {cycles[0]['source_type_shares']['scholarly']:.1f}% to {cycles[2]['source_type_shares']['scholarly']:.1f}%. The classifier is coarse, so these are directional indicators, not assessments of every page's quality.</p>
<h2>Vocabulary health</h2><div class="card"><h3>Document presence, whole corpus</h3>{bar_rows(dict(list(payload['vocabulary_health']['document_presence'].items())[:20]), limit=20)}</div><p><strong>Commons Enclosure</strong> appears in 82 of 91 artifacts and needs a literal access-gate test; <strong>Governance Vacuum</strong> rises to 29 of 31 Cycle 3 artifacts and needs institution/capability/consequence fields. <strong>Emergent Concealment</strong> appears in one document and should retire from new use. <strong>Sabbath Visibility</strong> remains legitimate but moves to retirement-watch after only one Cycle 3 document. No Cycle 3 candidate is promoted: the strongest remain concentrated in one episode.</p>
<h2>Anomaly lifecycle</h2><div class="grid"><div class="card stat"><strong>{c3_an.get('resolved',0)}</strong><span>resolved</span></div><div class="card stat"><strong>{c3_an.get('persistently_absent',0)}</strong><span>persistently absent</span></div><div class="card stat"><strong>{c3_an.get('silently_died',0)}</strong><span>silently died</span></div><div class="card stat"><strong>{c3_an.get('open_not_yet_due',0)}</strong><span>open / not yet due</span></div></div><p>The first complete ledger shows that anomaly production has not yet become cumulative learning. “Silently died” is deliberately an attention metric, not a claim that the underlying issue vanished. Stable IDs, next observables, and fair review dates are required for the next cycle.</p>
<h2>Research and public-writing fit</h2><div class="scroll"><table><thead><tr><th>Fit</th><th>Research surface</th><th>Examples</th><th>Public action</th></tr></thead><tbody>{fit_rows}</tbody></table></div><p>The governing test is directness: a public bridge must change a construct, mechanism, boundary condition, empirical design, or observable. Shared vocabulary is not enough. Adjacent bridges remain useful, but belong in the private research graph rather than in public Research Program Relevance or article promotion.</p>
<h2>Production quality</h2><div class="grid"><div class="card"><h3>What strengthened</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in payload['production_quality']['strengths'])}</ul></div><div class="card"><h3>What remains structurally weak</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in payload['production_quality']['defects'])}</ul></div></div>
<h2>Changes for the next quarter</h2>{recs}
<footer>Reproducible data: <a href="_raw/quarter-001-corpus.json">quarter-001-corpus.json</a> · Machine-readable review: <a href="quarter-001.yaml">quarter-001.yaml</a> · Chain audit: <a href="cycle-003.html">Cycle 003</a></footer>
</main></body></html>"""


def main() -> None:
    raw = json.loads(RAW.read_text())
    cycle3 = yaml.safe_load(CYCLE3.read_text())
    payload = build_payload(raw, cycle3)
    YAML_OUT.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=110))
    HTML_OUT.write_text(build_html(payload))
    print(json.dumps({
        "yaml": str(YAML_OUT.relative_to(REPO)), "html": str(HTML_OUT.relative_to(REPO)),
        "dated_artifacts": payload["dated_artifacts"],
        "canonical_chains": payload["corpus_manifest"]["canonical_audited_chains"],
        "recommendations": len(payload["recommendations"]),
    }, indent=2))


if __name__ == "__main__":
    main()
