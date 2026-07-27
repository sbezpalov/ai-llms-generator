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
import html
import ipaddress
import json
import re
import socket
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from aio_heuristics import absolute_https_links, classify_llms, dump_signals

USER_AGENT = (
    "aio-lint/0.1 (+https://github.com/sbezpalov/ai-llms-generator; research)"
)
MAX_REDIRECTS = 3
MAX_BODY_BYTES = {
    "robots": 64 * 1024,
    "llms": 256 * 1024,
    "html": 512 * 1024,
}
DEFAULT_TIMEOUT = 10.0
JSONLD_SCRIPT_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
CANONICAL_RE = re.compile(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
META_DESC_RE = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
SITEMAP_LINE_RE = re.compile(r"(?im)^\s*Sitemap:\s*(\S+)\s*$")
USER_AGENT_LINE_RE = re.compile(r"(?im)^\s*User-agent:\s*(\S+)\s*$")
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
)


@dataclass
class FetchResult:
    url: str
    status_code: int | None
    body: str | None
    error: str | None = None
    final_url: str | None = None


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


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data.strip():
            self._chunks.append(data.strip())

    def text(self) -> str:
        return " ".join(self._chunks)


def strip_tags(fragment: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html.unescape(fragment))
        parser.close()
    except Exception:
        return re.sub(r"<[^>]+>", "", fragment).strip()
    return parser.text()


def is_public_ip(ip_str: str) -> bool:
    ip = ipaddress.ip_address(ip_str)
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
        or (ip.version == 6 and ip.ipv4_mapped and not is_public_ip(str(ip.ipv4_mapped)))
    )


def assert_safe_https_url(url: str, *, allow_hosts: set[str] | None = None) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"only https URLs are allowed: {url}")
    if parsed.username or parsed.password:
        raise ValueError(f"URL credentials are forbidden: {url}")
    if parsed.port not in (None, 443):
        raise ValueError(f"non-default HTTPS ports are forbidden: {url}")
    host = parsed.hostname
    if not host:
        raise ValueError(f"missing host: {url}")
    if host.lower() in {"localhost"} or host.endswith(".localhost"):
        raise ValueError(f"localhost targets are forbidden: {url}")
    if allow_hosts is not None and host.lower() not in allow_hosts:
        raise ValueError(f"redirect/host not on allow-list: {host}")

    try:
        infos = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed for {host}: {exc}") from exc
    if not infos:
        raise ValueError(f"DNS resolution returned no addresses for {host}")
    for info in infos:
        ip = info[4][0]
        if not is_public_ip(ip):
            raise ValueError(f"resolved to non-public IP {ip} for {host}")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Force callers to validate each hop (SSRF-safe redirect handling)."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


_OPENER = urllib.request.build_opener(NoRedirect)


def fetch_https(
    url: str,
    *,
    kind: str,
    timeout: float,
    origin_host: str,
) -> FetchResult:
    allow_hosts = {origin_host.lower()}
    current = url
    try:
        for _ in range(MAX_REDIRECTS + 1):
            assert_safe_https_url(current, allow_hosts=allow_hosts)
            request = urllib.request.Request(
                current,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/plain,text/html,application/json;q=0.9,*/*;q=0.1",
                },
                method="GET",
            )
            try:
                with _OPENER.open(request, timeout=timeout) as response:
                    status = getattr(response, "status", None) or response.getcode()
                    raw = response.read(MAX_BODY_BYTES[kind] + 1)
                    if len(raw) > MAX_BODY_BYTES[kind]:
                        return FetchResult(
                            url=url,
                            status_code=status,
                            body=None,
                            error=f"body exceeds {MAX_BODY_BYTES[kind]} bytes",
                            final_url=current,
                        )
                    charset = response.headers.get_content_charset() or "utf-8"
                    body = raw.decode(charset, errors="replace")
                    return FetchResult(
                        url=url,
                        status_code=status,
                        body=body,
                        final_url=current,
                    )
            except urllib.error.HTTPError as exc:
                if exc.code in {301, 302, 303, 307, 308}:
                    location = exc.headers.get("Location")
                    if not location:
                        return FetchResult(
                            url=url,
                            status_code=exc.code,
                            body=None,
                            error="redirect without Location",
                            final_url=current,
                        )
                    current = urljoin(current, location)
                    continue
                raw = exc.read(MAX_BODY_BYTES[kind]) if exc.fp else b""
                charset = "utf-8"
                if exc.headers:
                    charset = exc.headers.get_content_charset() or "utf-8"
                body = raw.decode(charset, errors="replace") if raw else None
                return FetchResult(
                    url=url,
                    status_code=exc.code,
                    body=body,
                    final_url=current,
                )
        return FetchResult(
            url=url,
            status_code=None,
            body=None,
            error=f"too many redirects (>{MAX_REDIRECTS})",
        )
    except Exception as exc:  # noqa: BLE001 — surface as fetch error
        return FetchResult(url=url, status_code=None, body=None, error=str(exc))


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


def extract_jsonld_types(html_text: str) -> list[str]:
    types: list[str] = []
    for match in JSONLD_SCRIPT_RE.finditer(html_text):
        raw = match.group(1).strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            types.append("(invalid-json)")
            continue
        nodes = data if isinstance(data, list) else [data]
        if isinstance(data, dict) and "@graph" in data and isinstance(data["@graph"], list):
            nodes = data["@graph"]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_type = node.get("@type")
            if isinstance(node_type, list):
                types.extend(str(item) for item in node_type)
            elif node_type:
                types.append(str(node_type))
    return types


def score_l0(html_fetch: FetchResult) -> LayerResult:
    if html_fetch.error:
        return LayerResult("fail", [f"homepage fetch error: {html_fetch.error}"])
    if html_fetch.status_code != 200 or not html_fetch.body:
        return LayerResult(
            "fail",
            [f"homepage HTTP {html_fetch.status_code}"],
        )
    body = html_fetch.body
    evidence: list[str] = []
    title = TITLE_RE.search(body)
    h1 = H1_RE.search(body)
    canonical = CANONICAL_RE.search(body)
    meta_desc = META_DESC_RE.search(body)
    if title:
        evidence.append(f"title: {strip_tags(title.group(1))[:120]}")
    else:
        evidence.append("missing <title>")
    if h1:
        evidence.append(f"h1: {strip_tags(h1.group(1))[:120]}")
    else:
        evidence.append("missing <h1>")
    if canonical:
        evidence.append(f"canonical: {canonical.group(1)}")
    else:
        evidence.append("no canonical link")
    if meta_desc:
        evidence.append("meta description present")
    else:
        evidence.append("no meta description")

    missing_core = (not title) or (not h1)
    status = "fail" if missing_core else ("ok" if canonical and meta_desc else "weak")
    return LayerResult(
        status,
        evidence,
        {
            "has_title": bool(title),
            "has_h1": bool(h1),
            "has_canonical": bool(canonical),
            "has_meta_description": bool(meta_desc),
        },
    )


def score_l1(robots: FetchResult) -> LayerResult:
    if robots.error:
        return LayerResult("fail", [f"robots fetch error: {robots.error}"])
    if robots.status_code == 404 or robots.body is None:
        return LayerResult("fail", ["robots.txt missing (404)"])
    if robots.status_code != 200:
        return LayerResult("weak", [f"robots.txt HTTP {robots.status_code}"])

    body = robots.body
    sitemaps = SITEMAP_LINE_RE.findall(body)
    agents = [match for match in USER_AGENT_LINE_RE.findall(body)]
    ai_hits = sorted(
        {
            agent
            for agent in agents
            if any(token.lower() == agent.lower() for token in KNOWN_AI_AGENTS)
        }
    )
    evidence = [
        f"Sitemap lines: {len(sitemaps)}",
        f"User-agent groups: {len(agents)}",
    ]
    if ai_hits:
        evidence.append("AI-related user-agents: " + ", ".join(ai_hits))
    else:
        evidence.append("no explicit AI user-agent groups (may inherit User-agent: *)")
    if "# " in body and "llms.txt" in body.lower():
        evidence.append("contains llms.txt comment (editor note, not a crawler directive)")

    status = "ok" if sitemaps else "weak"
    return LayerResult(
        status,
        evidence,
        {"sitemaps": sitemaps, "ai_user_agents": ai_hits, "user_agents": agents},
    )


def score_l2(llms: FetchResult) -> LayerResult:
    if llms.error:
        return LayerResult("fail", [f"llms.txt fetch error: {llms.error}"])
    classification = classify_llms(llms.body, status_code=llms.status_code)
    evidence: list[str] = [f"classification: {classification}"]
    details: dict[str, Any] = {"classification": classification}
    if llms.body:
        signals = dump_signals(llms.body)
        size = len(llms.body.encode("utf-8"))
        links = absolute_https_links(llms.body)
        evidence.append(f"size_bytes: {size}")
        evidence.append(f"https_links: {len(links)}")
        if signals:
            evidence.append("dump_signals: " + ", ".join(signals))
        details.update(
            {
                "size_bytes": size,
                "https_links": len(links),
                "dump_signals": signals,
            }
        )
        if size > 8 * 1024 and classification == "curated":
            evidence.append("warn: curated heuristic prefers ≲ 8 KB")

    status_map = {
        "curated": "ok",
        "missing": "fail",
        "empty": "fail",
        "dump": "fail",
        "malformed": "weak",
    }
    return LayerResult(status_map[classification], evidence, details)


def score_l3(html_fetch: FetchResult) -> LayerResult:
    if html_fetch.error:
        return LayerResult("fail", [f"homepage fetch error: {html_fetch.error}"])
    if html_fetch.status_code != 200 or not html_fetch.body:
        return LayerResult("fail", ["homepage unavailable for JSON-LD scan"])
    types = extract_jsonld_types(html_fetch.body)
    if not types:
        return LayerResult("fail", ["no application/ld+json blocks found"])
    if "(invalid-json)" in types and len(set(types)) == 1:
        return LayerResult("fail", ["JSON-LD present but invalid JSON"])
    evidence = ["@type values: " + ", ".join(sorted(set(types)))]
    useful = {"Organization", "WebSite", "WebPage", "Article", "BlogPosting", "Person", "FAQPage"}
    overlap = sorted(useful.intersection(types))
    status = "ok" if overlap else "weak"
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
    parsed = urlparse(url if "://" in url else f"https://{url}")
    if parsed.scheme != "https":
        raise ValueError("target must be an https URL")
    origin = f"https://{parsed.hostname}"
    host = parsed.hostname or ""
    assert_safe_https_url(origin + "/")
    fetches = {
        "robots": fetch_https(f"{origin}/robots.txt", kind="robots", timeout=timeout, origin_host=host),
        "llms": fetch_https(f"{origin}/llms.txt", kind="llms", timeout=timeout, origin_host=host),
        "html": fetch_https(origin + "/", kind="html", timeout=timeout, origin_host=host),
    }
    return audit_from_fetches(origin + "/", "live", fetches)


def render_markdown(report: AuditReport) -> str:
    lines = [
        f"# AIO lint report",
        "",
        f"Target: `{report.target}`",
        f"Mode: `{report.mode}`",
        f"Overall: `{'ok' if report.ok else 'fail'}`",
        "",
        "| Layer | Status | Evidence |",
        "|-------|--------|----------|",
    ]
    for name in ("L0", "L1", "L2", "L3"):
        layer = report.layers[name]
        evidence = "<br>".join(layer.evidence) if layer.evidence else "—"
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
        choices=("missing", "empty", "dump", "curated", "malformed"),
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
            if not args.url:
                print("url or --fixture is required", file=sys.stderr)
                return 2
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
