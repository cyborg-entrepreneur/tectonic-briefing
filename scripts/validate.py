#!/usr/bin/env python3
"""Read-only structural validation for the Tectonic Briefing site."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit


REPO = Path(__file__).resolve().parent.parent
BRIEFINGS = REPO / "briefings"
REGISTRY = REPO / "concepts" / "registry.json"
SEARCH_INDEX = REPO / "search-index.json"
STRUCTURAL = REPO / "STRUCTURAL_CONCEPTS.md"
REQUIRED_SECTIONS = ("ov", "ge", "te", "ec", "sc", "so", "en", "ig",
                     "li", "ie", "wa", "an", "sa")
LENSES = ("ge", "te", "ec", "sc", "so", "en", "ig", "li")
HEADER_RE = re.compile(
    r'class=["\'][^"\']*\bbn\b[^"\']*["\'][^>]*>'
    r'(?:\s*<[^>]+>)*\s*BRIEFING\s+NO\.?\s*(\d+)',
    re.I,
)


def next_issue_number():
    """Return the number after the archive's highest canonical header."""
    numbers = []
    for path in BRIEFINGS.glob("*.html"):
        match = HEADER_RE.search(path.read_text(encoding="utf-8", errors="replace"))
        if match:
            numbers.append(int(match.group(1)))
    return max(numbers, default=0) + 1


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, message):
        self.errors.append(message)

    def warn(self, message):
        self.warnings.append(message)


def plain_text(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def load_briefings(report):
    records = []
    for path in sorted(BRIEFINGS.glob("????-??-??.html")):
        text = path.read_text(encoding="utf-8", errors="replace")
        match = HEADER_RE.search(text)
        if not match:
            report.error(f"{path.name}: missing canonical .bn briefing number")
            continue
        records.append({"path": path, "date": path.stem,
                        "number": int(match.group(1)), "html": text})
    if not records:
        report.error("no canonical briefing files found")
    return records


def section_slices(text):
    matches = list(re.finditer(r'id=["\']s-([a-z]+)["\']', text))
    return {
        match.group(1): text[match.end():matches[index + 1].start()
                                  if index + 1 < len(matches) else len(text)]
        for index, match in enumerate(matches)
    }


def validate_local_links(path, text, report):
    for href in re.findall(r'href=["\']([^"\']+)["\']', text, re.I):
        parsed = urlsplit(html.unescape(href))
        if (parsed.scheme or parsed.netloc or not parsed.path
                or parsed.path.startswith(("#", "mailto:", "javascript:"))):
            continue
        target = (path.parent / unquote(parsed.path)).resolve()
        if not target.exists():
            report.error(f"{path.name}: broken local link {href}")


def validate_latest(record, patterns, report):
    path, text = record["path"], record["html"]
    lower = text.casefold()
    for token in ("<!doctype html", "<html", "<head", "</head>", "<body", "</body>", "</html>"):
        if token not in lower:
            report.error(f"{path.name}: missing {token}")
    if not re.search(r"<title>.+?</title>", text, re.I | re.S):
        report.error(f"{path.name}: missing non-empty title")

    sections = section_slices(text)
    missing = [section for section in REQUIRED_SECTIONS if section not in sections]
    if missing:
        report.error(f"{path.name}: missing section ids {', '.join(missing)}")
    for lens in LENSES:
        count = len(re.findall(r"<h3\b", sections.get(lens, ""), re.I))
        if count < 3:
            report.error(f"{path.name}: lens {lens} has {count} topics; minimum is 3")

    deep_dives = len(re.findall(r'class=["\'][^"\']*\bdd-panel\b', text, re.I))
    if not 2 <= deep_dives <= 4:
        report.error(f"{path.name}: {deep_dives} deep dives; expected 2-4")
    anomalies = len(re.findall(r"<h3\b", sections.get("an", ""), re.I))
    if anomalies < 4:
        report.error(f"{path.name}: anomaly section has {anomalies} items; minimum is 4")
    source_section = sections.get("sa", "")
    if len(re.findall(r"<h3\b", source_section, re.I)) < 3:
        report.error(f"{path.name}: source archive has fewer than 3 subsections")
    if not re.search(r'class=["\'][^"\']*\bsrc\b', source_section, re.I):
        report.error(f"{path.name}: source archive contains no source entries")

    vocab_entries = re.findall(
        r'<div\s+class=["\'][^"\']*\bvi\b[^"\']*["\'][^>]*>.*?</div>',
        text, re.I | re.S,
    )
    if len(vocab_entries) < len(patterns):
        report.error(
            f"{path.name}: {len(vocab_entries)} vocabulary cards for {len(patterns)} patterns"
        )
    vocab_text = plain_text(" ".join(vocab_entries)).casefold()
    absent_patterns = [p["name"] for p in patterns if p["name"].casefold() not in vocab_text]
    if absent_patterns:
        report.error(f"{path.name}: vocabulary cards omit {', '.join(absent_patterns[:5])}")

    identifiers = re.findall(r'\bid=["\']([^"\']+)["\']', text, re.I)
    duplicate_ids = [key for key, count in Counter(identifiers).items() if count > 1]
    if duplicate_ids:
        report.error(f"{path.name}: duplicate HTML ids {', '.join(duplicate_ids[:8])}")
    for marker in ("TB-NAV-WRAP:TOP:START", "TB-NAV-WRAP:BOT:START"):
        if text.count(marker) != 1:
            report.error(f"{path.name}: expected one {marker} marker")
    if "editorial discipline" not in lower or "fresh-domain" not in lower:
        report.error(f"{path.name}: missing fresh-domain editorial-discipline attestation")
    for label, pattern in {
        "review id": r"\bREV-\d{4}-\d+\b",
        "private user path": r"/Users/[^/\s<]+/",
        "private workflow item": r"workflow/(?:reviews|editorial/manuscripts)/",
    }.items():
        if re.search(pattern, text, re.I):
            report.error(f"{path.name}: possible confidential {label} exposed")
    validate_local_links(path, text, report)


def validate_generated(records, report):
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(f"concept registry unreadable: {exc}")
        return []
    patterns = registry.get("patterns")
    if not isinstance(patterns, list):
        report.error("concept registry patterns is not a list")
        return []
    names = [str(p.get("name", "")) for p in patterns]
    slugs = [str(p.get("slug", "")) for p in patterns]
    if not all(names) or len(names) != len(set(names)):
        report.error("concept registry has blank or duplicate pattern names")
    if not all(slugs) or len(slugs) != len(set(slugs)):
        report.error("concept registry has blank or duplicate slugs")

    canonical_count = len(re.findall(
        r'^- \*\*[^*]+\*\*\s*\*\(Briefing\s+\d+\)\*',
        STRUCTURAL.read_text(encoding="utf-8"), re.M,
    ))
    if len(patterns) != canonical_count:
        report.error(
            f"registry has {len(patterns)} patterns; STRUCTURAL_CONCEPTS has {canonical_count}"
        )
    expected_pages = {f"{slug}.html" for slug in slugs} | {"index.html"}
    actual_pages = {path.name for path in (REPO / "concepts").glob("*.html")}
    if expected_pages != actual_pages:
        missing = sorted(expected_pages - actual_pages)
        extra = sorted(actual_pages - expected_pages)
        if missing:
            report.error(f"missing concept pages: {', '.join(missing[:6])}")
        if extra:
            report.error(f"orphan concept pages: {', '.join(extra[:6])}")

    latest_date = max((record["date"] for record in records), default="1970-01-01")
    expected_timestamp = f"{latest_date}T00:00:00"
    if registry.get("generated_at") != expected_timestamp:
        report.error("concept registry build timestamp is stale or nondeterministic")
    try:
        search = json.loads(SEARCH_INDEX.read_text(encoding="utf-8"))
        if search.get("generated_at") != expected_timestamp:
            report.error("search index build timestamp is stale or nondeterministic")
        if len(search.get("briefings") or []) != len(records):
            report.error("search index briefing count does not match archive")
        if len(search.get("concepts") or []) != len(patterns):
            report.error("search index concept count does not match registry")
    except (OSError, json.JSONDecodeError) as exc:
        report.error(f"search index unreadable: {exc}")
    return patterns


def validate_history(records, report):
    by_number = defaultdict(list)
    for record in records:
        by_number[record["number"]].append(record["date"])
    duplicates = {number: dates for number, dates in by_number.items() if len(dates) > 1}
    if duplicates:
        detail = ", ".join(f"{number:03d} ({'/'.join(dates)})"
                           for number, dates in sorted(duplicates.items()))
        report.warn(f"historical duplicate issue numbers retained: {detail}")
    if by_number:
        missing = sorted(set(range(min(by_number), max(by_number) + 1)) - set(by_number))
        if missing:
            report.warn("historical missing issue numbers retained: "
                        + ", ".join(f"{number:03d}" for number in missing))
        latest = max(records, key=lambda record: record["date"])
        if latest["number"] != max(by_number):
            report.error(
                f"latest briefing is {latest['number']:03d}; archive maximum is {max(by_number):03d}"
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="validate local links in every briefing")
    parser.add_argument("--json", action="store_true", help="emit machine-readable results")
    parser.add_argument(
        "--next-number", action="store_true",
        help="print the next issue number from canonical briefing headers",
    )
    args = parser.parse_args()
    if args.next_number:
        print(f"{next_issue_number():03d}")
        return 0
    report = Report()
    records = load_briefings(report)
    patterns = validate_generated(records, report)
    validate_history(records, report)
    if records and patterns:
        latest = max(records, key=lambda record: record["date"])
        validate_latest(latest, patterns, report)
        if args.all:
            for record in records:
                if record is not latest:
                    validate_local_links(record["path"], record["html"], report)

    payload = {"ok": not report.errors, "errors": report.errors,
               "warnings": report.warnings, "briefings": len(records),
               "patterns": len(patterns)}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for warning in report.warnings:
            print(f"  ! {warning}")
        for error in report.errors:
            print(f"  ✗ {error}")
        if not report.errors:
            print(f"  ✓ structural validation passed ({len(records)} briefings, "
                  f"{len(patterns)} patterns)")
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
