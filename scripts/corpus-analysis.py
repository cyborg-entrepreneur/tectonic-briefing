#!/usr/bin/env python3
"""Deterministically extract portfolio and cycle evidence from Tectonic briefings."""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


REPO = Path(__file__).resolve().parent.parent
BRIEFINGS = REPO / "briefings"
LENSES = ("ge", "te", "ec", "sc", "so", "en", "ig", "li")
HEADER_RE = re.compile(r"BRIEFING\s+NO\.?\s*(\d+)", re.I)
READ_RE = re.compile(r"READ:\s*([ORH])\b", re.I)
LEGACY_STATUS_RE = re.compile(
    r"\[O\].{0,100}observed.{0,220}\[R\].{0,100}"
    r"(?:reasoned|inferred).{0,220}\[H\].{0,100}hypothetical",
    re.I | re.S,
)

THEMES = {
    "geopolitics_conflict": (
        "war", "strike", "missile", "military", "ceasefire", "naval", "army",
        "defense", "defence", "nuclear", "border", "sanction", "diplomat",
        "election", "president", "minister", "alliance", "nato", "iran",
        "russia", "ukraine", "israel", "gaza", "hormuz",
    ),
    "ai_models_agents": (
        "artificial intelligence", " ai ", "llm", "model", "agent", "openai",
        "anthropic", "gemini", "deepmind", "algorithm", "inference",
    ),
    "robotics_embodied": (
        "robot", "humanoid", "unitree", "optimus", "figure ai", "automation",
        "autonomous vehicle", "drone",
    ),
    "institutions_governance": (
        "regulat", "govern", "court", "congress", "policy", "rule", "law",
        "institution", "nist", "fda", "sec ", "fomc", "oversight", "standard",
    ),
    "markets_macro": (
        "market", "stock", "bond", "inflation", "cpi", "gdp", "fed", "rate",
        "employment", "earnings", "recession", "currency", "trade", "tariff",
    ),
    "energy_resources": (
        "oil", "gas", "energy", "copper", "lithium", "mineral", "uranium",
        "rare earth", "grid", "power", "fusion", "solar", "battery",
    ),
    "climate_ecology": (
        "climate", "fire", "wildfire", "ocean", "ice", "carbon", "warming",
        "weather", "el niño", "el nino", "ecolog", "sargassum", "amoc",
    ),
    "science_biomedicine": (
        "genome", "gene", "protein", "peptide", "disease", "health", "medical",
        "biology", "sensor", "material", "polymer", "researcher", "study",
    ),
    "space_quantum": (
        "space", "lunar", "moon", "mars", "satellite", "launch", "orbit",
        "quantum", "qubit", "cryptograph",
    ),
    "labor_demography_education": (
        "labor", "labour", "worker", "workforce", "job", "youth", "young",
        "birth", "fertility", "demograph", "university", "college", "student",
        "family", "pension",
    ),
    "infrastructure_cyber": (
        "cyber", "security", "telemetry", "infrastructure", "mainframe",
        "semiconductor", "chip", "data center", "water", "shipping", "port",
    ),
}

REGIONS = {
    "north_america": (
        "united states", " u.s.", " us ", "america", "canada", "mexico",
        "washington", "congress", "federal reserve", "fed ", "new york",
    ),
    "latin_america_caribbean": (
        "brazil", "argentina", "colombia", "chile", "peru", "venezuela",
        "caribbean", "panama", "latin america",
    ),
    "europe": (
        "europe", " eu ", "european", "uk ", "britain", "france", "germany",
        "italy", "spain", "ukraine", "russia", "nato", "brussels",
    ),
    "middle_east_north_africa": (
        "iran", "israel", "gaza", "lebanon", "saudi", "oman", "yemen",
        "iraq", "jordan", "syria", "hormuz", "gulf", "egypt",
    ),
    "sub_saharan_africa": (
        "africa", "mali", "niger", "burkina", "sudan", "zambia", "nigeria",
        "ethiopia", "kenya", "congo", "sahel", "ecowas", "sadc",
    ),
    "east_asia": (
        "china", "chinese", "japan", "korea", "taiwan", "beijing", "tokyo",
        "hong kong",
    ),
    "south_southeast_asia": (
        "india", "pakistan", "bangladesh", "asean", "indonesia", "vietnam",
        "philippines", "thailand", "myanmar", "singapore", "malaysia",
    ),
    "oceania_pacific": (
        "australia", "new zealand", "pacific", "fiji", "polynesia",
    ),
    "global_transnational": (
        "global", "world", "international", "planet", "basin-scale",
    ),
}

SOURCE_TYPES = {
    "wire_news": (
        "apnews.com", "reuters.com", "afp.com", "bbc.com", "bbc.co.uk",
        "cnn.com", "npr.org", "nytimes.com", "washingtonpost.com",
        "theguardian.com", "ft.com", "bloomberg.com", "cnbc.com",
        "aljazeera.com", "lemonde.fr",
    ),
    "scholarly": (
        "doi.org", "nature.com", "science.org", "sciencedirect.com",
        "springer.com", "wiley.com", "pnas.org", "arxiv.org", "usenix.org",
        "thelancet.com", "nejm.org", "cell.com",
    ),
    "official_primary": (
        ".gov", ".int", "un.org", "europa.eu", "nato.int", "who.int",
        "worldbank.org", "imf.org", "oecd.org", "federalreserve.gov",
        "bls.gov", "nist.gov", "nasa.gov",
    ),
}


def clean_text(node):
    if node is None:
        return ""
    return " ".join(node.get_text(" ", strip=True).split())


def section_map(soup):
    return {
        node.get("id")[2:]: node
        for node in soup.find_all(id=re.compile(r"^s-[a-z]+$"))
    }


def classify_terms(text, taxonomy):
    haystack = f" {text.casefold()} "
    matches = []
    for label, terms in taxonomy.items():
        if any(term in haystack for term in terms):
            matches.append(label)
    return matches or ["unknown"]


def source_type(domain):
    domain = domain.casefold()
    for label, suffixes in SOURCE_TYPES.items():
        if any(suffix in domain for suffix in suffixes):
            return label
    return "company_media_other"


def word_count(node):
    return len(re.findall(r"\b[\w’'-]+\b", clean_text(node)))


def multi_hyphen_count(text):
    return len(re.findall(r"\b\w+(?:-\w+){2,}\b", text))


def nearest_card_text(heading):
    parent = heading.parent
    while parent is not None:
        classes = set(parent.get("class") or [])
        if classes.intersection({"c", "card", "anomaly", "inf"}):
            return clean_text(parent)
        parent = parent.parent
    parts = [clean_text(heading)]
    sibling = heading.find_next_sibling()
    while sibling is not None and sibling.name not in {"h2", "h3"}:
        parts.append(clean_text(sibling))
        sibling = sibling.find_next_sibling()
    return " ".join(part for part in parts if part)


def extract_record(path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    soup = BeautifulSoup(raw, "html.parser")
    sections = section_map(soup)
    bn = soup.select_one(".bn")
    match = HEADER_RE.search(clean_text(bn) or raw)
    number = int(match.group(1)) if match else None
    cycle = (number - 1) // 30 + 1 if number else None
    title_node = soup.find("h1")
    title = clean_text(title_node)
    lens_items = {}
    item_records = []
    for lens in LENSES:
        node = sections.get(lens)
        titles = [clean_text(h) for h in node.find_all("h3")] if node else []
        lens_items[lens] = titles
        for heading in node.find_all("h3") if node else []:
            item_text = nearest_card_text(heading)
            item_records.append({
                "lens": lens,
                "title": clean_text(heading),
                "themes": classify_terms(item_text, THEMES),
                "regions": classify_terms(item_text, REGIONS),
            })

    external_links = []
    for link in soup.find_all("a", href=True):
        parsed = urlsplit(link["href"])
        if parsed.scheme in {"http", "https"} and parsed.netloc:
            domain = parsed.netloc.casefold().removeprefix("www.")
            is_repository_self_link = (
                domain == "github.com"
                and parsed.path.startswith("/cyborg-entrepreneur/tectonic-briefing")
            )
            if not is_repository_self_link and domain != "cyborg-entrepreneur.github.io":
                external_links.append(link["href"])
    unique_links = sorted(set(external_links))
    domains = sorted({urlsplit(link).netloc.casefold().removeprefix("www.")
                      for link in unique_links})

    concepts = []
    for badge in soup.select("a.vbadge"):
        if badge.find_parent(class_="vi") or badge.find_parent(id="s-sa"):
            continue
        href = badge.get("href", "")
        slug = Path(urlsplit(href).path).stem
        if slug and slug != "index":
            concepts.append(slug)

    anomaly_records = []
    anomaly_node = sections.get("an")
    if anomaly_node:
        for heading in anomaly_node.find_all("h3"):
            # Some historical briefings append the full structural-vocabulary
            # display inside #s-an.  Count only headings that live in an
            # anomaly card, not later META headings or vocabulary entries.
            anomaly_card = heading.find_parent(
                lambda tag: tag.name in {"div", "article"}
                and set(tag.get("class", [])).intersection(
                    {"c", "card", "anomaly"}
                )
            )
            if anomaly_card is None or heading.find_parent(class_="vi"):
                continue
            anomaly_records.append({
                "title": clean_text(heading),
                "text": nearest_card_text(heading),
            })
    else:
        legacy_heading = soup.find(
            lambda tag: tag.name in {"h2", "h3"}
            and clean_text(tag).casefold().startswith("anomaly detection")
        )
        legacy_card = legacy_heading.find_next_sibling("div") if legacy_heading else None
        if legacy_card:
            for paragraph in legacy_card.find_all("p", recursive=False):
                strong = paragraph.find("strong")
                title = clean_text(strong).rstrip(".") if strong else clean_text(paragraph)[:120]
                anomaly_records.append({
                    "title": title,
                    "text": clean_text(paragraph),
                })

    chain_records = []
    inference_node = sections.get("ie")
    legacy_collision = bool(
        inference_node and LEGACY_STATUS_RE.search(str(inference_node))
    )
    if inference_node:
        # The archive has used three equivalent wrappers for inference cards:
        # .chain-block (early cycles), .inf, and .chain.  Treating only the two
        # recent forms silently under-counted Cycle 2.
        for index, card in enumerate(
            inference_node.select(".chain-block, .inf, .chain"), start=1
        ):
            text = clean_text(card)
            label_node = card.find(["h3", "h4"]) or card.select_one(".lb")
            label = clean_text(label_node)
            explicit = READ_RE.search(f"{label} {text}")
            chain_id = (
                f"{number:03d}-{path.stem.replace('-', '')}-ie-{index}"
                if number is not None else f"{path.stem}-ie-{index}"
            )
            chain_records.append({
                "chain_id": chain_id,
                "label": label,
                "text": text,
                "explicit_read_mode": explicit.group(1).upper() if explicit else None,
                "legacy_status_tags_present": bool(
                    re.search(r"<strong>\[[ORH]\]</strong>", str(card), re.I)
                ),
            })

    section_words = {key: word_count(value) for key, value in sections.items()}
    content_soup = BeautifulSoup(str(soup), "html.parser")
    for selector in (
        ".vi", ".src", "#s-sa", "nav", "style", "script", "svg",
        ".vocab-display", ".vg",
    ):
        for node in content_soup.select(selector):
            node.decompose()
    analytic_words = word_count(content_soup)
    all_text = clean_text(soup)
    date_value = path.stem
    return {
        "date": date_value,
        "path": str(path.relative_to(REPO)),
        "number": number,
        "cycle": cycle,
        "title": title,
        "lens_items": lens_items,
        "items": item_records,
        "lens_item_count": sum(len(value) for value in lens_items.values()),
        "section_words": section_words,
        "analytic_word_count": analytic_words,
        "total_word_count": word_count(soup),
        "deep_dive_count": len(soup.select(".dd-panel")),
        "anomalies": anomaly_records,
        "anomaly_count": len(anomaly_records),
        "chains": chain_records,
        "chain_count": len(chain_records),
        "explicit_read_mode_count": sum(
            1 for chain in chain_records if chain["explicit_read_mode"]
        ),
        "legacy_orh_namespace_collision": legacy_collision,
        "external_links": unique_links,
        "external_link_count": len(unique_links),
        "source_domains": domains,
        "source_domain_count": len(domains),
        "source_types": dict(Counter(source_type(domain) for domain in domains)),
        "concept_citations": dict(Counter(concepts)),
        "concept_citation_count": len(concepts),
        "multi_hyphen_compounds": multi_hyphen_count(all_text),
    }


def aggregate(records):
    numbers = [record["number"] for record in records if record["number"] is not None]
    number_dates = defaultdict(list)
    for record in records:
        number_dates[record["number"]].append(record["date"])
    duplicates = {
        f"{number:03d}": dates for number, dates in sorted(number_dates.items())
        if number is not None and len(dates) > 1
    }
    missing = sorted(set(range(min(numbers), max(numbers) + 1)) - set(numbers))
    source_domains = Counter()
    source_types = Counter()
    concepts = Counter()
    concept_documents = Counter()
    concept_pairs = Counter()
    themes = Counter()
    regions = Counter()
    lenses = Counter()
    for record in records:
        source_domains.update(record["source_domains"])
        source_types.update(record["source_types"])
        concepts.update(record["concept_citations"])
        concept_documents.update(record["concept_citations"].keys())
        unique_concepts = sorted(record["concept_citations"])
        concept_pairs.update(" × ".join(pair) for pair in combinations(unique_concepts, 2))
        for item in record["items"]:
            themes.update(item["themes"])
            regions.update(item["regions"])
            lenses[item["lens"]] += 1
    total_domain_mentions = sum(source_domains.values())
    hhi = (
        sum((count / total_domain_mentions) ** 2 for count in source_domains.values())
        if total_domain_mentions else 0
    )
    by_cycle = {}
    for cycle in sorted({record["cycle"] for record in records if record["cycle"]}):
        subset = [record for record in records if record["cycle"] == cycle]
        by_cycle[str(cycle)] = aggregate_subset(subset)
    return {
        "dated_artifacts": len(records),
        "nominal_number_range": [min(numbers), max(numbers)] if numbers else [],
        "date_range": [records[0]["date"], records[-1]["date"]] if records else [],
        "duplicate_numbers": duplicates,
        "missing_numbers": missing,
        "lens_items": dict(lenses),
        "themes": dict(themes.most_common()),
        "regions": dict(regions.most_common()),
        "source_domain_mentions": total_domain_mentions,
        "unique_source_domains": len(source_domains),
        "top_source_domains": source_domains.most_common(25),
        "source_type_domain_mentions": dict(source_types),
        "source_domain_hhi": round(hhi, 6),
        "concept_citations": dict(concepts.most_common()),
        "concept_document_presence": dict(concept_documents.most_common()),
        "concept_cooccurrences": concept_pairs.most_common(30),
        "by_cycle": by_cycle,
    }


def aggregate_subset(records):
    lens_counts = Counter()
    themes = Counter()
    regions = Counter()
    domains = Counter()
    concepts = Counter()
    concept_documents = Counter()
    source_types = Counter()
    for record in records:
        for lens, titles in record["lens_items"].items():
            lens_counts[lens] += len(titles)
        for item in record["items"]:
            themes.update(item["themes"])
            regions.update(item["regions"])
        domains.update(record["source_domains"])
        concepts.update(record["concept_citations"])
        concept_documents.update(record["concept_citations"].keys())
        source_types.update(record["source_types"])
    count = len(records)
    return {
        "dated_artifacts": count,
        "dates": [records[0]["date"], records[-1]["date"]] if records else [],
        "lens_items": dict(lens_counts),
        "themes": dict(themes.most_common()),
        "regions": dict(regions.most_common()),
        "mean_analytic_words": round(
            sum(record["analytic_word_count"] for record in records) / count, 1
        ) if count else 0,
        "mean_lens_items": round(
            sum(record["lens_item_count"] for record in records) / count, 2
        ) if count else 0,
        "mean_external_links": round(
            sum(record["external_link_count"] for record in records) / count, 2
        ) if count else 0,
        "mean_source_domains": round(
            sum(record["source_domain_count"] for record in records) / count, 2
        ) if count else 0,
        "deep_dives": sum(record["deep_dive_count"] for record in records),
        "anomalies": sum(record["anomaly_count"] for record in records),
        "chains": sum(record["chain_count"] for record in records),
        "explicit_read_mode_tags": sum(
            record["explicit_read_mode_count"] for record in records
        ),
        "legacy_orh_collision_files": [
            record["date"] for record in records
            if record["legacy_orh_namespace_collision"]
        ],
        "top_source_domains": domains.most_common(15),
        "source_type_domain_mentions": dict(source_types),
        "top_concepts": concepts.most_common(15),
        "top_concept_document_presence": concept_documents.most_common(15),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--min-number", type=int, default=1)
    parser.add_argument("--max-number", type=int, default=90)
    args = parser.parse_args()
    records = []
    for path in sorted(BRIEFINGS.glob("????-??-??.html")):
        record = extract_record(path)
        if (
            record["number"] is not None
            and args.min_number <= record["number"] <= args.max_number
        ):
            records.append(record)
    payload = {
        "schema_version": 1,
        "generated_at": f"{records[-1]['date']}T00:00:00" if records else None,
        "scope": {
            "min_number": args.min_number,
            "max_number": args.max_number,
            "unit": "dated_html_artifact",
        },
        "summary": aggregate(records),
        "records": records,
    }
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(target),
        "dated_artifacts": len(records),
        "chains": sum(record["chain_count"] for record in records),
        "anomalies": sum(record["anomaly_count"] for record in records),
        "sha256_ready": True,
    }, indent=2))


if __name__ == "__main__":
    main()
