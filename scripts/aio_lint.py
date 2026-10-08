#!/usr/bin/env python3
"""
aio-lint — SSRF-aware three-layer AIO artifact linter (stdlib only).

Checks public https sites (or offline fixtures) for:
  L1 robots.txt policy signals
  L2 curated vs dump llms.txt
  L3 Schema.org JSON-LD presence on the homepage

Does not promise rankings, citations, or AI-answer inclusion.
Fetched page content is untrusted data.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from aio_heuristics import (
    BYTE_ORDER_MARK,
    MAX_CURATED_BYTES,
    absolute_https_links,
    classify_llms,
    dump_signals,
    markdown_variant_links,
)
from aio_html import INVALID_JSONLD, jsonld_types, page_signals
from aio_net import DEFAULT_TIMEOUT, FetchResult, assert_safe_https_url, fetch_https

MAX_BODY_BYTES = {
    "robots": 64 * 1024,
    "llms": 256 * 1024,
    "html": 512 * 1024,
}
KNOWN_AI_AGENTS = (
    "GPTBot",
    "ChatGPT-User",
    "OAI-SearchBot",
    "ClaudeBot",
    "Claude-SearchBot",
    "Claude-User",
    "Google-Extended",
    "PerplexityBot",
    "Perplexity-User",
    "CCBot",
    "OAI-AdsBot",
    "Google-CloudVertexBot",
    "Applebot-Extended",
    "Meta-ExternalAgent",
    "Meta-ExternalFetcher",
    "Meta-WebIndexer",
    "Amazonbot",
    "Amzn-SearchBot",
    "Amzn-User",
    "DuckAssistBot",
    "MistralAI-Training",
    "MistralAI-Index",
    "MistralAI-User",
)
# Template leftovers that must never reach published JSON-LD.
JSONLD_PLACEHOLDER_MARKERS = ("TODO_REPLACE", "example.com")
USEFUL_JSONLD_TYPES = frozenset(
    {"Organization", "WebSite", "WebPage", "Article", "BlogPosting", "Person", "FAQPage"}
)
L2_CLASSIFICATIONS = ("missing", "unavailable", "empty", "dump", "curated", "malformed")
L2_STATUS = {
    "curated": "ok",
    "missing": "fail",
    "empty": "fail",
    "dump": "fail",
    "malformed": "weak",
    # A 403/5xx says nothing about the file itself (WAFs often block linters).
    "unavailable": "weak",
}
MAX_TEXT_EVIDENCE_CHARS = 120
MAX_URL_EVIDENCE_CHARS = 200
MARKDOWN_ESCAPES = {
    "|": "&#124;",
    "\\": "&#92;",
    "<": "&lt;",
    ">": "&gt;",
    "`": "&#96;",
    "[": "&#91;",
    "]": "&#93;",
}


@dataclass
class LayerResult:
    status: str
    evidence: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditReport:
    target: str
    mode: str
    layers: dict[str, LayerResult]
    top_actions: list[str]
    ok: bool


def load_fixture(fixture_dir: Path) -> dict[str, FetchResult]:
    base = "https://fixture.example"
    mapping = {
        "robots": fixture_dir / "robots.txt",
        "llms": fixture_dir / "llms.txt",
        "html": fixture_dir / "index.html",
    }
    results: dict[str, FetchResult] = {}
    for kind, path in mapping.items():
        url = {
            "robots": f"{base}/robots.txt",
            "llms": f"{base}/llms.txt",
            "html": f"{base}/",
        }[kind]
        if not path.is_file():
            results[kind] = FetchResult(url=url, status_code=404, body=None)
            continue
        body = path.read_text(encoding="utf-8")
        results[kind] = FetchResult(url=url, status_code=200, body=body, final_url=url)
    return results


def score_l0(html_fetch: FetchResult) -> LayerResult:
    if html_fetch.error:
        return LayerResult("fail", [f"homepage fetch error: {html_fetch.error}"])
    if html_fetch.status_code != 200 or not html_fetch.body:
        return LayerResult(
            "fail",
            [f"homepage HTTP {html_fetch.status_code}"],
        )
    signals = page_signals(html_fetch.body)
    has_title = signals.title is not None
    has_h1 = signals.h1 is not None
    has_canonical = signals.canonical is not None
    evidence = [
        f"title: {signals.title[:MAX_TEXT_EVIDENCE_CHARS]}" if has_title else "missing <title>",
        f"h1: {signals.h1[:MAX_TEXT_EVIDENCE_CHARS]}" if has_h1 else "missing <h1>",
        f"canonical: {signals.canonical[:MAX_URL_EVIDENCE_CHARS]}"
        if has_canonical
        else "no canonical link",
        "meta description present" if signals.has_meta_description else "no meta description",
    ]

    if not (has_title and has_h1):
        status = "fail"
    else:
        status = "ok" if has_canonical and signals.has_meta_description else "weak"
    return LayerResult(
        status,
        evidence,
        {
            "has_title": has_title,
            "has_h1": has_h1,
            "has_canonical": has_canonical,
            "has_meta_description": signals.has_meta_description,
        },
    )


def robots_directives(body: str) -> list[tuple[str, str]]:
    """(field, value) pairs with comments stripped; field names lower-cased."""
    directives: list[tuple[str, str]] = []
    for line in body.lstrip(BYTE_ORDER_MARK).splitlines():
        field_name, separator, value = line.split("#", 1)[0].partition(":")
        if separator:
            directives.append((field_name.strip().lower(), value.strip()))
    return directives


def has_llms_comment(body: str) -> bool:
    return any("llms.txt" in line.partition("#")[2].lower() for line in body.splitlines())


def score_l1(robots: FetchResult) -> LayerResult:
    if robots.error:
        return LayerResult("fail", [f"robots fetch error: {robots.error}"])
    status = robots.status_code
    # RFC 9309 2.3.1: 4xx = unavailable (allow-all), 5xx = unreachable (disallow-all).
    if status is not None and 500 <= status < 600:
        return LayerResult(
            "fail",
            [f"robots.txt HTTP {status}: crawlers must assume a complete disallow (RFC 9309)"],
        )
    if status is not None and 400 <= status < 500:
        return LayerResult(
            "weak",
            [f"robots.txt HTTP {status}: no crawl policy; crawlers treat it as allow-all (RFC 9309)"],
        )
    if status != 200 or robots.body is None:
        return LayerResult("weak", [f"robots.txt HTTP {status}"])

    directives = robots_directives(robots.body)
    sitemap_values = [value for name, value in directives if name == "sitemap" and value]
    sitemaps = [value for value in sitemap_values if value.lower().startswith(("https://", "http://"))]
    agents = [value for name, value in directives if name == "user-agent" and value]
    known = {token.lower() for token in KNOWN_AI_AGENTS}
    ai_hits = sorted({agent for agent in agents if agent.lower() in known})
    evidence = [
        f"Sitemap lines: {len(sitemaps)}",
        f"User-agent groups: {len(agents)}",
    ]
    if len(sitemap_values) > len(sitemaps):
        evidence.append(
            f"ignored {len(sitemap_values) - len(sitemaps)} non-absolute Sitemap value(s)"
        )
    if ai_hits:
        evidence.append("AI-related user-agents: " + ", ".join(ai_hits))
    else:
        evidence.append("no explicit AI user-agent groups (may inherit User-agent: *)")
    if has_llms_comment(robots.body):
        evidence.append("contains llms.txt comment (editor note, not a crawler directive)")

    return LayerResult(
        "ok" if sitemaps else "weak",
        evidence,
        {"sitemaps": sitemaps, "ai_user_agents": ai_hits, "user_agents": agents},
    )


def score_l2(llms: FetchResult) -> LayerResult:
    if llms.error:
        return LayerResult("fail", [f"llms.txt fetch error: {llms.error}"])
    classification = classify_llms(llms.body, status_code=llms.status_code)
    evidence: list[str] = [f"classification: {classification}"]
    details: dict[str, Any] = {"classification": classification}
    if classification == "unavailable":
        evidence.append(f"HTTP {llms.status_code}: could not assess /llms.txt")
        details["http_status"] = llms.status_code
    elif classification != "missing" and llms.body:
        signals = dump_signals(llms.body)
        size = len(llms.body.encode("utf-8"))
        links = absolute_https_links(llms.body)
        markdown_links = markdown_variant_links(links)
        evidence.append(f"size_bytes: {size}")
        evidence.append(f"https_links: {len(links)}")
        evidence.append(f"markdown_links: {len(markdown_links)}")
        if signals:
            evidence.append("dump_signals: " + ", ".join(signals))
        details.update(
            {
                "size_bytes": size,
                "https_links": len(links),
                "markdown_links": len(markdown_links),
                "dump_signals": signals,
            }
        )
        if size > MAX_CURATED_BYTES and classification == "curated":
            evidence.append("warn: curated heuristic prefers ≲ 8 KB")
        if links and not markdown_links and classification == "curated":
            evidence.append(
                "info: no .md link variants (llmstxt.org suggests them where the site publishes them)"
            )

    return LayerResult(L2_STATUS[classification], evidence, details)


def score_l3(html_fetch: FetchResult) -> LayerResult:
    if html_fetch.error:
        return LayerResult("fail", [f"homepage fetch error: {html_fetch.error}"])
    if html_fetch.status_code != 200 or not html_fetch.body:
        return LayerResult("fail", ["homepage unavailable for JSON-LD scan"])
    blocks = page_signals(html_fetch.body).jsonld_blocks
    types = jsonld_types(blocks)
    if not types:
        return LayerResult("fail", ["no application/ld+json blocks found"])
    if all(found == INVALID_JSONLD for found in types):
        return LayerResult("fail", ["JSON-LD present but invalid JSON"])
    evidence = ["@type values: " + ", ".join(sorted(set(types)))]
    overlap = sorted(USEFUL_JSONLD_TYPES.intersection(types))
    has_placeholders = any(
        marker in block for block in blocks for marker in JSONLD_PLACEHOLDER_MARKERS
    )
    status = "ok" if overlap and not has_placeholders else "weak"
    if has_placeholders:
        evidence.append("warn: placeholder values left in JSON-LD (TODO_REPLACE / example.com)")
    if overlap:
        evidence.append("recognized types: " + ", ".join(overlap))
    else:
        evidence.append("JSON-LD found, but no common Organization/Article/WebSite types")
    return LayerResult(status, evidence, {"types": types})


def build_actions(layers: dict[str, LayerResult]) -> list[str]:
    actions: list[str] = []
    l2 = layers["L2"].details.get("classification")
    if l2 == "missing":
        actions.append("Create a curated /llms.txt (see /generate-llms-txt); keep sitemap.xml separate.")
    elif l2 == "dump":
        actions.append(
            "Replace plugin dump /llms.txt with a curated map "
            "(docs/replace-rank-math-llms.md)."
        )
    elif l2 == "unavailable":
        actions.append(
            f"Find out why /llms.txt returns HTTP {layers['L2'].details.get('http_status')} "
            "(server error or bot blocking) and re-run."
        )
    if layers["L3"].status in {"fail", "weak"}:
        actions.append("Add factual JSON-LD (Organization/WebSite/Article) via /draft-json-ld.")
    if layers["L1"].status != "ok":
        actions.append("Ensure robots.txt is reachable and includes a Sitemap: line.")
    if layers["L0"].status != "ok":
        actions.append("Fix homepage title/H1 and consider canonical + meta description.")
    if not actions:
        actions.append("Artifacts look healthy; re-audit after major IA changes.")
    return actions[:5]


def audit_from_fetches(target: str, mode: str, fetches: dict[str, FetchResult]) -> AuditReport:
    layers = {
        "L0": score_l0(fetches["html"]),
        "L1": score_l1(fetches["robots"]),
        "L2": score_l2(fetches["llms"]),
        "L3": score_l3(fetches["html"]),
    }
    ok = all(layer.status != "fail" for layer in layers.values())
    return AuditReport(
        target=target,
        mode=mode,
        layers=layers,
        top_actions=build_actions(layers),
        ok=ok,
    )


def audit_live(url: str, timeout: float) -> AuditReport:
    target = url if "://" in url else f"https://{url}"
    # Validate what the user typed, so credentials or a port are refused, not dropped.
    assert_safe_https_url(target)
    host = urlparse(target).hostname or ""
    origin = f"https://[{host}]" if ":" in host else f"https://{host}"
    paths = {"robots": "/robots.txt", "llms": "/llms.txt", "html": "/"}
    fetches = {
        kind: fetch_https(
            origin + path,
            max_bytes=MAX_BODY_BYTES[kind],
            timeout=timeout,
            origin_host=host,
        )
        for kind, path in paths.items()
    }
    return audit_from_fetches(origin + "/", "live", fetches)


def md_cell(value: str) -> str:
    """Neutralize untrusted text for a single-line Markdown table cell."""
    collapsed = " ".join(value.split())
    return "".join(MARKDOWN_ESCAPES.get(char, char) for char in collapsed if char.isprintable())


def render_markdown(report: AuditReport) -> str:
    lines = [
        "# AIO lint report",
        "",
        f"Target: `{md_cell(report.target)}`",
        f"Mode: `{report.mode}`",
        f"Overall: `{'ok' if report.ok else 'fail'}`",
        "",
        "| Layer | Status | Evidence |",
        "|-------|--------|----------|",
    ]
    for name in ("L0", "L1", "L2", "L3"):
        layer = report.layers[name]
        evidence = "<br>".join(md_cell(item) for item in layer.evidence) or "—"
        lines.append(f"| {name} | {layer.status} | {evidence} |")
    lines.extend(["", "## Top actions", ""])
    for index, action in enumerate(report.top_actions, start=1):
        lines.append(f"{index}. {action}")
    lines.append("")
    lines.append(
        "This report does not guarantee crawling, rankings, citations, or AI-answer inclusion."
    )
    return "\n".join(lines)


def report_to_dict(report: AuditReport) -> dict[str, Any]:
    return {
        "target": report.target,
        "mode": report.mode,
        "ok": report.ok,
        "layers": {
            name: asdict(layer) for name, layer in report.layers.items()
        },
        "top_actions": report.top_actions,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint AIO artifacts (robots.txt, llms.txt, JSON-LD) for a public https site."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("url", nargs="?", help="https site origin or URL")
    source.add_argument(
        "--fixture",
        type=Path,
        help="offline fixture directory with robots.txt, llms.txt, index.html",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON instead of Markdown")
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"per-request timeout seconds (default {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--expect-l2",
        choices=L2_CLASSIFICATIONS,
        help="for fixtures/CI: require this L2 classification (exit 1 on mismatch)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 when overall ok is false (any layer status=fail)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.fixture:
            fixture_dir = args.fixture.resolve()
            if not fixture_dir.is_dir():
                print(f"fixture directory not found: {fixture_dir}", file=sys.stderr)
                return 2
            report = audit_from_fetches(
                f"fixture:{fixture_dir.name}",
                "fixture",
                load_fixture(fixture_dir),
            )
        else:
            report = audit_live(args.url, timeout=args.timeout)
    except ValueError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report_to_dict(report), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))

    if args.expect_l2:
        actual = report.layers["L2"].details.get("classification")
        if actual != args.expect_l2:
            print(
                f"L2 classification mismatch: expected {args.expect_l2}, got {actual}",
                file=sys.stderr,
            )
            return 1

    if args.strict and not report.ok:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
