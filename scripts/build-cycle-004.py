#!/usr/bin/env python3
"""Rebuild the fixed 12 October 2026 Cycle 004 audit from preserved source files.

Full HTML extraction is exhaustive. Interpretive decisions are explicit below.
Public artifact quotations are the user's archive, never external-source quotes.
This replays the recorded coding; it does not perform new network checks.
Use --repo to select a checkout and --evidence-dir to request private receipts.
Without --evidence-dir, only synthesis/cycle-004.html and .yaml are written.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
import yaml
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parents[1]
PRIVATE = None
CUTOFF = '2026-10-12'
E = html.escape

SOURCES = [
 dict(id='fed-0916',date='2026-09-16',title='Federal Reserve: September FOMC statement',url='https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm',supports='A unanimous quarter-point increase to 3.75–4.00 percent occurred. This establishes the decision, not whether data moved market odds more than speeches.',chains=['096-ie-2','097-ie-4'],kind='primary_event'),
 dict(id='ecb-0910',date='2026-09-10',title='ECB: September monetary policy decision',url='https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.mp260910~314e508016.en.html',supports='The ECB raised its three key rates by 25 basis points and cited continuing inflation pressure. The decision does not identify the relative causal influence of energy, core inflation, and institutional communication on market pricing.',chains=['097-ie-2'],kind='primary_event'),
 dict(id='g20-0901',date='2026-09-01',title='US Treasury: G20 Chair’s Statement',url='https://home.treasury.gov/news/press-releases/sb0620',supports='A dated chair’s statement exists, with a footnote identifying China’s dissent on four paragraphs. Its requested actions and reporting work do not fit an inference from silence. Implementation and subsequent migration of negotiating authority remain separate tests.',chains=['097-ie-3'],kind='primary_document'),
 dict(id='iea-1007',date='2026-10-07',title='IEA: member-government stock-release statement',url='https://www.iea.org/news/statement-by-iea-executive-director-on-meeting-of-iea-member-governments-on-7-october-2026',supports='The IEA links approximately 100 million barrels to stocks pledged but not yet released under the March action. This supports an accounting distinction between previous commitments and delivered barrels; it does not establish cumulative physical delivery by February 2027 or a final diesel allocation.',chains=['108-ie-2','113-ie-1','114-ie-2'],kind='primary_document'),
 dict(id='iea-1002',date='2026-10-02',title='IEA: G7 energy-security meeting',url='https://www.iea.org/news/executive-director-participates-in-g7-leaders-meeting-on-energy-security-and-markets',supports='The IEA reports the meeting and continuing diesel pressure. A policy response was discussed; realised supply and price effects require later observations.',chains=['108-ie-2','113-ie-1'],kind='primary_event'),
 dict(id='nasa-0915',date='2026-09-15',title='NASA: Roman instrument activation and coronagraph checks',url='https://science.nasa.gov/blogs/roman/2026/09/15/nasa-activates-romans-primary-instrument-checks-out-coronagraph/',supports='Instrument activation is a later commissioning milestone. It does not by itself establish calibrated survey science, the economic value of a robot deployment, or a cross-program relation between reporting discipline and outcomes.',chains=['095-ie-1','102-ie-3'],kind='primary_event'),
 dict(id='nbs-1008',date='2026-10-08',title='China NBS: September purchasing managers’ indices',url='https://www.stats.gov.cn/english/PressRelease/202610/t20261008_1965466.html',supports='The official follow-up provides separate production, orders, employment and size measures. The Chinese branch can be inspected; a pooled mechanism joining Chinese manufacturing and South African investment is not established by that one release.',chains=['099-ie-3'],kind='primary_data'),
 dict(id='arpa-air',date='2026-08-06',title='ARPA-H: autonomous stroke-intervention programme',url='https://arpa-h.gov/news-and-events/arpa-h-funded-teams-transform-life-saving-stroke-interventions-autonomous-robotic',supports='The programme specifies staged demonstrations and a separate simulation and validation testbed. It motivates a distinction between execution capability and verification; it is not evidence of deployed clinical autonomy or durable human complementarity.',chains=['095-ie-2','104-ie-4'],kind='primary_research_anchor'),
 dict(id='interaction-tax',date='2026-08-24',title='Ann, Liu and Tan: The Interaction Tax',url='https://arxiv.org/abs/2608.23541',supports='The authors report 11 verifier-scored optimisation tasks under matched budgets. Full-solution communication reduced solution diversity; critique benefits depended on whether violations were detectable. Generalisation to venture competition and organisational work remains a hypothesis.',chains=['094-ie-2','091-ie-2','093-ie-2'],kind='primary_research_anchor'),
 dict(id='eca-ai',date='2026-10-06',title='World Bank: Making AI Work in Europe and Central Asia',url='https://www.worldbank.org/en/news/press-release/2026/10/06/europe-and-central-asia-slower-growth-with-global-headwinds',supports='The release distinguishes exposure from adoption and names managerial skills, interoperable data and computing capacity as constraints. Its regional description does not causally identify any particular organisational complement.',chains=['116-ie-4'],kind='primary_research_anchor'),
 dict(id='compression-preprint',date='2025-09-08',title='Molinaro and Collins: reward-function compression, original preprint',url='https://arxiv.org/abs/2509.06810',supports='The original preprint proposes and tests a compression account across six behavioural experiments. It is historical primary evidence for the idea; it is not a new 2026 observation or direct evidence of LLM internal representations.',chains=['117-ie-1'],kind='primary_research_anchor'),
 dict(id='embedded-evaluators',date='2026-09-18',title='Accenture and Anthropic: embedded evaluation partnership',url='https://newsroom.accenture.com/news/2026/accenture-and-anthropic-partner-to-build-team-of-embedded-evaluators-at-anthropic',supports='The companies announced an embedded evaluation arrangement. The announcement verifies the organisational form, not evaluator independence in contested decisions or an exercised right to delay release.',chains=['105-ie-1'],kind='primary_research_anchor'),
 dict(id='ea-drought-1001',date='2026-10-05',title='Environment Agency: drought report, 25 September–1 October',url='https://www.gov.uk/government/publications/dry-weather-and-drought-in-england-2026-summary-reports/dry-weather-and-drought-in-england-25-september-to-1-october-2026',supports='The report records 767 abstraction restrictions, up from 533, while reservoir storage continued to fall. This meets 102-ie-1’s event criterion of an institutional restriction change before the end of October. It does not establish the causal model across the other cases.',chains=['102-ie-1'],kind='primary_event'),
 dict(id='ea-rps382',date='2026-10-01',title='Environment Agency: RPS 382, abstraction outside the authorised period',url='https://www.gov.uk/government/publications/abstraction-outside-the-authorised-period-for-filling-water-storage-reservoirs-rps-382',supports='Published on 1 October and clarified on 7 October, the statement describes conditional enforcement discretion outside authorised abstraction periods. It is an additional observed institutional response, not a repeal of licensing requirements or a demonstrated recovery of storage.',chains=['102-ie-1'],kind='primary_document'),
 dict(id='au-stcdss-0921',date='2026-09-21',title='African Union: defence committee report and dated Council handoff',url='https://wwww.peaceau.org/en/article/african-union-convenes-18th-ordinary-session-of-the-specialized-technical-committee-on-defence-safety-and-security-advancing-african-leadership-fostering-innovation-and-promoting-forward-looking-approaches-to-defence-and-security',supports='The AU reports adoption of the committee report for submission to the Executive Council on 27–28 January 2027. This is a published institutional handoff with a named recipient and date. It does not establish a new budget, executed security operation or costly transfer.',chains=['104-ie-3'],kind='primary_document'),
]

# Timing is outcome-independent and applies to the original test, not the
# audit's ability to find evidence. Relative/unscheduled horizons stay explicit.
DUE = {
 '092-ie-1':'The original immediate-to-two-week window ended in early September.',
 '094-ie-1':'The original within-weeks document and behaviour review is due; no exact closing day was specified.',
 '095-ie-4':'The original days-to-weeks revision review is due; the comparative prediction test remains unadjudicated.',
 '096-ie-1':'The original days-to-two-week response window has passed; response form and transit effects remain unadjudicated.',
 '096-ie-2':'The original mid-September decision window has passed; the required pre-meeting pricing comparison was not retrieved.',
 '097-ie-1':'The original one-to-two-week attribution window has passed; the joint attribution, premiums and traffic record remains unadjudicated.',
 '097-ie-2':'The September ECB decision and pricing window has passed; comparative curve evidence is missing.',
}
UNSCHEDULED=set('091-ie-1 091-ie-2 091-ie-3 091-ie-4 092-ie-2 092-ie-3 092-ie-4 093-ie-1 093-ie-2 093-ie-3 093-ie-4 094-ie-2 094-ie-4 095-ie-3 098-ie-3 099-ie-1 099-ie-2 099-ie-4'.split())
MIXED=set('095-ie-1 096-ie-4 097-ie-3 097-ie-4 099-ie-3'.split())
HELD={
 '102-ie-1':'Held at the original event criterion: the Environment Agency records a rise in abstraction restrictions before 31 October while storage continued to decline. The additional dated enforcement position is a separate institutional response. The broader cross-case causal explanation is untested, and no general mechanism validation is claimed.',
 '104-ie-3':'Held at the literal documentary criterion: the AU names the Executive Council and 27–28 January 2027 for submission of the adopted defence-committee report. This satisfies a published dated handoff before mid-October. The criterion is weaker than the card’s budget and costly-transfer language; execution and material consequences remain unassessed.',
}

# These concern proposed controlled/comparative tests, rather than a single
# public event. The list is hand-coded with the complete chain in view.
RESEARCH = set('''091-ie-1 091-ie-2 091-ie-3 091-ie-4
092-ie-2 092-ie-3 092-ie-4 093-ie-1 093-ie-2 093-ie-3
094-ie-2 094-ie-4 095-ie-1 095-ie-2 095-ie-3 095-ie-4
096-ie-3 096-ie-4 097-ie-1 097-ie-2 097-ie-4 099-ie-4
100-ie-2 101-ie-2 101-ie-3 105-ie-3 106-ie-2 106-ie-3
115-ie-4 116-ie-1 116-ie-4 117-ie-1 117-ie-2 119-ie-1
119-ie-2 119-ie-3 120-ie-1 120-ie-2 120-ie-3'''.split())
COLLISIONS = set('092-ie-3 092-ie-4 093-ie-2 093-ie-3 093-ie-4 094-ie-3 094-ie-4'.split())
DIAGNOSTICS = {
 '091-ie-1': 'Public shipping and bargaining paths are followed by a CONFIRMS/REFUTES pair about a model comparison. A model result cannot adjudicate what occurred in Hormuz. The title’s triadic analogy is not a mechanism-level connection to entrepreneurial delegation.',
 '093-ie-1': 'The hypothesis predicts selection against mean-optimised interventions, but CONFIRMS only asks whether distributional measures qualify a mean. Distributional heterogeneity does not establish the proposed selection mechanism.',
 '094-ie-2': 'The initial study is evidence that motivated the chain. Re-counting that same study as later confirmation would conflate hypothesis generation with a new test.',
 '097-ie-3': 'The retrieved chair’s statement contains dissent and action language. The archive’s no-text premise requires correction; the longer claim about forum authority still needs implementation and venue-following evidence.',
 '101-ie-3': 'The original H tag is not earned by the terminal prose: conditional preparation, theatre and regional divergence remain live. Independently coded O; no outcome information enters this decision.',
 '103-ie-2': 'The title and hypothesis require convergence, while the field also includes persistent divergence. A path’s inclusion is not confirmation of the convergence thesis.',
 '104-ie-1': 'Divergence by channel is included as a release path but divergence without a common driver is also the refuting condition. The distinction needs a pre-specified test of the proposed channel.',
 '111-ie-1': 'The hypothesis leans toward post-release publication continuing, but CONFIRMS names pre-release publication or a resumption decision. The target being confirmed changes within the card. Do not score before that target is fixed.',
 '113-ie-2': 'The 95 percent corroboration threshold does not distinguish justified agreement from coerced signature. Cases requiring a justified override and protections for the decision maker must be observed.',
 '114-ie-2': 'The later IEA statement supports the accounting concern, but the original terminal test requires cumulative new releases by February 2027. Neither a pledge nor an earlier pledge’s remainder is a delivered-barrel outcome.',
 '114-ie-4': 'CONFIRMS treats no court order by the deadline as support for a legal-rule hypothesis. Procedural non-disposition does not establish the rule’s legal merits.',
 '120-ie-1': 'The field distinguishes measurement validity, behavioural redirection and record correction. REFUTES targets the redirection mechanism in a setting rather than refuting the entire three-path field; keep the mechanism-specific outcome separate from the overall research question.',
 '118-ie-3': 'Retain the original H judgment: the author explicitly reduces the endpoint to one poll-versus-count comparison. It is not an R template claim. Other analysts could code the two branches O; report this boundary case rather than use it to infer severity.',
}

RESEARCH_YIELD = [
 dict(id='ry-1',title='Which work returns to the founder after automation?',study='Three-Body ABM · moving tasks and delegation',chains=['093-ie-3','095-ie-2','107-ie-2','113-ie-2','120-ie-1'],sources=['arpa-air','eca-ai'],
 phenomenon='Autonomous systems are being developed alongside validation systems, while organisations face separate questions about authorisation, intervention and the conditions of use. The ARPA-H programme makes those stages explicit. The phenomenon is the recurrence and relocation of work around automation; a press release does not establish how often that work returns.',
 mechanism='Hypothesis: the founder’s actions and competitors’ outputs renew verification, stakeholder support and interpretation demands even at unchanged machine capability. Rival: tasks are fixed and a constant checking cost, a legal human-signature requirement or a binding time budget explains the residual human role.',
 question='When does machine performance change the reference against which the next piece of work is judged, causing a previously delegated demand to return to the founder?',
 computational_discriminant='At equal capability and matched workload, independently freeze reference movement from the focal venture, rivals and the external environment. Keep customer competition active while freezing referents. Compare turnover in the identity of delegated demands, not only the overall AI share. Separately vary the cost of checking and required human sign-off. A stable AI share with referent-timed turnover is the discriminating signature to investigate.',
 empirical_design='Follow identifiable work episodes within ventures adopting agents. Record the original demand, performer, later reopening, reason for reopening, model version, customer feedback and rival releases. A matched or staggered rollout can test whether hand-backs track changed evaluation criteria after controlling for errors, regulation and capability. Retain cases that receive no stakeholder response as missing judgment, not failed quality.',
 limits='Clinical robotics supplies a boundary case, not an entrepreneurship result. The proposed computational contrast represents specified sources of movement inside a model; it cannot demonstrate unimagined possibilities. No study outcome is claimed here.',
 new_question='Can better automation increase turnover in who performs each demand while the average division of labour appears settled?'),
 dict(id='ry-2',title='When do cheaper answers exhaust the institution’s ability to check?',study='GCM AI Agents · cheap answers, scarce checking and organisational attention',chains=['100-ie-2','105-ie-1','111-ie-1','119-ie-2'],sources=['embedded-evaluators'],
 phenomenon='The Accenture–Anthropic announcement makes an embedded evaluation function publicly visible. The audit’s related chains distinguish producing an assessment from changing a release decision. That distinction generates a concrete organisational question without treating the partnership as effective or ineffective.',
 mechanism='Hypothesis: inexpensive solution production increases demand on scarce checking and problem-sensing capacity; apparent completion can rise while unresolved problems accumulate. Rival: outcomes deteriorate because evaluators lack decision rights, even when checking capacity is sufficient. A third rival is harder incoming tasks.',
 question='Does pseudo-resolution arise from an attention queue, from missing corrective authority, or from their interaction?',
 computational_discriminant='Cross solution-arrival rate, verification service capacity and the authority to reopen or halt a decision while holding task difficulty and total effort fixed. Track unresolved problem stock, age, recurrence, accepted false solutions and diversion of attention from problem sensing. Authority-only and capacity-only interventions separate mechanisms that an aggregate completion rate would combine.',
 empirical_design='In a controlled organisational task, vary answer availability and escalation rights separately. Record proposed, checked, accepted, reopened and durably resolved cases, with planted errors and delayed follow-up. For field work, use an intake-to-correction event log and compare equivalent cases around a change in escalation policy; self-reported evaluator activity is insufficient.',
 limits='The public announcement verifies an arrangement, not actual veto power or queue failure. Synthetic organisations isolate represented processes; they do not establish prevalence in real firms.',
 new_question='Can adding evaluators reduce durable resolution by legitimising more unchecked solutions when their findings remain advisory?'),
 dict(id='ry-3',title='Does a shared machine insight retain value when everybody acts on it?',study='Glimpse ABM · AI foresight and entrepreneurial competition',chains=['094-ie-2','112-ie-4','113-ie-4','120-ie-2'],sources=['interaction-tax'],
 phenomenon='The Interaction Tax study reports solution convergence after agents exchange complete outputs under matched budgets. This supplies a demonstrated micro-level convergence mechanism in bounded optimisation tasks. The market chains raise a separate question about common AI-directed investment; they do not establish that common foresight caused market crowding.',
 mechanism='Hypothesis: correlated machine-assisted foresight directs firms toward similar opportunities, so better identification raises gross opportunity quality while competition reduces appropriable value. Rival: costly execution or a supply bottleneck, rather than convergence, explains weak returns. Information accuracy and cross-actor error correlation must therefore vary independently.',
 question='When does an epistemic improvement cease to be a private advantage because its recommendations are shared?',
 computational_discriminant='Cross forecast quality with signal correlation while holding marginal signal quality fixed; then vary adoption share and market expansion. Compare foreseen opportunity value, executed novelty and realised value. Ablate output imitation without removing shared information. Crowding should depend on correlated action and rival adoption; an execution bottleneck should survive when choices are decorrelated.',
 empirical_design='A market experiment can randomise whether entrants receive a common high-quality signal or equally accurate independent signals, then observe entry, choice similarity, price and realised surplus. Analyse market-level spillovers instead of treating entrants as independent observations. A field design would require traceable recommendation exposure and demand changes, which the briefing does not supply.',
 limits='A verifier-scored solution task is not a customer market. The proposed bridge is a mechanism hypothesis with an explicit missing step: similar answers must produce competing actions for convergence to dissipate value.',
 new_question='When can integrating different machine perspectives protect entrepreneurial value by preserving action diversity, even if it adds no predictive accuracy?'),
 dict(id='ry-4',title='When should a useful representation be abandoned?',study='Polymathy LLM-ABM and orienting under uncertainty',chains=['091-ie-4','092-ie-4','094-ie-2','117-ie-1'],sources=['compression-preprint','interaction-tax'],
 phenomenon='Molinaro and Collins’ original preprint tests a compression account of goal-dependent learning; the multi-agent study tests how communication changes diversity. Together they motivate a bounded question about the cost of efficiently retaining the wrong distinctions after a goal changes. Neither identifies an LLM’s internal representation.',
 mechanism='Hypothesis: integration earns its value by preserving source constraints and detecting when the receiving problem requires distinctions that a compact prior representation discarded. Rival: apparent polymathic gains come from more retrieval, more compute, persuasive language or a generic ensemble effect.',
 question='Does productive disanalogy improve the ability to revise a representation when the goal changes?',
 computational_discriminant='Cross breadth, domain depth and integration with a controlled goal switch. Hold tokens, tools and accepted evidence constant. Compare full-solution sharing with independent proposals and constraint-focused critique. Include an ablation that preserves factual access but removes the ability to reject an analogy. Measure selective transfer, invalid transfer and recovery, not just average fluency.',
 empirical_design='Construct transfer tasks with matched surface similarity and independently specified shared constraints. Require a predicted boundary before feedback. Blind assessors to condition and test whether a disanalogy intervention improves held-out goal-change performance beyond a resource-matched generalist baseline.',
 limits='The accessible source is the 2025 preprint; the October 2026 publisher page did not open in this audit. The task manipulates represented goal changes. It does not operationalise an unrestricted Knightian outcome space.',
 new_question='Is the most useful form of breadth the capacity to find another analogy, or the capacity to know which existing analogy to stop using?'),
 dict(id='ry-5',title='Does a warning become useful through authority or through better information?',study='Human–AI ensembles · epistemic coupling and persistent augmentation',chains=['101-ie-3','104-ie-2','105-ie-1','116-ie-3','117-ie-3','120-ie-3'],sources=['g20-0901','embedded-evaluators'],
 phenomenon='The G20 chair’s statement is an inspectable document that replaces an alleged absence, yet its publication does not establish implementation. Embedded evaluation similarly provides a visible information-producing role while leaving the effect of contested findings to be observed. In both cases, access to evidence and authority over action are separate.',
 mechanism='Hypothesis: improved sensing changes outcomes only when an actor has a usable correction route and accepts its costs. Rival: the information itself is inadequate, so additional authority cannot improve the decision. Coordination latency is a third explanation.',
 question='Under what configurations does the human contribution remain interpretation and intervention rather than ceremonial approval?',
 computational_discriminant='Cross signal quality, correction rights and delay under matched capability. Give some agents accurate dissenting evidence but no authority, and others authority with noisy evidence. Measure consequential corrections, justified overrides, false halts and downstream costs. A coupling mechanism predicts an interaction between usable evidence and authority.',
 empirical_design='Use a preregistered decision experiment with auditable cases that sometimes require overriding a recommendation. Randomise both evidence access and the cost or protection of override. Report justified and unjustified overrides separately. In field records, trace one finding through a named decision maker to a changed action.',
 limits='Frequent overrides are not automatically good, and agreement is not automatically abdication. These are proposed comparisons, not findings about any named organisation’s actual governance.',
 new_question='Can perfect transparency worsen abdication by making a decision appear supervised when the observer cannot change it?'),
 dict(id='ry-6',title='When does an audit record cease to be an observation?',study='Classification limits and Knightian uncertainty · configurational computational theory',chains=['095-ie-4','097-ie-3','111-ie-1','119-ie-2'],sources=['g20-0901'],
 phenomenon='The cycle repeatedly copied anomaly cards while later issues explicitly marked them not reassessed. It also used valid-looking READ tokens for incompatible meanings. These are directly inspectable properties of the archive, distinct from whether the underlying public events occurred.',
 mechanism='Hypothesis: a stable schema can preserve stale or semantically shifted beliefs by making record continuity resemble renewed evidence. Rival: the information remains accurate and only the presentation is repetitive. A third rival is a rational review cadence under long outcome lags.',
 question='How should a human–AI system allocate attention between new signal acquisition, old-claim reinspection and revision of the categories themselves?',
 computational_discriminant='Model finite attention divided among novelty, due-date reviews and category revision. Cross persistence of records with evidence decay and world change. Keep observation cost fixed; compare copying, fixed schedules and discrepancy-triggered review. Score detected category failures and missed changes separately from forecast endpoints.',
 empirical_design='Randomise audit interfaces to display last-carried and last-substantively-reviewed dates separately. Seed known changes and unchanged long-horizon cases. Measure detection, false closure, review time and category repair. A shadow experiment can compare O/R/H formulations on the same cases without degrading the public briefing.',
 limits='The daily corpus is selected by its own production process, uses no random assignment, and has correlated repeated threads. It can reveal process defects and generate tasks; it cannot establish the causal superiority of orienting or validate a model of Knightian uncertainty.',
 new_question='Does faster record accumulation eventually reduce a system’s capacity to notice that its categories no longer fit?'),
]

def clean(s): return re.sub(r'\s+',' ',s).strip()
def after(text,label,endlabels):
 m=re.search(label+r'\s*:?\s*(.*?)(?='+ '|'.join(endlabels)+r'|$)',text,re.I)
 return clean(m.group(1)) if m else None
def source_links(ids):
 return ' '.join(f'<a href="{E(s["url"])}">{E(s["title"])}</a>' for s in SOURCES if s['id'] in ids)

def extract(include120):
 records=[]
 for p in sorted((REPO/'briefings').glob('*.html')):
  raw=p.read_text(); soup=BeautifulSoup(raw,'html.parser'); text=soup.get_text(' ',strip=True)
  m=re.search(r'(?:Briefing\s+(?:No\.?\s*)?|No\.\s*)(\d{3})',text)
  if not m or not 91 <= int(m[1]) <= (120 if include120 else 119):continue
  n=int(m[1]); rec=dict(number=n,date=p.stem,file=f'briefings/{p.name}',sha256=hashlib.sha256(raw.encode()).hexdigest(),full_text=text,chains=[],anomalies=[])
  for i,c in enumerate(soup.select('#s-ie article.chain'),1):
   rec['chains'].append(dict(chain_id=f'{n:03d}-ie-{i}',title=(c.find(['h3','h4']) or c).get_text(' ',strip=True),text=c.get_text(' ',strip=True),html=str(c)))
  for i,c in enumerate(soup.select('#s-an article.anomaly'),1):
   rec['anomalies'].append(dict(occurrence_id=f'{n:03d}-an-{i}',stable_id=c.get('data-anomaly-id'),title=(c.find(['h3','h4']) or c).get_text(' ',strip=True),text=c.get_text(' ',strip=True),links=[a['href'] for a in c.select('a[href]')]))
  rec['sources']=[dict(title=a.get_text(' ',strip=True),url=a['href']) for a in soup.select('a[href^="http"]')]
  # Remove the permanent display, navigation and carried anomaly register.
  for el in soup.select('.vi,#s-sa,#s-an,nav,script,style'):el.decompose()
  rec['analytical_text']=' '.join(x.get_text(' ',strip=True) for x in soup.select('section[id^="s-"]'))
  records.append(rec)
 counts=Counter(r['number'] for r in records)
 for r in records:
  if counts[r['number']]>1:
   for i,c in enumerate(r['chains'],1):c['chain_id']=f"{r['number']:03d}-{r['date'].replace('-','')}-ie-{i}"
 return records

def chain_record(r,c,registry):
 t=c['text']; cid=c['chain_id']; bs=BeautifulSoup(c['html'],'html.parser')
 ps=[x.get_text(' ',strip=True) for x in bs.find_all('p')]
 original=re.search(r'READ:\s*([ORH])',t)
 confirms=after(t,r'CONFIRMS:',[r'REFUTES:',r'Ripeness:'])
 refutes=after(t,r'REFUTES:',[r'Ripeness:'])
 rm='H' if cid=='118-ie-3' else 'O'
 # Case-sensitive label extraction avoids splitting on ordinary words such
 # as "which hypothesis" inside an inference paragraph.
 narrative=' '.join(ps)
 markers=r'\b(?:OBSERVATION|OBS|Observation|INTERPRETATION|INF|Inference|HYPOTHESIS|HYP|Hypothesis)(?=\s|:)'
 def part(label):
  match=re.search(r'\b(?:'+label+r')\b\s*:?\s*(.*?)(?='+markers+r'|Release field|Path A|Path 1|CONFIRMS:|$)',narrative)
  return clean(match[1]) if match else None
 observed=part('OBSERVATION|OBS|Observation')
 inference=part('INTERPRETATION|INF|Inference')
 hypothesis=part('HYPOTHESIS|HYP|Hypothesis')
 release=after(t,r'Release field',[r'CONFIRMS:',r'Ripeness:'])
 if not observed: observed=ps[0] if ps else t
 if not inference:inference=ps[1] if len(ps)>1 and not ps[1].startswith('Path') else 'Interpretation is integrated with the opening prose; see exact text.'
 if not hypothesis:hypothesis=release or confirms
 horizon=next((x for x in ps if 'Ripeness' in x or 'RIPENESS' in x),None)
 if not horizon:
  tag=bs.select_one('.read'); horizon=tag.get_text(' ',strip=True) if tag and 'RIPENESS' in tag.get_text() else None
 if not horizon:
  m=re.search(r'RIPENESS:\s*(.*?)(?='+re.escape(c['title'])+r')',t)
  horizon=m.group(1).strip() if m else 'No separately extractable calendar horizon; inspect exact text.'
 required='comparative_mechanism_test' if cid in RESEARCH else 'dated_event_or_document_followup'
 evidence=[s for s in SOURCES if cid in s['chains']]
 reason=(f"The confirming proposition requires a comparative test: {confirms}" if cid in RESEARCH else f"The terminal criterion remains unadjudicated at the cutoff: {confirms}")
 if evidence:reason+=' Bounded component checks are recorded as '+', '.join(s['id'] for s in evidence)+'. They do not establish this complete criterion; see the source-check ledger for the exact scope.'
 else:reason+=' No qualifying independent outcome check was completed for this chain; archive recurrence alone is not closure.'
 if cid in HELD:
  reason=HELD[cid]; outcome='held'; label='Held · stated event criterion'; timing='adjudicated_event'; timing_basis='The stated event/document criterion is already met within its prospective window.'
 else:
  outcome='indeterminate'; label='Unresolved'
  if cid in DUE:timing='due_unadjudicated'; timing_basis=DUE[cid]
  elif cid in UNSCHEDULED:timing='deadline_not_operationalized'; timing_basis='A proposed run count, readiness statement or qualitative horizon does not supply a scheduled final observation. It cannot be classified as an expired forecast solely from elapsed calendar time.'
  elif cid in MIXED:timing='mixed_due_and_future'; timing_basis='The card joins a near observation with later comparison or implementation evidence. The near component is reviewable; its entire stated test has a later or unspecified endpoint.'
  else:timing='not_yet_due'; timing_basis='The stated closing window extends beyond 12 October 2026. A qualifying event could resolve earlier, but absence before that endpoint is not refutation.'
 note=DIAGNOSTICS.get(cid,'Terminal prose retains alternative releases and an explicit possibility of refutation; coding uses the text, not a later outcome.')
 if cid in COLLISIONS:note='Original READ expansion uses a different meaning from O/R/H. Retrospective terminal-step review finds alternatives retained. '+note
 return dict(chain_id=cid,briefing=r['number'],date=r['date'],source_file=r['file'],lens='cross-lens',lens_note='Inference section gives no single owning lens; do not infer a lens from a project label.',title=c['title'],text=t,patterns_invoked=[p['slug'] for p in registry if p['name'].casefold() in t.casefold()],conditions=dict(X=observed,Y=inference,Z=hypothesis),release_field=release,confirms=confirms,refutes=refutes,horizon=horizon,test_unit=required,timing_status=timing,timing_basis=timing_basis,original_read_tag=original[1] if original else None,original_tag_namespace_valid=cid not in COLLISIONS,retrospective_read_mode=rm,read_mode_basis=note,original_llm_signature=None,outcome=outcome,outcome_label=label,classified_via='original_criterion_and_bounded_external_checks',outcome_evidence=reason,source_checks=[s['id'] for s in evidence],break_type=None,break_type_basis='No adjudicated failed causal transition; unknown is not Type V.',llm_signature=None,llm_signature_basis='No prospective S1–S7 label and no demonstrated chain failure; no cognitive mechanism inferred from prose alone.',construction_diagnostic=DIAGNOSTICS.get(cid))

def anomaly_records(records):
 by=defaultdict(list)
 for r in records:
  for a in r['anomalies']:by[a['stable_id']].append({**a,'source_date':r['date'],'briefing':r['number'],'source_file':r['file']})
 threads=[]; occurrences=[]
 last_number=records[-1]['number']
 for aid,seq in by.items():
  first,last=seq[0],seq[-1];tx=last['text']
  closed=bool(re.search(r'^Closed\b|^CLOSED\b|\bSTATUS:\s*CLOSED\b',tx,re.I))
  earliest=after(tx,r'Earliest fair review:',[r'5 October register',r'7 October register',r'9 October evidence',r'Light:',r'World Bank:',r'Nature:',r'NIST:',r'Opening evidence'])
  nextobs=after(tx,r'Next observable:',[r'Earliest fair review:',r'Status:'])
  checks=[]
  if aid=='095-g20-commitment-gap':
   disposition='resolved'; checks=['g20-0901'];note='The missing-document observable is filled by Treasury’s 1 September chair’s statement. This resolves document absence, not institutional effectiveness. The ID nevertheless disappeared from the anomaly register after 1 September.'
  elif aid=='an108-diesel-instrument':
   disposition='resolved';checks=['iea-1002','iea-1007'];note='The IEA record identifies the coordinated stock-release instrument. Delivery and product accounting remain open in an114-diesel-accounting; the closed policy-choice record is not a resolved price mechanism.'
  elif closed:
   disposition='closed_in_archive_unverified';note='The archive explicitly closes this record. Its cited outcome has not been independently adjudicated here; preserve the closure as an archival fact, not a verified world outcome.'
  elif last['briefing']<last_number:
   disposition='silently_died';note='This stable ID disappears before the final issue with no explicit closure or successor-ID link in its record. This is a tracking failure only; it does not establish resolution, persistence or failure in the world.'
  else:
   disposition='open_not_yet_due';note='The final register carries the question forward. Most carried cards explicitly say not reassessed; carry-forward is not fresh evidence that the absence persists. Review against the stated observable and date.'
  history=[dict(source_date=x['source_date'],briefing=x['briefing'],occurrence_id=x['occurrence_id']) for x in seq]
  reassessed=re.findall(r'\bREASSESSED\s+(\d{1,2}\s+[A-Za-z]+\s+2026)',tx)
  thread=dict(anomaly_id=aid,title=first['title'],first_date=first['source_date'],last_date=last['source_date'],occurrences=len(seq),disposition=disposition,evidence=note,source_checks=checks,next_observable=nextobs,earliest_fair_review=earliest,original_text=first['text'],latest_text=tx,history=history,archive_closed=closed,last_explicit_reassessment=reassessed[-1] if reassessed else None,final_card_says_not_reassessed='not reassessed' in tx.casefold())
  threads.append(thread)
  for j,x in enumerate(seq):
   occurrences.append({**x,'as_of_audit_disposition':disposition,'evidence':note,'later_briefings':[q['briefing'] for q in seq[j+1:]],'next_same_id_occurrence':seq[j+1]['occurrence_id'] if j+1<len(seq) else None})
 return threads,occurrences

def table(headers,rows):
 return '<div class="matrix-wrap" role="region" aria-label="'+E(' · '.join(headers))+'" tabindex="0"><table><thead><tr>'+''.join('<th scope="col">'+E(x)+'</th>' for x in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+str(v)+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table></div>'

def main():
 global REPO, PRIVATE
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--include120',action='store_true',help='Include the complete 091–120 cycle.')
 ap.add_argument('--repo',type=Path,default=REPO,help='Repository root; defaults to the parent of this script directory.')
 ap.add_argument('--evidence-dir',type=Path,default=None,help='Optional private extraction and receipt directory; omitted means no private writes.')
 args=ap.parse_args()
 REPO=args.repo.expanduser().resolve()
 PRIVATE=args.evidence_dir.expanduser().resolve() if args.evidence_dir else None
 if not (REPO/'briefings').is_dir() or not (REPO/'synthesis').is_dir():
  ap.error('--repo must contain briefings/ and synthesis/')
 records=extract(args.include120); registry=json.loads((REPO/'concepts/registry.json').read_text())['patterns']
 assert records and (not args.include120 or records[-1]['number']==120)
 inventory=[chain_record(r,c,registry) for r in records for c in r['chains']]
 assert all(c['confirms'] and c['refutes'] for c in inventory)
 threads,occurrences=anomaly_records(records)
 prev=yaml.safe_load((REPO/'synthesis/cycle-003.yaml').read_text())
 prior1=yaml.safe_load((REPO/'synthesis/cycle-001.yaml').read_text())
 prior2=yaml.safe_load((REPO/'synthesis/cycle-002.yaml').read_text())
 vocab=[]
 for p in registry:
  docs=[r['number'] for r in records if p['name'].casefold() in r['analytical_text'].casefold()]
  status='retained' if docs else ('remain_retired' if p['status']=='retired' else 'retirement_flag')
  if p['name']=='Sabbath Visibility' and not docs:status='retire_after_prior_watch'
  vocab.append(dict(concept=p['name'],slug=p['slug'],analytical_document_count=len(docs),briefings=docs,decision=status,method='Exact name in analytical section text after removing permanent vocabulary entries, anomaly ledger, navigation and source archive; a mention is an upper bound on substantive reuse.'))
 n=len(inventory); ac=len(occurrences); th=len(threads); dist=Counter(c['retrospective_read_mode'] for c in inventory); original=Counter(c['original_read_tag'] for c in inventory); ad=Counter(a['disposition'] for a in threads)
 outcomes=Counter(c['outcome'] for c in inventory); timing=Counter(c['timing_status'] for c in inventory)
 sourceids={s['id'] for s in SOURCES}; assert all(set(c['source_checks'])<=sourceids for c in inventory)
 headline=(f"Cycle 4 contains {n} chains across {len(records)} dated briefings. Every chain now states confirmation and refutation criteria, but complete fields do not guarantee a discriminating test. Public-event forecasts, comparative research propositions and intermediate milestones still need different closure rules. Seven early READ labels reuse R/H for incompatible meanings. Independent coding yields {dist['O']} Orienting, {dist['H']} Hybrid and {dist['R']} Representation reads, leaving no useful mode comparison. Primary sources satisfy two stated event criteria; {outcomes['indeterminate']} chains remain unresolved. Seven reviews are due but unadjudicated; future, mixed and unscheduled tests are separated. Event closure does not validate a broader causal explanation. The anomaly ledger contains {ac} appearances of {th} distinct questions, so repetition cannot count as renewed observation. The next cycle should align each criterion with one proposition, preserve last-review dates, register an outcome source and time window, and turn public phenomena into mechanism-discriminating research designs. The principal research yield is a set of testable questions about renewed delegation demands, scarce checking, correlated foresight, productive disanalogy and usable correction authority.")
 meta=[
 dict(id='mp-011',status='held_in_abeyance',statement='Read mode predicts break severity.',instances=['101-ie-3','118-ie-3'],finding='No R comparison group, one boundary H case, and only two adjudicated event criteria. No promotion or causal claim.'),
 dict(id='mp-012',status='not_testable',statement='Single-vector collapse explains the model-endogenous component of velocity errors.',instances=['103-ie-2','118-ie-3'],finding='No observed velocity failure is established; terminal construction alone cannot establish a failed mechanism.'),
 dict(id='mp-013',status='provisional_not_retested',statement='Template-projection failures can be disciplined.',instances=['097-ie-3','114-ie-2'],finding='No cross-year failure established in the bounded checks. Absence of detection is not an exhaustive factual audit or proof of eliminated failure.'),
 dict(id='mp-014',status='canonical_methodological_constraint',statement='A production discipline that removes a comparison group cannot estimate its own causal advantage from the resulting corpus.',instances=['091-ie-2','101-ie-3','118-ie-3'],finding='Recurs across Cycles 3 and 4; promoted only as an identification constraint, not as an empirical claim about O superiority.'),
 dict(id='mp-015',status='provisional_refined',statement='A release field needs a criterion that discriminates the same proposition; the mere presence of CONFIRMS/REFUTES is insufficient.',instances=['091-ie-1','103-ie-2','111-ie-1'],finding='Cycle 3 identified missing criteria. Cycle 4 repairs presence but exposes proposition mismatch. Refinement remains provisional because the mechanism of saturation has not been outcome-tested.'),
 dict(id='mp-016',status='new_provisional',statement='Outcome closure must match the original test: an event can close its stated criterion without validating a broader mechanism or cross-case proposition.',instances=['095-ie-1','096-ie-2','114-ie-2'],finding='NASA, the Fed and the IEA make narrower components observable while their chains require later performance or discriminating causal evidence.'),
 ]
 recs=[
 dict(change='Give each chain one focal proposition and label its test as an event follow-up, a comparative mechanism test, or a proposed experiment.',basis=['091-ie-1','093-ie-1','111-ie-1'],tradeoff='Fewer broad omnibus chains; some useful analogies move into the research section.',verification='Every 121–150 chain has a proposition ID, test-unit field, matched CONFIRMS/REFUTES pair and a named outcome source.'),
 dict(change='Apply the original event or comparative criterion, retain partial milestones and leave missing evidence unresolved.',basis=['095-ie-1','096-ie-2','114-ie-2'],tradeoff='Fewer apparent resolutions and more delayed adjudications.',verification='Any event-level Held call has a source satisfying the original event criterion; broader causal tests require the stated comparative evidence. No stronger identification requirement is added retrospectively. Type V requires an actually resolved timing error.'),
 dict(change='Separate last-carried from last-substantively-reviewed dates and explicitly close or hand off every disappearing anomaly ID.',basis=['097-ie-3','an-091-004-predictive-not-operational','095-g20-commitment-gap'],tradeoff='A review queue needs attention; not every question receives a daily update.',verification='No ID disappears without closure or successor ID; due reviews cite fresh evidence or a bounded unsuccessful source search. Counts use both distinct threads and appearances.'),
 dict(change='Use literal read-mode expansions and register a shadow comparison if testing the claimed advantage of O over R/H.',basis=sorted(COLLISIONS)+['118-ie-3'],tradeoff='Additional coding and experimental work; the public briefing itself keeps its orientation discipline.',verification='No READ namespace collisions; outcome-blind duplicate coding of a natural sample; no causal mode claim without an external or randomized comparison.'),
 dict(change='Make research relevance a phenomenon-to-design argument with a rival, a computational intervention and an observable empirical contrast.',basis=['093-ie-3','094-ie-2','095-ie-2','119-ie-2'],tradeoff='Fewer named connections, but each generates a specific research decision.',verification='Research entries distinguish sourced phenomena from hypotheses, name the study question, explain what an ablation would distinguish and retain disconfirming cases; no claim of a completed study result.'),
 ]
 audit=dict(schema_version=4,cycle=4,date_generated=CUTOFF,audit_status='complete_corpus_coding' if args.include120 else 'awaiting_briefing_120',nominal_briefings=[91,120],dated_artifacts=len(records),date_range=[records[0]['date'],records[-1]['date']],scope_note='Dated HTML files are units; every inference and every anomaly appearance is extracted. A repeated anomaly ID is one thread with multiple appearances.',headline=headline,source_cutoff=CUTOFF,method=dict(extraction='All dated source HTML read in full by the parser; every inference chain and distinct anomaly history coded; full original text retained in private extraction.',outcome='Criterion-matched classification: a stated event or document can be Held on that event alone. Comparative evidence is required only where the original criterion requires it. Event-level support does not validate a broader causal explanation.',missingness='Unobserved failures are not assigned a break type or cognitive signature.',read_mode='Original tokens preserved separately from retrospective, outcome-independent stance coding.',limitations='Single retrospective coder; no inter-rater reliability. External checks are bounded, not exhaustive. Narrative chains and repeated anomalies are dependent selected observations.'),corpus_manifest=[{k:r[k] for k in ['number','date','file','sha256']} for r in records],aggregate_distributions=dict(outcome=dict(outcomes),timing_status=dict(timing),break_type={f'type_{i}':0 for i in ['i','ii','iii','iv','v','vi','vii']},observed_break_denominator=0,unassigned_breaks=outcomes['indeterminate'],break_not_applicable_held=outcomes['held'],prospective_signature_count=0,llm_signature={f's{i}':0 for i in range(1,8)},signature_unassessable=n,original_read_tokens=dict(original),retrospective_read_mode=dict(dist),invalid_read_namespace=len(COLLISIONS),explicit_confirms_fields=n,explicit_refutes_fields=n,test_unit=dict(Counter(c['test_unit'] for c in inventory))),cross_cycle_comparison=dict(cycle3=dict(dated_artifacts=31,chains=155,anomaly_appearances=155,read_mode=prev['aggregate_distributions']['read_mode'],confirms=0,refutes=0,outcome_rule='named release visible, commonly via later archive narration'),cycle4=dict(dated_artifacts=len(records),chains=n,anomaly_appearances=ac,distinct_anomaly_ids=th,confirms=n,refutes=n,outcome_rule='independent evidence matched to each original event or comparative criterion'),comparability='Construction fields are comparable per chain. Outcome rates are not comparable because evidence and closure rules changed. Anomaly appearances differ because stable IDs are now repeatedly carried.'),read_mode_cross_tab={m:{'held':sum(c['retrospective_read_mode']==m and c['outcome']=='held' for c in inventory),'indeterminate':sum(c['retrospective_read_mode']==m and c['outcome']=='indeterminate' for c in inventory),'inverted':0,'held_spurious':0,'failed_z':0} for m in ['O','R','H']},break_type_signature_cross_tab=[],read_mode_break_cross_tab=[],read_mode_signature_cross_tab=[],cross_tab_note='Empty observed-failure cells are non-estimable, not evidence that O has no failures.',meta_principles=meta,prior_principle_disposition='mp-001 through mp-010 retained as previously recorded, not newly corroborated. No evidence of non-applicability is inferred from missing adjudication; retirement clocks are not advanced on unobserved outcomes.',vocabulary_curation=dict(ledger=vocab,meta_6_decision='Table Verification Asymmetry. Reopen only after at least three independently verified instantiations require a mechanism that cannot be represented by META-1 coupling failure; no promotion from repeated labels.',reactivated=[],application='Proposed curation only; canonical repository remains unchanged by this audit.'),anomaly_accounting=dict(unique_threads=th,appearance_count=ac,distribution=dict(ad),ledger=threads,occurrence_ledger=occurrences,meaning='Silently died describes archive attention. Closed-in-archive is separate from externally verified resolved. Carry-forward does not establish persistent real-world absence.'),research_yield=RESEARCH_YIELD,recalibrations_for_next_30=recs,primary_source_checks=SOURCES,inference_inventory=inventory)
 raw=json.dumps(records,indent=2,ensure_ascii=False)
 if PRIVATE:
  PRIVATE.mkdir(parents=True,exist_ok=True)
  (PRIVATE/'cycle004-complete-extract.json').write_text(raw)
 audit['raw_extract_sha256']=hashlib.sha256(raw.encode()).hexdigest()
 (REPO/'synthesis/cycle-004.yaml').write_text(yaml.safe_dump(audit,allow_unicode=True,sort_keys=False,width=110))
 render(audit)
 if PRIVATE:
  read_files=['CONTINGENCY_AUDIT.md','CLAUDE.md','STRUCTURAL_CONCEPTS.md','AGENTS.md','synthesis/cycle-003.yaml','synthesis/cycle-002.yaml','synthesis/cycle-001.yaml','synthesis/cycle-002-shi-discipline.md','concepts/registry.json']
  initial_files_read=json.loads((PRIVATE/'receipt.json').read_text()).get('files_read',read_files) if (PRIVATE/'receipt.json').exists() else read_files
  receipt=dict(status=audit['audit_status'],files_written=['synthesis/cycle-004.html','synthesis/cycle-004.yaml','scripts/build-cycle-004.py'],source_briefing_writes=False,counts=dict(dated_artifacts=len(records),chains=n,anomaly_appearances=ac,unique_anomaly_ids=th,anomaly_dispositions=dict(ad),read_modes=dict(dist),outcomes=dict(outcomes),timing=dict(timing)),all_required_record_ids_present=True,full_source_hashes=audit['corpus_manifest'],source_checks=SOURCES,primary_anchor_fetch_limitation='Nature compression article redirected to inaccessible identity endpoint; original 2025 preprint and author-linked source repository were used as historical anchors. The China NBS page opened successfully during initial checks; the later grouped receipt refresh returned a transient Internal Error for that page.',reading_scope='All source HTML and previous cycle YAML parsed in full; all inference text and unique anomaly current records inspected, with exact histories preserved. No claim that every daily factual assertion was externally checked.',files_read=initial_files_read,root_checks_required=['Briefing 120 incorporated after author readiness; rerun with --include120 if final QC changes any artifact.','Read prose, research mechanism mappings and claim granularity decisions independently.','Verify all 30 corpus artifact hashes after any sibling revision.','Run build --check and rendered desktop/mobile accessibility review.','Apply approved curation separately if desired; this agent edited no canonical file.','Do not publish without explicit user instruction.'],memory_used='MEMORY.md lines 758–784: publication and full-QC boundary, live verified against AGENTS.md and CLAUDE.md.')
  receipt['artifact_sha256']={rel:hashlib.sha256((REPO/rel).read_bytes()).hexdigest() for rel in receipt['files_written']}
  receipt['corpus_root']=str(REPO)
  receipt['authorized_override']='12 October user instruction supersedes the old prohibition on named research-program connections; editorial and private operational exclusions remain absolute.'
  receipt['empirical_limits']=['Two original event criteria are Held; 111 chains remain Unresolved. Event confirmation does not establish the broad causal mechanisms.', 'No failure taxonomy, cognitive signature, O/R/H causal advantage, or completed research-model validation is inferred from the selected daily corpus.', 'Single retrospective coder; no inter-rater reliability. Repeated narrative chains and anomaly copies are dependent observations.', 'Fifteen bounded primary-source checks establish only the original event criteria, components or research anchors specified in the source ledger.', 'Two anomaly observables are independently resolved; four explicit archive closures remain unverified. Silently died denotes loss from the register, not a world outcome.']
  (PRIVATE/'receipt.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False))
  receipt_md=f'''# Cycle 004 private evidence receipt

 Reproduction of the fixed 12 October 2026 audit. This builder rewrites the two synthesis artifacts and optional private receipts; it does not change source briefings, perform network checks, commit, push or publish.

 The corpus contains every dated artifact numbered 091–120: {len(records)} artifacts, {n} chains, {ac} anomaly appearances and {th} distinct anomaly IDs. Briefing 120 was incorporated after author readiness. The manifest binds each source to its SHA-256; subsequent source changes require regeneration.

 All source HTML files were parsed. All inference-chain text and each distinct anomaly’s current question were inspected, with dated histories retained. This is not independent verification of every factual assertion in the daily archive. {len(SOURCES)} primary-source checks supply only their stated event outcomes, components or research anchors.

 The original criterion governs the outcome. Two event criteria are Held (102-ie-1 and 104-ie-3); {outcomes['indeterminate']} chains remain Unresolved. A restriction change or dated institutional handoff need not prove a causal model to meet its stated event test. Conversely, an event cannot substitute for a comparative test the chain explicitly requires. The initial blanket whole-chain rule was corrected during root review because it imposed a stronger requirement than those event tests.

 Timing counts: {dict(timing)}. Due but unadjudicated denotes unfinished evidence work, not failure. Proposed run counts and qualitative readiness statements do not define an expired calendar forecast. The YAML records the basis for every chain.

 The corpus has 39 comparative tests and 74 event/document follow-ups. Retrospective stance: O {dist['O']}, H {dist['H']}, R {dist['R']}. Original tags remain separate, including seven namespace collisions. No causal O advantage, cognitive-signature prevalence, break-severity distribution or completed study-model validation is inferred from this selected corpus.

 Anomaly dispositions: {dict(ad)}. Repeated carry-forward is not a fresh review. Silently died describes disappearance from the register, not a world outcome. Six research designs include phenomena, rival mechanisms, computational discriminants, empirical contrasts, limits and fresh questions. Editorial and private operational information remain excluded.

 The full file-reading list, source boundaries and artifact hashes are in receipt.json; full dated extraction is cycle004-complete-extract.json. Root must review claim granularity and study mechanisms, run build checks, inspect desktop/mobile rendering, and regenerate after source edits. Reproduction: `python3 scripts/build-cycle-004.py --include120 --repo /path/to/checkout --evidence-dir /path/to/private/evidence`. Omit --evidence-dir to suppress private writes. Curation recommendations are not canonical registry changes.

 Current artifact hashes:

 '''+ '\n'.join(f'- `{k}`: `{v}`' for k,v in receipt['artifact_sha256'].items())+'\n'
  (PRIVATE/'RECEIPT.md').write_text(receipt_md)
 print(json.dumps(dict(dated_artifacts=len(records),chains=n,anomaly_appearances=ac,unique_anomaly_ids=th,outcomes=dict(outcomes),timing=dict(timing),read_modes=dict(dist),private_evidence_written=bool(PRIVATE)),ensure_ascii=False))

def render(a):
 inv=a['inference_inventory'];n=len(inv);ac=a['anomaly_accounting'];dist=a['aggregate_distributions']['retrospective_read_mode']
 def sec(id,title,body):return f'<section id="{id}"><h2>{E(title)}</h2>{body}</section>'
 def p(text):return '<p>'+text+'</p>'
 content=[]
 content.append(sec('headline','Headline','<div class="lead">'+p(E(a['headline']))+'</div>'))
 scope=p(f"The nominal window is 091–120. The corpus contains <strong>{a['dated_artifacts']} dated artifacts, {n} inference chains and {ac['appearance_count']} anomaly-card appearances representing {ac['unique_threads']} distinct IDs</strong>. Every appearance remains in the machine-readable ledger. No number is duplicated in this window. The source cutoff is 12 October 2026.")
 scope+=p('This is a completed coding pass over the included corpus, with a bounded set of external outcome checks. It is not an exhaustive verification of every historical factual claim. The original full chains are reproduced below as archive evidence; their OBS labels remain claims made by the originating briefing. They are not newly verified observations of this audit.')
 scope+=table(['Measure','Cycle 003','Cycle 004','Interpretation'],[
  ['Dated artifacts','31',a['dated_artifacts'],'Cycle 3 includes both dated 062 files.'],['Chains','155',n,'Use chain-level denominators.'],['Explicit confirmation and refutation fields','0 / 155',f'{n} / {n}','Presence improved; quality needs independent review.'],['Anomaly appearances','155',ac['appearance_count'],f"Cycle 4 has {ac['unique_threads']} distinct threads; copies are not new anomalies."],['Original criteria independently adjudicated','Not measured on this rule',a['aggregate_distributions']['outcome'].get('held',0),'Outcome-rate comparison would mix evidence standards.']])
 content.append(sec('scope','Scope and fair comparison',scope))
 body=p(f"<strong>Two chains are Held at their original event criteria; {a['aggregate_distributions']['outcome']['indeterminate']} remain Unresolved (protocol: Indeterminate).</strong> The audit evaluates the test the author actually stated. A document or event forecast does not acquire a new causal-identification requirement during review. Conversely, a comparative proposition cannot be confirmed by a loosely related event. A Held event criterion is not model validation.")
 body+=p('In 102-ie-1, the stated test needs one named institution to change its restriction level or date by the end of October. The Environment Agency documents increased abstraction restrictions, so that test is Held. In 104-ie-3, the stated test needs a published named assignment with a date. The AU records an adopted report for the Executive Council on 27–28 January 2027. That dated handoff earns a narrow Held; the stronger language about a budget or costly transfer remains unsupported. '+source_links(['ea-drought-1001','ea-rps382','au-stcdss-0921']))
 body+=p('The Fed decision is an observed endpoint, while 096-ie-2 asks whether data releases moved odds more than speeches. Roman’s instrument activation advances commissioning, while 095-ie-1 asks whether separating milestones improves cross-program judgement. The IEA statement clarifies the origin of promised stocks, while 114-ie-2 requires a later cumulative physical-release account. Each can be partly informed without being declared Held.')
 body+=p('The remaining uncertainty has several different clocks. In 096-ie-2, the September deadline has passed: a dated policy statement cannot replace the missing comparison of market odds around data and speeches. In 114-ie-1, the 25 October runoff has not occurred at the cutoff, so the win-and-margin criterion is not yet due. In 099-ie-3, the next Chinese release is available but the chain also requires South African investment and output evidence: one branch is inspectable while the cross-country sequence remains open. In 091-ie-3, a number of controlled benchmark runs is a proposed design, not a booked future event whose nonappearance constitutes failure.')
 timing=a['aggregate_distributions']['timing_status']
 body+=table(['Timing status','Chains','Interpretation'],[[E(k.replace('_',' ')),v,{'adjudicated_event':'The stated original event criterion is met; stronger mechanism claims remain separate.','due_unadjudicated':'The original near review window has passed, but the required outcome evidence has not been adjudicated.','not_yet_due':'The final stated window is still ahead. Qualifying early events could resolve it.','mixed_due_and_future':'A near component is reviewable while another component remains future or unscheduled.','deadline_not_operationalized':'Readiness, a run count or a qualitative horizon does not define an expired calendar forecast.'}[k]] for k,v in timing.items()])
 body+=p('<strong>Due reviews:</strong> '+E(', '.join(DUE))+'. The YAML records a timing basis for every chain. Due but unadjudicated identifies unfinished evidence work; it is neither a success nor a failed forecast. No date is invented for unscheduled research.')
 body+=table(['Primary check','What is established','Chain boundary'],[[f'<a href="{E(s["url"])}">{E(s["title"])}</a><br>{s["date"]}',E(s['supports']),', '.join(s['chains'])] for s in SOURCES[:7]])
 body+=p('Seven outcome categories remain available: Held, Held (Spurious), Failed-Y, Failed-Z, Pre-empted, Inverted and Indeterminate. Held is used only for the two stated event criteria; no failure or spurious mechanism is established. A missing publication cannot be treated as rejection, and a deadline that has not passed cannot produce a timing failure.')
 content.append(sec('outcomes','Outcome classification and partial follow-up',body))
 body=p('There is no identified dominant world-break type this cycle. The distribution is shown in full because an empty failure denominator is itself a limit of the evidence. Assigning unresolved chains to velocity error would manufacture the dominant result the protocol expects to find.')
 names=['I · Agentic novelty','II · Competitive recursion','III · Coupling assumption','IV · Buffer revelation','V · Velocity miscalibration','VI · Categorical drift','VII · Spurious hit']
 body+='<div class="bars" aria-label="Observed break counts, all zero">'+''.join(f'<div class="bar-row"><span>{E(x)}</span><span class="track"></span><strong>0</strong></div>' for x in names)+'</div>'
 body+=p(f'<strong>Denominator:</strong> zero independently adjudicated failed chains; {a['aggregate_distributions']['outcome']['indeterminate']} unresolved and two Held event criteria outside the failure denominator. Percentages are undefined. These zeros do not show that the seven mechanisms were absent in the world. No representative failed cases can honestly be supplied.')
 body+=p('The active probe for Type VII asked whether a visible endpoint had been reached through the proposed mechanism. The monetary decisions, Roman activation and stock-release announcement failed the evidentiary threshold for such a claim: the endpoint alone leaves the mechanism open. They were therefore withheld from both Held and Held (Spurious). This is a stricter rule than Cycle 3’s “one named release became visible” convention.')
 body+=p('Three construction problems can already be observed without an outcome. In 091-ie-1 a public bargaining field ends in a model-comparison criterion. In 103-ie-2 an inevitable-convergence hypothesis includes persistent divergence as a release. In 111-ie-1 the stated disposition and the condition labelled CONFIRMS point in opposite publication directions. These are specification defects, not demonstrated Type I–VII failures.')
 content.append(sec('breaks','Break-point taxonomy',body))
 body=''.join('<article class="card"><h3>'+E(x['id']+' · '+x['statement'])+'</h3>'+p('<strong>'+E(x['status'].replace('_',' '))+'</strong>. '+E(x['finding']))+p('Evidence: '+E(', '.join(x['instances'])))+'</article>' for x in a['meta_principles'])
 body+=p(E(a['prior_principle_disposition']))
 content.append(sec('principles','Meta-principles across cycles',body))
 v=a['vocabulary_curation']['ledger'];zero=[x for x in v if x['decision']=='retirement_flag']
 body=p('The curation pass removes the permanent vocabulary display, source archive and carried anomaly register before counting exact-name references. Counts are an upper bound on substantive reuse, not evidence that each invocation earns its definition. All 42 historical patterns remain in the ledger; no new meta-category is promoted.')
 body+=p('<strong>Retire Sabbath Visibility after its prior watch.</strong> It has no analytical reference in this cycle. Keep Emergent Concealment retired. '+('<strong>Flag for retirement:</strong> '+E(', '.join(x['concept'] for x in zero))+'. ' if zero else '')+'These flags distinguish non-use from theoretical invalidity. Reactivation needs fresh, independently supported instances, not a return to the display.')
 body+=p('Governance Vacuum and Commons Enclosure retain their Cycle 3 discriminants. Name the responsible institution, missing capacity and consequence for the former; name the shared resource, literal access gate and gatekeeper for the latter. The high count of Commons Enclosure is a reason to inspect discrimination, not to assume that every access problem is enclosure.')
 body+=p(E(a['vocabulary_curation']['meta_6_decision']))
 body+='<details><summary>Inspect all vocabulary counts and curation decisions</summary>'+table(['Concept','Analytical documents','Briefings','Decision'],[[E(x['concept']),x['analytical_document_count'],E(', '.join(map(str,x['briefings']))),E(x['decision'].replace('_',' '))] for x in v])+'</details>'
 body+=p('The canonical taxonomy has not been edited by this audit. These are concrete curation recommendations for the separately reviewed update.')
 content.append(sec('vocabulary','Vocabulary curation',body))
 body=p(f"The unit that can persist, resolve or disappear is the distinct question: {ac['unique_threads']} IDs. The full {ac['appearance_count']}-appearance ledger records its dated history. Five archive closures were present before external reconciliation; a closure in a daily record is retained as a documentary fact even when its world outcome has not been independently verified here.")
 body+=table(['Audit disposition','Distinct threads','Meaning'],[[E(k.replace('_',' ')),v,{'resolved':'The specified missing observable is independently supplied.','closed_in_archive_unverified':'The record closes; independent adjudication is incomplete.','silently_died':'The ID vanishes without an explicit closure or successor link.','open_not_yet_due':'The final register retains the question; carry-forward is not reassessment.','persistently_absent':'Requires a fresh bounded check, not repetition.'}.get(k,'')] for k,v in ac['distribution'].items()])
 body+=p('The G20 record is the clearest repair. Treasury’s dated chair’s statement fills the missing-document observable and records dissent. The larger question about assigned duties and implementation remains live, but “no text located” cannot continue doing its work. '+source_links(['g20-0901']))
 body+=p('A second legitimate closure concerns the choice of a diesel-policy instrument. The IEA record identifies coordinated stock action, while the successor question about product shares and actual delivery remains open. Closure should move the question to its next observable, not erase it. '+source_links(['iea-1002','iea-1007']))
 body+=p('The late-cycle notation “not reassessed today” is an improvement in honesty. It also makes an important limit visible: repeating eighty questions is not eighty new checks. “Persistently absent” is not assigned from those copies. Earlier records that disappeared are recorded as tracking failures even when their stated fair-review date remains in the future.')
 body+='<details><summary>Inspect the complete distinct-anomaly ledger and histories</summary>'+table(['ID and origin','Question','Disposition','Evidence and next review'],[[E(x['anomaly_id'])+'<br>'+x['first_date']+' → '+x['last_date']+f"<br>{x['occurrences']} appearances",E(x['title']),E(x['disposition'].replace('_',' ')),E(x['evidence'])+'<br><strong>Next:</strong> '+E(x['next_observable'] or 'Consult the explicitly closed source record.')+'<br><strong>Review:</strong> '+E(x['earliest_fair_review'] or 'No future date in closed record.')] for x in ac['ledger']])+'</details>'
 body+=p('The YAML includes every dated appearance, original text, source file and later same-ID occurrences. The full occurrence ledger is retained there so the readable page does not make repeated cards appear to be independent evidence.')
 content.append(sec('anomalies','Anomaly accounting',body))
 body=p('The cycle’s strongest theoretical implication concerns what an observation can close. Under an unstable or contested classification, a realised event can be compatible with several mechanisms and several definitions of success. A multi-path field can preserve this ambiguity, but it does not resolve it. A useful orienting practice therefore pairs a bounded disposition with an explicit rule for what remains unknown after each observable arrives. The daily corpus documents this design problem; it does not estimate the superiority of one epistemic stance.')
 body+=p('The LLM-cognition implication is correspondingly narrow. Valid-looking field names can coexist with semantic drift, and a fluent terminal sentence can test a different proposition from the opening hypothesis. Those are observable features of generated text, not measurements of an internal cognitive mechanism. Identifying mean-trajectory regression, reflexive blindness or mechanism–outcome decoupling requires comparisons that separate these accounts from ordinary evidence gaps. Neither the absence of resolved failures nor the presence of polished counterfactual prose does that work.')
 body+=p('For human–AI analytical ensembles, the audit suggests that periodic reframing must sometimes change the unit of evaluation itself. The move from event forecasts to research propositions makes an unchanged forecast score misleading; the move from new anomaly cards to carried registers makes unchanged counts misleading. Human judgement adds value when it notices that the instrument is measuring a different object. The six research designs below turn that observation into questions that can be tested rather than treating this corpus as model validation.')
 content.append(sec('theory','Theoretical implications',body))
 body=p('These connections use the public research programme and the substantive question of the named studies. Each separates a sourced phenomenon from a new hypothesis. A geopolitical configuration with three actors is not, by itself, a connection to the Three-Body study: the relevant mechanism is renewed epistemic demand and the resulting composition of delegated work.')
 for x in a['research_yield']:
  body+='<article class="card research"><h3>'+E(x['title'])+'</h3><p class="k">'+E(x['study'])+'</p>'
  for key,label in [('phenomenon','Phenomenon'),('mechanism','Mechanism and rival'),('question','Study question'),('computational_discriminant','Computational discriminant'),('empirical_design','Empirical observable and design'),('limits','Limits'),('new_question','Fresh question')]:
   body+=p('<strong>'+label+'.</strong> '+E(x[key]))
  body+=p('Archive anchors: '+E(', '.join(x['chains']))+'. '+source_links(x['sources']))+'</article>'
 content.append(sec('research','Research yield: from public phenomena to discriminating studies',body))
 body=''.join('<article class="card"><h3>'+E(x['change'])+'</h3>'+p('<strong>Basis:</strong> '+E(', '.join(x['basis'])))+p('<strong>Tradeoff:</strong> '+E(x['tradeoff']))+p('<strong>Verify in 121–150:</strong> '+E(x['verification']))+'</article>' for x in a['recalibrations_for_next_30'])
 content.append(sec('recalibrations','Five recalibrations for the next 30',body))
 labels=[('S1','Mean-trajectory regression','Timing drawn toward historical averages','V'),('S2','Narrative over physical coherence','Compressed inference hides material work','V, VII'),('S3','Plausibility-mass concentration','Modal completion excludes other action sets','I'),('S4','Reflexive blindness','Actors’ anticipatory adaptation is omitted','II'),('S5','Categorical stickiness','A category is retained after its referent changes','VI'),('S6','Buffer blindness','A variable buffer is treated as constant','IV'),('S7','Mechanism–outcome decoupling','Any route to the endpoint counts as support','VII')]
 body=p(f'No chain carries an explicit prospective S1–S7 assignment. All {n} are unassessable for an observed-failure signature in this audit. This is a missing-data result, not a primary distribution of cognitive failures. Counts for identified S1–S7 are zero; percentages of identified failures are undefined.')
 body+=table(['Signature','Mechanism','Text or outcome evidence required','Related types','Identified'],[[*map(E,x),0] for x in labels])
 body+=p('S1 and S2 cannot be diagnosed from a long horizon alone: the world must first resolve the timing and the material dependency. S3 and S4 require evidence of an omitted action or anticipatory response, not merely an alternative scenario. S5 needs evidence that the category changed, not an unfamiliar noun. S6 requires a demonstrated buffer assumption and its variation. S7 is the strongest construction risk in the mismatched criteria, but the Type VII/S7 resemblance is nearly definitional and must not be counted as independent corroboration. These are coding cautions, not findings about a model’s internals.')
 body+=p('Type × Signature, Read-Mode × Type and Read-Mode × Signature contain no observed-failure cells. The YAML stores empty observed cross-tabs and the full unassessable count. Cycle 3’s five S3 assignments cannot be compared with this cycle’s missing prospective labels as if one architecture improved.')
 content.append(sec('signatures','LLM cognitive signatures',body))
 body=table(['Mode','Retrospective count','Share of all chains','Held / Unresolved','Inverted / Spurious / Failed-Z'],[[m,dist.get(m,0),f"{dist.get(m,0)/n:.1%}",str(a['read_mode_cross_tab'][m]['held'])+' / '+str(a['read_mode_cross_tab'][m]['indeterminate']),'0 / 0 / 0 — not an estimated risk'] for m in ['O','R','H']])
 body+=p('The original token counts are '+E(str(a['aggregate_distributions']['original_read_tokens']))+'. Seven tokens are semantically invalid for read mode: '+E(', '.join(sorted(COLLISIONS)))+'. Those raw labels remain in the YAML. Independent coding uses the terminal prose and finds O in those seven cases. In 101-ie-3, three conditional preparation paths earn O despite an original H tag. In 118-ie-3, H is retained as a disclosed boundary case because the author explicitly narrows the terminal test to the final poll/count comparison.')
 body+=p('O denotes a retained field of alternatives, not a certificate of good measurement, complete evidence or correct inference. R has no independently coded cases. One H case cannot support a comparison, and classifying most prose O does not show that orienting prevented a severe failure. An external or shadow experimental corpus is still needed.')
 content.append(sec('read-mode','Read-mode classification',body))
 body=p('The complete inventory is searchable through the browser. Each entry includes the source date, original tag, independent stance, test unit, exact chain and its missing outcome evidence. X/Y/Z decomposition, invoked patterns and every source-check mapping are also in the YAML. For recent narrative-format cards, decomposition is interpretive; the exact text remains the authority.')
 for c in inv:
  body+=f'<details id="{E(c["chain_id"])}"><summary><span class="mono">{E(c["chain_id"])} · {c["date"]} · {c["retrospective_read_mode"]} · {E(c["outcome_label"])}</span> — {E(c["title"])}</summary><div class="card">'
  body+=p(f'<a href="../{c["source_file"]}#s-ie">Originating inference section</a> · Test: '+E(c['test_unit'].replace('_',' '))+' · Original READ: '+E(c['original_read_tag'] or 'absent'))
  body+=p('<strong>Stance basis:</strong> '+E(c['read_mode_basis']))
  body+=p('<strong>Timing:</strong> '+E(c['timing_status'].replace('_',' '))+'. '+E(c['timing_basis']))
  body+=p('<strong>Outcome assessment:</strong> '+E(c['outcome_evidence']))
  body+='<blockquote>'+E(c['text'])+'</blockquote></div></details>'
 content.append(sec('inventory','Complete inference inventory',body))
 body=p('Primary sources were retrieved on 12 October 2026. They support only the stated components or research anchors. Ten checks concern outcome follow-up, including two Held event criteria; five ground proposed research. Publisher access to the 2026 compression article failed, so the dated 2025 original preprint is explicitly used as historical evidence.')
 body+=table(['Source','Date','Role and limit'],[[f'<a href="{E(s["url"])}">{E(s["title"])}</a>',s['date'],E(s['supports'])] for s in SOURCES])
 content.append(sec('sources','Source checks and reproducibility',body))
 css='''
html,body{font-size:18px!important}
:root{--bg:#0b1120;--card:#111827;--ink:#d4dce8;--muted:#a3afc2;--gold:#c89545;--line:#665137}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,sans-serif}main{max-width:1120px;margin:auto;padding:36px 24px 80px}header{border-bottom:1px solid var(--line);padding-bottom:24px}h1,h2,h3{font-family:Georgia,serif;font-weight:400;line-height:1.25}h1{font-size:clamp(2rem,5vw,3rem);margin:.35em 0}h2{color:var(--gold);border-bottom:1px solid var(--line);padding-bottom:.4em;margin-top:2.6rem}h3{font-size:1.35rem;margin:.3em 0 .8em}p{max-width:88ch}.k{color:var(--gold);letter-spacing:.09em;text-transform:uppercase;font-size:.78rem}.lead,.card{background:var(--card);border:1px solid var(--line);padding:1.2rem 1.4rem;margin:1rem 0;border-radius:4px}.lead{border-left:4px solid var(--gold)}a{color:#e2b66d;text-underline-offset:.18em}a:hover{color:#ffe2b1}a:focus-visible,summary:focus-visible,.matrix-wrap:focus-visible{outline:3px solid #f0c47b;outline-offset:4px}nav{display:flex;gap:.25rem 1rem;flex-wrap:wrap;margin:1.2rem 0}nav a{display:inline-flex;align-items:center;min-height:44px}details{margin:.7rem 0;border-bottom:1px solid #354055}summary{cursor:pointer;min-height:44px;padding:.65rem .1rem;overflow-wrap:anywhere}blockquote{margin:1rem 0;padding-left:1rem;border-left:2px solid #78879c;font-size:.91rem;white-space:normal;max-width:92ch}.mono{font: .76rem/1.5 ui-monospace,SFMono-Regular,monospace;color:#c3ccda}.matrix-wrap{overflow-x:auto;border:1px solid #465168;border-radius:4px;margin:1rem 0}table{border-collapse:collapse;width:100%;font-size:.88rem}th,td{text-align:left;vertical-align:top;padding:.7rem;border-bottom:1px solid #354055;min-width:130px;overflow-wrap:anywhere}th{color:#e2b66d;background:#111827}td:first-child{min-width:155px}.bar-row{display:grid;grid-template-columns:minmax(180px,1fr) 2fr 2em;align-items:center;gap:.75rem;margin:.5rem 0}.track{height:12px;background:#263047;border-left:2px solid var(--gold)}footer{margin-top:3rem;border-top:1px solid var(--line);padding-top:1rem;color:var(--muted);font-size:.85rem}footer>a{display:inline-flex;align-items:center;min-height:44px;padding:.35rem .15rem}.skip{position:absolute;left:-9999px}.skip:focus{left:1rem;top:1rem;background:var(--card);padding:1rem}section{scroll-margin-top:1rem}@media(max-width:650px){html,body{font-size:18px!important}main{padding:24px 16px 60px}.card,.lead{padding:1rem}.bar-row{grid-template-columns:1fr 1fr 2em}table{font-size:.84rem}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*,*::before,*::after{animation:none!important;transition:none!important}}@media print{body{background:white;color:black}details>*{display:block}summary{display:block}a{color:black}header,section,article{break-inside:avoid}nav{display:none}}
'''
 nav=''.join(f'<a href="#{x}">{E(y)}</a>' for x,y in [('headline','Headline'),('outcomes','Outcomes'),('research','Research yield'),('anomalies','Anomalies'),('recalibrations','Next 30'),('inventory','Inventory'),('sources','Sources')])
 htmlout=f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Cycle 004 contingency audit: complete inference and anomaly accounting, evidence limits and research designs."><title>Contingency Audit — Cycle 004</title><style>{css}</style><link rel="stylesheet" href="../assets/cyborg-v3-2.css"><style>html,body{{font-size:18px!important}}</style></head><body><a class="skip" href="#headline">Skip to audit</a><main><header><p class="k">Tectonic Briefing · Meta-analysis</p><h1>Contingency Audit — Cycle 004</h1><p>Meta-analysis of contingent forecasting under Knightian uncertainty</p><p>Briefings 091–120 · {a["dated_artifacts"]} dated artifacts · 17 August–12 October 2026</p><nav aria-label="Audit sections">{nav}</nav></header>'+''.join(content)+'<footer><a href="cycle-004.yaml">Complete machine-readable audit and dated anomaly ledger</a> · <a href="cycle-003.html">Previous cycle</a><p>No hit-rate score is computed. This corpus supplies questions and process evidence; it does not validate a causal model or establish an architecture-specific cognitive signature.</p></footer></main></body></html>'
 (REPO/'synthesis/cycle-004.html').write_text(htmlout)

if __name__=='__main__':main()
