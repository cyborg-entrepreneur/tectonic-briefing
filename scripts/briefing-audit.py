#!/usr/bin/env python3
"""Build continuity evidence and audit a Tectonic candidate against prior issues."""

from __future__ import annotations

import argparse
import json
import re
import sys
import os
import tempfile
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


NUMBER_RE = re.compile(
    r"(?<![\w-])(?:\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)"
    r"(?:\s?(?:%|percent|million|billion|trillion|people|workers|users|jobs|days|years))?",
    re.I,
)


def _normalize(value):
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


IGNORED_LEADS = {
    "geopolitical and security",
    "economics and markets",
    "technology and science",
    "society institutions and infrastructure",
    "climate and civil protection",
    "what today s landscape means for the work",
}


def _substantive_lead(value):
    normalized = _normalize(value)
    return bool(normalized and normalized not in IGNORED_LEADS
                and not re.fullmatch(r"meta \d+ .+ \d+", normalized))


def _material_number(value):
    if re.search(r"[,%.]", value) or re.search(
        r"\b(?:million|billion|trillion|people|workers|users|jobs|days|years)\b",
        value, re.I,
    ):
        return True
    try:
        return float(re.sub(r"[^0-9.]", "", value)) >= 10
    except ValueError:
        return False


class BriefingExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._ignored = 0
        self._heading = None
        self._heading_parts = []
        self.headings = []
        self.text_parts = []
        self.sources = []

    def handle_starttag(self, tag, attrs):
        tag = tag.casefold()
        if tag in {"script", "style", "svg"}:
            self._ignored += 1
            return
        if self._ignored:
            return
        if tag == "h3":
            self._heading = tag
            self._heading_parts = []
        if tag == "a":
            href = dict(attrs).get("href", "")
            parsed = urlparse(href)
            if parsed.scheme in {"http", "https"} and parsed.netloc:
                self.sources.append(href)

    def handle_endtag(self, tag):
        tag = tag.casefold()
        if tag in {"script", "style", "svg"} and self._ignored:
            self._ignored -= 1
            return
        if not self._ignored and tag == self._heading:
            heading = " ".join("".join(self._heading_parts).split())
            if heading:
                self.headings.append(heading)
            self._heading = None
            self._heading_parts = []

    def handle_data(self, data):
        if self._ignored:
            return
        self.text_parts.append(data)
        if self._heading:
            self._heading_parts.append(data)


def extract_briefing(path):
    path = Path(path)
    parser = BriefingExtractor()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    text = " ".join(" ".join(parser.text_parts).split())
    claims = []
    for match in NUMBER_RE.finditer(text):
        value = match.group(0).strip()
        digits = re.sub(r"\D", "", value)
        if len(digits) == 4 and 1900 <= int(digits) <= 2100:
            continue
        if not _material_number(value):
            continue
        start = max(0, match.start() - 100)
        end = min(len(text), match.end() + 100)
        claims.append({
            "value": value,
            "context": text[start:end].strip(),
        })
    return {
        "path": str(path),
        "date": path.stem,
        "lead_titles": [item for item in parser.headings if _substantive_lead(item)],
        "normalized_lead_titles": [
            _normalize(item) for item in parser.headings if _substantive_lead(item)
        ],
        "claim_ledger": claims[:400],
        "sources": sorted(set(parser.sources)),
    }


def build_context_manifest(repo, target_date, limit=4):
    repo = Path(repo)
    target = date.fromisoformat(str(target_date))
    prior = []
    for path in sorted((repo / "briefings").glob("*.html"), reverse=True):
        try:
            issue_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if issue_date < target:
            prior.append(extract_briefing(path))
        if len(prior) >= limit:
            break
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "target_date": target.isoformat(),
        "issues": prior,
        "continuity_contract": {
            "compare_lead_titles": True,
            "compare_numeric_claims": True,
            "require_source_links": True,
        },
    }


def audit_candidate(candidate, context):
    current = extract_briefing(candidate)
    errors = []
    warnings = []
    previous_titles = {}
    for issue in context.get("issues", []):
        for raw, normalized in zip(
            issue.get("lead_titles", []), issue.get("normalized_lead_titles", [])
        ):
            previous_titles.setdefault(normalized, []).append((issue.get("date"), raw))
    for raw, normalized in zip(
        current["lead_titles"], current["normalized_lead_titles"]
    ):
        if normalized and normalized in previous_titles:
            dates = ", ".join(item[0] for item in previous_titles[normalized])
            errors.append(f"Repeated lead title from prior issue(s) {dates}: {raw}")
    if not current["sources"]:
        errors.append("Candidate contains no external source links")
    prior_claims = [
        claim for issue in context.get("issues", []) for claim in issue.get("claim_ledger", [])
    ]
    prior_values = {claim.get("value", "").casefold() for claim in prior_claims}
    repeated_values = sorted({
        claim["value"] for claim in current["claim_ledger"]
        if claim["value"].casefold() in prior_values
    })
    if repeated_values:
        warnings.append(
            "Numeric values also appeared in recent issues; verify date and denominator: "
            + ", ".join(repeated_values[:20])
        )
    return {
        "schema_version": 1,
        "ok": not errors,
        "candidate": str(candidate),
        "errors": errors,
        "warnings": warnings,
        "lead_titles": current["lead_titles"],
        "claim_ledger": current["claim_ledger"],
        "sources": current["sources"],
        "prior_issue_dates": [issue.get("date") for issue in context.get("issues", [])],
    }


def _write_or_print(value, output):
    rendered = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    if output:
        target = Path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary = tempfile.mkstemp(
            prefix=f".{target.name}.", suffix=".tmp", dir=target.parent
        )
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(rendered)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    else:
        print(rendered, end="")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    context_parser = sub.add_parser("context")
    context_parser.add_argument("--repo", default=".")
    context_parser.add_argument("--target-date", required=True)
    context_parser.add_argument("--limit", type=int, default=4)
    context_parser.add_argument("--output")
    candidate_parser = sub.add_parser("candidate")
    candidate_parser.add_argument("--candidate", required=True)
    candidate_parser.add_argument("--context", required=True)
    candidate_parser.add_argument("--output")
    args = parser.parse_args()
    if args.command == "context":
        value = build_context_manifest(args.repo, args.target_date, max(1, min(args.limit, 12)))
        _write_or_print(value, args.output)
        return
    context = json.loads(Path(args.context).read_text(encoding="utf-8"))
    value = audit_candidate(args.candidate, context)
    _write_or_print(value, args.output)
    raise SystemExit(0 if value["ok"] else 1)


if __name__ == "__main__":
    main()
