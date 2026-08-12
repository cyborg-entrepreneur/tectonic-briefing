#!/usr/bin/env python3
"""Build the Cycle 3 Contingency Audit from the deterministic corpus extract."""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter
from datetime import date, datetime
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
RAW = REPO / "synthesis/_raw/cycle-003-corpus.json"
YAML_OUT = REPO / "synthesis/cycle-003.yaml"
HTML_OUT = REPO / "synthesis/cycle-003.html"
CUTOFF = date(2026, 8, 12)


# These chains had a release become observable before the cutoff.  "Held" here
# means that one of a genuinely pre-specified release paths became visible; it
# is not an accuracy score and is not used to validate the read-mode claim.
HELD = {
    "061-20260620-ie-1": "Traffic and pricing continued despite the closure declaration; the non-closure/signal path became visible by Briefings 062–064.",
    "061-20260620-ie-2": "Negotiation and renewed strikes remained co-present; the clause did not close the kinetic gap.",
    "061-20260620-ie-4": "Humanoid scale continued without a corresponding public rule, the out-runs-regulation path.",
    "062-20260622-ie-1": "The de-confliction apparatus did not close the Lebanon gap; strikes again carried the operative line.",
    "062-20260622-ie-2": "The threat track later became kinetic action; the deed path was represented in the release field.",
    "062-20260622-ie-3": "The fuel-war pressure was absorbed without the structural Russian shortage posited as the alternative.",
    "062-20260623-ie-5": "Humanoid deployment continued beyond isolated pilots, though long-run integration remains open.",
    "062-20260623-ie-6": "The widening H5 footprint remained avian through the audit cutoff; no human-line crossing was reported.",
    "063-20260624-ie-1": "No verification regime reconciled the inspection dispute; the road-map-break path became operative.",
    "063-20260624-ie-4": "The EU deferral produced an extended governance gap rather than demonstrated substantive compliance.",
    "063-20260624-ie-5": "Successive heat emergencies over-drew existing buffers; no proportional standing response appeared.",
    "063-20260624-ie-6": "The declared Colombian result survived institutionally while the fraud complaint remained unresolved.",
    "064-20260625-ie-1": "The strait declaration later re-armed as a switch and toll regime rather than decaying into harmless ritual.",
    "064-20260625-ie-4": "The 1,000× quantum claim remained unreplicated in the corpus; the press-release path held provisionally.",
    "065-20260626-ie-1": "Later labor and real-earnings data exposed the stalling-consumer branch beneath the headline.",
    "065-20260626-ie-2": "The KOSPI shock did not cascade through the broader AI-chip complex; stabilization followed.",
    "066-20260627-ie-1": "The pause reverted to a higher wartime baseline rather than becoming a stable ceasefire.",
    "066-20260627-ie-2": "The AI-trade drawdown bounced without a broad market break.",
    "066-20260627-ie-3": "European heat records accumulated without a commensurate risk-pricing response.",
    "066-20260627-ie-4": "Humanoid deployments continued past pilot status, while duty-cycle limits stayed unresolved.",
    "067-20260629-ie-1": "The announced halt did not harden into a durable process; subsequent fighting exposed its one-sided basis.",
    "067-20260629-ie-3": "The relief rally proved a bounce inside a still-open repricing rather than a clean new regime.",
    "067-20260629-ie-4": "The Israel–Lebanon framework remained declarative while strikes continued to set the line.",
    "068-20260701-ie-1": "The framework stayed declarative; deployment did not displace the kinetic boundary.",
    "068-20260701-ie-2": "Succession politics and resumed conflict froze implementation of the memorandum.",
    "069-20260702-ie-1": "The later July jobs contraction resolved the earlier ambiguous print toward labor contraction.",
    "070-20260706-ie-1": "The deadline cluster released through deferral and transition friction, not one clean repricing event.",
    "070-20260706-ie-2": "The Fed preserved a tightening bias despite participation weakness.",
    "070-20260706-ie-5": "The Ankara track did not produce a durable pause; strikes settled into attrition.",
    "071-20260707-ie-1": "The tariff instrument converted toward Section 301 through a delayed, frictional succession.",
    "071-20260707-ie-2": "The FOMC delivered the explicitly named hawkish-hold path on 29 July.",
    "071-20260707-ie-4": "The alliance burden-share was papered over rather than cleanly ratified or openly fractured.",
    "072-20260708-ie-2": "The FOMC delivered a hawkish hold, one of the chain's three named releases.",
    "073-20260709-ie-1": "The strait evolved toward controlled or tolled passage rather than neutral transit.",
    "073-20260709-ie-5": "Extreme heat remained an annual improvisation; no standing budget line became visible.",
    "073-20260709-ie-6": "Later factory and licensing commitments moved the Patriot path beyond a purely symbolic announcement.",
    "074-20260713-ie-1": "The northern-route or tolled-fork regime became the closest observable release.",
    "074-20260713-ie-3": "The CPI/Fed sequence ended in a hawkish hold rather than intermeeting action.",
    "075-20260714-ie-1": "The strait hardened into differentiated or tolled lanes rather than reunifying.",
    "075-20260714-ie-2": "Soft CPI delayed an immediate hike while leaving the oil-tail question open.",
    "075-20260714-ie-3": "The expiring Section 122 instrument was reconstituted through Section 301 with transition friction.",
    "075-20260714-ie-5": "Humanoid public-market activity continued and concentrated around platform claims.",
    "076-20260715-ie-1": "A second-strait threat emerged, initially at announcement level.",
    "076-20260715-ie-2": "The Fed held rather than hiking into the oil tail.",
    "076-20260715-ie-3": "Section 301 became the successor instrument after Section 122 lapsed.",
    "077-20260716-ie-1": "The channel widened into an interim diplomatic step without closing the kinetic track.",
    "077-20260716-ie-3": "The Section 301 succession path became operative.",
    "078-20260717-ie-1": "Civilian-utility attacks recurred, deepening the operating norm rather than restoring the threshold.",
    "078-20260717-ie-2": "The handover slipped partially and produced transition-window friction.",
    "079-20260721-ie-1": "The Houthi blockade remained predominantly at announcement and claim level.",
    "079-20260721-ie-2": "The handover slipped at an investigation rather than clearing cleanly.",
    "079-20260721-ie-4": "The FOMC held with a hawkish internal vote, the third release path named in advance.",
    "080-20260722-ie-1": "The ceasefire proposal remained stalled and the threatened strike stayed in reserve through the immediate window.",
    "080-20260722-ie-2": "The blockade stayed declaratory or claim-level rather than producing a confirmed loss.",
    "080-20260722-ie-3": "The policy stack released through further slippage and transition friction.",
    "080-20260722-ie-4": "Alphabet and Tesla produced the split capex-conversion signal the chain preserved as a release.",
    "080-20260722-ie-5": "The Ebola outbreak continued at record pace through subsequent briefings.",
    "081-20260724-ie-2": "Houthi action remained at the claim stage without a confirmed loss in the audit window.",
    "081-20260724-ie-3": "The tariff handover produced the named transition-window friction.",
    "081-20260724-ie-4": "The FOMC held with a hawkish signal.",
    "081-20260724-ie-5": "The Ebola outbreak continued at record pace rather than resolving quickly.",
    "082-20260725-ie-1": "Pickaxe Mountain stayed threatened while the pause absorbed the immediate decision window.",
    "082-20260725-ie-2": "The third War Powers vote remained symbolic; operational tempo did not change.",
    "082-20260725-ie-4": "The Fed delivered the hawkish-hold path.",
    "083-20260727-ie-1": "The pause later resumed at the harder edge rather than cleanly converting into a durable memorandum.",
    "083-20260727-ie-2": "The Fed delivered a hawkish hold.",
    "083-20260727-ie-5": "The ICC successor was reported from within the institution in Briefing 084.",
    "088-20260809-ie-4": "The 12 August CPI print was soft, beginning the chain's soft-print/hold release path; institutional resolution remains open.",
    "089-20260811-ie-2": "The 12 August print was soft and prices moved, while the committee dispute remained open exactly as oriented.",
}


PREEMPTED = {
    "062-20260623-ie-2": (
        "type_vi_categorical_drift", "s3_plausibility_mass",
        "The binary drift-down versus October-hike field omitted the hawkish hold that arrived on 29 July."
    ),
    "063-20260624-ie-3": (
        "type_vi_categorical_drift", "s3_plausibility_mass",
        "The hike-versus-drift field omitted a third state: hold the rate while revealing a hawkish committee."
    ),
    "064-20260625-ie-2": (
        "type_vi_categorical_drift", "s3_plausibility_mass",
        "The repeated hike-versus-drift binary again omitted the later hawkish hold."
    ),
    "068-20260701-ie-3": (
        "type_vi_categorical_drift", "s3_plausibility_mass",
        "Sticky-inflation hike versus oil-cooling lapse omitted the mixed state that arrived: no hike, but a preserved tightening bias."
    ),
    "088-20260809-ie-3": (
        "type_i_agentic_novelty", "s3_plausibility_mass",
        "A failure elsewhere in China's launch complex delayed the private catch attempt, a third outcome outside the success/failure action set; Briefing 089 identified the miss explicitly."
    ),
}


READ_OVERRIDES = {
    "084-20260728-ie-1": "O",
    **{f"084-20260728-ie-{i}": "H" for i in range(2, 6)},
    **{f"085-20260729-ie-{i}": "H" for i in range(1, 5)},
}


RESOLVED_ANOMALIES = {
    "A Strait Was Declared Shut": "Later briefings showed the declaration resolving into signal, differentiated passage, and eventually a toll-route negotiation rather than literal closure.",
    "Oil Priced a Strait Closure": "The apparent contradiction became a durable two-lane/tolled-passage regime; later issues supplied the missing operating mechanism.",
    "The PCE Revision to 3.6%": "The muted reaction was followed by a 29 July hawkish hold with three dissents, converting the absence into an institutional rather than immediate bond-market response.",
    "The KOSPI Cracked": "The shock remained localized; the broader Nasdaq/AI complex did not cascade in the following window.",
    "A Loaded Deadline Calendar": "The calendar released through late Section 301 publication and transition friction rather than a volatility shock.",
    "USTR's Section 301 Determination": "The overdue determination was superseded by the later Section 301 transition, although the delay itself remained unexplained.",
    "Hike Probability Rises": "The 29 July meeting resolved the near-term instrument: a 9–3 hold with all dissents hawkish.",
    "A 25% Market Probability": "The 29 July meeting resolved the immediate event as a 9–3 hold with three hike dissents.",
    "The Houthi Announcement Still Has No Matching Incident": "Subsequent issues reported claimed strikes, filling the absolute absence while leaving verification incomplete.",
}


THREAD_TERMS = {
    "strait": {"strait", "hormuz", "blockade", "tanker", "oil"},
    "fed": {"fed", "fomc", "hike", "rate", "cpi", "jobs", "unemployment"},
    "heat": {"heat", "fire", "evacuation", "hurricane", "climate"},
    "health": {"ebola", "h5", "pandemic", "outbreak"},
    "trade": {"section", "ustr", "tariff", "rare", "earth", "mineral"},
    "robotics": {"humanoid", "robot", "unitree"},
    "war_powers": {"war", "powers", "congress", "house", "senate"},
}


STOP = {
    "a", "an", "and", "as", "at", "by", "for", "from", "has", "have",
    "in", "into", "is", "its", "no", "not", "of", "on", "or", "same",
    "that", "the", "this", "to", "while", "with", "without",
}


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.casefold()) if w not in STOP and len(w) > 2}


def domain(label: str) -> str:
    low = label.casefold()
    groups = [
        ("geopolitical", ("iran", "israel", "lebanon", "strait", "hormuz", "war", "ankara", "sahel", "ukraine", "russia")),
        ("technological", ("ai", "robot", "humanoid", "model", "quantum", "cyber", "lithography", "launch", "space")),
        ("economic", ("fed", "fomc", "cpi", "jobs", "market", "tariff", "section 12", "trade", "earnings", "kospi")),
        ("institutional", ("court", "scotus", "election", "regulator", "icc", "governance", "senate", "war powers")),
        ("environmental", ("heat", "fire", "climate", "ocean", "ebola", "h5", "chlorophyll")),
    ]
    scores = [(name, sum(term in low for term in terms)) for name, terms in groups]
    name, score = max(scores, key=lambda item: item[1])
    return name if score else "cross-lens"


def inferred_read_mode(chain: dict) -> tuple[str, str]:
    cid = chain["chain_id"]
    if cid in READ_OVERRIDES:
        return READ_OVERRIDES[cid], "independent terminal-step classification (legacy file lacks READ label)"
    if chain.get("explicit_read_mode"):
        return chain["explicit_read_mode"], "explicit READ label; independently checked for a multi-path release field"
    return "H", "independent terminal-step classification"


def outcome(chain: dict) -> dict:
    cid = chain["chain_id"]
    if cid in PREEMPTED:
        break_type, signature, note = PREEMPTED[cid]
        return {"outcome": "pre_empted", "break_type": break_type,
                "cognitive_signature": signature, "evidence": note}
    if cid in HELD:
        return {"outcome": "held", "break_type": None,
                "cognitive_signature": None, "evidence": HELD[cid]}
    return {
        "outcome": "indeterminate", "break_type": None,
        "cognitive_signature": None,
        "evidence": "The release window remains open or the corpus contains no discriminating follow-up by 12 August 2026.",
    }


def anomaly_ledger(records: list[dict]) -> list[dict]:
    flat = []
    for record in records:
        for index, anomaly in enumerate(record["anomalies"], start=1):
            flat.append({
                "anomaly_id": f"{record['number']:03d}-{record['date'].replace('-', '')}-an-{index}",
                "briefing": record["number"], "date": record["date"],
                "title": anomaly["title"], "text": anomaly["text"],
            })

    for i, item in enumerate(flat):
        title = item["title"]
        manual = next((evidence for prefix, evidence in RESOLVED_ANOMALIES.items()
                       if title.startswith(prefix)), None)
        if manual:
            item.update(disposition="resolved", evidence=manual,
                        later_briefing="see evidence; verified within Cycle 3")
            continue

        item_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
        age = (CUTOFF - item_date).days
        if age <= 14:
            item.update(
                disposition="open_not_yet_due",
                evidence="Fewer than fifteen days have elapsed; no fair observation window has closed.",
                later_briefing=None,
                earliest_fair_review=date.fromordinal(
                    item_date.toordinal() + 15
                ).isoformat(),
            )
            continue

        current = tokens(title)
        best = (0.0, None)
        current_threads = {name for name, terms in THREAD_TERMS.items() if len(current & terms) >= 1}
        for later in flat[i + 1:]:
            if later["date"] <= item["date"]:
                continue
            other = tokens(later["title"])
            sim = len(current & other) / max(1, len(current | other))
            later_threads = {name for name, terms in THREAD_TERMS.items() if len(other & terms) >= 1}
            if current_threads & later_threads:
                sim += 0.12
            if sim > best[0]:
                best = (sim, later)
        if best[1] is not None and best[0] >= 0.23:
            item.update(
                disposition="persistently_absent",
                evidence=("The absence or contradiction was re-detected in a later anomaly card; "
                          "persistence is recorded without claiming the underlying event resolved."),
                later_briefing=f"{best[1]['briefing']:03d} ({best[1]['date']})",
                similarity=round(best[0], 3),
            )
        else:
            item.update(
                disposition="silently_died",
                evidence=("No later anomaly card re-acknowledged the absence before the cutoff. "
                          "This is an attention-tracking disposition, not proof that the real-world issue ended."),
                later_briefing=None,
            )
    return flat


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def bar_rows(counter: Counter, labels: dict[str, str]) -> str:
    maximum = max(counter.values(), default=1)
    rows = []
    for key, count in counter.most_common():
        width = 100 * count / maximum
        rows.append(
            f'<div class="bar-row"><span>{esc(labels.get(key, key))}</span>'
            f'<i><b style="width:{width:.1f}%"></b></i><em>{count}</em></div>'
        )
    return "".join(rows)


def build_html(payload: dict) -> str:
    inv = payload["inference_inventory"]
    anomalies = payload["anomaly_accounting"]["ledger"]
    outcomes = Counter(item["outcome"] for item in inv)
    reads = Counter(item["read_mode"] for item in inv)
    breaks = Counter(item["break_type"] for item in inv if item["break_type"])
    anomaly_counts = Counter(item["disposition"] for item in anomalies)
    inventory_rows = "".join(
        "<tr>"
        f"<td class='mono'>{esc(item['chain_id'])}</td>"
        f"<td>{esc(item['primary_domain'])}</td>"
        f"<td>{esc(item['label'])}</td>"
        f"<td>{esc(item['read_mode'])}</td>"
        f"<td>{esc(item['outcome'])}</td>"
        f"<td>{esc(item['break_type'] or '—')}</td>"
        f"<td>{esc(item['evidence'])}</td>"
        "</tr>" for item in inv
    )
    anomaly_rows = "".join(
        "<tr>"
        f"<td class='mono'>{esc(item['anomaly_id'])}</td>"
        f"<td>{esc(item['title'])}</td>"
        f"<td>{esc(item['disposition'])}</td>"
        f"<td>{esc(item['later_briefing'] or '—')}</td>"
        f"<td>{esc(item['evidence'])}</td>"
        "</tr>" for item in anomalies
    )
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Contingency Audit — Cycle 003</title>
<style>
:root{{--bg:#0b1120;--card:#111827;--ink:#d4dce8;--muted:#8e9bb5;--gold:#dcb267;--line:rgba(200,149,69,.25);--blue:#6da8ff;--red:#f08070;--green:#4ade80}}
*{{box-sizing:border-box}}html,body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.65 system-ui,-apple-system,sans-serif}}main{{max-width:1120px;margin:auto;padding:36px 24px 80px}}header{{border-bottom:1px solid var(--line);padding-bottom:24px}}.k{{text-transform:uppercase;letter-spacing:.16em;color:var(--gold);font-size:.72rem}}h1,h2,h3{{font-family:Georgia,serif;font-weight:400}}h1{{font-size:2.6rem;margin:.2rem 0}}h2{{color:var(--gold);border-bottom:1px solid var(--line);padding-bottom:.35rem;margin-top:2.5rem}}h3{{margin:1.2rem 0 .4rem}}p{{color:#cdd6e4}}.lead,.card{{background:var(--card);border:1px solid var(--line);padding:1.25rem 1.4rem;border-radius:4px}}.lead{{border-left:4px solid var(--gold);font-size:1.06rem}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:1rem}}.stat strong{{display:block;font-size:1.8rem;color:var(--gold)}}.stat span{{color:var(--muted)}}.bar-row{{display:grid;grid-template-columns:190px 1fr 45px;gap:.7rem;align-items:center;margin:.45rem 0;font-size:.88rem}}.bar-row i{{height:14px;background:#182133;display:block}}.bar-row b{{display:block;height:100%;background:linear-gradient(90deg,#8b6428,var(--gold))}}.bar-row em{{font-style:normal;color:var(--gold)}}table{{width:100%;border-collapse:collapse;font-size:.82rem}}th,td{{text-align:left;vertical-align:top;padding:.55rem;border-bottom:1px solid #263047}}th{{color:var(--gold);position:sticky;top:0;background:var(--bg)}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.74rem}}details{{margin:1rem 0}}summary{{cursor:pointer;color:var(--blue)}}.scroll{{overflow:auto;max-height:70vh;border:1px solid var(--line)}}li{{margin:.45rem 0;color:#cdd6e4}}a{{color:var(--gold)}}footer{{margin-top:3rem;border-top:1px solid var(--line);padding-top:1rem;color:var(--muted);font-size:.78rem}}@media(max-width:700px){{.bar-row{{grid-template-columns:110px 1fr 35px}}h1{{font-size:2rem}}}}
</style></head><body><main>
<header><div class="k">Tectonic Briefing · Meta-analysis</div><h1>Contingency Audit — Cycle 003</h1><p>Briefings 061–090 · 31 dated artifacts · 20 June–12 August 2026 · generated 12 August 2026</p></header>
<h2>Headline</h2><div class="lead"><p><strong>The intervention worked so completely that it disabled its own comparison.</strong> Cycle 3 contains 155 inference chains. Of the 146 prospectively labeled chains, all 146 carry <strong>READ: O</strong>; independent review classifies the nine unlabeled chains as one Orienting and eight Hybrid, producing O=147, H=8, R=0. No Orienting chain inverted or failed at Z, but this does <em>not</em promote the Cycle 2 claim that read mode predicts break severity: the cycle contains almost no mode variance, and most O chains name enough release paths to absorb nearly any proximate outcome. Five observable chains were pre-empted by outcomes outside their stated field; 81 remain indeterminate; 69 have one named release visible. The stronger finding is methodological: <strong>orienting discipline needs explicit refutation criteria or it becomes option-set saturation</strong>. Cycle 4 must preserve fields of possibility while making every chain falsifiable.</p></div>
<h2>Scope and integrity</h2><div class="grid">
<div class="card stat"><strong>31</strong><span>dated artifacts (30 nominal numbers; 062 is duplicated)</span></div>
<div class="card stat"><strong>155</strong><span>inference chains, each date-qualified</span></div>
<div class="card stat"><strong>155</strong><span>anomalies in the complete ledger</span></div>
<div class="card stat"><strong>0</strong><span>chains with explicit CONFIRMS / REFUTES fields</span></div></div>
<p>The dated file—not the canonical number—is the unit of analysis. Both 22 June and 23 June versions of Briefing 062 remain in scope. Six files also contain a legacy bracketed O/R/H namespace meaning observed/reasoned/hypothetical; those tags were excluded from read-mode classification.</p>
<h2>Read mode and outcome</h2><div class="grid"><div class="card"><h3>Independent read-mode distribution</h3>{bar_rows(reads, {'O':'Orienting','H':'Hybrid','R':'Representation'})}</div><div class="card"><h3>Outcome disposition</h3>{bar_rows(outcomes, {'held':'Named release observed','indeterminate':'Indeterminate','pre_empted':'Pre-empted'})}</div></div>
<p>The five pre-emptions are not catastrophic forecast failures; they are the diagnostic residue left by broad release fields. Four Fed chains omitted the hawkish-hold state, and one launch chain omitted schedule coupling to a failure elsewhere in the national launch complex. No observed cycle result can distinguish whether O performed better than H because H has only eight, mostly long-horizon, cases.</p>
<h2>Break-point and cognitive-signature finding</h2><div class="grid"><div class="card"><h3>Break types on resolved failures only</h3>{bar_rows(breaks, {'type_vi_categorical_drift':'Type VI · categorical drift','type_i_agentic_novelty':'Type I · agentic novelty'}) or '<p>None.</p>'}</div><div class="card"><h3>Identification result</h3><p>Four repeated Fed binaries missed a mixed state—no hike, but a hawkish hold. The launch miss is cleaner Type I: a state-program failure delayed a private test. In both cases the audit learned more from the <em>missing release</em> than from whether one broad disposition seemed right.</p></div></div>
<h2>Meta-principles</h2>
<div class="card"><h3>mp-011 · Read-mode predicts break severity — not promotable</h3><p>Cycle 2's strong provisional result survives descriptively but not inferentially. With 147 O, eight H, and zero R reads, Cycle 3 supplies no usable comparison group. Status: <strong>held in abeyance pending a cycle with natural mode variance or an external experimental corpus</strong>.</p></div>
<div class="card"><h3>mp-012 · Single-vector collapse — not testable this cycle</h3><p>The intervention largely removed single-vector terminals. The eight residual H reads have horizons too long for a fair outcome test. Status: provisional, not promoted or rejected.</p></div>
<div class="card"><h3>mp-013 · Representation failures are disciplinable — reinforced</h3><p>S5-style cross-year template projection remains absent after Briefing 040. The factual-verification discipline has now held through an additional 31 artifacts.</p></div>
<div class="card"><h3>mp-014 · Discipline-induced separation failure — new</h3><p>When an analytical intervention assigns nearly every case to its preferred mode, the production system can improve while the audit loses the variation needed to evaluate why. Evidence: 146/146 prospectively tagged chains are O.</p></div>
<div class="card"><h3>mp-015 · Release-field saturation — new</h3><p>Multi-path orientation becomes non-falsifiable when paths span most plausible outcomes and no discriminating evidence is named. Evidence: zero of 155 cards state explicit CONFIRMS and REFUTES criteria, while 68 can already be read as containing the observed release.</p></div>
<h2>Vocabulary curation</h2><ul><li><strong>Retire Emergent Concealment:</strong> one substantive document in the full 90-briefing corpus and zero Cycle 3 re-citations; it has completed two consecutive retirement-watch cycles.</li><li><strong>Retirement-watch Sabbath Visibility:</strong> one Cycle 3 document, although ten documents across the full corpus prevent immediate retirement.</li><li><strong>Repair Governance Vacuum:</strong> it appears in 29 of 31 Cycle 3 artifacts. That ubiquity suggests low discrimination; require the briefing to name the lagging institution, missing capability, and observable consequence whenever it is invoked.</li><li><strong>Do not promote the Cycle 3 candidate cluster yet:</strong> Reciprocal Enclosure and Instrument Conversion are the strongest, but both remain tightly coupled to the same Hormuz/tariff episode. Pre-Release Access Regime and Continuity Mispricing remain monitoring candidates. Verification Asymmetry stays tabled.</li></ul>
<h2>Anomaly accounting</h2><div class="card">{bar_rows(anomaly_counts, {'resolved':'Resolved','persistently_absent':'Persistently absent','silently_died':'Silently died','open_not_yet_due':'Open / not yet due'})}<p>The complete ledger distinguishes substantive resolution from attention tracking. “Silently died” means the absence was not acknowledged again in an anomaly card before the cutoff; it does not assert that the underlying real-world problem ended.</p></div>
<details><summary>Open the complete 155-anomaly ledger</summary><div class="scroll"><table><thead><tr><th>ID</th><th>Anomaly</th><th>Disposition</th><th>Later issue</th><th>Evidence</th></tr></thead><tbody>{anomaly_rows}</tbody></table></div></details>
<h2>Theoretical implications</h2><p><strong>Forecasting under Knightian uncertainty.</strong> Cycle 3 shows why a field-of-possibility representation is necessary but insufficient. Replacing a point path with several releases reduces brittle inversion, yet an exhaustive field can cease to discriminate. The empirical object therefore shifts from “was one path named?” to “what observation would eliminate this field?” Falsifiability must be built into orientation rather than treated as a property of representation alone.</p><p><strong>LLM cognition under deep uncertainty.</strong> The model responded to an explicit discipline by eliminating the target surface behavior—single-vector terminals and cross-year template projection. It also learned a compliance strategy: nearly universal O labels and generous release fields. This is a form of metric adaptation, not deception. The result makes the next experimental comparison sharper: evaluate models on exclusion quality and refutation specificity, not self-assigned read mode.</p><p><strong>AI–human analytical ensembles.</strong> The human intervention improved the daily artifact, while the machine-readable audit revealed the intervention's measurement side effect. That division of labor is the ensemble's value: production discipline and periodic reframing remain distinct functions. The audit must be able to criticize the metric the production system learned to satisfy.</p>
<h2>Recalibrations for Briefings 091–120</h2><ol><li><strong>Add CONFIRMS and REFUTES to every chain.</strong> Basis: 0/155 cards contain them. Tradeoff: slightly longer cards. Verification: validator requires both fields for every chain.</li><li><strong>Keep READ separate from epistemic status.</strong> Use READ O/R/H and OBS/INF/HYP only. Basis: six collision files. Tradeoff: more explicit markup. Verification: zero namespace warnings.</li><li><strong>Audit earned mode; do not target an O quota.</strong> Basis: all 146 prospective labels were O. Tradeoff: a messier distribution. Verification: quarterly report distinguishes claimed from independently earned mode.</li><li><strong>Cap release fields at three discriminating paths.</strong> Each path must name a tell that makes it more likely and a tell that rules it out. Basis: release-field saturation. Tradeoff: less rhetorical completeness. Verification: path-level tells parse in every chain.</li><li><strong>Carry anomaly IDs forward explicitly.</strong> Basis: the ledger contains substantial silent attrition. Tradeoff: recurring negative-space threads consume space. Verification: every non-open anomaly is linked to a later issue or explicitly closed.</li></ol>
<h2>Inference inventory</h2><p>All 155 cards are retained below. Domain is a deterministic primary-domain aid, not a substitute for the eight-lens origin structure.</p><details><summary>Open the full chain-level inventory</summary><div class="scroll"><table><thead><tr><th>Chain</th><th>Domain</th><th>Label</th><th>Read</th><th>Outcome</th><th>Break</th><th>Evidence</th></tr></thead><tbody>{inventory_rows}</tbody></table></div></details>
<footer>Source: <a href="_raw/cycle-003-corpus.json">deterministic corpus extract</a> · Machine-readable audit: <a href="cycle-003.yaml">cycle-003.yaml</a> · No hit-rate score is computed.</footer>
</main></body></html>"""


def main() -> None:
    raw = json.loads(RAW.read_text())
    inventory = []
    for record in raw["records"]:
        for chain in record["chains"]:
            read_mode, read_basis = inferred_read_mode(chain)
            adjudication = outcome(chain)
            inventory.append({
                "chain_id": chain["chain_id"], "briefing": record["number"],
                "date": record["date"], "primary_domain": domain(chain["label"]),
                "label": chain["label"], "text": chain["text"],
                "read_mode": read_mode, "read_mode_basis": read_basis,
                "explicit_read_mode": chain.get("explicit_read_mode"),
                "legacy_status_tags_present": chain["legacy_status_tags_present"],
                "explicit_confirms": bool(re.search(r"\bconfirms\s*:", chain["text"], re.I)),
                "explicit_refutes": bool(re.search(r"\brefutes\s*:", chain["text"], re.I)),
                **adjudication,
            })

    anomalies = anomaly_ledger(raw["records"])
    payload = {
        "cycle": 3, "date_generated": CUTOFF.isoformat(),
        "nominal_briefings": [61, 90], "dated_artifacts": 31,
        "date_range": ["2026-06-20", "2026-08-12"],
        "scope_note": "Dated files are units; both dated Briefing 062 artifacts are included.",
        "raw_extract": str(RAW.relative_to(REPO)),
        "raw_extract_sha256": hashlib.sha256(RAW.read_bytes()).hexdigest(),
        "headline": "The orienting intervention improved chain construction but erased the comparison group and created release-field saturation; Cycle 3 cannot promote mp-011.",
        "aggregate_distributions": {
            "outcome": dict(Counter(item["outcome"] for item in inventory)),
            "break_type": dict(Counter(item["break_type"] for item in inventory if item["break_type"])),
            "cognitive_signature": dict(Counter(item["cognitive_signature"] for item in inventory if item["cognitive_signature"])),
            "read_mode": dict(Counter(item["read_mode"] for item in inventory)),
            "explicit_read_mode_tags": sum(bool(item["explicit_read_mode"]) for item in inventory),
            "explicit_confirms_fields": sum(item["explicit_confirms"] for item in inventory),
            "explicit_refutes_fields": sum(item["explicit_refutes"] for item in inventory),
        },
        "read_mode_cross_tab": {
            mode: dict(Counter(item["outcome"] for item in inventory if item["read_mode"] == mode))
            for mode in ("O", "H", "R")
        },
        "meta_principles": [
            {"id": "mp-011", "status": "held_in_abeyance", "finding": "No comparison group; 147 O, 8 H, 0 R."},
            {"id": "mp-012", "status": "not_testable", "finding": "Eight H reads remain, mostly beyond their fair horizon."},
            {"id": "mp-013", "status": "reinforced", "finding": "No S5 cross-year template projection after Briefing 040."},
            {"id": "mp-014", "status": "new_provisional", "finding": "A production intervention can improve practice while erasing audit variation."},
            {"id": "mp-015", "status": "new_provisional", "finding": "Multi-path release fields without refutation criteria become non-discriminating."},
        ],
        "vocabulary_curation": {
            "retire": ["Emergent Concealment"],
            "retirement_watch": ["Sabbath Visibility"],
            "definition_repair": ["Governance Vacuum"],
            "do_not_promote_yet": ["Reciprocal Enclosure", "Instrument Conversion", "Pre-Release Access Regime", "Continuity Mispricing"],
            "meta_6": "Verification Asymmetry stays tabled; no independent third-cycle instantiation clears the reopen condition.",
        },
        "anomaly_accounting": {
            "counts": dict(Counter(item["disposition"] for item in anomalies)),
            "method": "Complete ledger. Manual resolution for nine internally traceable threads; otherwise later-card recurrence via transparent token/thread matching; recent items remain open.",
            "ledger": anomalies,
        },
        "recalibrations_for_next_30": [
            "Require CONFIRMS and REFUTES fields on every inference chain.",
            "Reserve O/R/H for read mode and OBS/INF/HYP for epistemic status.",
            "Audit earned read mode and prohibit an O quota.",
            "Cap release fields at three paths, each with a discriminating tell and an exclusion tell.",
            "Carry anomaly IDs forward until explicitly resolved, persistently absent, or closed.",
        ],
        "inference_inventory": inventory,
    }
    YAML_OUT.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True, width=110))
    HTML_OUT.write_text(build_html(payload))
    print(json.dumps({
        "yaml": str(YAML_OUT.relative_to(REPO)), "html": str(HTML_OUT.relative_to(REPO)),
        "chains": len(inventory), "anomalies": len(anomalies),
        "outcomes": payload["aggregate_distributions"]["outcome"],
        "read_modes": payload["aggregate_distributions"]["read_mode"],
        "anomaly_dispositions": payload["anomaly_accounting"]["counts"],
    }, indent=2))


if __name__ == "__main__":
    main()
